"""
This module contains some handy function, please refer to bellow function list.

-----
"""
import csv
import inspect
import logging
import logging.config
import os
import random
import re
import string
import sys
import time
from datetime import datetime, timedelta
from functools import wraps

import arrow
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.remote.webdriver import WebDriver

from .internal.objects import Cache, Configuration

# ignore http insecure request warning, no such module in py27 so try it
try:
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass


def read_csv(csv_path, as_dict=False, skip_header=True):
    """
    Read a csv file then return as dict or list. Example::

        for id, name in read_csv('path/to/csv'):
          print(id, name)

        for row in read_csv('path/to/csv', as_dict=True):
          print(row['id'], row['name'])

    :param csv_path: the path to a csv file
    :param as_dict: return as dict instead of list
    :param skip_header: skip the header row
    :return:
    """
    with open(csv_path) as f:

        if as_dict:
            reader = csv.DictReader(f)
        else:
            reader = csv.reader(f)
            if skip_header:
                next(reader)

        for row in reader:
            yield row


def _get_csv_open_args(csv_path, mode):
    """
    http://stackoverflow.com/questions/3348460/csv-file-written-with-python-has-blank-lines-between-each-row
    """
    args = {'mode': mode}

    if sys.version_info[0] == 3:
        args['newline'] = ''
        args['file'] = csv_path
        args['encoding'] = 'utf-8'
    else:
        args['mode'] = mode + 'b'
        args['name'] = csv_path

    return args


def write_csv_row(row, csv_path, from_dict=False):
    """Write a row of data to csv from list or dict, append if existed."""
    with open(**_get_csv_open_args(csv_path, 'a')) as f:

        if from_dict:
            headers = row.keys()
            writer = csv.DictWriter(f, headers)
            writer.writeheader()
        else:
            writer = csv.writer(f)

        writer.writerow(row)


def write_csv_rows(rows, csv_path, headers=None, from_dict=False):
    """Write many rows of data to csv, always overwrite existed file."""
    with open(**_get_csv_open_args(csv_path, 'w')) as f:

        if from_dict:
            if not headers:
                headers = rows[0].keys()

            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

        else:
            writer = csv.writer(f)

            if headers:
                writer.writerow(headers)

        writer.writerows(rows)


def get_random_item(in_seq):
    return random.choice(list(in_seq))


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

    from ectools.logger import get_logger

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


def wait_for(method, return_as=None, timeout=Configuration.default_timeout, poll_time=Configuration.default_poll_time):
    """
    Wait for a method with timeout until method return as you expected value, return its result or raise error.
    If return_as validator is not provided, the expecting result should NOT be False or equal to False.
    """

    end_time = time.time() + timeout
    info = None

    while True:
        try:
            value = method()
            if not return_as:
                if value:
                    return value
            else:
                if return_as(value):
                    return value

        except Exception as exc:
            args_as_str = [convert_to_str(x) for x in exc.args]
            info = (type(exc).__name__, ','.join(args_as_str))

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

    from ectools.logger import get_logger
    end_time = time.time() + timeout

    while True:
        try:
            value = method()
            if value:
                return value

        except Exception as exc:
            args_as_str = [convert_to_str(x) for x in exc.args]
            get_logger().debug("Try wait for '{}()'. [{}]: {}".format(
                method.__name__, type(exc).__name__, ','.join(args_as_str)))

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

    from ectools.logger import get_logger
    assert retry_times > 0, 'retry_times must larger than 0!'

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

                    if retry > retry_times:
                        raise exc
                    else:
                        time.sleep(poll_time)

        return wrapper

    return wrapper_


