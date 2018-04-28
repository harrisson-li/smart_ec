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

from ectools import ecdb_helper_v2 as ecdb_v2
from ectools.config import config
from ectools.config import is_api_available
from ectools.internal.objects import Configuration
from ectools.utility import ignore_error
from .constants import HTTP_STATUS_OK

PHOENIX_PACK_MAP = {'Rupe': 1101, 'Ecsp': 1105}
PHOENIX_PROD_MAP = {'Rupe': '01tO0000005UVjlIAG', 'Ecsp': '01tO0000005UVjlIAG'}


def get_new_account_link(is_e10):
    url = '{}/services/oboe2/salesforce/test/CreateMemberFore14hz?ctr={}&partner={}'
    url = url.format(config.etown_root_http, config.country_code, config.partner)

    if is_e10:
        return url.replace('e14hz', config.partner)
    else:
        return "{}&v=2".format(url)


def get_activate_account_link(is_e10):
    url = '{}/services/oboe2/salesforce/test/ActivateV2'
    url = url.format(config.etown_root_http)

    if is_e10:
        return url.replace('V2', 'E10')
    else:
        return url


def get_activate_pack_link():
    url = '{}/services/Oboe2/SalesForce/test/ActivatePack?r=json'
    return url.format(config.etown_root_http)


def get_login_post_link():
    return '{}/login/secure.ashx'.format(config.etown_root)


def get_success_message(student):
    if student['is_phoenix']:
        success_text = '"isSuccess":true'
    elif student['is_e10']:
        success_text = 'success'
    else:
        success_text = 'IsSuccess:True'

    return success_text


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
    # always treat if as disable if not auto determine
    if not auto_determine:
        return False

    # China student will enable Online OC by default, except E10 or some test center turn it off
    if config.partner in ['Cool', 'Mini', 'Socn'] \
            and not student['is_e10'] \
            and 'OnlineOC-Off' not in school['tags'] \
            and student['is_v2']:
        return True

    # Phoenix student will enable Online OC by default
    if student['is_phoenix']:
        return True

    return False


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


def center_pack_activation_data(pack_index):
    return {'PackList[{}].OrderProductId'.format(pack_index): 'CenterPack',
            'PackList[{}].PackageProductId'.format(pack_index): PHOENIX_PACK_MAP[config.partner],
            'PackList[{}].SalesforceProductId'.format(pack_index): PHOENIX_PROD_MAP[config.partner],
            'PackList[{}].TemplateData'.format(pack_index): '{"coupons":[{"name":"F2F","count":5},' +
                                                            '{"name":"WS","count": 5},' +
                                                            '{"name": "LC","count": 5}]}'}


def online_pack_activation_data(pack_index):
    return {'PackList[{}].OrderProductId'.format(pack_index): 'OnlinePack',
            'PackList[{}].PackageProductId'.format(pack_index): PHOENIX_PACK_MAP[config.partner],
            'PackList[{}].SalesforceProductId'.format(pack_index): PHOENIX_PROD_MAP[config.partner],
            'PackList[{}].TemplateData'.format(pack_index): '{"coupons":[{"name":"PL20","count":5},' +
                                                            '{"name":"PL40","count": 5},' +
                                                            '{"name": "GL","count": 5}]}'}


def tweak_activation_data_for_phoenix(data):
    data['OrderId'] = arrow.now().timestamp  # for refund purpose
    data['DaysOfExpiredCouponRetention'] = 30
    data['RedemptionCode'] = data['mainRedemptionCode']
    data['RedemptionQty'] = data['mainRedemptionQty']
    data['ExtendSubscriptionType'] = 'FromExpiredDate'

    to_be_deleted = ['includesenroll', 'mainRedemptionCode', 'mainRedemptionQty',
                     'startLevel', 'levelQty', 'productId', 'freeRedemptionCode',
                     'freeRedemptionQty', 'packageProductIds']

    for key in to_be_deleted:
        data.pop(key, None)

    # workaround: if RedemptionQty <= 12 it probably means months, we update it to days
    qty = int(data['RedemptionQty'])

    if qty <= 12:
        data['RedemptionQty'] = qty * 30


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

    if is_api_available():
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
    sql = "select * from ec_test_accounts where environment like '%{}%'".format(config.env)
    sql += " and tags like '%{}%'".format(tag)

    if expiration_days:
        date = arrow.utcnow().shift(days=-expiration_days).format('YYYY-MM-DD')
        sql += "and created_on > '{}'".format(date)

    sql += " order by created_on desc"

    accounts = ecdb_v2.fetch_all(sql, as_dict=True)
    return [_refine_account(a) for a in accounts]


