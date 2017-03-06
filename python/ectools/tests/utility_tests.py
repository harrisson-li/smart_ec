from os import remove, path
from tempfile import NamedTemporaryFile
from time import sleep

from ectools.config import get_logger
from ectools.internal.data_helper import get_csv_path, get_data_dir
from ectools.utility import *


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


def test_read_csv():
    csv_path = get_csv_path('partners')
    for name, domain, country in read_csv(csv_path, as_dict=False):
        print(name, domain, country)
        assert name == 'Cool'
        assert domain == 'CN'
        break

    for row in read_csv(csv_path, as_dict=True):
        print(row)
        assert row['name'] == 'Cool'
        assert row['domain'] == 'CN'
        break


def test_write_csv_list():
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

    remove(csv_path)


def test_write_csv_dict():
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

    remove(csv_path)


def test_read_text():
    ecdbsql = path.join(get_data_dir(), 'ecdb.sql')
    content = read_text(ecdbsql)
    assert "DROP TABLE IF EXISTS environment" in content
