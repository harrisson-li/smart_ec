# -*- coding: utf-8 -*-

"""
This module provides methods to get or set student flags, as well as member site settings.

-----
"""
import json
import re
from datetime import datetime

import arrow
import numpy
from ectools.config import config
from ectools.constant import Memcached, ClearCacheType
from ectools.internal import sf_service_helper as sf
from ectools.internal import troop_service_helper
from ectools.internal.business.enums import Timezone
from ectools.internal.business.time_helper import get_current_china_date_time, convert_utc_to_target_timezone
from ectools.internal.constants import HTTP_STATUS_OK
from ectools.internal.troop_service_helper import DEFAULT_PASSWORD
from ectools.token_helper import get_token, get_site_version
from ectools.utility import camelcase_to_underscore, no_ssl_requests
from lxml import etree

GRAPHQL_SERVICE_URL = "/services/api/ecplatform/graphql"

STUDENT_BASICS = {"URL": "/services/ecsystem/Tools/StudentInspection/Basics",
                  "DATA": "studentId"}
STUDENT_PRODUCTS = {"URL": "/services/ecsystem/Tools/StudentInspection/Products",
                    "DATA": "studentId"}
STUDENT_SUBSCRIPTIONS = {"URL": "/services/ecsystem/Tools/StudentInspection/Subscriptions",
                         "DATA": "studentId"}
STUDENT_STATUS_AND_SETTINGS = {"URL": "/services/ecsystem/Tools/StudentInspection/StatusAndSettings",
                               "DATA": "studentId"}
STUDENT_FAGS = {"URL": "/services/ecsystem/Tools/StudentInspection/FAGs",
                "DATA": "studentId"}
STUDENT_ENROLLMENTS = {"URL": "/services/ecsystem/Tools/StudentInspection/Enrollments",
                       "DATA": "studentId"}
STUDENT_ONLINE_CLASSES = {"URL": "/services/ecsystem/Tools/StudentInspection/OnlineClasses",
                          "DATA": "studentId"}
STUDENT_OFFLINE_CLASSES = {"URL": "/services/ecsystem/Tools/StudentInspection/OfflineClasses",
                           "DATA": "studentId"}
STUDENT_COUPONS = {"URL": "/services/ecsystem/Tools/StudentInspection/Coupons",
                   "DATA": "studentId"}
STUDENT_PACKAGES = {"URL": "/services/ecsystem/Tools/StudentInspection/Packages",
                    "DATA": "studentId"}
STUDENT_MAINTENANCE_HISTORIES = {"URL": "/services/ecsystem/Tools/StudentInspection/StudentMaintenanceHistories",
                                 "DATA": "studentId"}


def is_v2_student(student_id):
    site_settings = get_member_site_settings(student_id)
    return site_settings.get('student.platform.version', '2.0') == '2.0'


def is_e19_student(student_id):
    site_settings = get_member_site_settings(student_id)
    return site_settings.get('student.platform.mapcode', 'ec') == 'ec19'


def get_member_site_settings(student_id, site_area='school'):
    site_settings = {}
    datetime_format = "%Y-%m-%d %H:%M:%S"

    target_url = "{}/services/ecplatform/Tools/StudentSettings?id={}&token={}".format(
        config.etown_root, student_id, get_token())
    result = no_ssl_requests().get(target_url)

    assert result.status_code == HTTP_STATUS_OK, "Failed to get student settings: {}".format(result.text)

    html = etree.HTML(result.text)
    items = html.xpath("//table[@id='membersitesetting']/tbody/tr")
    for i, item in enumerate(items):
        try:
            area = html.xpath("//table[@id='membersitesetting']/tbody/tr[{}]/td[1]/text()".format(i + 1))[0]
        except IndexError:
            area = ''

        try:
            key = html.xpath("//table[@id='membersitesetting']/tbody/tr[{}]/td[2]/text()".format(i + 1))[0]
        except IndexError:
            key = ''

        try:
            value = html.xpath("//table[@id='membersitesetting']/tbody/tr[{}]/td[3]/text()".format(i + 1))[0]
        except IndexError:
            value = ''

        if area == site_area:
            if value and re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', value):
                value = datetime.strptime(value, datetime_format)
            site_settings[key] = value

    return site_settings


def get_student_status_flag(student_id):
    student_status_flag = {}
    target_url = "{}/services/ecplatform/Tools/StudentSettings?id={}&token={}".format(
        config.etown_root, student_id, get_token())
    result = no_ssl_requests().get(target_url)

    assert result.status_code == HTTP_STATUS_OK, "Failed to get student settings: {}".format(result.text)
    html = etree.HTML(result.text)
    items = html.xpath("//table[@id='statusFlag']/tbody/tr")

    for i, item in enumerate(items):
        try:
            key = html.xpath("//table[@id='statusFlag']/tbody/tr[{}]/td[2]/text()".format(i + 1))[0]
        except IndexError:
            key = ''

        try:

            value = html.xpath("//table[@id='statusFlag']/tbody/tr[{}]/td[3]/text()".format(i + 1))[0]
        except IndexError:
            value = ''

        student_status_flag[key] = value if value != 'N/A' else None

    return student_status_flag


