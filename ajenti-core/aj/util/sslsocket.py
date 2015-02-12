"""
Heavily based on https://github.com/Eugeny/gevent_openssl/blob/master/gevent_openssl/SSL.py
"""

import OpenSSL.SSL
import select
import socket
import sys


class SSLSocket(object):
    def __init__(self, context, sock=None):
        self._context = context
        self.__socket = sock
        self._connection = OpenSSL.SSL.Connection(context, sock)
        self._connection.set_accept_state()
        self._makefile_refs = 0

    def __getattr__(self, attr):
        if attr == '_sock':
            return self
        if attr not in ('_context', '_sock', '_connection', '_makefile_refs'):
            return getattr(self._connection, attr)
        else:
            raise AttributeError

    def __iowait(self, io_func, *args, **kwargs):
        timeout = self.__socket.gettimeout() or 0.1
        fd = self.__socket.fileno()
        while True:
            try:
                return io_func(*args, **kwargs)
            except (OpenSSL.SSL.WantReadError, OpenSSL.SSL.WantX509LookupError):
                sys.exc_clear()
                _, _, errors = select.select([fd], [], [fd], timeout)
                if errors:
                    break
            except OpenSSL.SSL.WantWriteError:
                sys.exc_clear()
                _, _, errors = select.select([], [fd], [fd], timeout)
                if errors:
                    break

    def accept(self):
        _, _, _ = select.select([self.__socket.fileno()], [], [])
        conn, addr = self._connection.accept()
        client = SSLSocket(self._context, connection=conn)
        return client, addr

    def connect(self, *args, **kwargs):
        return self.__iowait(self._connection.connect, *args, **kwargs)

    def sendall(self, data, flags=0):
        try:
            return self.__iowait(self._connection.sendall, data, flags)
        except OpenSSL.SSL.SysCallError as e:
            if e[0] == -1 and not data:
                # errors when writing empty strings are expected and can be ignored
                return 0
            raise

    def send(self, data, flags=0):
        try:
            return self.__iowait(self._connection.send, data, flags)
        except OpenSSL.SSL.SysCallError as e:
            if e[0] == -1 and not data:
                # errors when writing empty strings are expected and can be ignored
                return 0
            raise

    def recv(self, bufsiz, flags=0):
        pending = self._connection.pending()
        if pending:
            return self._connection.recv(min(pending, bufsiz))
        try:
            return self.__iowait(self._connection.recv, bufsiz, flags)
        except OpenSSL.SSL.ZeroReturnError:
            return ''
        except OpenSSL.SSL.SysCallError as e:
            if e[0] == -1 and 'Unexpected EOF' in e[1]:
                # errors when reading empty strings are expected and can be ignored
                return ''
            raise

    def read(self, bufsiz, flags=0):
        return self.recv(bufsiz, flags)

    def write(self, buf, flags=0):
        return self.sendall(buf, flags)

    def close(self):
        if self._makefile_refs < 1:
            self._connection = None
            if self.__socket:
                self.__socket.close()
        else:
            self._makefile_refs -= 1

    def makefile(self, mode='r', bufsize=-1):
        self._makefile_refs += 1
        return socket._fileobject(self, mode, bufsize, close=True)
