from ix.server.settings import *


LOGGING = LOGGING.copy()
LOGGING["loggers"] = {
    "ix": {
        "handlers": [],
        "level": logging.DEBUG,
    },
}