def set_member_site_settings(student_id, key_name, key_value, site_area='school', is_time_value=False):
    if is_time_value:
        key_value = arrow.get(key_value).format('M/D/YYYY hh:mm:ss')

    url = '{}/services/ecplatform/Tools/StudentSettings/SaveMemberSiteSetting?token={}'.format(config.etown_root,
                                                                                               get_token())
    data = {'studentId': student_id,
            'siteArea': site_area,
            'key': key_name,
            'value': key_value}

    response = no_ssl_requests().post(url, data=data)
    assert '"IsSuccess":true' in response.text, response.text


def get_student_info(student_id):
    """
    Will return a dict contains student information.
    """
    info = {'member_id': student_id}

    more_info = ecplatform_load_student(student_id)
    info.update(more_info)
    info['username'] = info['user_name']

    more_info = score_helper_load_student(student_id)
    info.update(more_info)

    info = {k: v for k, v in info.items() if v is not None}

    # dict key name refine
    info['partner'] = info['oboe_partner']
    info['division_code'] = info['oboe_division_code']

    del info['oboe_partner']
    del info['user_name']
    del info['oboe_division_code']
    del info['is_success']
    del info['collapsed']
    del info['id']

    return info


def get_student_basics(student_id):
    url = config.etown_root + STUDENT_BASICS["URL"] + '?token={}'.format(get_token())
    result = no_ssl_requests().post(url, data={STUDENT_BASICS["DATA"]: student_id})

    info = {}
    for k, v in result.json().items():
        info[camelcase_to_underscore(k)] = v

    result2 = account_service_load_student(student_id)
    info.update(result2)
    return info


def get_student_product(student_id):
    url = config.etown_root + STUDENT_PRODUCTS["URL"] + '?token={}'.format(get_token())
    result = no_ssl_requests().post(url, data={STUDENT_PRODUCTS["DATA"]: student_id})

    info = {}
    for k, v in result.json().items():
        info[camelcase_to_underscore(k)] = v

    return info


def ecplatform_load_student(student_id):
    basics = get_student_basics(student_id)
    product = get_student_product(student_id)

    query_string = 'q=ecapi_student!current'
    student_info = query_troop_service(basics['user_name'],
                                       query_string=query_string,
                                       password=basics['password'])

    info = {}
    for k, v in student_info.items():
        info[camelcase_to_underscore(k)] = v

    info.update(basics)
    info.update(product)
    return info


def score_helper_load_student(student_name_or_id):
    """Get student info via S15 submit score helper."""
    token = get_token()
    data = {'cmd': 'loadStudentInfo',
            'member_id': student_name_or_id,
            'token': token}
    target_url = "/services/school/_tools/progress/SubmitScoreHelper.aspx"
    response = no_ssl_requests().post(config.etown_root + target_url, data=data)
    match_char = u'★'
    result = {}

    if response.status_code == 200 and '|' in response.text:
        raw = response.text.split('|')
        result = {'username': raw[1], 'member_id': int(raw[3]), 'partner': raw[4]}
        levels = raw[5].split('#')
        units = raw[6].split('#')

        current_level = [l for l in levels if match_char in l][0]  # e.g. '378$★GE2013 Level3'
        current_unit = [l for l in units if match_char in l][0]  # e.g. '1803$★Level 1 - Unit 6'
        if 'Level' not in current_level:
            result['current_level_code'] = current_level[current_level.index(match_char) + 1:]
            result['current_level_name'] = result['current_level_code']
            result['current_unit'] = current_unit[current_unit.index(match_char) + 1:]

        else:
            result['current_level_code'] = re.findall(r'Level(.+)', current_level)[0].strip()  # not stable
            result['current_level_name'] = re.findall(r'Level(.+)-', current_unit)[0].strip()  # A, B, 1~14
            result['current_unit'] = int(re.findall(r'Unit([\d ]+)', current_unit)[0].strip())  # 1~6

    return result


def query_troop_service(student_or_teacher_name,
                        query_string,
                        login_required=True,
                        password=DEFAULT_PASSWORD,
                        return_first_item=True,
                        use_default_context=True,
                        is_to_axis=False):
    if login_required:
        if is_to_axis:
            troop_service_helper.login_axis(student_or_teacher_name, password)
        else:
            troop_service_helper.login(student_or_teacher_name, password)

    url_with_context = True if student_or_teacher_name else False
    return troop_service_helper.query(student_or_teacher_name,
                                      query_string,
                                      url_with_context=url_with_context,
                                      return_first_item=return_first_item,
                                      use_default_context=use_default_context)


def troop_service_translate_blurb(blurb_id, culture_code='en'):
    query_string = 'q=blurb!{}'.format(blurb_id)
    url_query_string = 'c=culturecode={}'.format(culture_code)
    return troop_service_helper.query(None, query_string,
                                      url_with_context=False,
                                      url_query_string=url_query_string)['translation']


def troop_service_load_student(student_name, password=DEFAULT_PASSWORD):
    query_string = 'q=user!current'
    return query_troop_service(student_name, query_string=query_string, password=password)


def troop_service_reminder_settings(student_name, password=DEFAULT_PASSWORD):
    query_string = 'q=ecapi_notificationprofile!current'
    return query_troop_service(student_name, query_string=query_string, password=password)