def ignore_error(func):
    """Decorator to ignore all errors for a function."""

    @wraps(wrapped=func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            from ectools.logger import get_logger
            get_logger().warn("Ignore error for function: {} - [{}]:{}"
                              .format(func.__name__, type(e).__name__, e.args))

    return wrapper


def close_browser(browser_id=None):
    if not browser_id:
        from ectools.config import config
        browser_id = config.browser_id

    if hasattr(Cache, browser_id):
        getattr(Cache, browser_id).quit()
        delattr(Cache, browser_id)


def get_browser(browser_type=Configuration.browser_type, browser_id=None, headless=None):
    from ectools.config import config

    if not browser_id:
        browser_id = config.browser_id

    if not hasattr(Cache, browser_id):
        LOGGER.setLevel(logging.WARNING)
        if browser_type == 'Chrome':
            options = Options()
            options.add_argument('--disable-infobars')

            if headless == None:
                headless = config.browser_headless

            if headless:
                options.add_argument('--no-sandbox')
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument('--window-size=1280x1024')
                options.add_argument('--ignore-certificate-errors')

            browser = webdriver.Chrome(options=options)
        else:
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


def read_text(path, encoding=None, errors=None):
    """
    Open the file in text mode, read it, and close the file.
    """
    with open(path, mode='r', encoding=encoding, errors=errors) as f:
        return f.read()


def camelcase_to_underscore(name):
    """Convert a string from CamelCase to camel_case, which will be useful for dict keys."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def no_ssl_requests():
    """get requests instance without SSL verify."""
    from ectools.config import config
    s = requests.Session()

    if config.domain == 'CN':
        referer_url = '{}/partner/englishcenters/cn?z=1234567'.format(config.etown_root)
    else:
        referer_url = '{}/partner/englishcenters?z=1234567'.format(config.etown_root)

    s.headers = {
        'User-Agent': 'Mozilla (Windows NT 10.0; Win64; x64) AppleWebKit (KHTML, like Gecko) Chrome Safari',
        'Referer': referer_url
    }

    s.verify = False

    return s


def get_pkg_version(name='ectools'):
    """Get current version of a installed pip package."""
    import pkg_resources

    try:
        return pkg_resources.require(name)[0].version
    except pkg_resources.DistributionNotFound:
        return None


def get_python_cmd():
    """Get current running python.exe"""
    return sys.executable


def update_pkg(name='ectools', *args):
    """Update a pypi package with pip."""

    arguments = [get_python_cmd(), '-m pip install -U', name]
    arguments.extend(args)

    if name in ['ectools', 'ef-common']:
        arguments.append('--extra-index-url http://10.179.237.165:8081/pypi')
        arguments.append('--trusted-host 10.179.237.165')

    cmd = ' '.join(arguments)

    print('Update {}: \n{}\n'.format(name, cmd))
    os.system(cmd)


def ensure_safe_query(sql):
    """Should not allow dangerous query."""
    sql = sql.lower()

    if 'select ' in sql:
        assert 'top' in sql or 'where' in sql, 'Do not allow SELECT without TOP or WHERE!'

    if 'update ' in sql:
        assert 'where' in sql, 'Do not allow UPDATE without WHERE!'

    if 'delete ' in sql:
        assert 'where' in sql, 'Do not allow DELETE without WHERE!'


def is_corp_net():
    """Check current network is in corporation intranet."""
    try:
        no_ssl_requests().get(Configuration.version_url, timeout=2)
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False


def config_sys_logging(to_console=True, log_file_dir=None, log_file_name=None):
    """
    Simplify sys logging configuration, call this method to use sys.logging module methods.
    :param to_console: will output log to console.
    :param log_file_dir: if set will output log to specified directory, else will not write log to file.
    :param log_file_name: if not set, will use default log file pattern: YYYY-MM-DD.log
    :return:
    """
    handlers = []

    if to_console:
        handlers.append('console')

    if log_file_dir:
        handlers.append('file')

    if not log_file_name:
        log_file_name = arrow.utcnow().format('YYYY-MM-DD.log')

    if not log_file_dir:
        log_file_dir = '.'

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(levelname)-7s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'formatter': 'default',
                'filename': os.path.join(log_file_dir, log_file_name),
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            '': {
                'handlers': handlers,
                'level': 'DEBUG'
            }
        }
    })
    return logging.getLogger()


def password_generator(password_length=8):
    letters_digits = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.sample(letters_digits, password_length))
