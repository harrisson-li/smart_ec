from ectools.config import set_environment
from ectools.dbquery_helper import fetch_one, fetch_all, execute_query, ensure_safe_query


def test_fetch_one():
    set_environment('qa')
    sql = 'select top 10 * from oboe.dbo.student'
    result = fetch_one(sql)
    print(result)
    assert len(result) == 1


def test_fetch_all():
    set_environment('qa')
    sql = 'select top 10 * from oboe.dbo.student'
    result = fetch_all(sql)
    print(result)
    assert len(result) == 10


def test_query_bad_sql():
    set_environment('qa')
    sql = 'not a sql!'
    try:
        fetch_one(sql)
    except ValueError as e:
        expected = "Query Error: Incorrect syntax near the keyword 'not'."
        assert e.args[0] == expected
    else:
        assert False, 'should raise error!'


def test_execute_query():
    set_environment('qa')
    sql = 'UPDATE oboe.dbo.Booking SET IsDeleted=1 WHERE Booking_id=30000000'
    result = execute_query(sql)
    assert result == '2 rows affected.'


def test_ensure_safe_query():
    try:
        ensure_safe_query('select *from table')
    except AssertionError as e:
        assert e.args[0] == 'Do not allow SELECT without TOP or WHERE!'
    else:
        assert False

    try:
        ensure_safe_query('update table')
    except AssertionError as e:
        assert e.args[0] == 'Do not allow UPDATE without WHERE!'
    else:
        assert False

    try:
        ensure_safe_query('delete table')
    except AssertionError as e:
        assert e.args[0] == 'Do not allow DELETE without WHERE!'
    else:
        assert False
