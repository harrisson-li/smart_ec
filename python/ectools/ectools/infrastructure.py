import inspect
import time
from functools import wraps

from ectools.config import get_logger

TIMEOUT_SECONDS = 60
POLL_TIME = 1
MAX_RETRY_TIMES = 3


def detail_on_failure(func):
    """Decorator to log function and arguments detail when on failure."""

    @wraps(wrapped=func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            argspec = inspect.getargspec(func)
            args_map = {}
            if argspec.defaults is not None:
                args_map.update(dict(zip(reversed(argspec.args), reversed(argspec.defaults))))

            args_map.update(dict(zip(argspec.args, args)))

            if argspec.varargs is not None:
                args_map[argspec.varargs] = args[len(argspec.args):]

            if argspec.keywords is not None:
                args_map[argspec.keywords] = kwargs

            def dump():
                detail = ""
                for key, value in args_map.items():
                    if key != 'self':  # ignore 'self' as it is not useful
                        detail += "{}={}, ".format(key, value)
                return detail[:-2:]

            message = "Failure when calling {}({})".format(func.__name__, dump())
            get_logger().warn(message)
            raise

    return wrapper


def wait_for(method, message='', timeout=TIMEOUT_SECONDS):
    """Function to wait for a method with timeout."""
    stack_trace = None
    end_time = time.time() + timeout
    while True:
        try:
            value = method()
            if value:
                return value
        except BaseException as exc:
            stack_trace = getattr(exc, 'stacktrace', None)
        time.sleep(POLL_TIME)
        if time.time() > end_time:
            break
    message = "{}\nTimeout to wait for {} in {} seconds.\n{}".format(
        message, method.__name__, timeout, stack_trace)
    raise Exception(message)


def retry_for_error(error, retry_times=MAX_RETRY_TIMES, poll_time=POLL_TIME):
    """Decorator to retry for specified error."""

    def wrapper_(func):
        @wraps(wrapped=func)
        def wrapper(*args, **kwargs):
            retry = 1
            while retry <= retry_times:
                try:
                    return func(*args, **kwargs)
                except error:
                    msg = "retry for {} for {} time...".format(error.__name__, retry)
                    get_logger().info(msg)
                    retry += 1
                    time.sleep(poll_time)

        return wrapper

    return wrapper_
