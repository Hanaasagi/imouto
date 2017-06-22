import sys
import logging
import logging.config


class ColorizingStreamHandler(logging.StreamHandler):

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

    def __init__(self, *args, **kwargs):
        """override this method in subclass can customize color"""
        self.level_map = {
            logging.DEBUG: (None, 'blue', False),
            logging.INFO: (None, 'white', False),
            logging.WARNING: (None, 'yellow', False),
            logging.ERROR: (None, 'red', False),
            logging.CRITICAL: ('red', 'white', True),
        }
        super().__init__()

    @property
    def is_tty(self):
        """Returns true if the handler's stream is a terminal."""
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            self.stream.write(message)
            self.stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def colorize(self, message, record):
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
                message = '{}{}m{}{}'.format(self.csi, ';'.join(params),
                                             message, self.reset)
        return message

    def format(self, record):
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
        super().__init__(*args, **kwargs)
        self.level_map = {
            logging.DEBUG: (None, 'cyan', False),
            logging.INFO: (None, 'magenta', False),
            logging.WARNING: (None, 'yellow', False),
            logging.ERROR: (None, 'red', False),
            logging.CRITICAL: ('red', 'white', True),
        }


DEFAULT_LOGGING = {
    'version': 1,
    'handlers': {
        'simple': {
            '()': ColorHandler,
            'formatter': 'simple',
            'stream': sys.stdout,
        },
        'access': {
            '()': ColorHandler,
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
            'format': ('[%(method)s] %(asctime)s [%(status)d] '
                       '%(path)s %(message)s'),
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

# Logger objects
access_log = logging.getLogger("imouto.access")
app_log = logging.getLogger("imouto.application")

if __name__ == '__main__':
    logging.config.dictConfig(DEFAULT_LOGGING)
    app_log.debug("Hello world")     # output should be in blue
    app_log.info("Hello world")      # output should be in green
    app_log.warn("Hello world")      # output should be in yellow
    app_log.error("Hello world")     # output should be in red
    # output should be in white with a red back ground
    app_log.critical("Hello world")