def is_account_expired(account, expiration_days):
    date = arrow.utcnow().shift(days=-expiration_days).format('YYYY-MM-DD')
    return account['created_on'] < date


@ignore_error
def get_account(member_id):
    if is_api_available():
        return _api_get_account(member_id)
    else:
        return _db_get_account(member_id)


def _api_get_account(member_id):
    data = {'env': config.env, 'username_or_id': member_id}
    response = requests.post(Configuration.remote_api + 'get_account', json=data)

    if response.status_code == HTTP_STATUS_OK:
        return _refine_account(response.json())


def _db_get_account(member_id):
    sql = "select * from ec_test_accounts where environment like '%{}%'".format(config.env)
    sql += " and member_id = {}".format(member_id)
    sql += " order by created_on desc"

    account = ecdb_v2.fetch_one(sql, as_dict=True)

    if account:
        return _refine_account(account)


def get_student_tags(student):
    """Get tags from a student dict."""
    tags = [student['partner'], student['environment']]

    if student['is_e10']:
        tags.append('E10')
    else:
        tags.append('S18' if student['is_s18'] else 'S15')

    if student['is_eclite']:
        tags.append('ECLite')

    if student['is_onlineoc']:
        tags.append('OC')

    if student['is_phoenix']:
        tags.append('Phoenix')

    return tags


@ignore_error
def save_account(account, add_tags=None, remove_tags=None):
    """
    Save a test account to ecdb, you can add or remove multiple tags to it.
    The add_tags and remove_tags should be in list format as ['Tag1', 'Tag2']
    """

    if is_api_available():
        return _api_save_account(account, add_tags, remove_tags)
    else:
        return _db_save_account(account, add_tags, remove_tags)


def _api_save_account(account, add_tags=None, remove_tags=None):
    data = {'detail': account,
            'env': config.env,
            'member_id': int(account['member_id']),
            'created_by': getpass.getuser()}

    if remove_tags:
        removed_tags = ','.join(remove_tags)
        data['remove_tags'] = removed_tags

    if add_tags:
        data['add_tags'] = ','.join(add_tags)

    response = requests.post(Configuration.remote_api + 'save_account', json=data)
    assert response.status_code == HTTP_STATUS_OK, response.text


def _db_save_account(account, add_tags=None, remove_tags=None):
    tags = ['ectools']
    target_table = 'ec_test_accounts'
    existed_account = get_account(account['member_id'])

    if add_tags:
        tags += add_tags

    if existed_account:
        tags += existed_account['tags'].split(',')

        if remove_tags:  # remove tags after fetch existed tags
            tags = (set(tags) - set(remove_tags))

        account['tags'] = ','.join(set(tags))

        search_by = {'member_id': account['member_id'], 'environment': config.env}
        update_dict = {'detail': json.dumps(account),
                       'tags': account['tags'],
                       'created_by': getpass.getuser()}
        ecdb_v2.update_rows(target_table, search_by, update_dict)

    else:

        if remove_tags:
            tags = (set(tags) - set(remove_tags))

        account['tags'] = ','.join(set(tags))
        ecdb_v2.add_row(target_table,
                        config.env,
                        account['member_id'],
                        account['username'],
                        json.dumps(account),
                        arrow.utcnow().format('YYYY-MM-DD HH:mm:ss.SSS'),
                        getpass.getuser(),
                        account['tags'])
