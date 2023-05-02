import grp
import json
import logging
import os
import pwd
import gevent
import traceback
import setproctitle
import sys
from gevent.event import Event
from jadi import Context

import aj
from aj.api.http import SocketEndpoint, HttpMiddleware
from aj.http import HttpMiddlewareAggregator, HttpContext
from aj.auth import AuthenticationMiddleware, AuthenticationService
from aj.routing import CentralDispatcher
from aj.log import set_log_params, init_log_forwarding


class WorkerSocketNamespace():
    def __init__(self, context, _id):
        self.context = context
        self.id = _id
        logging.debug(f'Socket namespace {self.id} created')
        self.endpoints = [
            cls(self.context)
            for cls in SocketEndpoint.classes()
        ]

    def process_event(self, event, msg):
        for endpoint in self.endpoints:
            if not msg or msg['plugin'] in ['*', endpoint.plugin]:
                data = msg['data'] if msg else None
                try:
                    getattr(endpoint, f'on_{event}')(data)
                # pylint: disable=W0703
                except Exception:
                    logging.error('Exception in socket event handler')
                    traceback.print_exc()

    def destroy(self):
        logging.debug(f'Socket namespace {self.id} is being destroyed')
        for endpoint in self.endpoints:
            endpoint.destroy()


class Worker():
    def __init__(self, stream, gate):
        aj.worker = self
        self.stream = stream
        self.gate = gate
        aj.master = False
        os.setpgrp()
        setproctitle.setproctitle(f'{sys.argv[0]} worker [{self.gate.name}]')
        set_log_params(tag=self.gate.log_tag)
        init_log_forwarding(self.send_log_event)

        logging.info(
            f'New worker "{self.gate.name}" PID {os.getpid()}, '
            f'EUID {os.geteuid()}, EGID {os.getegid()}'
        )

        self.context = Context(parent=aj.context)
        self.context.session = self.gate.session
        self.context.worker = self
        self.handler = HttpMiddlewareAggregator([
            AuthenticationMiddleware.get(self.context),
            CentralDispatcher.get(self.context),
        ])

        self._master_config_reloaded = Event()

    def demote(self, uid, gid=None):
        try:
            username = pwd.getpwuid(uid).pw_name
            if not gid:
                gid = pwd.getpwuid(uid).pw_gid
        except KeyError:
            username = None
            gid = uid

        if os.getuid() == uid:
            return

        if os.getuid() != 0:
            logging.warning('Running Ajenti as a limited user, setuid() unavailable!')
            return

        logging.info(
            f'Worker {os.getpid()} is demoting to UID {uid} / GID {gid}...'
        )

        groups = [
            g.gr_gid
            for g in grp.getgrall()
            if username in g.gr_mem or g.gr_gid == gid
        ]
        os.setgroups(groups)
        os.setgid(gid)
        os.setuid(uid)
        logging.info(f'...done, new EUID {os.geteuid()} EGID {os.getegid()}')

    def run(self):
        if self.gate.restricted:
            restricted_user = aj.config.data['restricted_user']
            self.demote(pwd.getpwnam(restricted_user).pw_uid)
        else:
            if self.gate.initial_identity:
                AuthenticationService.get(self.context).login(
                    self.gate.initial_identity, demote=True
                )

        try:
            socket_namespaces = {}
            while True:
                rq = self.stream.recv()
                
                if not rq:
                    return

                if rq.object['type'] == 'http':
                    gevent.spawn(self.handle_http_request, rq)

                if rq.object['type'] == 'socket':
                    msg = rq.object['message']
                    nsid = rq.object['namespace']
                    event = rq.object['event']

                    if event == 'connect':
                        socket_namespaces[nsid] = WorkerSocketNamespace(
                            self.context, nsid
                        )

                    socket_namespaces[nsid].process_event(event, msg)

                    if event == 'disconnect':
                        socket_namespaces[nsid].destroy()
                        logging.debug('Socket disconnected, destroying endpoints')

                if rq.object['type'] == 'config-data':
                    logging.debug('Received a config update')
                    aj.config.data = rq.object['data']['config']
                    aj.users.data = rq.object['data']['users']
                    self._master_config_reloaded.set()

                if rq.object['type'] == 'session-list':
                    logging.debug('Received a session list update')
                    aj.sessions = rq.object['data']

                if rq.object['type'] == 'verify-totp':
                    userid = rq.object['data']['userid']
                    result = rq.object['data']['result']
                    aj.tfa_config.verify_totp[userid] = result

                if rq.object['type'] == 'update-tfa-config':
                    aj.tfa_config.data = rq.object['data']

        # pylint: disable=W0703
        except Exception:
            logging.error('Worker crashed!')
            traceback.print_exc()

    def terminate(self):
        self.send_to_upstream({
            'type': 'terminate',
        })

    def change_totp(self, data):
        self.send_to_upstream({
            'type': 'change-totp',
            'data': data,
        })

    def verify_totp(self, userid, code):
        self.send_to_upstream({
            'type': 'verify-totp',
            'userid': userid,
            'code': code,
        })

    def update_sessionlist(self):
        self.send_to_upstream({
            'type': 'update-sessionlist',
        })

    def restart_master(self):
        self.send_to_upstream({
            'type': 'restart-master',
        })

    def reload_master_config(self):
        self.send_to_upstream({
            'type': 'reload-config',
        })
        self._master_config_reloaded.wait()
        self._master_config_reloaded.clear()

    def send_log_event(self, method, message, *args, **kwargs):
        self.send_to_upstream({
            'type': 'log',
            'method': method,
            'message': message % args,
            'kwargs': kwargs,
        })

    def handle_http_request(self, rq):
        response_object = {
            'type': 'http',
        }

        try:
            http_context = HttpContext.deserialize(rq.object['context'].encode())
            logging.debug(
                f'                    ... {http_context.method} {http_context.path}'
            )

            # Generate response
            stack = HttpMiddleware.all(self.context)
            content = HttpMiddlewareAggregator(stack + [self.handler]).handle(http_context)
            # ---

            http_context.add_header('X-Worker-Name', str(self.gate.name))

            response_object['content'] = list(content)
            response_object['status'] = http_context.status
            response_object['headers'] = http_context.headers
            self.stream.reply(rq, response_object)
        # pylint: disable=W0703
        except Exception as e:
            logging.error(traceback.format_exc())
            response_object.update({
                'error': str(e),
                'exception': repr(e),
            })
            self.stream.reply(rq, response_object)

    def send_to_upstream(self, obj):
        self.stream.reply(None, obj)


class WorkerError(Exception):
    def __init__(self, response):
        Exception.__init__(self)
        self.response = response

    def __str__(self):
        return json.dumps(self.response)[:1000]
