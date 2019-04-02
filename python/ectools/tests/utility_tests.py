from os import remove, path
from tempfile import NamedTemporaryFile
from time import sleep

from ectools.logger import get_logger
from ectools.ecdb_helper import _get_data_dir
from ectools.utility import *


def test_get_browser():
    browser = get_browser()
    assert browser.name == 'chrome'
    browser.get('http://ec.ef.com')
    close_browser()

    browser = get_browser(browser_type='Chrome', browser_id='my')
    assert browser.name == 'chrome'
    close_browser(browser_id='my')

    browser = get_browser(browser_type='Chrome', browser_id='my', headless=True)
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


def foo(*args):
    return args


def bar(**kwargs):
    return 'no kwargs!' if kwargs == {} else None


def bar2(**kwargs):
    return kwargs


def void_func():
    get_logger().info("This is void function")


def test_wait_for_return_as():
    value = wait_for(method=lambda: foo(1, 2, 3), return_as=lambda r: r is not None)
    assert value == (1, 2, 3)

    value = wait_for(method=lambda: foo(True), return_as=lambda r: r is not None)
    assert value == (1,)

    value = wait_for(bar2, return_as=lambda r: r == {})
    assert value == {}

    value = wait_for(void_func, return_as=lambda r: r is None)
    assert value is None


def test_wait_for_value():
    value = wait_for(lambda: foo(1, 2, 3))
    assert value == (1, 2, 3)

    value = wait_for(lambda: foo(1), timeout=5)
    assert value == (1,)

    value = wait_for(bar, timeout=5, poll_time=1)
    assert value == 'no kwargs!'

    value = wait_for(lambda: bar(a=1, b=2, c=3) is None)
    assert value == True  # note: lambada will return True, but the return of function is None


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


def test_read_write_csv_list():
    header = ['first', 'last']
    row = ['toby', 'qin']
    csv_path = NamedTemporaryFile(delete=False).name
    write_csv_row(header, csv_path)
    write_csv_row(row, csv_path)

    for first, last in read_csv(csv_path):
        assert first == 'toby'

    rows = [['toby', 'qin'], ['ef', 'labs']]
    write_csv_rows(rows, csv_path, header)

    result = list(read_csv(csv_path))
    assert result[1][0] == 'ef'
    assert result[1][1] == 'labs'

    for first, last in read_csv(csv_path, as_dict=False):
        print(first, last)
        assert first == 'toby'
        assert last == 'qin'
        break

    remove(csv_path)


def test_read_write_csv_dict():
    row = {'first': 'toby', 'last': 'qin'}
    csv_path = NamedTemporaryFile(delete=False).name
    write_csv_row(row, csv_path, from_dict=True)

    for row in read_csv(csv_path, as_dict=True):
        assert row['first'] == 'toby'

    rows = [{'first': 'toby', 'last': 'qin'}, {'first': 'ef', 'last': 'labs'}]
    write_csv_rows(rows, csv_path, from_dict=True)

    result = list(read_csv(csv_path, as_dict=True))
    assert result[1]['first'] == 'ef'
    assert result[1]['last'] == 'labs'

    for row in read_csv(csv_path, as_dict=True):
        print(row)
        assert row['first'] == 'toby'
        assert row['last'] == 'qin'
        break

    remove(csv_path)


def test_read_text():
    ecdbsql = path.join(_get_data_dir(), 'ecdb.sql')
    content = read_text(ecdbsql)
    assert "DROP TABLE IF EXISTS environment" in content


def test_get_pkg_version():
    v = get_pkg_version()
    assert v is not None

    v = get_pkg_version('requests')
    assert v is not None


def test_get_python_cmd():
    cmd = get_python_cmd()
    assert cmd is not None


def test_update_pkg():
    update_pkg('ectools')
    update_pkg('requests')


def test_config_sys_logging():
    config_sys_logging(log_file_dir='.')
    logging.debug('hello')

    config_sys_logging(to_console=False, log_file_dir='.')
    logging.info('hi')

    config_sys_logging(log_file_dir='.', log_file_name='test_unicode.log')
    logging.info('你好')
