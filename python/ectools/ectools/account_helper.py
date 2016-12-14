import re

import requests

from internal.data_helper import *
from config import get_logger, config
from internal.objects import *


def create_account_without_activation(is_e10=False):
    """
    To create a test account, but not activate it.

    :param is_e10: Use E10 create account url.

    """

    def get_link():
        url = '{}/services/oboe2/salesforce/test/CreateMemberFore14hz?ctr={}&partner={}'
        url = url.format(config.etown_root, config.country_code, config.partner)

        if is_e10:
            return url.replace('e14hz', config.partner)
        else:
            return "{}&v=2".format(url)

    student = {'is_e10': is_e10, 'environment': config.env}
    link = get_link()
    result = requests.get(link)

    assert result.status_code is 200 and 'Success' in result.text, result.text
    pattern = r'.+studentId\: (?P<id>\d+), username\: (?P<name>.+), password\: (?P<pw>.+)<br.+'
    match = re.match(pattern, result.text)

    if match:
        student['member_id'] = match.group('id')
        student['username'] = match.group('name')
        student['password'] = match.group('pw')
        get_logger().debug('New test account: %s', student)
        return student

    else:
        raise SystemError('Cannot create new account: {}'.format(result.text))


def _merge_activation_data(source_dict, *args):
    """Merge multiple dictionaries into source_dict dictionary."""
    for data in args:
        source_dict.update(data)
    return source_dict


def activate_account(product_id=None, school_name=None, is_v2=True, student=None, **kwargs):
    """
    To activate a test account and return a student object

    :param product_id: If not specified will randomly get a major product (home/school) from current partner.
    :param school_name: If not specified will randomly get a school from current partner.
    :param is_v2: True will activate Platform 2.0 student.
    :param student: Specify a student to activate. (student['member_id'] must be valid.).

    :keyword: mainRedemptionQty = 3
              freeRedemptionQty = 3
              startLevel        = '0A'
              levelQty          = '16'
              securityverified  = 'on'
              includesenroll    = 'on'


    :return: A student dict with all info.
    :rtype: dict

    """

    def get_link(is_e10):
        url = '{}/services/oboe2/salesforce/test/ActivateV2'
        url = url.format(config.etown_root)

        if is_e10:
            return url.replace('V2', 'E10')
        else:
            return url

    if product_id is None:
        product = get_any_product()
    else:
        product = get_product_by_id(product_id)

    if school_name is None:
        school = get_any_v2_school() if is_v2 else get_any_school()
    else:
        school = get_school_by_name(school_name)

    get_logger().info('Start to activate test account...')
    assert school['Partner'] == product['Partner'], "Partner not match for school and product!"

    if student is None:
        student = create_account_without_activation(is_e10=product.is_e10)
    else:
        assert isinstance(student, dict)

    student.is_v2 = is_v2
    student.is_e10 = product.is_e10
    link = get_link(product.is_e10)

    data = get_default_activation_data(product)
    data = _merge_activation_data(data, kwargs)
    data['memberId'] = student['member_id']
    data['divisionCode'] = school['DivisionCode']

    if not student.is_e10:
        del data['levelQty']  # e10 student cannot set 'levelQty'

    get_logger().debug('Activation data: %s', data)
    result = requests.post(link, data=data)

    assert result.status_code is 200 and 'success' in result.text, result.text
    student['product'] = product
    student['school'] = school
    student['data'] = data
    student['is_activated'] = True
    student['partner'] = config.partner
    student['country_code'] = config.country_code
    return student