def troop_service_get_teacher_info(teacher_name_or_id, password=DEFAULT_PASSWORD):
    query_string = 'q=axis_profile!current'

    teacher = account_service_load_student(teacher_name_or_id)
    teacher_name = teacher['user_name']
    password = teacher['password']

    return query_troop_service(teacher_name, query_string=query_string, password=password, is_to_axis=True)['data']


def get_sms_reminder_mobile_phone(student_name, password=DEFAULT_PASSWORD):
    sms_reminder_info = troop_service_reminder_settings(student_name, password)

    return sms_reminder_info['items'][0]['target']


def get_sms_reminder_settings(student_name, password=DEFAULT_PASSWORD):
    sms_reminder_info = troop_service_reminder_settings(student_name, password)

    settings = {}
    for item in sms_reminder_info['items']:
        settings[camelcase_to_underscore(item['name'])] = item['isOn']

    return settings


def account_service_load_student(student_name_or_id):
    datetime_format = "%Y-%m-%d %H:%M:%S"

    if isinstance(student_name_or_id, int) or (isinstance(student_name_or_id, str) and student_name_or_id.isdigit()):
        target_url = "{}/services/oboe2/salesforce/Account/GetMemberInfo/{}?token={}".format(
            config.etown_root, student_name_or_id, get_token())
        id_response = no_ssl_requests().post(target_url)
        assert id_response.status_code == HTTP_STATUS_OK, id_response.text
        response = json.loads(id_response.text)
    else:
        target_url = "{}/services/oboe2/salesforce/Account/GetMemberByEmailOrUserName/{}?token={}".format(
            config.etown_root, student_name_or_id, get_token())

        name_response = no_ssl_requests().post(target_url)
        assert name_response.status_code == HTTP_STATUS_OK, name_response.text
        response = json.loads(name_response.text)

    # convert the key from camelcase to underscore
    info = {}
    for key, value in response.items():
        if isinstance(value, str) and re.match(r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2}:\d{1,2}', value):
            # value = eg. '3/15/2017 3:42:00 AM'
            value = datetime.strptime(value, "%m/%d/%Y %I:%M:%S %p").strftime(datetime_format)
        info[camelcase_to_underscore(key)] = value

    return info


def account_service_update_phone2(student_id, phone_number):
    account_service_update_info(student_id, {'mobile': phone_number})


def account_service_update_info(student_id, info):
    """
    info: dict data to update the account, e.g.{'mobile':123, firstName:'test', lastName:'test'}
    """
    url_partial = ''
    for k, v in info.items():
        url_partial = url_partial + '&{}={}'.format(k, v)
    target_url = '{}/services/oboe2/salesforce/Account/UpdateAccountForMember/{}?token={}{}'.format(
        config.etown_root, student_id, get_token(), url_partial)

    response = no_ssl_requests().post(target_url)
    assert response.status_code == HTTP_STATUS_OK and '"IsSuccess":true' in response.text, response.text


def account_service_cancel_student(student_id):
    target_url = '{}/services/oboe2/salesforce/Account/CancelAccountForMember/{}?reason=Vacation&token={}'.format(
        config.etown_root, student_id, get_token())

    response = no_ssl_requests().post(target_url)
    assert '"IsSuccess":true' in response.text, response.text


def adjust_level(student_id, to_level_code):
    sf.change_level(student_id, to_level_code)


def adjust_stage(student_id, to_stage_number):
    sf.adjust_stage(student_id, to_stage_number)


def add_offline_coupon(student_id, coupon_type, add_count):
    """
    Add offline coupons for a student.
    :param student_id: the member id.
    :param coupon_type: "F2F"/"Face to Face"/"WS"/"Workshop"/"LC"/"Life Club"/"Apply"
    :param add_count: counts to add.
    :return:
    """
    map = {'F2F': 'F2FQty', 'Face to Face': 'F2FQty',
           'WS': 'WSQty', 'Workshop': 'WSQty',
           'LC': 'LCQty', 'Life Club': 'LCQty',
           'Apply': 'ApplyQty'}
    url = '{}/services/oboe2/salesforce/test/UpsellCoupon?token={}'.format(config.etown_root, get_token())
    response = no_ssl_requests().post(url, data={
        'memberId': student_id,
        map[coupon_type]: add_count,
        'token': 'b175934dbe21f41945759f3797b50c86ac1f'
    })
    assert response.text == 'Coupons granted!', response.text


def adjust_coupon(student_id, coupon_tye, adjust_count):
    """
    increase or reduce the coupon count
    :param student_id:
    :param coupon_tye: eg. F2F, WS, LC, PL40, GL
    :param adjust_count: eg. 10 or -10
    :return:
    """
    url = '{}/services/oboe2/salesforce/test/AdjustCoupon?token={}'.format(config.etown_root, get_token())
    data = {'MemberId': student_id,
            'CouponAttribute': "[{\"name\": " + "\"" + coupon_tye + "\"" + ",\"count\": " + str(adjust_count) + "}]"
            }

    response = no_ssl_requests().post(url, data=data)
    assert "Success" in response.text, response.text


