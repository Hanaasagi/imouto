import os
import time
import sys
import signal
import tempfile
import subprocess
import threading
import _thread as thread


def autoload(interval=1):
    """autoload the user code, work as the following control flow
    -----------         -----------
    |         |  poll() |         |
    |  main   |   ==>   |   sub   | exec user code
    | process |   <==   | process |
    |         |  signal |         |
    -----------         -----------
                         ||    /\
                         \/    || if file updated, `thread.interrupt_main()`
                        -----------
                        |         |
                        |  check  |
                        |  file   |
                        |  thread |
                        -----------
    """
    # os.environ['IMOUTO_APP'] is vairable to identify main/sub process
    if not os.environ.get('IMOUTO_APP'):
        try:
            lockfile = None
            fd, lockfile = tempfile.mkstemp(
                prefix='IMOUTO_APP', suffix='.lock')
            os.close(fd)

            while os.path.exists(lockfile):
                args = [sys.executable] + sys.argv
                environ = os.environ.copy()
                environ['IMOUTO_APP'] = 'true'
                environ['IMOUTO_LOCKFILE'] = lockfile

                # execute the code in the same environment
                p = subprocess.Popen(args, env=environ)

                # Check if child process has terminated
                # A None value indicates that the process hasn’t terminated
                # yet.
                while p.poll() is None:
                    # update the modified time
                    os.utime(lockfile, None)
                    time.sleep(interval)

                if p.poll() != 3:
                    if os.path.exists(lockfile):
                        os.unlink(lockfile)
                    sys.exit(p.poll())
        except KeyboardInterrupt:
            print('\nUser Exit[<Ctrl-C>]')
        finally:
            if os.path.exists(lockfile):
                os.unlink(lockfile)
        # no return because it is a function
        sys.exit()

    # elif os.environ.get('IMOUTO_APP_CHECK'):
    #     while True:
    #         time.sleep(2)

    elif os.environ.get('IMOUTO_APP', False):
        def interrupt_handler(signal, frame):
            if not bgcheck.status:
                bgcheck.status = 'exit'
            bgcheck.join()
            if bgcheck.status == 'reload':
                # subprocess exit and send signal 3
                sys.exit(3)
            sys.exit()
        lockfile = os.environ.get('IMOUTO_LOCKFILE')
        bgcheck = FileCheckerThread(lockfile, interval)
        # signal.SIGINT is KeyboardInterrupt singal
        signal.signal(signal.SIGINT, interrupt_handler)
        bgcheck.start()
        # os.environ['IMOUTO_APP_CHECK'] = 'true'
        return

    else:
        # never execute
        assert False


class FileCheckerThread(threading.Thread):

    def __init__(self, lockfile, interval):
        super(FileCheckerThread, self).__init__()
        self.lockfile, self.interval = lockfile, interval
        self.status = None

    def run(self):
        def mtime(path):
            return os.stat(path).st_mtime
        files = dict()

        # get all imported modules and their filepath
        for module in list(sys.modules.values()):
            path = getattr(module, '__file__', '')
            # if file extension are pyo or pyc, change to py
            if path[-4:] in ('.pyo', '.pyc'):
                path = path[:-1]
            if path and os.path.exists(path):
                files[path] = mtime(path)

        while not self.status:
            if not os.path.exists(self.lockfile)\
                    or mtime(self.lockfile) < time.time() - self.interval - 5:
                self.status = 'error'
                thread.interrupt_main()

            # check the all file modified time
            for path, lmtime in list(files.items()):
                if not os.path.exists(path) or mtime(path) > lmtime:
                    self.status = 'reload'
                    # raise a KeyboardInterrupt exception in the main thread.
                    thread.interrupt_main()
                    break
            time.sleep(self.interval)
