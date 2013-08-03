# coding=utf-8
"""
OpenVPN Management API for Python
(http://svn.openvpn.net/projects/openvpn/contrib/dazo/management/management-notes.txt)
"""
__author__ = "Ilya Voronin"
__version__ = "0.1"
__all__ = ['manager']

import socket

CRLF = "\r\n"
PASSWORD_PROMPT = "ENTER PASSWORD:"
STATUS_SUCCESS = "SUCCESS: "
STATUS_ERROR = "ERROR: "
END_MARKER = "END"
NOTIFICATION_PREFIX = ">"


class lsocket(socket.socket):
    """Socket subclass for buffered line-oriented i/o
    @version: 1.0
    @group Line functions: recvl, peekl, sendl, recvuntil
    @group Byte functions: recvb, peekb
    @sort: sendl,recvl,peekl,recvuntil,recvb,peekb
    @ivar _b: Internal read buffer"""
    def __init__(self, *args, **kwargs):
        """Calls superclass constructor and initializes instance variables."""
        super(lsocket, self).__init__(*args, **kwargs)
        self._b = ""

    def sendl(self, line):
        """Adds CRLF to the supplied line and sends it
        @type line: str
        @param line: Line to send"""
        #print "> {0}".format(line)
        self.send(line + CRLF)

    def recvl(self, peek=False):
        """Fills internal buffer with data from socket and returns first found line.
        @type peek: Bool
        @param peek: Keeps line in the buffer if true
        @rtype: str
        @return: First found line"""
        while True:
            i = self._b.find(CRLF)
            if i == -1:
                self._b += self.recv(1024)
            else:
                line = self._b[:i]
                if not peek:
                    self._b = self._b[i+2:]
                #print "{0} {1}".format("?" if peek else ">", line)
                return line

    def recvb(self, count, peek=False):
        """Fills internal buffer with data from socket and returns first B{count} received bytes.
        @type count: int
        @param count: Number of bytes to recieve
        @type peek: Bool
        @param peek: Keeps bytes in the buffer if true
        @rtype: str
        @return: First B{count} received bytes"""
        while True:
            if count > len(self._b):
                self._b += self.recv(count - len(self._b))
            else:
                bytez = self._b[:count]
                if not peek:
                    self._b = self._b[count:]
                #print "{0} {1}".format("?" if peek else ">", bytez)
                return bytez

    def peekb(self, count):
        """Same as peekb(count, peek = True)
        @type count: int
        @param count: Number of bytes to peek
        @rtype: str
        @return: First B{count} received bytes"""
        return self.recvb(count, peek=True)

    def peekl(self):
        """Same as recvl(peek = True)
        @rtype: str
        @return: First found line"""
        return self.recvl(peek=True)

    def recvuntil(self, marker):
        """Returns list of lines received until the line matching the B{marker} was found.
        @type marker: str
        @param marker: Marker
        @rtype: list
        @return: List of strings"""
        lines = []
        while True:
            line = self.recvl()
            if line == marker:
                return lines
            lines.append(line)


