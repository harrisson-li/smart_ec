import getpass
import json

import arrow
import requests

from ectools import ecdb_helper as ecdb
from ectools.config import config
from ectools.config import is_api_available
from ectools.internal.objects import Configuration
from ectools.utility import ignore_error


def get_new_account_link(is_e10):
    url = '{}/services/oboe2/salesforce/test/CreateMemberFore14hz?ctr={}&partner={}'
    url = url.format(config.etown_root, config.country_code, config.partner)

    if is_e10:
        return url.replace('e14hz', config.partner)
    else:
        return "{}&v=2".format(url)


def get_activate_account_link(is_e10):
    url = '{}/services/oboe2/salesforce/test/ActivateV2'
    url = url.format(config.etown_root)

    if is_e10:
        return url.replace('V2', 'E10')
    else:
        return url


def get_default_activation_data(product):
    return {'mainRedemptionQty': 3,
            'freeRedemptionQty': 3,
            'startLevel': '0A',
            'levelQty': 16,
            'securityverified': 'on',
            'includesenroll': 'on',
            'productId': product['id'],
            'mainRedemptionCode': product['main_code'],
            'freeRedemptionCode': product['free_code']
            }


def merge_activation_data(source_dict, **more):
    source_dict.update(more)

    for key in ['securityverified', 'includesenroll']:
        if source_dict.get(key, 'on') != 'on':
            del source_dict[key]

    return source_dict


@ignore_error
def get_accounts_by_tag(tag, expiration_days=None):
    """
    Get test accounts with specified tag
    If expiration day provided, will return accounts within expired days.
    """

    if not ecdb._using_remote_db() and is_api_available():
        return _api_get_accounts_by_tag(tag, expiration_days)
    else:
        return _db_get_accounts_by_tag(tag, expiration_days)


def _api_get_accounts_by_tag(tag, expiration_days=None):
    pass


def _db_get_accounts_by_tag(tag, expiration_days=None):
    sql = 'select * from test_accounts where environment like "%{}%"'.format(config.env)
    sql += ' and tags like "%{}%"'.format(tag)

    if expiration_days:
        date = arrow.utcnow().shift(days=-expiration_days).format('YYYY-MM-DD')
        sql += 'and created_on > "{}"'.format(date)

    sql += ' order by created_on desc'

    accounts = []

    for account in ecdb.fetch_all(sql, as_dict=True):
        account.update(json.loads(account['detail']))
        del account['detail']
        accounts.append(account)

    return accounts


def is_account_expired(account, expiration_days):
    date = arrow.utcnow().shift(days=-expiration_days).format('YYYY-MM-DD')
    return account['created_on'] < date


@ignore_error
def save_account(account, *tags):
    """
    Save a test account to ecdb, you can add multiple tags to it.
    """
    if not ecdb._using_remote_db() and is_api_available():
        return _api_save_account(account, *tags)
    else:
        return _db_save_account(account, *tags)


def _api_save_account(account, *tags):
    tags = list(tags)
    tags.append('ectools')
    tags = ','.join(tags)
    created_by = getpass.getuser()

    data = {'add_tags': tags, 'created_by': created_by, 'detail': account, 'env': config.env,
            'member_id': account['member_id']}

    requests.post(Configuration.remote_api + 'save_account', json=data)


def _db_save_account(account, *tags):
    tags = list(tags)
    tags.append('ectools')
    tags = ','.join(tags)
    created_by = getpass.getuser()

    target_table = 'test_accounts'
    search_by = {'member_id': account['member_id'], 'environment': config.env}

    found = ecdb.search_rows(target_table, search_by)
    if found:
        account.update(json.loads(found[0]['detail']))

    ecdb.delete_rows(target_table, search_by)

    ecdb.add_row(target_table,
                 config.env,
                 account['member_id'],
                 account['username'],
                 json.dumps(account),
                 str(arrow.utcnow()),
                 created_by,
                 tags)
