from ectools.account_helper import *
from ectools.config import set_environment
from ectools.internal import account_service


def test_get_account_by_tag():
    set_environment('live')
    accounts = account_service._db_get_accounts_by_tag('ectools')
    assert len(accounts) > 0

    set_environment('qa')
    accounts = account_service._api_get_accounts_by_tag('UnitTest', expiration_days=365)
    assert len(accounts) > 0


def test_get_account_by_member_id():
    set_environment('live')
    accounts = account_service._db_get_accounts_by_tag('ectools')
    assert len(accounts) > 0

    account = account_service._db_get_account(accounts[0]['member_id'])
    assert account is not None
    assert account['username'] == accounts[0]['username']

    account = account_service._api_get_account(accounts[0]['member_id'])
    assert account is not None
    assert account['username'] == accounts[0]['username']

    account = account_service._db_get_account('invalid')
    assert account == None

    account = account_service._api_get_account('invalid')
    assert account == None


def test_is_account_expired():
    account = {'created_on': str(arrow.utcnow().shift(years=-1, days=-1))}
    assert is_account_expired(account, expiration_days=350)
    assert not is_account_expired(account, expiration_days=370)


def test_save_account():
    set_environment('qa')
    account = get_or_activate_account('UnitTest')

    account_service._api_save_account(account, add_tags=['QA', 'S15'], remove_tags=['ABC'])
    account_service._db_save_account(account, add_tags=['Cool', 'V2'], remove_tags=['ABC'])
