#
# Copyright (C) 2010-2013 Vinay Sajip. All rights reserved.
#
import sys
import ctypes
import logging
import logging.config
import os


try:
    unicode
except NameError:
    unicode = None

class ColorizingStreamHandler(logging.StreamHandler):
    """
    A stream handler which supports colorizing of console streams
    under Windows, Linux and Mac OS X.
    :param strm: The stream to colorize - typically ``sys.stdout``
                 or ``sys.stderr``.
    Common usage is to derive a new class and set the level_map
    class ColorLog(ColorizingStreamHandler):
        def __init__(self, *args, **kwargs):
            super(ColorLog, self).__init__(*args, **kwargs)
            self.level_map = {
                #logger: bg, fg, bold
                logging.DEBUG: (None, 'blue', True),
                logging.INFO: (None, 'white', False),
                logging.WARNING: (None, 'yellow', True),
                logging.ERROR: (None, 'red', True),
                logging.CRITICAL: ('red', 'white', True),
            }

    then use this class as your handler
    """
    def __init__(self, *args, **kwargs):

        #levels to (background, foreground, bold/intense)
        if os.name == 'nt':
            self.level_map = {
                logging.DEBUG: (None, 'blue', True),
                logging.INFO: (None, 'white', False),
                logging.WARNING: (None, 'yellow', True),
                logging.ERROR: (None, 'red', True),
                logging.CRITICAL: ('red', 'white', True),
            }
        else:
            "Maps levels to colour/intensity settings."
            self.level_map = {
                logging.DEBUG: (None, 'blue', False),
                logging.INFO: (None, 'white', False),
                logging.WARNING: (None, 'yellow', False),
                logging.ERROR: (None, 'red', False),
                logging.CRITICAL: ('red', 'white', True),
            }

        return super(ColorizingStreamHandler, self).__init__()

    # color names to indices
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }
    csi = '\x1b['
    reset = '\x1b[0m'

    @property
    def is_tty(self):
        "Returns true if the handler's stream is a terminal."
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if unicode and isinstance(message, unicode):
                enc = getattr(stream, 'encoding', 'utf-8')
                message = message.encode(enc, 'replace')
            if not self.is_tty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    if os.name != 'nt':
        def output_colorized(self, message):
            """
            Output a colorized message.
            On Linux and Mac OS X, this method just writes the
            already-colorized message to the stream, since on these
            platforms console streams accept ANSI escape sequences
            for colorization. On Windows, this handler implements a
            subset of ANSI escape sequence handling by parsing the
            message, extracting the sequences and making Win32 API
            calls to colorize the output.
            :param message: The message to colorize and output.
            """
            self.stream.write(message)
    else:
        import re
        ansi_esc = re.compile(r'\x1b\[((?:\d+)(?:;(?:\d+))*)m')

        nt_color_map = {
            0: 0x00,    # black
            1: 0x04,    # red
            2: 0x02,    # green
            3: 0x06,    # yellow
            4: 0x01,    # blue
            5: 0x05,    # magenta
            6: 0x03,    # cyan
            7: 0x07,    # white
        }

        def output_colorized(self, message):
            """
            Output a colorized message.
            On Linux and Mac OS X, this method just writes the
            already-colorized message to the stream, since on these
            platforms console streams accept ANSI escape sequences
            for colorization. On Windows, this handler implements a
            subset of ANSI escape sequence handling by parsing the
            message, extracting the sequences and making Win32 API
            calls to colorize the output.
            :param message: The message to colorize and output.
            """
            parts = self.ansi_esc.split(message)
            write = self.stream.write
            h = None
            fd = getattr(self.stream, 'fileno', None)
            if fd is not None:
                fd = fd()
                if fd in (1, 2): # stdout or stderr
                    h = ctypes.windll.kernel32.GetStdHandle(-10 - fd)
            while parts:
                text = parts.pop(0)
                if text:
                    write(text)
                if parts:
                    params = parts.pop(0)
                    if h is not None:
                        params = [int(p) for p in params.split(';')]
                        color = 0
                        for p in params:
                            if 40 <= p <= 47:
                                color |= self.nt_color_map[p - 40] << 4
                            elif 30 <= p <= 37:
                                color |= self.nt_color_map[p - 30]
                            elif p == 1:
                                color |= 0x08 # foreground intensity on
                            elif p == 0: # reset to default color
                                color = 0x07
                            else:
                                pass # error condition ignored
                        ctypes.windll.kernel32.SetConsoleTextAttribute(h, color)

    def colorize(self, message, record):
        """
        Colorize a message for a logging event.
        This implementation uses the ``level_map`` class attribute to
        map the LogRecord's level to a colour/intensity setting, which is
        then applied to the whole message.
        :param message: The message to colorize.
        :param record: The ``LogRecord`` for the message.
        """
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append('1')
            if params:
                message = ''.join((self.csi, ';'.join(params),
                                   'm', message, self.reset))
        return message

    def format(self, record):
        """
        Formats a record for output.
        This implementation colorizes the message line, but leaves
        any traceback unolorized.
        """
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            if record.levelno == logging.ERROR:
                # Don't colorize any traceback
                parts = message.split('\nTraceback', 1)
                parts[0] = self.colorize(parts[0], record)
                return '\nTraceback'.join(parts)
            else:
                return self.colorize(message, record)
        return message


class ColorHandler(ColorizingStreamHandler):

    def __init__(self, *args, **kwargs):
        super(ColorHandler, self).__init__(*args, **kwargs)
        self.level_map = {
            # Provide you custom coloring information here
            logging.DEBUG: (None, 'cyan', False),
            logging.INFO: (None, 'magenta', False),
            logging.WARNING: (None, 'yellow', False),
            logging.ERROR: (None, 'red', False),
            logging.CRITICAL: ('red', 'white', True),
}


CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'simple': {
            '()': ColorHandler,
            'info': 'white',
            'level': 'DEBUG',
            'formatter': 'simple',
            'stream': sys.stdout,
        },
        'access': {
            '()': ColorHandler,
            'info': 'white',
            'level': 'DEBUG',
            'formatter': 'access',
            'stream': sys.stdout,
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(levelname)s] %(asctime)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'access': {
            'format': '[%(method)s] %(asctime)s [%(status)d] %(path)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'loggers': {
        'imouto.access': {
            'level': 'DEBUG',
            'handlers': ['access'],
        },
        'imouto.application': {
            'level': 'DEBUG',
            'handlers': ['simple'],
        },
    },
}

logging.config.dictConfig(CONFIG)
# Logger objects
access_log = logging.getLogger("imouto.access")
app_log = logging.getLogger("imouto.application")