def call_troop_command_service(student_name,
                               command_url,
                               data,
                               login_required=True,
                               password=DEFAULT_PASSWORD,
                               return_first_item=True,
                               use_default_context=True):
    if login_required:
        troop_service_helper.login(student_name, password)

    return troop_service_helper.troop_command_service(student_name, command_url, data,
                                                      return_first_item=return_first_item,
                                                      use_default_context=use_default_context)


def troop_command_update_information(student_name, data, password=DEFAULT_PASSWORD):
    command_url = 'ecapi_myaccount_information/updateinformation'

    return call_troop_command_service(student_name,
                                      command_url=command_url,
                                      data=data,
                                      password=password)


def update_student_password(student_name, old_password, new_password):
    password_info = {'OldPassword': old_password,
                     'NewPassword': new_password,
                     'NewPasswordConfirmed': new_password}
    data = {'updateItemInfos': {
        'password': json.dumps(password_info, sort_keys=False)}}

    return troop_command_update_information(student_name, data, old_password)


def update_student_first_name(student_name, old_password, new_first_name):
    data = {'updateItemInfos': {'firstname': new_first_name}}

    return troop_command_update_information(student_name, data, old_password)


def update_student_last_name(student_name, old_password, new_last_name):
    data = {'updateItemInfos': {'firstname': new_last_name}}

    return troop_command_update_information(student_name, data, old_password)


def update_student_display_name(student_name, old_password, new_display_name):
    data = {'updateItemInfo': {'displayname': new_display_name}}

    return troop_command_update_information(student_name, data, old_password)


def update_student_email(student_name, old_password, new_email):
    data = {'updateItemInfos': {'email': {
        'Email': new_email,
        'Password': old_password
    }}}

    return troop_command_update_information(student_name, data, old_password)


def update_student_address(student_name, student_password=DEFAULT_PASSWORD,
                           country_code='cn', state_code='',
                           city_code='', billing_address='',
                           postal_code=''):
    data = {"updateItemInfos": {
        "billinginfo": "{\"CountryCode\":" + "\"" + country_code + "\""
                       + ",\"StateCode\":" + "\"" + state_code + "\""
                       + ",\"CityCode\":" + "\"" + city_code + "\""
                       + ",\"Address\":" + "\"" + billing_address + "\""
                       + ",\"PostalCode\":" + "\"" + postal_code + "\"}"
    }}

    return troop_command_update_information(student_name, data=data, password=student_password)


def clear_memcached(cache_key):
    return clear_memcached_by_type(ClearCacheType.MEM_CACHED_VALUE_CLEAR, cache_key)


def clear_memcached_by_type(cache_type, paras):
    target_url = "{}/services/ecplatform/Tools/CacheClear/Clear?token={}".format(config.etown_root, get_token())
    data = {
        'cachetype': cache_type,
        'paras': paras
    }

    response = no_ssl_requests().post(target_url, data)

    if response.status_code == HTTP_STATUS_OK:
        return response.text
    else:
        raise ValueError(response.text)


def get_memcached_key(cache_key_string, **kwargs):
    """
    Get the membercached key with certain format
    :param cache_key_string: cache key string is Memcached in constant.py
    :param kwargs: give the parameters as the {} in cache_key_string,
    eg. _{site_version}_, then should pass site_version = xxx
    :return:
    """
    return cache_key_string.format(**kwargs)


def clear_booking_mem_cache_by_date_range(student_id):
    return clear_memcached_by_type(ClearCacheType.BOOKING_MEM_CACHE_BY_DATE_RANGE, student_id)


def clear_offline_class_taken_cache(student_id):
    clear_memcached(
        get_memcached_key(Memcached.CLASS_TAKEN_OFFLINE, site_version=get_site_version(), student_id=student_id))


def clear_course_progress(student_id):
    if is_e19_student(student_id):
        clear_course_progress_cache_e19(student_id)
    else:
        clear_course_progress_cache_s18(student_id)


def clear_course_progress_cache_s18(student_id):
    # S18 GE course id: 10000014
    clear_memcached(get_memcached_key(Memcached.COURSE_PROGRESS,
                                      student_id=student_id,
                                      course_id=10000014))


def clear_course_progress_cache_e19(student_id):
    # E19 GE course id: 10000119
    clear_memcached(get_memcached_key(Memcached.COURSE_PROGRESS,
                                      student_id=student_id,
                                      course_id=10000119))


def clear_online_class_taken_cache(student_id):
    clear_memcached(get_memcached_key(Memcached.CLASS_ATTENDANCE_ONLINE, student_id=student_id))


def clear_class_taken_memcached(student_id):
    clear_offline_class_taken_cache(student_id)
    clear_online_class_taken_cache(student_id)


def clear_student_basic_info_cache(student_id):
    clear_memcached_by_type(ClearCacheType.STUDENT_BASIC_INFO, student_id)


def get_student_active_subscription(student_id):
    """
    Get active subscriptions
    :param student_id:
    :return: list
    """
    url = config.etown_root + STUDENT_SUBSCRIPTIONS["URL"] + '?token={}'.format(get_token())
    result = no_ssl_requests().post(url, data={STUDENT_SUBSCRIPTIONS["DATA"]: student_id})

    assert result.status_code == HTTP_STATUS_OK, result.text
    active_subscriptions = []
    for subscription in result.json()['Subscriptions']:
        if subscription['IsActive']:
            info = {}
            for k, v in subscription.items():
                info[camelcase_to_underscore(k)] = v
            active_subscriptions.append(info)

    return active_subscriptions


