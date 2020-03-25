# -*- coding: utf-8 -*-

"""
This module provides methods to get or set student flags, as well as member site settings.

-----
"""
import json
import re
from datetime import datetime
from io import StringIO
from xml.etree import ElementTree

import arrow
import requests

from ectools.config import config
from ectools.constant import Memcached, ClearCacheType
from ectools.internal import sf_service_helper as sf
from ectools.internal import troop_service_helper
from ectools.internal.constants import HTTP_STATUS_OK
from ectools.internal.troop_service_helper import DEFAULT_PASSWORD
from ectools.token_helper import get_token, get_site_version
from ectools.utility import camelcase_to_underscore, no_ssl_requests

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
    return site_settings.get('student.platform.version', '1.0') == '2.0'


def is_e19_student(student_id):
    site_settings = get_member_site_settings(student_id)
    return site_settings.get('student.platform.mapcode', 'ec') == 'ec19'


def get_member_site_settings(student_id, site_area='school'):
    service_url = '/services/shared/1.0/membersettings.svc'
    headers = {'SOAPAction': "EFSchools.Englishtown.SharedServices.Client.MemberSettings/"
                             "IMemberSettingsService/LoadMemberSiteSettings",
               'Content-type': 'text/xml',
               'Accept': 'text/plain'}

    data = """<s:Envelope
                xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                <s:Body>
                    <LoadMemberSiteSettings
                        xmlns="EFSchools.Englishtown.SharedServices.Client.MemberSettings">
                        <input
                            xmlns:a="EFSchools.Englishtown.SharedServices.Client.MemberSettings.DataContracts"
                            xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                            <a:Member_id>{}</a:Member_id>
                            <a:SiteArea>{}</a:SiteArea>
                        </input>
                    </LoadMemberSiteSettings>
                </s:Body>
            </s:Envelope>"""
    result = no_ssl_requests().post(config.etown_root_http + service_url, data=data.format(student_id, site_area),
                                    headers=headers)
    assert result.status_code == HTTP_STATUS_OK, "Failed to call membersettings.svc: {}".format(result.text)

    site_settings = {}
    datetime_format = "%Y-%m-%d %H:%M:%S"
    setting_xpath = ".//b:KeyValueOfstringstring"

    root = ElementTree.fromstring(result.text)
    namespaces = dict([node for _, node in ElementTree.iterparse(
        StringIO(result.text), events=['start-ns'])])

    for element in root.findall(setting_xpath, namespaces):
        key = element.find('b:Key', namespaces).text
        value = element.find('b:Value', namespaces).text

        if value and re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', value):
            value = datetime.strptime(value, datetime_format)

        site_settings[key] = value

    return site_settings


def set_member_site_settings(student_id, key_name, key_value, site_area='school', is_time_value=False):
    if is_time_value:
        key_value = arrow.get(key_value).format('M/D/YYYY hh:mm:ss')

    url = '{}/services/ecplatform/Tools/StudentSettings/SaveMemberSiteSetting'.format(config.etown_root)
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

    def get_name_and_email(student_id):
        target_url = "{}/services/ecplatform/Tools/StudentView?id={}&token={}".format(
            config.etown_root, student_id, get_token())
        response = no_ssl_requests().get(target_url)

        if response.status_code == HTTP_STATUS_OK:
            result = re.findall('\[Name\] : (.*) \[Email\] : (.*)', response.text)
            return result[0][0].strip(), result[0][1].strip()
        else:
            raise ValueError("Failed to get student name and email!")

    username, email = get_name_and_email(student_id)
    info = {'username': username, 'email': email, 'member_id': student_id}

    more_info = {camelcase_to_underscore(k): v for k, v in ecplatform_load_student(student_id).items()}
    info.update(more_info)

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

    return info


def call_ecplatform_service(service_url, payload):
    headers = {
        '_ECToken': '9657ade8014d71344604800e3d34a3579bd1',
        'Content-Type': 'application/json',
        'Accept': 'text/plain'
    }
    response = no_ssl_requests().post(config.etown_root_http + service_url, json=payload, headers=headers)
    if response.status_code == HTTP_STATUS_OK:
        return json.loads(response.text)
    else:
        raise ValueError(response.text)


def ecplatform_load_student(student_id):
    """Call service: EFSchools.EC.Platform.Service.IStudentService | LoadStudent"""
    service_url = "/services/ecplatform/studentservice.svc/rest/LoadStudent"
    payload = {"StudentId": "{}".format(student_id)}
    return call_ecplatform_service(service_url, payload)


def ecplatform_load_student_basic_info(student_id):
    """Call service: EFSchools.EC.Platform.Service.IStudentService | LoadStudentBasicInfo"""
    service_url = "/services/ecplatform/studentservice.svc/rest/LoadStudentBasicInfo"
    payload = {"StudentId": "{}".format(student_id)}
    return call_ecplatform_service(service_url, payload)


def ecplatform_load_student_status_flag(student_id):
    """Call service: EFSchools.EC.Platform.Service.IStudentService | LoadStudentStatusFlag"""
    service_url = "/services/ecplatform/studentservice.svc/rest/LoadStudentStatusFlag"
    payload = {"StudentId": "{}".format(student_id)}
    return call_ecplatform_service(service_url, payload)


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


