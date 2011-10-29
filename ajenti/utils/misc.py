import subprocess
import threading
import sys


class BackgroundWorker:
    """
    A stoppable background operation.

    Instance vars:

    - ``alive`` - `bool`, if the operation is running
    """
    def __init__(self, *args):
        self.thread = KThread(target=self.__run, args=args)
        self.thread.daemon = True
        self.alive = False
        self.output = ''
        self._aborted = False

    def is_running(self):
        """
        Checks if background thread is running.
        """
        if self.alive:
            return not self.thread.killed
        return False

    def start(self):
        """
        Starts the operation
        """
        if not self.is_running():
            self.thread.start()
        self.alive = True

    def run(self, *args):
        """
        Put the operation body here.
        """

    def __run(self, *args):
        self.run(*args)
        self.alive = False

    def kill(self):
        """
        Aborts the operation thread.
        """
        self._aborted = True
        if self.is_running():
            self.thread.kill()


class BackgroundProcess (BackgroundWorker):
    """
    A class wrapping a background subprocess.
    See :class:`BackgroundWorker`.

    Instance vars:

    - ``output`` - `str`, process' stdout data
    - ``errors`` - `str`, process' stderr data
    - ``exitcode`` - `int`, process' exit code
    - ``cmdline`` - `str`, process' commandline
    """
    def __init__(self, cmd):
        BackgroundWorker.__init__(self, cmd)
        self.output = ''
        self.errors = ''
        self.exitcode = None
        self.cmdline = cmd

    def run(self, c):
        """
        Runs the process in foreground
        """
        self.process = subprocess.Popen(c, shell=True,
                                           stderr=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stdin=subprocess.PIPE)

        self.output += self.process.stdout.readline() # Workaround; waiting first causes a deadlock
        while self.process.returncode is None and not self._aborted:
            self.output += self.process.stdout.readline()
            self.process.poll()
        self.errors += self.process.stderr.read()
        self.output += self.process.stdout.read()
        self.exitcode = self.process.returncode

    def feed_input(self, data):
        """
        Sends stdin to the process
        """
        if self.is_running():
            self.process.stdin.write(data)

    def kill(self):
        """
        Interrupts the process
        """
        if self.is_running():
            try:
                self.process.terminate()
            except:
                pass
            try:
                self.process.kill()
            except:
                pass
            BackgroundWorker.kill(self)


class KThread(threading.Thread):
    """
    A killable Thread class, derived from :class:`threading.Thread`.
    Instance var ``killed`` - `bool`, shows if the thread was killed.
    """

    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        """
        Emits ``SystemExit`` inside the thread.
        """
        self.killed = True