def parse_xml(response_xml):
    # get all return field names
    fields = re.findall('<a:([^>/]+)>', response_xml)

    # get all field value and convert to dict
    info = {}
    for field in fields:
        value = re.findall('<a:{0}>(.*)</a:{0}>'.format(field), response_xml)[0]
        info[camelcase_to_underscore(field)] = value

    return info


def get_student_info_by_graphql(student, info):
    troop_service_helper.login(student.username, student.password)
    client = troop_service_helper.get_request_session(student.username)

    data = {"variables": {},
            "query": "{student {" + info + "}}"}
    graphql_url = config.etown_root + GRAPHQL_SERVICE_URL + '?token={}'.format(get_token())

    graphql_result = no_ssl_requests().post(graphql_url,
                                            data=json.dumps(data),
                                            headers={"X-EC-CMUS": client.cookies['CMus'],
                                                     "X-EC-SID": client.cookies['et_sid'],
                                                     "X-EC-LANG": "en"})

    return graphql_result.json()["data"]["student"][info]


def get_student_coupon_info(student_id):
    """
    Get the student coupon info
    :param student_id
    :return: coupon info, eg.
{
    'ClassicCoupons': [{'CouponName': 'F2F', 'Count': 5},
                       {'CouponName': 'Workshop', 'Count': 5},
                       {'CouponName': 'LifeClub', 'Count': 5}],
    'LegacyCoupons': [{'CouponName': 'F2F', 'Count': 5},
                      {'CouponName': 'Workshop', 'Count': 5},
                      {'CouponName': 'LifeClub', 'Count': 5}],
    'MergedCoupons': [{'CouponName': 'F2F', 'Count': 5},
                      {'CouponName': 'Workshop', 'Count': 5},
                      {'CouponName': 'LifeClub', 'Count': 5}],
    'SpecialCoupons': [],
    'OnlineCoupons': [{'CouponName': 'PL40', 'Count': 50},
                      {'CouponName': 'GL', 'Count': 155}],
    'IsSuccess': True,
    'Message': ''
}
    """
    target_url = config.etown_root + STUDENT_COUPONS['URL'] + '?token={}'.format(get_token())
    data = {
        STUDENT_COUPONS['DATA']: student_id
    }

    response = no_ssl_requests().post(target_url, data=data)

    assert response.status_code == HTTP_STATUS_OK, response.text

    return response.json()


def get_student_feature_access_grants(student_id):
    """
    Get the student coupon info
    :param student_id
    :return: coupon info, eg.
[{'FeatureAccessGrantId': 4006314, 'FeatureAccessId': 4, 'FeatureAccess': 'FaceToFace', 'TotalQuantity': -1,
'RemainingQuantity': 0, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006315, 'FeatureAccessId': 11, 'FeatureAccess': 'GroupLesson', 'TotalQuantity': 0,
'RemainingQuantity': 0, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006316, 'FeatureAccessId': 12, 'FeatureAccess': 'TOEICTrainer', 'TotalQuantity': 12,
'RemainingQuantity': 0, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006317, 'FeatureAccessId': 15, 'FeatureAccess': 'TOEICTest_Blue', 'TotalQuantity': 12,
'RemainingQuantity': 0, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006318, 'FeatureAccessId': 16, 'FeatureAccess': 'TOEFLTrainer', 'TotalQuantity': 12,
'RemainingQuantity': 0, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006319, 'FeatureAccessId': 19, 'FeatureAccess': 'TOEFLTest_Blue', 'TotalQuantity': 12,
'RemainingQuantity': 0, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006320, 'FeatureAccessId': 21, 'FeatureAccess': 'SelfStudy_Extendable', 'TotalQuantity': -1,
'RemainingQuantity': 0, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006321, 'FeatureAccessId': 33, 'FeatureAccess': 'WritingClassUnlimited', 'TotalQuantity': -1,
'RemainingQuantity': 0, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006322, 'FeatureAccessId': 42, 'FeatureAccess': 'PL20', 'TotalQuantity': 1,
'RemainingQuantity': 1, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006323, 'FeatureAccessId': 43, 'FeatureAccess': 'PL20UnitMoveOn', 'TotalQuantity': -1,
'RemainingQuantity': 0, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006324, 'FeatureAccessId': 44, 'FeatureAccess': 'GLDaliyDelivert', 'TotalQuantity': -1,
'RemainingQuantity': 0, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None},
{'FeatureAccessGrantId': 4006325, 'FeatureAccessId': 56, 'FeatureAccess': 'EEA', 'TotalQuantity': 360,
'RemainingQuantity': 360, 'CostQuantity': 0, 'ActiveFromESTDate': '2020-07-09T02:22:03.477',
'ActiveFromUTCDate': '2020-07-09T06:22:03.477Z', 'ActiveToESTDate': '2021-07-04T02:22:03.477',
'ActiveToUTCDate': '2021-07-04T06:22:03.477Z', 'OrderId': 452182, 'OrderItemId': 452182, 'Status': None}]
    """
    target_url = config.etown_root + STUDENT_FAGS['URL'] + '?token={}'.format(get_token())
    data = {
        STUDENT_COUPONS['DATA']: student_id
    }

    response = no_ssl_requests().post(target_url, data=data)

    assert response.status_code == HTTP_STATUS_OK, response.text

    return response.json()['FAGs']


