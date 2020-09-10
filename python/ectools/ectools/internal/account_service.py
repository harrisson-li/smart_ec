"""
We will try to use ecdb_v2 locally for account service, if not working we will use api (for MacOS / Linux)

so we have code like this::

    if ecdb_v2.is_db_available():
        return _api_get_accounts_by_tag(tag, expiration_days)
    else:
        return _db_get_accounts_by_tag(tag, expiration_days)

"""
import getpass
import json

import arrow

from ectools import ecdb_helper_v2 as ecdb_v2
from ectools.config import config
from ectools.ecdb_helper_v2 import get_config_value
from ectools.internal.data_helper import get_phoenix_pack
from ectools.internal.objects import Configuration
from ectools.service_helper import account_service_update_info, get_student_active_subscription
from ectools.token_helper import get_token
from ectools.utility import ignore_error, no_ssl_requests
from .constants import HTTP_STATUS_OK


def append_token(url, join_by='&'):
    url += join_by + 'token=' + get_token()

    return url


def get_new_account_link(is_e10):
    url = '{}/services/oboe2/salesforce/test/CreateMemberFore14hz?ctr={}&partner={}'
    url = url.format(config.etown_root, config.country_code, config.partner)

    if is_e10:
        url = url.replace('e14hz', config.partner)
    else:
        url = "{}&v=2".format(url)

    return append_token(url)


def get_activate_account_link(is_e10):
    url = '{}/services/oboe2/salesforce/test/ActivateV2'
    url = url.format(config.etown_root)

    if is_e10:
        url = url.replace('V2', 'E10')

    return append_token(url, join_by='?')


def get_activate_pack_link():
    url = '{}/services/Oboe2/SalesForce/test/ActivatePack?r=json'
    url = url.format(config.etown_root)
    return append_token(url)


def get_login_post_link():
    return '{}/login/secure.ashx'.format(config.etown_root)


def get_login_url(username, password, on_success_url=None):
    url = '{}/services/oboe2/salesforce/test/login'.format(config.etown_root)

    default_on_success_url = '{}/school/course/currentcourse/handler.aspx?entry=true&lng=en&ctr={}'.format(
        config.etown_root, config.domain)

    if on_success_url is None:
        on_success_url = default_on_success_url

    data = {
        'UserName': username,
        'Password': password,
        'Domain': config.etown_root,
        'OnSuccessUrl': on_success_url,
        'Token': get_token()
    }

    response = no_ssl_requests().post(url, data=data)

    assert response.status_code == HTTP_STATUS_OK, response.text

    return response.text


def get_beginner_questionnaire_link():
    url = '{}/services/api/proxy/commandproxy/ecplatform/ecapi_myaccount_beginnerquestionnaire/UpdateAnswers'
    return url.format(config.etown_root)


def get_level0_tool_link():
    url = '{}/services/ecsystem/Tools/Level0'
    url = url.format(config.etown_root)
    return append_token(url).replace('&', '?')


def get_e19_course_info_link():
    url = '{}/services/ecsystem/Tools/Level0/MarkEnrollingToL0GE?'
    url = url.format(config.etown_root)
    return append_token(url).replace('&', '')


def get_s18_course_info_link():
    url = '{}/services/ecsystem/Tools/Level0/MarkEnrollingToGE?'
    url = url.format(config.etown_root)
    return append_token(url).replace('&', '')


def get_mobile_enroll_url():
    url = '{}/ecplatform/mvc/mobile/enrollcourse'
    return url.format(config.etown_root)


def get_set_oc_url():
    url = '{}/services/oboe2/salesforce/test/SetOC?token={}'
    return url.format(config.etown_root, get_token())


def get_activate_oboe_package_link():
    url = '{}/services/oboe2/salesforce/test/ActivatePackage?token={}'
    return url.format(config.etown_root, get_token())


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
            'freeRedemptionQty': 0,
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

    # China & Indo student will enable Online OC by default, except E10 or some test center turn it off
    if config.partner in ['Cool', 'Mini', 'Socn', 'Indo'] \
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


