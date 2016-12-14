import re

import requests

from internal.data_helper import *
from config import get_logger, config


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
              securityverified  = True
              includesenroll    = True


    :return: A student dict with all info.
    :rtype: dict

    """

    def merge_activation_data(source_dict, **more):
        source_dict.update(more)

        for key in ['securityverified', 'includesenroll']:
            if source_dict.get(key, 'on') != 'on':
                del source_dict[key]

        return source_dict

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
        is_v2 = is_v2_school(school_name)

    get_logger().info('Start to activate test account...')
    assert school['partner'].lower() == product['partner'].lower(), "Partner not match for school and product!"

    if student is None:
        student = create_account_without_activation(is_e10=is_item_has_tag(product, 'E10'))
    else:
        assert isinstance(student, dict)

    student['is_v2'] = is_v2
    student['is_e10'] = is_item_has_tag(product, 'E10')
    link = get_link(is_item_has_tag(product, 'E10'))

    data = get_default_activation_data(product)
    data = merge_activation_data(data, **kwargs)
    data['memberId'] = student['member_id']
    data['divisionCode'] = school['division_code']

    if not student['is_e10']:
        del data['levelQty']  # e10 student cannot set 'levelQty'

    get_logger().debug('Activation data: %s', data)
    result = requests.post(link, data=data)

    assert result.status_code is 200 and 'success' in result.text, result.text
    student['product'] = product
    student['school'] = school
    student['is_activated'] = True
    student['partner'] = config.partner
    student['country_code'] = config.country_code
    student.update(kwargs)
    return student


def activate_e10_student(product_id=None, school_name=None, **kwargs):
    if product_id is None:
        product_id = get_any_e10_product()['id']
    return activate_account(product_id=product_id, school_name=school_name, is_v2=False, **kwargs)


def activate_s15_student(product_id=None, school_name=None, **kwargs):
    return activate_account(product_id=product_id, school_name=school_name, is_v2=False, **kwargs)


def activate_home_student(school_name=None, **kwargs):
    product_id = get_any_home_product()['id']
    return activate_account(product_id=product_id, school_name=school_name, is_v2=False, **kwargs)


def activate_school_student(school_name=None, **kwargs):
    product_id = get_any_school_product()['id']
    return activate_account(product_id=product_id, school_name=school_name, is_v2=False, **kwargs)


def activate_s15_v2_student(product_id=None, school_name=None, **kwargs):
    return activate_account(product_id=product_id, school_name=school_name, **kwargs)


def activate_home_v2_student(school_name=None, **kwargs):
    product_id = get_any_home_product()['id']
    return activate_account(product_id=product_id, school_name=school_name, **kwargs)


def activate_school_v2_student(school_name=None, **kwargs):
    product_id = get_any_school_product()['id']
    return activate_account(product_id=product_id, school_name=school_name, **kwargs)


def activate_school_student_with_random_level(product_id=None,
                                              school_name=None,
                                              is_v2=True,
                                              min_level=1,
                                              max_level=16,
                                              **kwargs):
    level = get_random_level(min_level, max_level)
    kwargs.update({'startLevel': level})
    if not product_id:
        product_id = get_any_school_product()['id']

    return activate_account(product_id=product_id, school_name=school_name, is_v2=is_v2, **kwargs)


def activate_home_student_with_random_level(product_id=None,
                                            school_name=None,
                                            is_v2=True,
                                            min_level=1,
                                            max_level=16,
                                            **kwargs):
    level = get_random_level(min_level, max_level)
    kwargs.update({'startLevel': level})
    if not product_id:
        product_id = get_any_home_product()['id']

    return activate_account(product_id=product_id, school_name=school_name, is_v2=is_v2, **kwargs)


def convert_student_to_object(student_dict,
                              student_object_type,
                              product_object_type=None,
                              school_object_type=None):
    """
    Method to convert student dict into student object.
    :param student_dict: Usually get from after activating a test account.
    :param student_object_type: The class name of student object, must import first.
    :param product_object_type: The class name of product object, will not convert if none.
    :param school_object_type: The class name of school object, will not convert if none.
    :return: A student object in 'student_object_type'
    """
    assert isinstance(student_dict, dict), "student_dict must be a dict!"
    student_object = student_object_type()

    for k, v in student_dict.items():
        if k == 'product' and product_object_type:
            product = product_object_type()
            for pk, pv in v.items():
                setattr(product, pk, pv)
            setattr(student_object, 'product', product)

        elif k == 'school' and school_object_type:
            school = school_object_type()
            for sk, sv in v.items():
                setattr(school, sk, sv)
            setattr(student_object, 'school', school)

        else:
            setattr(student_object, k, v)

    return student_object