def get_EEA_coupon(student_id):
    """
    Get EEA total coupon count and remaining coupon count
    :param student_id:
    :return: [total_coupon_count, remaining_coupon_count]
    """
    features = get_student_feature_access_grants(student_id)

    found = [(feature['TotalQuantity'], feature['RemainingQuantity'])
             for feature in features if
             feature['FeatureAccess'] == 'EEA'
             and datetime.strptime(feature['ActiveToESTDate'].replace('T', ' ').split('.')[0],
                                   '%Y-%m-%d %H:%M:%S') > datetime.now()
             ]

    if len(found) > 0:
        total_remaining_coupon = numpy.sum(found, axis=0)
    else:
        return [0, 0]
    return total_remaining_coupon


def get_student_enrollments_info(student_id):
    """
    Get the student enrollments info
    :param student_id:
    :return: enrollments info, eg.
{
    "EnrolledGEStageLevels": [
        "5"
    ],
    "EnrolledGELevels": [
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14"
    ],
    "EnrolledGELevelsValidation": {
        "ErrorLevel": null,
        "ErrorLevelString": "",
        "Cause": null
    },
    "CurrentLocation": {
        "StudentCourse": {
            "CourseItemId": 10000014,
            "StudentCourseItemId": "37758110-9bc1-419b-89f5-bcb5819c6e98",
            "CourseVersion": "2.0.1.0",
            "StatusId": 0
        },
        "StudentLevel": {
            "CourseItemId": 20000754,
            "StudentCourseItemId": "fa1b4aec-3044-4a4e-be9a-f08040a54f4c",
            "CourseVersion": "2.0.1.0",
            "StatusId": 0
        },
        "StudentUnit": {
            "CourseItemId": 30003007,
            "StudentCourseItemId": "c16c36a2-9c2a-4692-8dd6-f95ecc87ab1a",
            "CourseVersion": "2.0.1.0",
            "StatusId": 0
        },
        "StudentLesson": {
            "CourseItemId": 40013234,
            "StudentCourseItemId": "076c0d91-5de9-4e96-9739-d96588da11b5",
            "CourseVersion": "2.0.1.0",
            "StatusId": 0
        }
    },
    "CurrentGECourseLocation": {
        "CourseVersion": "2.0.1.0",
        "CourseId": 10000014,
        "CourseTypeCode": "GE",
        "Levels": [
            {
                "RootStudentCourseItemId": "00000000-0000-0000-0000-000000000000",
                "StudentLevelId": "00000000-0000-0000-0000-000000000000",
                "LevelId": 20000754,
                "LevelCode": "5",
                "LevelNo": 7,
                "StartDate": null,
                "CourseVersion": null,
                "EnrollDate": null,
                "Units": [
                    {
                        "UnitId": 30003007,
                        "UnitNo": 1,
                        "UnitName": null,
                        "StatusId": 0,
                        "CourseVersion": null,
                        "RootStudentCourseItemId": "00000000-0000-0000-0000-000000000000",
                        "StudentUnitId": "00000000-0000-0000-0000-000000000000",
                        "Lessons": [
                            {
                                "LessonId": 40013234,
                                "LessonNo": 1,
                                "PCPassed": false,
                                "MOBPassed": false,
                                "LessonName": null,
                                "LessonDescr": null,
                                "LessonImage": null
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "StudentGELevels": [
        {
            "StudentLevelId": "fa1b4aec-3044-4a4e-be9a-f08040a54f4c",
            "StudentId": 24010444,
            "TemplateLevelId": 20000754,
            "CourseVersion": "2.0.1.0",
            "LevelName": "getTrans::176689",
            "ParentId": "37758110-9bc1-419b-89f5-bcb5819c6e98",
            "RootId": "37758110-9bc1-419b-89f5-bcb5819c6e98",
            "LevelNo": 7,
            "LevelCode": "5",
            "LegacyLevelId": 548,
            "HasCertificate": false,
            "CertificateDate": null,
            "StatusId": 0,
            "Score": null,
            "StartDate": null,
            "CompleteDate": null,
            "LastModifiedDate": "2020-04-03T06:15:11.127",
            "StudentUnits": [
                {
                    "StudentUnitId": "c16c36a2-9c2a-4692-8dd6-f95ecc87ab1a",
                    "StudentId": 24010444,
                    "TemplateUnitId": 30003007,
                    "CourseVersion": "2.0.1.0",
                    "UnitName": "getTrans::479205",
                    "ParentId": "fa1b4aec-3044-4a4e-be9a-f08040a54f4c",
                    "RootId": "37758110-9bc1-419b-89f5-bcb5819c6e98",
                    "UnitNo": 1,
                    "UnitImage": "getMedia::179958",
                    "UnitDescr": null,
                    "LegacyUnitId": 1990,
                    "StatusId": 0,
                    "Score": null,
                    "StartDate": null,
                    "CompleteDate": null,
                    "LastModifiedDate": "2020-04-03T06:15:11.127",
                    "StudentLessons": [
                        {
                            "StudentLessonId": "076c0d91-5de9-4e96-9739-d96588da11b5",
                            "StudentId": 24010444,
                            "TemplateLessonId": 40013234,
                            "CourseVersion": "2.0.1.0",
                            "LessonName": "getTrans::479206",
                            "LessonNo": 1,
                            "LessonImage": "getMedia::130099",
                            "LessonDescr": "getTrans::664775",
                            "LessonTypeId": 1,
                            "LegacyLessonId": 8515,
                            "ParentId": "c16c36a2-9c2a-4692-8dd6-f95ecc87ab1a",
                            "RootId": "37758110-9bc1-419b-89f5-bcb5819c6e98",
                            "StatusId": 0,
                            "Score": null,
                            "StartDate": null,
                            "CompleteDate": null,
                            "LastModifiedDate": "2020-04-03T06:15:11.583",
                            "StudentSteps": [ ],
                            "CreateDate": "2020-04-03T06:15:00",
                            "ItemTypeId": 4,
                            "TimeSpentInMins": null,
                            "PCPassed": false,
                            "MOBPassed": false
                        },
                        {
                            "StudentLessonId": "af139039-df6a-4e6a-ad8a-c842bac3b1df",
                            "StudentId": 24010444,
                            "TemplateLessonId": 40013235,
                            "CourseVersion": "2.0.1.0",
                            "LessonName": "getTrans::479212",
                            "LessonNo": 2,
                            "LessonImage": "getMedia::130100",
                            "LessonDescr": "getTrans::664794",
                            "LessonTypeId": 1,
                            "LegacyLessonId": 8516,
                            "ParentId": "c16c36a2-9c2a-4692-8dd6-f95ecc87ab1a",
                            "RootId": "37758110-9bc1-419b-89f5-bcb5819c6e98",
                            "StatusId": 0,
                            "Score": null,
                            "StartDate": null,
                            "CompleteDate": null,
                            "LastModifiedDate": "2020-04-03T06:15:11.127",
                            "StudentSteps": [ ],
                            "CreateDate": "2020-04-03T06:15:00",
                            "ItemTypeId": 4,
                            "TimeSpentInMins": null,
                            "PCPassed": false,
                            "MOBPassed": false
                        },
                        {
                            "StudentLessonId": "8a4f8463-587d-47fb-8323-a23d18300291",
                            "StudentId": 24010444,
                            "TemplateLessonId": 40013236,
                            "CourseVersion": "2.0.1.0",
                            "LessonName": "getTrans::479218",
                            "LessonNo": 3,
                            "LessonImage": "getMedia::130101",
                            "LessonDescr": "getTrans::664815",
                            "LessonTypeId": 1,
                            "LegacyLessonId": 8517,
                            "ParentId": "c16c36a2-9c2a-4692-8dd6-f95ecc87ab1a",
                            "RootId": "37758110-9bc1-419b-89f5-bcb5819c6e98",
                            "StatusId": 0,
                            "Score": null,
                            "StartDate": null,
                            "CompleteDate": null,
                            "LastModifiedDate": "2020-04-03T06:15:11.127",
                            "StudentSteps": [ ],
                            "CreateDate": "2020-04-03T06:15:00",
                            "ItemTypeId": 4,
                            "TimeSpentInMins": null,
                            "PCPassed": false,
                            "MOBPassed": false
                        },
                        {
                            "StudentLessonId": "00e7231d-73de-482e-ba34-352d835fd19e",
                            "StudentId": 24010444,
                            "TemplateLessonId": 40013237,
                            "CourseVersion": "2.0.1.0",
                            "LessonName": "getTrans::479223",
                            "LessonNo": 4,
                            "LessonImage": "getMedia::130098",
                            "LessonDescr": "getTrans::664830",
                            "LessonTypeId": 1,
                            "LegacyLessonId": 8518,
                            "ParentId": "c16c36a2-9c2a-4692-8dd6-f95ecc87ab1a",
                            "RootId": "37758110-9bc1-419b-89f5-bcb5819c6e98",
                            "StatusId": 0,
                            "Score": null,
                            "StartDate": null,
                            "CompleteDate": null,
                            "LastModifiedDate": "2020-04-03T06:15:11.127",
                            "StudentSteps": [ ],
                            "CreateDate": "2020-04-03T06:15:00",
                            "ItemTypeId": 4,
                            "TimeSpentInMins": null,
                            "PCPassed": false,
                            "MOBPassed": false
                        }
                    ],
                    "CreateDate": "2020-04-03T06:15:00"
                }
            ],
            "EnrollDate": "2020-04-03T06:15:11",
            "CreateDate": "2020-04-03T06:15:00",
            "StudentLevelTest": null
        }
    ],
    "InitialLevelCode": "5",
    "InitialLevelCodeValidation": {
        "ErrorLevel": null,
        "ErrorLevelString": "",
        "Cause": null
    },
    "E12Enrolled": "True",
    "E12EnrolledValidation": {
        "ErrorLevel": null,
        "ErrorLevelString": "",
        "Cause": null
    },
    "IsSuccess": true,
    "Message": ""
}
    """
    target_url = config.etown_root + STUDENT_ENROLLMENTS['URL'] + '?token={}'.format(get_token())

    data = {
        STUDENT_ENROLLMENTS['DATA']: student_id
    }

    response = no_ssl_requests().post(target_url, data=data)
    if response.status_code == HTTP_STATUS_OK:
        return response.json()
    else:
        raise ValueError(response.text)


