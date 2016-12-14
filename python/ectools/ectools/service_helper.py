import requests
from config import config
import xmltodict


def is_platform_20_student(student_id):
    return True


def get_member_site_settings(student_id):
    root = config.etown_root
    headers = {'SOAPAction': "EFSchools.Englishtown.SharedServices.Client.MemberSettings/"
                             "IMemberSettingsService/LoadMemberSiteSettings",
               'Content-type': 'text/xml',
               'Accept': 'text/plain'}

    svc = '/services/shared/1.0/membersettings.svc'
    data = '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">' \
           '<s:Body><LoadMemberSiteSettings ' \
           'xmlns="EFSchools.Englishtown.SharedServices.Client.MemberSettings">' \
           '<input xmlns:a="EFSchools.Englishtown.SharedServices.Client.MemberSettings.DataContracts" ' \
           'xmlns:i="http://www.w3.org/2001/XMLSchema-instance"><a:Member_id>{}</a:Member_id>' \
           '<a:SiteArea>{}</a:SiteArea></input></LoadMemberSiteSettings></s:Body></s:Envelope>'
    result = requests.post(root + svc, data=data.format(student_id, 'school'), headers=headers)
    school_settings = xmltodict.parse(result.text)
    site_settings = school_settings['s:Envelope']['s:Body']['LoadMemberSiteSettingsResponse']['LoadMemberSiteSettingsResult']['a:SiteSettings']['b:KeyValueOfstringstring']
    for i in site_settings:
        for v in i.values():
            print(v)

    result = requests.post(root + svc, data=data.format(student_id, 'school_ec'), headers=headers)
    school_settings.update(xmltodict.parse(result.text))
    return school_settings
