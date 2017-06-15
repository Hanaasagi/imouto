CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'info': 'white',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
    },
    'formatters': {
        'detailed': {
            'format': '[%(asctime)s] [%(levelname)s] %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'loggers': {
        'info': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}

