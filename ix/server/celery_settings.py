from ix.server.settings import *  # noqa:F403
import logging


# use celery logging settings
LOGGING = LOGGING.copy()  # noqa:F405
LOGGING["loggers"] = {
    "ix": {
        "handlers": [],
        "level": logging.DEBUG,
    },
}
