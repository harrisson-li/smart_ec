"""
This module contains some handy function, please refer to bellow function list.

-----
"""
import csv
import inspect
import logging
import random
import sys
import time
from datetime import datetime, timedelta
from functools import wraps
import sys

from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.remote.webdriver import WebDriver

from .internal.objects import Cache, Configuration


def read_csv_as_dict(csv_path):
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def get_random_item(in_seq):
    return random.choice(in_seq)


def get_score(min_score=70, max_score=100):
    """Return a random score in range between min_score and max_score."""
    return random.choice(range(min_score, max_score + 1))


def random_date(start, end, fmt=None):
    """
    If no format specified will use start and end as datetime object.

    Example::

        random_date('2010-1-1', '2012-1-1', '%Y-%m-%d')

        s = datetime.now() + timedelta(days=-29)
        e = datetime.now() + timedelta(days=-1)
        random_date(s, e)

    """

    if fmt:
        start = datetime.strptime(start, fmt)
        end = datetime.strptime(end, fmt)

    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    return start + timedelta(seconds=random.randrange(int_delta))


def detail_on_failure(func):
    """Decorator to log function and arguments detail when on failure."""

    from ectools.config import get_logger

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


def wait_for(method, timeout=Configuration.default_timeout, poll_time=Configuration.default_poll_time):
    """Wait for a method with timeout, return its result or raise error."""

    end_time = time.time() + timeout

    while True:
        try:
            return method()

        except Exception as exc:
            info = (type(exc).__name__, exc.args[0])

        time.sleep(poll_time)
        if time.time() > end_time:
            break

    message = "Timeout to wait for '{}()' in {} seconds.".format(
        method.__name__, timeout)

    if info:
        message += " [%s]: %s" % info

    raise Exception(message)


def try_wait_for(method, timeout=Configuration.default_timeout, poll_time=Configuration.default_poll_time):
    """Try to wait for a method, return its value or return False when failed."""

    from ectools.config import get_logger
    end_time = time.time() + timeout

    while True:
        try:
            return method()

        except Exception as exc:
            get_logger().debug("Try wait for '{}()'. [{}]: {}".format(
                method.__name__, type(exc).__name__, exc.args[0]))

            time.sleep(poll_time)
            if time.time() > end_time:
                break

    get_logger().info("Failed to wait for '{}()', return False.".format(method.__name__))
    return False


def retry_for_error(error, retry_times=Configuration.default_retry_times, poll_time=Configuration.default_poll_time):
    """
    Decorator to retry for specified error.

    Example::

        @retry_for_error(error=RuntimeError)
        def func():
            pass

    """

    def wrapper_(func):
        @retry_for_errors(errors=(error,), retry_times=retry_times, poll_time=poll_time)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return wrapper_


def retry_for_errors(errors, retry_times=Configuration.default_retry_times,
                     poll_time=Configuration.default_poll_time):
    """
    Decorator to retry for multiple errors.

    Example::

        @retry_for_errors(errors=(RuntimeError,NameError))
        def func():
            pass
    """

    from ectools.config import get_logger

    def wrapper_(func):
        @wraps(wrapped=func)
        def wrapper(*args, **kwargs):
            retry = 1
            while retry <= retry_times:
                try:
                    return func(*args, **kwargs)
                except errors as exc:
                    msg = "Retry for {} for {} time...".format(type(exc).__name__, retry)
                    get_logger().info(msg)
                    retry += 1
                    time.sleep(poll_time)

        return wrapper

    return wrapper_


def close_browser(browser_id=None):
    if not browser_id:
        from ectools.config import config
        browser_id = config.browser_id

    if hasattr(Cache, browser_id):
        getattr(Cache, browser_id).quit()
        delattr(Cache, browser_id)


def get_browser(browser_type=Configuration.browser_type, browser_id=None):
    if not browser_id:
        from ectools.config import config
        browser_id = config.browser_id

    if not hasattr(Cache, browser_id):
        LOGGER.setLevel(logging.WARNING)
        browser = getattr(webdriver, browser_type)()
        setattr(Cache, browser_id, browser)
    else:
        browser = getattr(Cache, browser_id)

    if isinstance(browser, WebDriver):
        return browser
    else:
        raise EnvironmentError("Failed to get a browser!")


def convert_to_str(value):
    """Convert a value to str, to work with python2 and python3."""
    if sys.version_info.major == 3:
        return str(value)
    else:
        if type(value) not in (str, unicode):
            return str(value)
        else:
            return value
