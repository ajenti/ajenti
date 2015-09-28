"""
Heavily based on https://github.com/Eugeny/gevent_openssl/blob/master/gevent_openssl/SSL.py
"""

import OpenSSL.SSL
from six import StringIO, PY2, PY3
import select
import socket
import sys
import threading

if PY3:
    import io

    class BytesIOWrapper(io.BufferedRWPair):
        def __init__(self, raw, bufsize):
            io.BufferedRWPair.__init__(self, raw, raw, 1)
            self.__text = io.TextIOWrapper(raw, None, None, None)

        def readline(self, *args, **kwargs):
            # print('>> readline')
            data = self.__text.readline()
            # print('<< ', data)
            return data


class SSLSocket(object):
    def __init__(self, context, sock=None):
        self._context = context
        self.__socket = sock
        self._connection = OpenSSL.SSL.Connection(context, sock)
        self._connection.set_accept_state()
        self._makefile_refs = 0
        self.__send_lock = threading.Lock()

    def __getattr__(self, attr):
        if attr == '_sock':
            return self
        if attr not in ('_context', '_connection', '_makefile_refs'):
            return getattr(self._connection, attr)
        else:
            raise AttributeError

    def __iowait(self, io_func, *args, **kwargs):
        timeout = self.__socket.gettimeout() or 0.1
        fd = self.__socket.fileno()
        while True:
            try:
                # print('>>', io_func.__name__)
                data = io_func(*args, **kwargs)
                # print('<<', io_func.__name__, repr(data))
                return data
            except (OpenSSL.SSL.WantReadError, OpenSSL.SSL.WantX509LookupError):
                if PY2:
                    sys.exc_clear()
                _, _, errors = select.select([fd], [], [fd], timeout)
                if errors:
                    break
            except OpenSSL.SSL.WantWriteError:
                if PY2:
                    sys.exc_clear()
                _, _, errors = select.select([], [fd], [fd], timeout)
                if errors:
                    break

    def accept(self):
        _, _, _ = select.select([self.__socket.fileno()], [], [])
        conn, addr = self._connection.accept()
        client = SSLSocket(self._context, conn)
        return client, addr

    def connect(self, *args, **kwargs):
        return self.__iowait(self._connection.connect, *args, **kwargs)

    def sendall(self, data, flags=0):
        n = 0
        while n < len(data):
            n += self.send(data[n:], flags=flags)
        return n

    def send(self, data, flags=0):
        io = StringIO()
        io.write(data)
        buffer = io.getvalue()

        self.__send_lock.acquire()

        try:
            return self.__iowait(self._connection.send, buffer, flags)
        except OpenSSL.SSL.SysCallError as e:
            if e.args[0] == -1 and not data:
                # errors when writing empty strings are expected and can be ignored
                return 0
            raise
        finally:
            self.__send_lock.release()

    def recv(self, bufsiz, flags=0):
        pending = self._connection.pending()
        if pending:
            return self._connection.recv(min(pending, bufsiz))
        try:
            return self.__iowait(self._connection.recv, bufsiz, flags)
        except OpenSSL.SSL.ZeroReturnError:
            return b''
        except OpenSSL.SSL.SysCallError as e:
            print(e)
            if e.args[0] == -1 and 'Unexpected EOF' in e.args[1]:
                # errors when reading empty strings are expected and can be ignored
                return b''
            raise

    def read(self, bufsiz, flags=0):
        return self.recv(bufsiz, flags)

    def write(self, buf, flags=0):
        return self.sendall(buf, flags)

    def recv_into(self, buffer, nbytes=None, flags=0):
        data = self.recv(nbytes or len(buffer), flags=flags)
        buffer[:len(data)] = data
        return len(data)

    def close(self):
        if self._makefile_refs < 1:
            self._connection = None
            if self.__socket:
                self.__socket.close()
        else:
            self._makefile_refs -= 1

    def makefile(self, mode='r', bufsize=-1):
        self._makefile_refs += 1
        if PY3:
            if bufsize == -1:
                bufsize = io.DEFAULT_BUFFER_SIZE
            raw = socket.SocketIO(self, 'rw')
            return BytesIOWrapper(raw, bufsize)

        # pylint: disable=W0212
        return socket._fileobject(self, mode, bufsize, close=True)
