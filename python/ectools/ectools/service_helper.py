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

import requests

from ectools.config import config
from ectools.internal.constants import HTTP_STATUS_OK
from ectools.token_helper import get_token


def is_v2_student(student_id):
    site_settings = get_member_site_settings(student_id)
    return site_settings.get('student.platform.version') == '2.0'


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
    result = requests.post(config.etown_root + service_url, data=data.format(student_id, site_area), headers=headers)
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

        if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', value):
            value = datetime.strptime(value, datetime_format)

        site_settings[key] = value

    return site_settings


def get_student_info(student_id):
    """
    Will return a dict contains username, email, member_id, level, unit info for the student.
    """

    def get_name_and_email(student_id):
        target_url = "{}/services/ecplatform/Tools/StudentView?id={}".format(config.etown_root, student_id)
        response = requests.get(target_url)

        if response.status_code == HTTP_STATUS_OK:
            result = re.findall('\[Name\] : (.*) \[Email\] : (.*)', response.text)
            return result[0][0].strip(), result[0][1].strip()
        else:
            raise ValueError("Failed to get student name and email!")

    username, email = get_name_and_email(student_id)
    info = {'username': username, 'email': email}
    info.update(score_helper_load_student(student_id))

    return info


def call_ecplatform_service(service_url, payload):
    headers = {
        '_ECToken': '9657ade8014d71344604800e3d34a3579bd1',
        'Content-Type': 'application/json',
        'Accept': 'text/plain'
    }
    response = requests.post(config.etown_root + service_url, json=payload, headers=headers)
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
    response = requests.post(config.etown_root + target_url, data=data)
    match_char = u'★'
    result = {}

    if response.status_code == 200 and '|' in response.text:
        raw = response.text.split('|')
        result = {'username': raw[1], 'member_id': int(raw[3]), 'partner': raw[4]}
        levels = raw[5].split('#')
        units = raw[6].split('#')
        current_level = [l for l in levels if match_char in l][0]
        current_unit = [l for l in units if match_char in l][0]
        result['current_level'] = current_level[current_level.index(match_char) + 1:]
        result['current_unit'] = current_unit.split(' - ')[1]

    return result
