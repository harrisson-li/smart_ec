"""
We should try to access ecdb and test api every time access account service, because on Mac or Linux it does not
support using ecdb in url as: //server/path/to/ecdb.sqlite

so we have code like this::

    if not ecdb._using_remote_db() and is_api_available():
        return _api_get_accounts_by_tag(tag, expiration_days)
    else:
        return _db_get_accounts_by_tag(tag, expiration_days)

"""
import getpass
import json

import arrow
import requests

from ectools import ecdb_helper as ecdb
from ectools.config import config
from ectools.config import is_api_available
from ectools.internal.objects import Configuration
from ectools.utility import ignore_error
from .constants import HTTP_STATUS_OK


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


def get_login_post_link():
    return '{}/login/secure.ashx'.format(config.etown_root).replace('http:', 'https:')


def get_default_activation_data(product):
    return {'mainRedemptionQty': 3,
            'freeRedemptionQty': 3,
            'startLevel': '0A',
            'levelQty': 16,
            'securityverified': 'on',
            'includesenroll': 'on',
            'productId': product['id'],
            'mainRedemptionCode': product['main_code'],
            'freeRedemptionCode': product['free_code'],
            'packageProductIds': ''
            }


def should_enable_onlineoc(auto_determine, student, school):
    return auto_determine \
           and config.partner in ['Cool', 'Mini'] \
           and not student['is_e10'] \
           and 'OnlineOC-Off' not in school['tags']


def merge_activation_data(source_dict, **more):
    source_dict.update(more)

    for key in ['securityverified', 'includesenroll']:

        # when key exist and value == True will update it to 'on'
        if key in source_dict and source_dict[key] == True:
            source_dict[key] = 'on'

        # delete the key when value != 'on'
        if source_dict.get(key, 'on') != 'on':
            del source_dict[key]

    return source_dict


def _refine_account(ecdb_account):
    """Merge the detail fields into account itself, original it is a json string."""
    if 'detail' in ecdb_account:
        ecdb_account.update(json.loads(ecdb_account['detail']))
        del ecdb_account['detail']

    return ecdb_account


@ignore_error
def get_accounts_by_tag(tag, expiration_days=None):
    """
    Get test accounts with specified tag
    If expiration days provided, will return accounts within expired days.
    """

    if not ecdb._using_remote_db() and is_api_available():
        return _api_get_accounts_by_tag(tag, expiration_days)
    else:
        return _db_get_accounts_by_tag(tag, expiration_days)


def _api_get_accounts_by_tag(tag, expiration_days=None):
    data = {'tag': tag,
            'env': config.env,
            'expiration_days': int(expiration_days)}

    response = requests.post(Configuration.remote_api + 'get_accounts_by_tag', json=data)
    assert response.status_code == HTTP_STATUS_OK, response.text
    return response.json()


def _db_get_accounts_by_tag(tag, expiration_days=None):
    sql = 'select * from test_accounts where environment like "%{}%"'.format(config.env)
    sql += ' and tags like "%{}%"'.format(tag)

    if expiration_days:
        date = arrow.utcnow().shift(days=-expiration_days).format('YYYY-MM-DD')
        sql += 'and created_on > "{}"'.format(date)

    sql += ' order by created_on desc'

    accounts = ecdb.fetch_all(sql, as_dict=True)
    return [_refine_account(a) for a in accounts]


def is_account_expired(account, expiration_days):
    date = arrow.utcnow().shift(days=-expiration_days).format('YYYY-MM-DD')
    return account['created_on'] < date


@ignore_error
def get_account(member_id):
    if not ecdb._using_remote_db() and is_api_available():
        return _api_get_account(member_id)
    else:
        return _db_get_account(member_id)


def _api_get_account(member_id):
    data = {'env': config.env, 'username_or_id': member_id}
    response = requests.post(Configuration.remote_api + 'get_account', json=data)

    if response.status_code == HTTP_STATUS_OK:
        return _refine_account(response.json())


def _db_get_account(member_id):
    sql = 'select * from test_accounts where environment like "%{}%"'.format(config.env)
    sql += ' and member_id = "{}"'.format(member_id)
    sql += ' order by created_on desc'

    account = ecdb.fetch_one(sql, as_dict=True)

    if account:
        return _refine_account(account)


@ignore_error
def save_account(account, add_tags=None, remove_tags=None):
    """
    Save a test account to ecdb, you can add or remove multiple tags to it.
    The add_tags and remove_tags should be in list format as ['Tag1', 'Tag2']
    """

    if not ecdb._using_remote_db() and is_api_available():
        return _api_save_account(account, add_tags, remove_tags)
    else:
        return _db_save_account(account, add_tags, remove_tags)


def _api_save_account(account, add_tags=None, remove_tags=None):
    data = {'detail': account,
            'env': config.env,
            'member_id': int(account['member_id'])}

    if remove_tags:
        removed_tags = ','.join(remove_tags)
        data['remove_tags'] = removed_tags

    added_tags = ['ectools']  # always append ectools if save account from here

    if add_tags:
        added_tags.extend(add_tags)

    data['add_tags'] = ','.join(added_tags)

    # only add created_by for new account
    if not get_account(account['member_id']):
        data['created_by'] = getpass.getuser()

    response = requests.post(Configuration.remote_api + 'save_account', json=data)
    assert response.status_code == HTTP_STATUS_OK, response.text


def _db_save_account(account, add_tags=None, remove_tags=None):
    tags = ['ectools']
    target_table = 'test_accounts'
    existed_account = get_account(account['member_id'])

    if add_tags:
        tags += add_tags

    if existed_account:
        tags += existed_account['tags'].split(',')

        if remove_tags:  # remove tags after fetch existed tags
            tags = (set(tags) - set(remove_tags))

        account['tags'] = ','.join(set(tags))

        search_by = {'member_id': account['member_id'], 'environment': config.env}
        update_dict = {'detail': json.dumps(account), 'tags': account['tags']}
        ecdb.update_rows(target_table, search_by, update_dict)

    else:

        if remove_tags:
            tags = (set(tags) - set(remove_tags))

        account['tags'] = ','.join(set(tags))
        ecdb.add_row(target_table,
                     config.env,
                     account['member_id'],
                     account['username'],
                     json.dumps(account),
                     str(arrow.utcnow()),
                     getpass.getuser(),
                     account['tags'])