class manager(object):
    """OpenVPN Management Client.
    @group Connection: connect,disconnect
    @group Commands: status, stats, killbyaddr, killbycn, signal, messages, pid
    @ivar _host: Hostname or address to connect to
    @ivar _port: Port number to connect to
    @ivar _path: Path to UNIX socket to connect to
    @ivar _password: Password
    @ivar _timeout: Connection timeout
    @ivar _s: Socket object"""
    def __init__(self, host=None, port=None, path=None, password="", timeout=5):
        """Initializes instance variables.
        @type host: str
        @param host: Hostname or address to connect to
        @type port: int
        @param port: Port number to connect to
        @type path: str
        @param path: Path to UNIX socket to connect to
        @type password: str
        @param password: Password
        @type timeout: int
        @param timeout: Connection timeout
        @note: host/port and path should not be specified at the same time """
        assert bool(host and port) ^ bool(path)
        (self._host, self._port, self._path, self._password, self._timeout) = (host, port, path, password, timeout)
        self._s = None

    def connect(self):
        """Initializes and opens a socket. Performs authentication if needed."""
        # UNIX Socket
        if self._path:
            self._s = lsocket(socket.AF_UNIX)
            self._s.settimeout(self._timeout)
            self._s.connect(self._path)
        # IPv4 or IPv6 Socket
        else:
            ai = socket.getaddrinfo(self._host, self._port, 0, socket.SOCK_STREAM)[0]
            self._s = lsocket(ai[0], ai[1], ai[2])
            self._s.settimeout(self._timeout)
            self._s.connect((self._host, self._port))

        # Check if management is password protected
        # We cannot use self.execute(), because OpenVPN uses non-CRLF terminated lines during auth
        if self._s.peekb(len(PASSWORD_PROMPT)) == PASSWORD_PROMPT:
            self._s.recvb(len(PASSWORD_PROMPT))
            self._s.sendl(self._password)
            # Check if OpenVPN asks for password again
            if self._s.peekb(len(PASSWORD_PROMPT)) == PASSWORD_PROMPT:
                self._s.recvb(len(PASSWORD_PROMPT)) # Consume "ENTER PASSWORD:"
                raise Exception("Authentication error")
            else:
                self._s.recvl() # Consume "SUCCESS: " line

    def disconnect(self):
        """Closes a socket."""
        self._s.close()
        self._s = None

    @property
    def connected(self):
        """Returns socket status."""
        return bool(self._s)

    def execute(self, name, *args):
        """Executes command and returns response as a list of lines.
        @type name: str
        @param name: Command name
        @type args: list
        @param args: Argument List
        @rtype: list
        @return: List of strings"""
        cmd = name
        if args:
            cmd += " " + " ".join(args)
        self._s.sendl(cmd)

        # Handle notifications
        while self._s.peekl().startswith(NOTIFICATION_PREFIX):
            self._s.recvl()  # Consume

        # Handle one-line responses
        if self._s.peekl().startswith(STATUS_SUCCESS):
            return [self._s.recvl()[len(STATUS_SUCCESS):]]
        elif self._s.peekl().startswith(STATUS_ERROR):
            raise Exception(self._s.recvl()[len(STATUS_ERROR):])

        # Handle multi-line reponses
        return self._s.recvuntil(END_MARKER)

    def status(self):
        """Executes "status 2" command and returns response as a dictionary.
        @rtype: dict
        @return: Dictionary"""
        status = dict()
        status["clients"] = list()
        # V2 status
        for line in self.execute("status", "2"):
            fields = line.split(",")
            if fields[0] == "TITLE":
                status["title"] = fields[1]
            elif fields[0] == "TIME":
                status["time"] = fields[1]
                status["timeu"] = fields[2]
            elif fields[0] == "HEADER":
                continue
            elif fields[0] == "CLIENT_LIST":
                status["clients"].append(dict(
                    zip(("cn", "raddress", "vaddress", "brecv", "bsent", "connsince", "connsinceu"), fields[1:])
                ))

        return status

    def messages(self):
        """Executes "log all" and returns response as a list of messages.
        Each message is a list of 3 elements: time, flags and text.
        @rtype: list
        @return: List of messages"""
        return map(lambda x: x.split(","), self.execute("log", "all"))

    def killbyaddr(self, addr):
        """Executes "kill IP:port" command and returns response as a string
        @type addr: str
        @param addr: Real address of client to kill (in IP:port format)
        @rtype: str
        @return: Response string"""
        return self.execute("kill", addr)[0]

    def killbycn(self, cn):
        """
        Executes "kill cn" command and returns response as a string
        @type cn: str
        @param cn: Common name of client(s) to kill
        @rtype: str
        @return: Response string
        """
        return self.execute("kill", cn)[0]

    @staticmethod
    def _pgenresp(response):
        """
        Parses generically formatted response (param1=value1,param2=value2,param3=value3)
        @type response: str
        @param response: Response string
        @return: Dictionary
        """
        return dict(map(lambda x: x.split("="), response.split(",")))

    def stats(self):
        """Executes "load-stats" command and returns response as a dictionary:

        >>> print manager.stats()
        {'nclients': '2', 'bytesout': '21400734', 'bytesin': '10129283'}

        @rtype: dict
        @return: Dictionary"""
        return self._pgenresp(self.execute("load-stats")[0])

    def signal(self, signal):
        """Executes "signal" command and returns response as a string.
        @type signal: str
        @param signal: Signal name (SIGHUP, SIGTERM, SIGUSR1 or SIGUSR2)
        @rtype: str
        @return: Response string"""
        assert signal in ["SIGHUP", "SIGTERM", "SIGUSR1", "SIGUSR2"]
        return self.execute("signal", signal)[0]

    def pid(self):
        """Executes "pid" command and returns response as a dictionary.
        @return: Dictionary"""
        return self._pgenresp(self.execute("pid")[0])["pid"]
