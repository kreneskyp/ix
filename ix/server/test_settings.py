from ix.server.settings import *  # noqa:F403
import logging


LOGGING = LOGGING.copy()  # noqa:F405
LOGGING["loggers"] = {
    "ix": {
        "handlers": [],
        "level": logging.DEBUG,
    },
}