def generate_activation_data_for_phoenix(data, phoenix_packs, is_v1_pack=True, is_smart_plus=False):
    """

    :param data:
    :param phoenix_packs: list, eg. ['1 Year Basic', '1 Year Private']
    dict, eg. {'1 Year Basic': {
    "coupons": [
        {
            "name": "F2F",
            "count": 1
        },
        {
            "name": "WS",
            "count": 1
        },
        {
            "name": "LC",
            "count": 1
        }
    ]
},
    '1 Year Private': {
        "coupons": [
            {
                "name": "PL20",
                "count": 1,
            },
            {
                "name": "GL",
                "count": 1
            }
        ]
    }
}
or
{'1 Year Basic': '{"coupons":[{"name":"PL40","count":1},{"name":"GL","count":1},{"name":"LC","count":1}]}'}
    :param is_v1_pack:
    :param is_smart_plus:
    :return:
    """
    # assert isinstance(phoenix_packs, list) and len(phoenix_packs) > 0

    if isinstance(phoenix_packs, list) and len(phoenix_packs) > 0:
        for i, name in enumerate(phoenix_packs):
            p = get_phoenix_pack(config.env, config.partner, name, is_v1_pack)
            data['PackList[{}].OrderProductId'.format(i)] = p['name']
            data['PackList[{}].PackageProductId'.format(i)] = p['package_id']
            data['PackList[{}].SalesforceProductId'.format(i)] = p['salesforce_id']
            data['PackList[{}].TemplateData'.format(i)] = p['data'] or ''
    elif isinstance(phoenix_packs, dict) and len(phoenix_packs) > 0:
        i = 0
        for name, coupon in phoenix_packs.items():
            p = get_phoenix_pack(config.env, config.partner, name, is_v1_pack)
            data['PackList[{}].OrderProductId'.format(i)] = p['name']
            data['PackList[{}].PackageProductId'.format(i)] = p['package_id']
            data['PackList[{}].SalesforceProductId'.format(i)] = p['salesforce_id']
            data['PackList[{}].TemplateData'.format(i)] = json.dumps(coupon) if isinstance(coupon, dict) else coupon
            i = i + 1

    data['OrderId'] = arrow.now().timestamp  # for refund purpose
    data['DaysOfExpiredCouponRetention'] = 30
    data['RedemptionCode'] = data['mainRedemptionCode']
    data['RedemptionQty'] = data['mainRedemptionQty']

    if not is_smart_plus:
        data['ExtendSubscriptionType'] = 'FromNow'
    else:
        data['ExtendSubscriptionType'] = 'FromExpiredDate'

    to_be_deleted = ['includesenroll', 'mainRedemptionCode', 'mainRedemptionQty',
                     'startLevel', 'levelQty', 'productId', 'freeRedemptionCode',
                     'freeRedemptionQty', 'packageProductIds']

    for key in to_be_deleted:
        data.pop(key, None)

    # hack: if RedemptionQty <= 12 we treat it as months, else as days
    qty = int(data['RedemptionQty'])

    if qty <= 12:
        # Flex VIP redemption code PHOENIXECCNMAIN duration is based on 30 days,
        # which can get from table CommerceContent.dbo.PaymentPlanFeature
        def is_flex_vip_pack():
            for pack in phoenix_packs:
                if 'Flex VIP' in pack:
                    return True

            return False

        def is_flex_pl_or_pro_for_support():
            for pack in phoenix_packs:
                if 'Support 1133' in pack or 'Support 1134' in pack:
                    return True
            return False

        if is_flex_vip_pack() or is_flex_pl_or_pro_for_support():
            data['RedemptionQty'] = qty
        else:
            data['RedemptionQty'] = qty * 30

    # legal duration = main redemption qty
    data['LegalDuration'] = data['RedemptionQty']

    # for trial product, remove legal duration and set qty = 7
    if phoenix_packs == ['Phoenix Free Trial']:
        del data['LegalDuration']
        data['RedemptionQty'] = 7


def _refine_account(ecdb_account):
    """Merge the detail fields into account itself, original it is a json string."""
    if 'detail' in ecdb_account:
        detail = json.loads(ecdb_account.pop('detail'))
        detail.update(ecdb_account)
        ecdb_account = detail

    if 'created_on' in ecdb_account:
        ecdb_account['created_on'] = arrow.get(ecdb_account['created_on']).format()

    return ecdb_account


@ignore_error
def get_accounts_by_tag(tag, expiration_days=None):
    """
    Get test accounts with specified tag
    If expiration days provided, will return accounts within expired days.
    """

    if ecdb_v2.is_db_available():
        return _db_get_accounts_by_tag(tag, expiration_days)
    else:
        return _api_get_accounts_by_tag(tag, expiration_days)


def _api_get_accounts_by_tag(tag, expiration_days=None):
    data = {'tag': tag,
            'env': config.env}

    if expiration_days:
        data['expiration_days'] = int(expiration_days)

    response = no_ssl_requests().post(Configuration.remote_api + 'get_accounts_by_tag', json=data)
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


def is_account_expired(member_id):
    active_subscription = get_student_active_subscription(member_id)
    return len(active_subscription) == 0


