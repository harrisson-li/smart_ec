# -*- coding: utf-8 -*-

"""
This module provides methods to suspend or resume student.

-----
"""
import uuid
from datetime import datetime

from bs4 import BeautifulSoup as bs

import ectools.ecdb_helper_v2 as ecdb_v2
from ectools.config import config
from ectools.internal.constants import HTTP_STATUS_OK
from ectools.utility import no_ssl_requests

SF_NEW_ORG_SERVICE_URL = "/services/Oboe2/1.0/SalesforceNewOrgService.svc"
SF_SERVICE_URL = "/services/Oboe2/1.0/SalesForceService.svc"
SALESFORCE_USERNAME = "SalesforceSmartUser"
SALESFORCE_PASSWORD = "SalesforceSmartPwd"


def suspend_student(member_id, suspend_date, resume_date):
    """

    :param member_id: student's member id
    :param suspend_date: format like 'yyyy-mm-dd', e.g. '2017-04-02'
    :param resume_date: format like 'yyyy-mm-dd', e.g. '2017-04-02'
    :return:
    """
    reason_code = 'Internal Test'
    transaction_id = uuid.uuid4()

    headers = {
        'SOAPAction': "\"http://tempuri.org/ISalesforceNewOrgService/SuspendV2\"",
        'Content-type': 'text/xml',
        'Accept': 'text/xml'
    }

    data = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"><s:Header><o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
    <o:UsernameToken>
      <o:Username>{0}</o:Username>
      <o:Password>{1}</o:Password>
    </o:UsernameToken></o:Security></s:Header>

    <s:Body>
      <SuspendV2 xmlns="http://tempuri.org/">
        <param xmlns:a="http://schemas.datacontract.org/2004/07/EFSchools.Englishtown.Oboe.Services.DataContract.SalesForce" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
          <a:IsAsync>false</a:IsAsync>
          <a:Member_id>{2}</a:Member_id>
          <a:ReasonCode>{3}</a:ReasonCode>
          <a:ResumeDate>{4}</a:ResumeDate>
          <a:SuspendDate>{5}</a:SuspendDate>
          <a:TransactionId>{6}</a:TransactionId>
        </param>
        </SuspendV2>
    </s:Body>
    </s:Envelope>"""

    search_result = ecdb_v2.search_rows('ec_suspend_info', {'member_id': member_id})
    if search_result:
        raise ValueError("This student {} has been suspended on {} and will resume on {}, no need to suspend again. "
                         "Please resume first".format(member_id, search_result[0]['suspend_date'],
                                                      search_result[0]['resume_date']))

    result = no_ssl_requests().post(config.etown_root + SF_NEW_ORG_SERVICE_URL,
                                    data=data.format(SALESFORCE_USERNAME,
                                                     SALESFORCE_PASSWORD,
                                                     member_id,
                                                     reason_code,
                                                     resume_date,
                                                     suspend_date,
                                                     transaction_id),
                                    headers=headers)

    assert result.status_code == HTTP_STATUS_OK, result.text

    doc = bs(result.content, 'xml')

    if doc.find('IsSuccess').string == 'true':
        suspend_external_id = doc.find('SuspendExternalId').string
        info = {'member_id': member_id,
                'suspend_date': suspend_date,
                'resume_date': resume_date,
                'suspend_external_id': suspend_external_id}

        ecdb_v2.add_row_as_dict('ec_suspend_info', info)
        return suspend_external_id
    else:
        error_code = doc.find('ErrorCode').string
        error_message = doc.find('ErrorMessage').string

        raise SystemError('Error code and error message are: \n{}.\n{}'.format(error_code, error_message))


def resume_student(member_id):
    transaction_id = uuid.uuid4()
    result = ecdb_v2.search_rows('ec_suspend_info', {'member_id': member_id})

    if result:
        external_id = result[0]['suspend_external_id']
    else:
        raise ValueError("Cannot find valid external id and cannot resume student, or this student "
                         "has already been resumed.")

    resume_date = datetime.now().strftime('%Y-%m-%d')

    headers = {
        'SOAPAction': "\"http://tempuri.org/ISalesforceNewOrgService/ResumeV2\"",
        'Content-type': 'text/xml'
    }

    data = """
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
        <s:Header>
        <o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <o:UsernameToken>
        <o:Username>{}</o:Username>
        <o:Password>{}</o:Password>
        </o:UsernameToken>
        </o:Security>
        </s:Header>

        <s:Body>
        <ResumeV2 xmlns="http://tempuri.org/"><param xmlns:a="http://schemas.datacontract.org/2004/07/EFSchools.Englishtown.Oboe.Services.DataContract.SalesForce" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <a:ExternalId>{}</a:ExternalId>
        <a:IsAsync>false</a:IsAsync>
        <a:IsResumeNow>true</a:IsResumeNow>
        <a:Member_id>{}</a:Member_id>
        <a:ResumeDate>{}</a:ResumeDate>
        <a:TransactionId>{}</a:TransactionId>
        </param>
        </ResumeV2>
        </s:Body>
    </s:Envelope>
    """
    result = no_ssl_requests().post(config.etown_root + SF_NEW_ORG_SERVICE_URL,
                                    data=data.format(SALESFORCE_USERNAME,
                                                     SALESFORCE_PASSWORD,
                                                     external_id,
                                                     member_id,
                                                     resume_date,
                                                     transaction_id),
                                    headers=headers)

    assert result.status_code == HTTP_STATUS_OK, result.text

    doc = bs(result.content, 'xml')

    if doc.find('IsSuccess').string != 'true':
        raise SystemError(result.content)
    else:
        ecdb_v2.delete_rows('ec_suspend_info', {'member_id': member_id})


def set_hima_test(member_id, level_code):
    """

    :param member_id: student's member id
    :param level_code: level code from 0A - 14 for all partners
    :return:
    """
    headers = {
        'SOAPAction': "\"http://tempuri.org/ISalesForceService/SetHimaTestInfo\"",
        'Content-type': 'text/xml'
    }

    data = """
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
        <s:Header>
        <o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
        <o:UsernameToken>
        <o:Username>{}</o:Username>
        <o:Password>{}</o:Password>
        </o:UsernameToken>
        </o:Security>
        </s:Header>

        <s:Body>
        <SetHimaTestInfo xmlns="http://tempuri.org/"><param xmlns:a="http://schemas.datacontract.org/2004/07/EFSchools.Englishtown.Oboe.Services.DataContract.SalesForce" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <a:LevelCode>{}</a:LevelCode>
        <a:StudentId>{}</a:StudentId>
        <a:TestId>28</a:TestId>
        </param>
        </SetHimaTestInfo>
        </s:Body>
    </s:Envelope>
    """

    result = no_ssl_requests().post(config.etown_root + SF_SERVICE_URL,
                                    data=data.format(SALESFORCE_USERNAME, SALESFORCE_PASSWORD, level_code, member_id),
                                    headers=headers)

    assert result.status_code == HTTP_STATUS_OK, result.text

    doc = bs(result.content, 'xml')

    # raise error message if failed to set hima
    if doc.find('IsSuccess').string != 'true':
        msg = doc.find('ErrorMessage').string
        raise SystemError(msg)
