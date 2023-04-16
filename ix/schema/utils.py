import logging
from functools import wraps
from graphql import GraphQLError


logger = logging.getLogger(__name__)


def handle_exceptions(func):
    """Decorator used to log errors"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(e, str(e))
            raise GraphQLError(str(e))

    return wrapper
