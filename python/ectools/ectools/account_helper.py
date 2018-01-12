"""
This module provides methods to create or activate EFEC test accounts.
Here is a quick example to play with this module::

  from ectools.account_helper import *

  account = activate_account(is_v2=True)  # will return a dict includes all details
  for k, v in account.items():
      print("account {0}: {1}".format(k,v))

  # you can convert the account to your self-defined object type
  from my.objects import Student, School, Product
  student = convert_account_to_object(account, Student, Product, School)  # Product and School are optional
  print(student.member_id)
  print(student.school.name)
  
  # or you might want to reuse an account, default expiration days = 365
  account = get_or_activate_account(tag='ECS-1254', is_v2=True)  # will activate one if not existed
  account = get_or_activate_account(tag='ECS-1254', is_v2=True)  # will return same one if not expired

For more info about using EFEC test account, please refer to confluence page or ping EC QA team.

-----

"""

from ectools.config import get_logger
from ectools.internal import sf_service_helper
from ectools.internal.account_service import *
from ectools.internal.constants import HTTP_STATUS_OK
from ectools.internal.data_helper import *
from ectools.service_helper import is_v2_student


def get_or_activate_account(tag, expiration_days=365, method='activate_account', **kwargs):
    """
    To get an account with specified tag, if not exist or expired will activate a new one.
    If the account is found by tag, it will contains a key named: found_by_tag.
    
    :param tag: Specified tag to search a test account.
    :param expiration_days: Will activate a new one if cannot get within expiration days.
    :param method: method to activate account, can be any activation method in this module.
    :param kwargs: Arguments for method **activate_account**.  
    """
    accounts = get_accounts_by_tag(tag)

    if accounts and not is_account_expired(accounts[0], expiration_days):
        account = accounts[0]
        account['found_by_tag'] = tag  # for call back actions
        get_logger().info('Found account with tag "{}": {}'.format(tag, account))
        return account

    else:
        # the account activation days should be larger than expiration day
        kwargs['mainRedemptionQty'] = (expiration_days // 30) + 1

        current_module = sys.modules[__name__].__dict__
        account = current_module[method](**kwargs)

        get_logger().info('Tag account with "{}"'.format(tag))
        save_account(account, add_tags=[tag])
        return account


def create_account_without_activation(is_e10=False):
    student = {'is_e10': is_e10, 'environment': config.env}
    link = get_new_account_link(is_e10)
    result = requests.get(link)

    assert result.status_code == HTTP_STATUS_OK and 'Success' in result.text, result.text

    # the correct result will look like: ...studentId: <id>, username: <name>, password: <pw>
    pattern = r'.+studentId\: (?P<id>\d+), username\: (?P<name>.+), password\: (?P<pw>[^<br]+)'

    match = re.match(pattern, result.text)
    if match:
        student['member_id'] = match.group('id')
        student['username'] = match.group('name')
        student['password'] = match.group('pw')

        save_account(student, add_tags=[config.env, 'not_activated'])
        return student
    else:
        raise EnvironmentError('Cannot create new account: {}'.format(result.text))


def activate_account(product_id=None,
                     school_name=None,
                     is_v2=True,
                     is_s18=False,
                     auto_onlineoc=True,
                     student=None,
                     **kwargs):
    """
    Activate a test account and return a dict object with account info.
    When activate cool and mini accounts will auto enable Online OC features.

    :param product_id: If not specified will randomly get a major product (home/school) from current partner.
    :param school_name: If not specified will randomly get a school from current partner.
    :param is_v2: True will activate Platform 2.0 student.
    :param is_s18: True will use S18 redemption code.
    :param auto_onlineoc: Cool or Mini will enable online OC automatically.
    :param student: Specify a student to activate, `student['member_id']` must be valid.

    :keyword: Can be one or more of below, please refer to account tool page for more detail.

              - mainRedemptionQty = 3
              - freeRedemptionQty = 3
              - startLevel        = '0A'
              - levelQty          = '16'
              - securityverified  = True
              - includesenroll    = True


    :return: A dict with all account info.
    """

    if product_id is None:
        product = get_any_product(is_s18=is_s18)
    else:
        product = get_product_by_id(product=product_id, is_s18=is_s18)

    if school_name is None:
        school = get_any_v2_school() if is_v2 else get_any_school()
    else:
        school = get_school_by_name(school_name)
        is_v2 = is_v2_school(school_name)  # fix account version according to school

    is_lite = is_lite_product(product)
    assert is_lite == is_lite_school(school), \
        "Miss match product [{}] and school [{}] for ECLite account!".format(product['id'], school['name'])

    get_logger().info('Start to activate test account...')
    assert school['partner'].lower() == product['partner'].lower(), "Partner not match for school and product!"

    if student is None:
        student = create_account_without_activation(is_e10=is_item_has_tag(product, 'E10'))
    else:
        assert isinstance(student, dict)

    student['is_v2'] = is_v2
    student['is_e10'] = is_item_has_tag(product, 'E10')
    link = get_activate_account_link(student['is_e10'])

    data = get_default_activation_data(product)
    data = merge_activation_data(data, **kwargs)
    data['memberId'] = student['member_id']
    data['divisionCode'] = school['division_code']
    should_enroll = data.get('includesenroll', False)

    if should_enable_onlineoc(auto_onlineoc, student, school) and 'includesenroll' in data:
        del data['includesenroll']

    if not student['is_e10']:
        del data['levelQty']  # e10 student cannot set 'levelQty'

    result = requests.post(link, data=data)
    success_text = 'success' if student['is_e10'] else 'IsSuccess:True'
    assert result.status_code == HTTP_STATUS_OK and success_text in result.text, result.text

    student['product'] = product
    student['school'] = school
    student['is_activated'] = True
    student['partner'] = config.partner
    student['country_code'] = config.country_code
    student['domain'] = config.domain
    student['environment'] = config.env
    student['is_eclite'] = is_lite
    student.update(kwargs)

    tags = [config.env, config.partner]
    if student['is_e10']:
        tags.append('E10')
    else:
        tags.append('S18' if is_s18 else 'S15')

    if is_v2:
        tags.append('V2')

    if is_lite:
        tags.append('ECLite')

    if should_enable_onlineoc(auto_onlineoc, student, school):
        # set hima test level and append tags

        set_hima = kwargs.get('set_hima', True)
        level_code = kwargs.get('startLevel', '0A')
        if set_hima:
            sf_set_hima_test(student['member_id'], level_code)

        tags.append('OnlineOC')
        student['is_onlineoc'] = True

    get_logger().debug('New test account: {}'.format(student))
    save_account(student, add_tags=tags, remove_tags=['not_activated'])

    if should_enroll:
        password = '1' if 'password' not in student else student['password']
        enroll_account(student['username'], password)

        # ensure account version is correct before return
        if is_v2 != is_v2_student(student['member_id']):
            raise AssertionError(
                "Incorrect account version! Please double check target school version: {}".format(school))

    return student


def enroll_account(username, password):
    """
    Enroll student with level and course info, only work for online oc students.
    Login via mobile enroll page will do the work.
    """
    if config.partner not in ['Cool', 'Mini', 'Socn']:
        get_logger().debug('No need to enroll account as it is not in CN partners')
        return

    login_url = get_login_post_link()
    data = {'username': username, 'password': password, 'onsuccess': '/ecplatform/mvc/mobile/dropin'}

    s = requests.session()
    response = s.post(url=login_url, data=data)

    if response.status_code == 200 and response.json()['success']:
        redirect = response.json()['redirect']
        result = s.get(redirect, allow_redirects=True)
        if 'mobile/welcome' in result.url:
            get_logger().info('Enroll account {} success'.format(username))
        else:
            get_logger().error('Enroll to {}, detail: {}'.format(result.url, result.text))
            raise AssertionError('Error occurred when enroll account {}'.format(username))

    else:
        raise ValueError('Fail to login with user {} / {}! '.format(username, password) + response.text)


def activate_account_by_dict(data):
    """Another method to activate account by data dict."""
    assert isinstance(data, dict), 'data must be in dict type!'
    product_id = data.pop('product_id', None)
    school_name = data.pop('school_name', None)
    is_v2 = data.pop('is_v2', True)
    student = data.pop('student', None)
    return activate_account(product_id=product_id,
                            school_name=school_name,
                            is_v2=is_v2,
                            student=student,
                            **data)


def activate_e10_student(**kwargs):
    kwargs['is_v2'] = False
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_e10_product()['id']
    return activate_account_by_dict(kwargs)


def activate_s15_student(**kwargs):
    kwargs['is_v2'] = False
    return activate_account_by_dict(kwargs)


def activate_home_student(**kwargs):
    kwargs['is_v2'] = False
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_home_product()['id']
    return activate_account_by_dict(kwargs)


def activate_school_student(**kwargs):
    kwargs['is_v2'] = False
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_school_product()['id']
    return activate_account_by_dict(kwargs)


def activate_s18_student(**kwargs):
    kwargs['is_s18'] = True
    return activate_account_by_dict(kwargs)


def activate_s18_home_student(**kwargs):
    kwargs['is_s18'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_home_product(is_s18=True)['id']
    return activate_account_by_dict(kwargs)


def activate_s18_school_student(**kwargs):
    kwargs['is_s18'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_school_product(is_s18=True)['id']
    return activate_account_by_dict(kwargs)


def activate_s15_v2_student(**kwargs):
    return activate_account_by_dict(kwargs)


def activate_home_v2_student(**kwargs):
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_home_product()['id']
    return activate_account_by_dict(kwargs)


def activate_school_v2_student(**kwargs):
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_school_product()['id']
    return activate_account_by_dict(kwargs)


def activate_eclite_student(**kwargs):
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_eclite_product()['id']

    if 'school_name' not in kwargs:
        kwargs['school_name'] = get_any_eclite_school()['name']

    return activate_onlineoc_student(**kwargs)


def activate_onlineoc_student(**kwargs):
    if 'school_name' not in kwargs:
        kwargs['school_name'] = get_any_onlineoc_school()['name']

    student = activate_account_by_dict(kwargs)
    return student


def activate_onlineoc_school_student(**kwargs):
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_school_product()['id']
    return activate_onlineoc_student(**kwargs)


def activate_onlineoc_home_student(**kwargs):
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_home_product()['id']
    return activate_onlineoc_student(**kwargs)


def activate_student_with_random_level(min_level=1, max_level=16, **kwargs):
    level = get_random_level(min_level, max_level)
    kwargs['startLevel'] = level
    return activate_account_by_dict(kwargs)


def activate_school_student_with_random_level(min_level=1, max_level=16, **kwargs):
    level = get_random_level(min_level, max_level)
    kwargs['startLevel'] = level
    return activate_school_student(**kwargs)


def activate_home_student_with_random_level(min_level=1, max_level=16, **kwargs):
    level = get_random_level(min_level, max_level)
    kwargs['startLevel'] = level
    return activate_home_student(**kwargs)


def convert_account_to_object(account_dict,
                              account_object_type,
                              product_object_type=None,
                              school_object_type=None):
    """
    Convert account dict(activated from methods in this module) into a self-defined object.

    :param account_dict: Usually get after activating a test account.
    :param account_object_type: The class type of student object, must import it first.
    :param product_object_type: (Optional) The class type of product object, will not convert if none.
    :param school_object_type: (Optional) The class type of school object, will not convert if none.
    :return: An object in 'student_object_type'
    """
    assert isinstance(account_dict, dict), "account_dict must be a dict!"
    student_object = account_object_type()

    for k, v in account_dict.items():
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


def sf_suspend_student(student_id, suspend_date, resume_date):
    return sf_service_helper.suspend_student(student_id, suspend_date, resume_date)


def sf_resume_student(student_id):
    return sf_service_helper.resume_student(student_id)


def sf_set_hima_test(student_id, level_code='0A'):
    return sf_service_helper.set_hima_test(student_id, level_code)
