import grp
import json
import logging
import os
import pwd
import gevent
import traceback
import setproctitle
import sys

import aj
from aj.api import *
from aj.api.http import SocketEndpoint
from aj.http import HttpMiddlewareAggregator, HttpContext
from aj.auth import AuthenticationMiddleware
from aj.routing import CentralDispatcher
from aj.log import set_log_params


class WorkerSocketNamespace (object):
    def __init__(self, context, id):
        self.context = context
        self.id = id
        logging.debug('Socket namespace %s created' % self.id)
        self.endpoints = [cls(self.context) for cls in SocketEndpoint.classes()]

    def process_event(self, event, msg):
        for endpoint in self.endpoints:
            if not msg or msg['plugin'] in ['*', endpoint.plugin]:
                data = msg['data'] if msg else None
                try:
                    getattr(endpoint, 'on_%s' % event)(data)
                except Exception as e:
                    logging.error('Exception in socket event handler')
                    traceback.print_exc()

    def destroy(self):
        logging.debug('Socket namespace %s is being destroyed' % self.id)
        for endpoint in self.endpoints:
            endpoint.destroy()


class Worker (object):
    def __init__(self, stream, gate):
        self.stream = stream
        self.gate = gate
        aj.master = False
        os.setpgrp()
        setproctitle.setproctitle('%s session worker #%i' % (sys.argv[0], os.getpid()))
        set_log_params(tag='worker')

        logging.info('New worker #%s, EUID %s, EGID %s' % (
            os.getpid(), os.geteuid(), os.getegid(),
        ))

        self.context = Context(parent=aj.context)
        self.context.session = self.gate.session
        self.context.worker = self
        self.handler = HttpMiddlewareAggregator([
            AuthenticationMiddleware.get(self.context),
            CentralDispatcher.get(self.context),
        ])

        logging.info('Serving client %s' % (
            self.context.session.client_info['address'],
        ))

    def demote(self, username):
        if os.getuid() != 0:
            logging.warn('Running as a limited user, setuid() unavailable!')
            return

        uid = pwd.getpwnam(username).pw_uid
        gid = pwd.getpwnam(username).pw_gid

        logging.info('Worker %s is demoting to %s (UID %s / GID %s)' % (os.getpid(), username, uid, gid))

        groups = [g.gr_gid for g in grp.getgrall() if username in g.gr_mem or g.gr_gid == gid]
        os.setgroups(groups)
        os.setgid(gid)
        os.setuid(uid)
        logging.info('Demoted, EUID %s EGID %s' % (os.geteuid(), os.getegid()))

    def run(self):
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
                        socket_namespaces[nsid] = WorkerSocketNamespace(self.context, nsid)

                    socket_namespaces[nsid].process_event(event, msg)

                    if event == 'disconnect':
                        socket_namespaces[nsid].destroy()
                        logging.debug('Socket disconnected, destroying endpoints')
        except Exception as e:
            logging.error('Worker crashed!')
            traceback.print_exc()

    def terminate(self):
        self.send_to_upstream({
            'type': 'terminate',
        })

    def restart_master(self):
        self.send_to_upstream({
            'type': 'restart-master',
        })

    def handle_http_request(self, rq):
        response_object = {
            'type': 'http',
        }

        try:
            http_context = HttpContext.deserialize(rq.object['context'])

            # Generate response
            content = self.handler.handle(http_context)
            # ---
            response_object['content'] = list(content)
            response_object['status'] = http_context.status
            response_object['headers'] = http_context.headers
            self.stream.reply(rq, response_object)
        except Exception as e:
            traceback.print_exc()
            response_object.update({
                'error': str(e),
                'exception': repr(e),
            })
            self.stream.reply(rq, response_object)

    def send_to_upstream(self, object):
        self.stream.reply(None, object)


class WorkerError (Exception):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return json.dumps(self.response)