def get_current_level_unit(student_id):
    enrollment_info = get_student_enrollments_info(student_id)
    current_level = enrollment_info['CurrentGECourseLocation']['Levels'][0]['LevelNo']
    current_unit = enrollment_info['CurrentGECourseLocation']['Levels'][0]['Units'][0]['UnitNo']
    return current_level, current_unit


def get_basic_offline_coupon_info(student_id):
    """
    Get offline left coupon
    :param student_id:
    :return: eg. {'F2F': 1, 'Workshop': 1, 'LCApply': 1, 'EEA': 0}
    """
    coupon_info = {}
    info = get_student_coupon_info(student_id)
    offline_basic_coupon_info = info['ClassicCoupons']

    for c in offline_basic_coupon_info:
        coupon_info[c['CouponName']] = c['Count']

    return coupon_info


def get_special_offline_coupon_info(student_id):
    """
    Get offline special left coupon, eg. career track, skills clinics
    :param student_id:
    :return: eg. {'CareerWorkshop': 8, 'Skills': 18}
    """
    coupon_info = {}
    info = get_student_coupon_info(student_id)
    special_coupon = info['SpecialCoupons']

    for c in special_coupon:
        coupon_info[c['CouponName']] = c['Count']

    return coupon_info


def get_online_coupon_info(student_id):
    """
    Get online left coupon
    :param student_id:
    :return: eg. {'GL': 0, 'PL20': 1, 'OSC': 18}
    """
    coupon_info = {}
    info = get_student_coupon_info(student_id)
    online_coupon = info['OnlineCoupons']

    for c in online_coupon:
        coupon_info[c['CouponName']] = c['Count']

    return coupon_info