def query_troop_service(student_name,
                        query_string,
                        login_required=True,
                        password=DEFAULT_PASSWORD,
                        return_first_item=True,
                        use_default_context=True):
    if login_required:
        troop_service_helper.login(student_name, password)

    url_with_context = True if student_name else False
    return troop_service_helper.query(student_name,
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


def account_service_load_student(student_name_or_id):
    """load account info via /services/commerce/1.0/AccountService.svc"""
    target_url = config.etown_root_http + '/services/commerce/1.0/AccountService.svc'
    headers = {'Content-Type': 'text/xml',
               'SOAPAction': 'http://tempuri.org/IAccountService/GetMemberInfo'}

    body = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">' \
           '<s:Body><GetMemberInfo xmlns="http://tempuri.org/"><member_id>{}</member_id>' \
           ' </GetMemberInfo></s:Body></s:Envelope>'.format(student_name_or_id)

    id_response = no_ssl_requests().post(target_url, data=body, headers=headers)
    response_xml = id_response.text

    # try to load as username if failed to load by id
    if id_response.status_code != HTTP_STATUS_OK:
        headers['SOAPAction'] = 'http://tempuri.org/IAccountService/GetMemberByEmailOrUserName'
        body = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">' \
               '<s:Body><GetMemberByEmailOrUserName xmlns="http://tempuri.org/">' \
               '<emailOrUserName>{}</emailOrUserName></GetMemberByEmailOrUserName>' \
               '</s:Body></s:Envelope>'.format(student_name_or_id)

        name_response = no_ssl_requests().post(target_url, data=body, headers=headers)
        assert name_response.status_code == HTTP_STATUS_OK, id_response.text + name_response.text
        response_xml = name_response.text

    return parse_xml(response_xml)


def account_service_update_phone2(student_id, phone_number):
    """update telephone2 via /services/commerce/1.0/AccountService.svc"""
    account_service_update_info(student_id, {'MobilePhone': phone_number})


def account_service_update_info(student_id, info):
    """
    update basic info via /services/commerce/1.0/AccountService.svc
    info: dict data to update the account, e.g.{'MobilePhone':123, FirstName:'test', LastName:'test'}
    """
    target_url = config.etown_root_http + '/services/commerce/1.0/AccountService.svc'
    headers = {'Content-Type': 'text/xml',
               'SOAPAction': 'http://tempuri.org/IAccountService/UpdateBasicInfo'}

    updates = '<efs:Member_id>{}</efs:Member_id>'.format(student_id)

    for k, v in info.items():
        updates += '<efs:{0}>{1}</efs:{0}>'.format(k, v)

    body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/" xmlns:efs="EFSchools.Englishtown.Commerce.Client.Members">
                   <soapenv:Header/>
                   <soapenv:Body>
                      <tem:UpdateBasicInfo>
                         <tem:member>{}</tem:member>
                      </tem:UpdateBasicInfo>
                   </soapenv:Body>
                </soapenv:Envelope> """.format(updates)

    response = no_ssl_requests().post(target_url, data=body, headers=headers)
    assert 'Success>true' in response.text, response.text


def adjust_level(student_id, to_level_code):
    sf.change_level(student_id, to_level_code)


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
    url = '{}/services/oboe2/salesforce/test/UpsellCoupon'.format(config.etown_root)
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
    url = '{}/services/oboe2/salesforce/test/AdjustCoupon'.format(config.etown_root)
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
    data = {"updateItemInfos": {
        "password": json.dumps(password_info, sort_keys=False)}}

    return troop_command_update_information(student_name, data, old_password)


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
    """load student active subscription info via /services/commerce/1.0/SubscriptionService.svc"""
    target_url = config.etown_root_http + '/services/commerce/1.0/SubscriptionService.svc'
    headers = {'Content-Type': 'text/xml',
               'SOAPAction': 'http://tempuri.org/ISubscriptionService/GetActiveSubscription'}
    body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
                <soapenv:Header/>
                <soapenv:Body>
                    <tem:GetActiveSubscription>
                    <!--Optional:-->
                    <tem:member_id>{}</tem:member_id>
                    </tem:GetActiveSubscription>
                </soapenv:Body>
            </soapenv:Envelope>""".format(student_id)

    response = no_ssl_requests().post(target_url, data=body, headers=headers)
    response_xml = response.text

    assert response.status_code == HTTP_STATUS_OK

    return parse_xml(response_xml)


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
    graphql_url = config.etown_root + GRAPHQL_SERVICE_URL

    graphql_result = requests.post(graphql_url,
                                   data=json.dumps(data),
                                   headers={"X-EC-CMUS": client.cookies['CMus'],
                                            "X-EC-SID": client.cookies['et_sid'],
                                            "X-EC-LANG": "en"})

    return graphql_result.json()["data"]["student"][info]


def get_student_coupon_info(student_id):
    """
    Get the student coupon info
    :param student_id
    :return: coupon info, eg. {'ClassicCoupons': [{'CouponName': 'F2F', 'Count': 5},
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
                               'Message': ''}
    """
    target_url = config.etown_root + STUDENT_COUPONS['URL']
    data = {
        STUDENT_COUPONS['DATA']: student_id
    }

    response = no_ssl_requests().post(target_url, data=data)
    return response.json()


def get_basic_offline_coupon_info(student_id):
    coupon_info = {}
    info = get_student_coupon_info(student_id)
    offline_basic_coupon_info = info['ClassicCoupons']

    for c in offline_basic_coupon_info:
        coupon_info[c['CouponName']] = c['Count']

    return coupon_info


def get_special_offline_coupon_info(student_id):
    coupon_info = {}
    info = get_student_coupon_info(student_id)
    special_coupon = info['SpecialCoupons']

    for c in special_coupon:
        coupon_info[c['CouponName']] = c['Count']

    return coupon_info


def get_online_coupon_info(student_id):
    coupon_info = {}
    info = get_student_coupon_info(student_id)
    online_coupon = info['OnlineCoupons']

    for c in online_coupon:
        coupon_info[c['CouponName']] = c['Count']

    return coupon_info
