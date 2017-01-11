from ectools.utility import *
from time import sleep
from ectools.config import get_logger


def test_get_browser():
    browser = get_browser()
    assert browser.name == 'chrome'
    close_browser()
    browser = get_browser(browser_type='Chrome', browser_id='my')
    assert browser.name == 'chrome'
    close_browser(browser_id='my')


def ok():
    sleep(Cache.timeout)
    return 'ok'


def not_ok():
    sleep(Cache.timeout)
    raise SystemError('so bad!')


def test_wait_for():
    Cache.timeout = 1
    result = wait_for(ok, timeout=2)
    assert result == 'ok'

    try:
        wait_for(not_ok, timeout=2)
    except Exception as e:
        expected_info = "Timeout to wait for 'not_ok()' in 2 seconds. [SystemError]: so bad!"
        get_logger().info(e.args[0])
        assert e.args[0] == expected_info


def test_try_wait_for():
    Cache.timeout = 1
    result = try_wait_for(ok, timeout=2, poll_time=0.1)
    assert result == 'ok'

    result = try_wait_for(not_ok, timeout=2)
    assert not result


def test_retry_for_error():
    @retry_for_error(error=RuntimeError)
    def try_me():
        if getattr(Cache, 'has_tried', False):
            del Cache.has_tried
            return "OK"

        else:
            Cache.has_tried = True
            raise RuntimeError('try again')

    try_me()

    @retry_for_errors(errors=(RuntimeError, NameError))
    def try_me():
        if getattr(Cache, 'try_2', False):
            return "OK"

        elif getattr(Cache, 'try_1', False):
            Cache.try_2 = True
            raise RuntimeError('try 2')

        else:
            Cache.try_1 = True
            raise NameError('try 1')

    try_me()

    def try_me():
        if getattr(Cache, 'has_tried', False):
            return "OK"

        else:
            Cache.has_tried = True
            raise RuntimeError('try again')

    try_me = retry_for_error(error=RuntimeError)(try_me)
    try_me()
