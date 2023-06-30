from typing import Callable, Any
import asyncio
import functools


def sync(f: Callable[..., asyncio.Future]) -> Callable[..., Any]:
    """
    This is a decorator that allows for synchronous calls to asynchronous functions.
    It runs the event loop until the passed coroutine completes execution, effectively
    making an asynchronous function synchronous.

    Args:
        f (Callable[..., asyncio.Future]): The coroutine function that is to be made synchronous.

    Returns:
        Callable[..., Any]: A function that can be called like a synchronous function and
        will return the result of the completed coroutine.

    Raises:
        Exception: Propagates any exceptions that might occur during the execution of the coroutine.
    """

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))

    return wrapper


def run_coroutine_in_new_loop(coroutine):
    """
    Runs a coroutine in a new event loop.
    """
    new_loop = asyncio.new_event_loop()
    try:
        return new_loop.run_until_complete(coroutine)
    finally:
        new_loop.close()
