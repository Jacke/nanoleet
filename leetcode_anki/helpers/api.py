import functools
import os
import time
from typing import Any, Callable, Tuple, Type, TypeVar
import logging
# https://github.com/prius/python-leetcode
import leetcode.api.default_api  # type: ignore
import leetcode.api_client  # type: ignore
import leetcode.auth  # type: ignore
import leetcode.configuration  # type: ignore

def _get_leetcode_api_client() -> leetcode.api.default_api.DefaultApi:
    """
    Leetcode API instance constructor.

    This is a singleton, because we don't need to create a separate client
    each time
    """
    configuration = leetcode.configuration.Configuration()
    session_id = os.environ["LEETCODE_SESSION_ID"]
    csrf_token = leetcode.auth.get_csrf_cookie(session_id)
    configuration.api_key["x-csrftoken"] = csrf_token
    configuration.api_key["csrftoken"] = csrf_token
    configuration.api_key["LEETCODE_SESSION"] = session_id
    configuration.api_key["Referer"] = "https://leetcode.com"
    configuration.debug = False
    api_instance = leetcode.api.default_api.DefaultApi(
        leetcode.api_client.ApiClient(configuration)
    )
    return api_instance


_T = TypeVar("_T")

class _RetryDecorator:
    _times: int
    _exceptions: Tuple[Type[Exception]]
    _delay: float

    def __init__(
        self, times: int, exceptions: Tuple[Type[Exception]], delay: float
    ) -> None:
        self._times = times
        self._exceptions = exceptions
        self._delay = delay

    def __call__(self, func: Callable[..., _T]) -> Callable[..., _T]:
        times: int = self._times
        exceptions: Tuple[Type[Exception]] = self._exceptions
        delay: float = self._delay

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> _T:
            for attempt in range(times - 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    logging.exception(
                        f"Exception occurred, try %s/%s", attempt + 1, times
                    )
                    time.sleep(delay)

            logging.error("Last try")
            return func(*args, **kwargs)

        return wrapper


def retry(
    times: int, exceptions: Tuple[Type[Exception]], delay: float
) -> _RetryDecorator:
    """
    Retry Decorator
    Retries the wrapped function/method `times` times if the exceptions listed
    in `exceptions` are thrown
    """

    return _RetryDecorator(times, exceptions, delay)