def set_account_info(student):
    """
    1. Set telephone2 to valid phone number for each partner.
    2. Update first name to current user.
    3. Update last name to member id.
    4. Update email to include full account info.
    """

    numbers = get_config_value('test_account_phone', is_json=True)
    created_by = student.get('created_by', getpass.getuser())
    student_id, username = student['member_id'], student['username']
    account_service_update_info(student_id, {'Mobile': numbers[config.partner]})
    account_service_update_info(student_id, {'FirstName': created_by})
    account_service_update_info(student_id, {'LastName': student_id})
    account_service_update_info(student_id, {'Email': '{}_{}_{}_{}@qp1.org'
                                .format(username, student_id, config.partner.lower(), config.env.lower())})


@ignore_error
def get_account(member_id):
    if ecdb_v2.is_db_available():
        return _db_get_account(member_id)
    else:
        return _api_get_account(member_id)


def _api_get_account(member_id):
    data = {'env': config.env, 'username_or_id': member_id}
    response = no_ssl_requests().post(Configuration.remote_api + 'get_account', json=data)

    if response.status_code == HTTP_STATUS_OK:
        return _refine_account(response.json())


def _db_get_account(member_id):
    try:
        member_id = int(member_id)
    except ValueError:
        return None

    sql = "select * from ec_test_accounts where environment like '%{}%'".format(config.env)
    sql += " and member_id = {}".format(member_id)
    sql += " order by created_on desc"

    account = ecdb_v2.fetch_one(sql, as_dict=True)

    if account:
        return _refine_account(account)


def get_student_tags(student):
    """Get tags from a student dict."""
    tags = [student['partner'], student['environment']]

    if student['is_phoenix']:
        tags.append('Phoenix')
    elif student['is_e10']:
        tags.append('E10')
    elif student['is_e19']:
        tags.append('E19')
    else:
        tags.append('S18' if student['is_s18'] else 'S15')

    if student['is_eclite']:
        tags.append('ECLite')

    if student['is_onlineoc']:
        tags.append('OC')

    if student['is_trial']:
        tags.append('Trial')

    if student['is_smart_plus']:
        tags.append('SmartPlus')

    return tags


@ignore_error
def save_account(account, add_tags=None, remove_tags=None):
    """
    Save a test account to ecdb, you can add or remove multiple tags to it.
    The add_tags and remove_tags should be in list format as ['Tag1', 'Tag2']
    """

    if ecdb_v2.is_db_available():
        return _db_save_account(account, add_tags, remove_tags)
    else:
        return _api_save_account(account, add_tags, remove_tags)


def _api_save_account(account, add_tags=None, remove_tags=None):
    """
    api to save account in ecdb.
    :param account: dict
    :param add_tags: list
    :param remove_tags: list
    :return:
    """
    created_by = account.get('created_by', getpass.getuser())
    data = {'detail': account,
            'env': config.env,
            'member_id': int(account['member_id']),
            'created_by': created_by}

    if remove_tags:
        removed_tags = ','.join(remove_tags)
        data['remove_tags'] = removed_tags

    if add_tags:
        data['add_tags'] = ','.join(add_tags)

    response = no_ssl_requests().post(Configuration.remote_api + 'save_account', json=data)
    assert response.status_code == HTTP_STATUS_OK, response.text


def _db_save_account(account, add_tags=None, remove_tags=None):
    """
    sql to save the account in ecdb.
    :param account: dict
    :param add_tags: list
    :param remove_tags: list
    :return:
    """
    tags = ['ectools']
    target_table = 'ec_test_accounts'
    existed_account = get_account(account['member_id'])
    created_by = account.get('created_by', None)
    account['created_by'] = created_by

    if add_tags:
        tags += add_tags

    if existed_account:
        tags += existed_account['tags'].split(',')

        if remove_tags:  # remove tags after fetch existed tags
            tags = (set(tags) - set(remove_tags))

        account['tags'] = ','.join(set(tags))
        existed_account.update(account)

        search_by = {'member_id': account['member_id'], 'environment': config.env}
        update_dict = {'detail': json.dumps(existed_account), 'tags': account['tags']}

        if created_by:
            update_dict['created_by'] = created_by

        ecdb_v2.update_rows(target_table, search_by, update_dict)

    else:

        if remove_tags:
            tags = (set(tags) - set(remove_tags))

        account['tags'] = ','.join(set(tags))
        assert 'username' in account, 'username is required to save the account!'
        ecdb_v2.add_row(target_table,
                        config.env,
                        account['member_id'],
                        account['username'],
                        json.dumps(account),
                        arrow.utcnow().format('YYYY-MM-DD HH:mm:ss.SSS'),
                        created_by or getpass.getuser(),
                        account['tags'])
