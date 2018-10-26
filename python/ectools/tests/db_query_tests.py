from ectools.config import set_environment, set_partner
from ectools.db_query import fetch_all, fetch_one


def test_uat_fetch_one():
    set_environment('uat')
    result = fetch_one(' SELECT top 10 m.DateExpires FROM ET_Commerce.dbo.Subscriptions m (NOLOCK)')
    print(result)
    assert result is not None


def test_uat_query():
    set_environment('uat')
    result = fetch_all('select top 2 * from oboe.dbo.student')
    print(result)
    assert result is not None


def test_qa_query():
    set_environment('qa')
    result = fetch_all('select top 2 * from oboe.dbo.student')
    print(result)
    assert result is not None


def test_live_query():
    # cool / mini / socn will query cn db, other will query us db.
    set_environment('live')
    set_partner('cool')

    result = fetch_all('select top 2 * from oboe.dbo.student WITH(NOLOCK)')
    print(result)
    assert result is not None


def test_no_result():
    set_environment('qa')
    result = fetch_all('select * from oboe.dbo.student where 1>2')
    assert result == []
