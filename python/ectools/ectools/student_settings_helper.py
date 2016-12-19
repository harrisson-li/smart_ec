"""
This module provides methods to get or set student flags, as well as member site settings.

-----
"""
import re
from datetime import datetime
from io import StringIO
from xml.etree import ElementTree

import requests

from ectools.config import config


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
    assert result.status_code == 200, "Failed to call membersettings.svc: {}".format(result.text)

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