def get_student_top_level_code(student_id):
    enrollment_info = get_student_enrollments_info(student_id)
    return enrollment_info['EnrolledGEStageLevels'][-1]


def get_student_account_info(student_name, password):
    """
    Get student info details which include accountInfo, basicInfo, contactInfo and preferenceInfo
    :param student:
    :return: eg.
        [
            {"accountInfoDetail":{"nameBlurbId": 712631, ..., "displayOrder":10}},
            {"basicInfoDetail": {"allowBatchUpdate": True, ..., "items": [...]}},
            {"contactInfoDetail": {"nameBlurbId": 121832, ..., "items": [...]}},
            {"preferenceInfoDetail": {"nameBlurbId": 712634, ..., "items": [...]}}
        ]
    """
    query_string = 'q=ecapi_myaccount_information!current'
    return query_troop_service(student_name, query_string, password=password, login_required=True)


def change_expiration_date(student_id, days_offset):
    """
    update the expiration date
    :param student_id: expired student id
    :param days_offset: less than 0
    :return:
    """
    url = '{}/services/oboe2/SalesForce/Test/UpdateStudentExpirationDate?token={}'.format(config.etown_root,
                                                                                          get_token())
    data = {'studentId': student_id,
            'dayOffset': days_offset}

    response = no_ssl_requests().post(url, data=data)
    assert '"Success":true' in response.text, response.text


def convert_to_smart_plus(student_id):
    url = '{}/services/oboe2/ProductConversion/Conversion/ConvertToSmartPlus'.format(config.etown_root)

    data = {
        'studentId': student_id,
        'operatorUser': 'qa.testauto',
        'token': '62c79778-c497-434f-89ab-e6debe4f2a18'
    }

    response = no_ssl_requests().post(url, data=data)

    assert response.status_code == HTTP_STATUS_OK and '"Success":true' in response.text, response.text


def get_student_left_days_by_subscription(student_id):
    """Get China S18 student left days. Need convert expired date to home center date."""
    subscription = get_student_active_subscription(student_id=student_id)
    expiration_date = datetime.strptime(subscription[0]['expiration_utc_date'].split('T')[0], '%Y-%m-%d')
    expiration_date = convert_utc_to_target_timezone(Timezone.CHINA, expiration_date)
    current_local_time = get_current_china_date_time()

    left_days = (expiration_date.date() - current_local_time.date()).days
    return left_days


def get_student_left_days_by_fag(student_id):
    """Get China S18 student left days. Need convert expired date to home center date."""
    grants = get_student_feature_access_grants(student_id=student_id)
    grant_list = [item for item in grants if item['FeatureAccessId'] == 11]

    # When having many GL FAG records, need filter out not expired record
    left_days = 0
    for item in grant_list:
        expiration_date = datetime.strptime(item['ActiveToUTCDate'].split('T')[0], '%Y-%m-%d')
        expiration_date = convert_utc_to_target_timezone(Timezone.CHINA, expiration_date)
        current_local_time = get_current_china_date_time()
        left_days = (expiration_date.date() - current_local_time.date()).days

        if left_days > 0:
            left_days = left_days
            break

    return left_days
