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
import uuid

from ectools.internal import sf_service_helper
from ectools.internal.account_service import *
from ectools.internal.constants import HTTP_STATUS_OK
from ectools.internal.data_helper import *
from ectools.logger import get_logger
from ectools.service_helper import account_service_load_student
from ectools.service_helper import is_v2_student
from ectools.utility import no_ssl_requests


def get_or_activate_account(tag, expiration_days=360, method='activate_account', **kwargs):
    """
    To get an account with specified tag, if not exist or expired will activate a new one.
    If the account is found by tag, it will contains a key named: found_by_tag.

    :param tag: Specified tag to search a test account.
    :param expiration_days: Will activate a new one if cannot get within expiration days.
    :param method: method to activate account, can be any activation method in this module.
    :param kwargs: Arguments for method **activate_account**.
    """
    accounts = get_accounts_by_tag(tag)

    if accounts and not is_account_expired(accounts[0]['member_id']):
        account = accounts[0]
        account['found_by_tag'] = tag  # for call back actions
        get_logger().info('Found account with tag "{}": {}'.format(tag, account))
        return account

    else:
        # the account activation days should be larger than expiration day
        length_months = expiration_days // 30
        kwargs['mainRedemptionQty'] = length_months if length_months > 0 else expiration_days

        current_module = sys.modules[__name__].__dict__
        account = current_module[method](**kwargs)

        get_logger().info('Tag account with "{}"'.format(tag))
        save_account(account, add_tags=[tag])
        return account


def create_account_without_activation(is_e10=False, **kwargs):
    student = {'is_e10': is_e10, 'environment': config.env, 'partner': config.partner}
    student.update(kwargs)
    link = get_new_account_link(is_e10)

    result = no_ssl_requests().get(link)

    assert result.status_code == HTTP_STATUS_OK and 'Success' in result.text, result.text
    info = result.text.split('<br />')[0]

    # the correct result will look like: ...studentId: <id>, username: <name>, password: <pw>
    pattern = r'.+studentId\: (?P<id>\d+), username\: (?P<name>.+), password\: (?P<pw>.+)'

    match = re.match(pattern, info)
    if match:
        student['member_id'] = match.group('id')
        student['username'] = match.group('name')
        student['password'] = match.group('pw')

        # update telephone 2 / first name / last name / email
        set_account_info(student)
        save_account(student, add_tags=[config.env, 'not_activated'])
        return student
    else:
        raise EnvironmentError('Cannot create new account: {}'.format(result.text))


def activate_account(product_id=None,
                     school_name=None,
                     is_v2=True,
                     is_s18=True,
                     is_e19=False,
                     is_smart_plus=False,
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
    :param is_e19: True will use to create ec19 course.
    :param is_smart_plus: True will use to create smart plus student.
    :param auto_onlineoc: Will auto determine if should go to online OC flow or not.
    :param student: Specify a student to activate, `student['member_id']` must be valid.

    :keyword: Can be one or more of below, please refer to account tool page for more detail.

              - mainRedemptionQty = 3
              - freeRedemptionQty = 3
              - startLevel        = '0A'
              - levelQty          = '16'
              - securityverified  = True
              - includesenroll    = True
              - cityCode          = e.g. 'sh_sh'
              - channel           = e.g. 'EC#SH_XJH'
              - onlineViceProducts= e.g. '{PL:20,CP20:30}'
              - packageProductIds = e.g. '1001,1010'
              - phoenix_packs     = e.g. ['pack1','pack2'], pack name => kiss.dbo.product / ProductName
              - is_v1_pack     = True



    :return: A dict with all account info.
    """
    get_logger().info('Start to activate test account...')
    get_logger().debug('Arguments: {}'.format(locals()))
    created_by = kwargs.pop('created_by', getpass.getuser())
    product_name = kwargs.pop('product_name', None)

    if not product_id and not school_name and not product_name:
        get_logger().info('Use default product and school.')
        product = get_default_product(is_s18=is_s18, is_e19=is_e19, is_smart_plus=is_smart_plus)
        school = get_default_school()

    else:
        # auto get product if not specified
        if not product_id and product_name:
            product = get_product_by_product_name(product_name)

        elif product_id:
            product = get_product_by_id(product=product_id, is_s18=is_s18, is_e19=is_e19, is_smart_plus=is_smart_plus)

        else:
            product = get_any_product(is_s18=is_s18, is_e19=is_e19, is_smart_plus=is_smart_plus)

        # auto get school if not specified
        if not school_name:
            school = get_any_v2_school() if is_v2 else get_any_v1_school()
        else:
            school = get_school_by_name(school_name)
            is_v2 = is_v2_school(school_name)  # fix account version according to school

    # initial student type
    is_s18 = is_s18_product(product)
    is_e19 = is_e19_product(product)
    is_smart_plus = is_smart_plus_product(product)
    is_lite = is_lite_product(product)
    is_phoenix = is_phoenix_product(product)
    is_trial = is_trial_product(product)

    # check eclite product should match eclite center
    if is_lite:
        if school_name is None:
            school = get_any_eclite_school()
        else:
            assert is_lite_school(school), \
                "Miss match product [{}] and school [{}] for ECLite account!".format(product['id'], school['name'])

    # partner of product and school should match for none-CN product
    if product['partner'] not in ['Socn', 'Cool', 'Mini']:
        assert school['partner'].lower() == product['partner'].lower(), "Partner not match for school and product!"

    # create member id if not specified
    if student is None:
        student = create_account_without_activation(
            is_e10=is_item_has_tag(product, 'E10'),
            created_by=created_by)
    else:
        assert isinstance(student, dict)

    # set course info in membersitesetting, eg. student.course.version = course.version.ec_e19 or course.version.ec_e17
    if product['partner'] in ['Socn', 'Cool', 'Mini'] and not is_e19:
        set_course_info(student['member_id'], is_e19)

    # generate activation data
    student['is_v2'], student['is_s18'] = is_v2, is_s18
    student['is_e10'] = is_item_has_tag(product, 'E10')
    student['is_eclite'] = is_lite
    student['is_phoenix'] = is_phoenix
    student['is_trial'] = is_trial
    student['is_e19'] = is_e19
    student['is_smart_plus'] = is_smart_plus
    student['source'] = kwargs.pop('source', 'ectools')

    link = get_activate_account_link(student['is_e10'])
    data = get_default_activation_data(product)
    data = merge_activation_data(data, **kwargs)
    data['memberId'], data['divisionCode'] = student['member_id'], school['division_code']
    data['orderId'] = str(uuid.uuid1())
    should_enroll = data.get('includesenroll', False)
    level_code = kwargs.get('startLevel', '0A')
    student['level_code'] = level_code

    # online oc student will need to enroll via login, so not include enroll when activate
    # others student will use set oc to enroll, so not include enroll when activate
    if should_enroll:
        del data['includesenroll']

    # e10 student cannot set 'levelQty'
    if not student['is_e10']:
        del data['levelQty']

    # Phoenix will use new activation link and activate center pack + online pack by default
    include_center_pack = data.pop('center_pack', True)
    include_online_pack = data.pop('online_pack', True)
    phoenix_packs = data.pop('phoenix_packs', [])

    if product['partner'] in ['Socn', 'Cool', 'Mini']:
        is_v1_pack = data.pop('is_v1_pack', False)
    else:
        is_v1_pack = True

    assert isinstance(phoenix_packs, list) or isinstance(phoenix_packs, dict), 'phoenix_packs should be a list or dict!'

    # For smart plus product, need phoenix_packs provided, don't need center pack + online pack
    if is_smart_plus:
        if not len(phoenix_packs):
            phoenix_packs.append(product['name'])  # smart plus product name is same with pack name

    # if phoenix_pack provided, will ignore 'center_pack' and 'online_pack' in argument
    if len(phoenix_packs):
        include_center_pack = False
        include_online_pack = False

    if is_phoenix:
        link = get_activate_pack_link()

        if include_center_pack:
            default_center_pack_name = 'Center Pack Basic' if is_v1_pack else '1 Year Basic'
            phoenix_packs.append(default_center_pack_name)

        if include_online_pack:
            default_online_pack_name = 'Online Pack Basic' if is_v1_pack else '1 Year Private'
            phoenix_packs.append(default_online_pack_name)

        # for trial product, always use trial pack
        if is_trial:
            phoenix_packs = ['Phoenix Free Trial']

        generate_activation_data_for_phoenix(data, phoenix_packs, is_v1_pack, is_smart_plus)
        student['is_v1_pack'] = is_v1_pack

    # post the data to activation tool
    result = no_ssl_requests().post(link, data=data)
    success_text = get_success_message(student)

    # save activation data will be good for troubleshooting
    data.update(kwargs)
    student['activation_data'] = data

    # handle activation failure flow, save account and append a tag as "Failed"
    if result.status_code != HTTP_STATUS_OK or success_text not in result.text:
        save_account(student, add_tags=['Failed', ])
        raise AssertionError(result.text)

    # update student detail as dict
    student['is_activated'], student['is_onlineoc'] = True, False
    student['product'], student['school'] = product, school
    student['partner'], student['country_code'] = config.partner, config.country_code
    student['domain'], student['environment'] = config.domain, config.env

    if should_enroll and student['is_v2']:
        # set hima test level for online oc student who will enroll
        if should_enable_onlineoc(auto_onlineoc, student, school):
            student['is_onlineoc'] = True
            set_hima = kwargs.get('set_hima', True)
            # set hima test level for online oc student who will enroll
            if set_hima:
                sf_set_hima_test(student['member_id'], level_code)

                s = account_service_load_student(student['member_id'])
                enroll_account(s['user_name'], s['password'], is_phoenix, level_code)

                # ensure account version is correct before return
                if is_v2 != is_v2_student(student['member_id']):
                    raise AssertionError(
                        "Incorrect account version! Please double check target school version: {}".format(school))
            else:
                raise ValueError("Unable to enroll course without set hima for online oc student")
        else:
            set_oc(student['member_id'], level_code)

    # save account to EC db then return
    get_logger().debug('New test account: {}'.format(student))
    tags = get_student_tags(student)
    save_account(student, add_tags=tags, remove_tags=['not_activated', 'Failed'])

    return student


def set_course_info(member_id, is_e19):
    link = get_level0_tool_link()

    if is_e19:
        url = get_e19_course_info_link()
    else:
        url = get_s18_course_info_link()

    s = no_ssl_requests()
    response = s.get(link)

    if response.status_code == HTTP_STATUS_OK:
        data = {'studentIds': member_id}

        r = s.post(url=url, data=data)
        if r.status_code == HTTP_STATUS_OK and r.json()['IsSuccess']:
            get_logger().info('Set account {} to {} course info success'.format(member_id, 'E19' if is_e19 else 'S18'))
        else:
            raise ValueError('Error occurred when set account {} to legacy S18 course info'.format(member_id))
    else:
        raise ValueError('Fail to open level 0 tool with error {}'.format(response.text))


def enroll_account(username, password, force=False, level_code='0A'):
    """
    Enroll student with level and course info, only work for online oc students.
    Login via mobile enroll page will do the work.
    """

    if not force and config.partner not in ['Cool', 'Mini', 'Socn', 'Indo']:
        get_logger().debug('No need to enroll account as it is not following Online OC flow')
        return

    def login_mobile_web(student_username, student_password):
        s = no_ssl_requests()

        url = get_login_post_link()
        d = {'username': student_username, 'password': student_password, 'onsuccess': '/ecplatform/mvc/mobile/dropin'}
        r = s.post(url=url, data=d)

        if r.status_code == HTTP_STATUS_OK and r.json()['success']:
            if config.domain.lower() == 'hk':
                redirect_url = config.etown_root + r.json()['redirect']
            else:
                redirect_url = r.json()['redirect']
            redirect_result = s.get(redirect_url, allow_redirects=True)
        else:
            raise ValueError('Fail to login with user {} / {}! '.format(student_username, student_password) + r.text)

        return s, redirect_result

    def submit_beginner_questionaire(student_level_code, login_session):
        url_questionnaire = get_beginner_questionnaire_link()

        if student_level_code == '0A':
            questionaire_data = {"studentAnswers": {"version": "BegQues_v1",
                                                    "answers": {
                                                        "BQ_S1_GUESS-WORD-SOUNDING": "{\"Choice\":\"BQ_S1_OP_GWS_NO\"}",
                                                        "BQ_S1_UNDERSTAND-BASIC-IDEA": "{\"Choice\":\"BQ_S1_OP_UBI_NO\"}",
                                                        "BQ_S1_ANSWER-SIMPLE-QUESTION": "{\"Choice\":\"BQ_S1_OP_ASQ_NO\"}",
                                                        "BQ_S1_SIMPLE-SENTENCES": "{\"Choice\":\"BQ_S1_OP_SS_NO\"}",
                                                        "BQ_S1_DIFFERENT-VOCABULARY": "{\"Choice\":\"BQ_S1_OP_DV_NO\"}",
                                                        "BQ_S2_ACTIVELY-LEARNING": "{\"Choice\":\"BQ_S2_OP_AL_NO\"}",
                                                        "BQ_S2_SKILLS-AND-STRATEGIES": "{\"Choice\":\"BQ_S2_OP_SNS_NO\"}",
                                                        "BQ_S2_SPEAKING-TO-OTHERS": "{\"Choice\":\"BQ_S2_OP_STO_NO\"}",
                                                        "BQ_S2_WITH-STRONGER-LEARNER": "{\"Choice\":\"BQ_S2_OP_WSL_NO\"}",
                                                        "BQ_S2_HARDER-THAN-EXPECTED": "{\"Choice\":\"BQ_S2_OP_HTE_STOP-COMING\"}"},
                                                    "duration": 17702}}
        else:
            questionaire_data = {"studentAnswers": {"version": "BegQues_v1",
                                                    "answers": {
                                                        "BQ_S1_GUESS-WORD-SOUNDING": "{\"Choice\":\"BQ_S1_OP_GWS_YES\"}",
                                                        "BQ_S1_UNDERSTAND-BASIC-IDEA": "{\"Choice\":\"BQ_S1_OP_UBI_YES\"}",
                                                        "BQ_S1_ANSWER-SIMPLE-QUESTION": "{\"Choice\":\"BQ_S1_OP_ASQ_YES\"}",
                                                        "BQ_S1_SIMPLE-SENTENCES": "{\"Choice\":\"BQ_S1_OP_SS_YES\"}",
                                                        "BQ_S1_DIFFERENT-VOCABULARY": "{\"Choice\":\"BQ_S1_OP_DV_YES\"}",
                                                        "BQ_S2_ACTIVELY-LEARNING": "{\"Choice\":\"BQ_S2_OP_AL_YES\"}",
                                                        "BQ_S2_SKILLS-AND-STRATEGIES": "{\"Choice\":\"BQ_S2_OP_SNS_YES\"}",
                                                        "BQ_S2_SPEAKING-TO-OTHERS": "{\"Choice\":\"BQ_S2_OP_STO_YES\"}",
                                                        "BQ_S2_WITH-STRONGER-LEARNER": "{\"Choice\":\"BQ_S2_OP_WSL_YES\"}",
                                                        "BQ_S2_HARDER-THAN-EXPECTED": "{\"Choice\":\"BQ_S2_OP_HTE_CONT-ATTENDING\"}"},
                                                    "duration": 37516}}

        response_questionnaire = login_session.post(url=url_questionnaire, json=questionaire_data)

        if response_questionnaire.status_code != HTTP_STATUS_OK:
            raise ValueError('Fail to complete beginner questionaire.')
        return response_questionnaire

    def enroll_course_new_flow(student_username, student_password):
        login_session, login_result = login_mobile_web(student_username, student_password)
        enroll_result = login_session.get(get_mobile_enroll_url(), allow_redirects=True)

        if enroll_result.status_code != HTTP_STATUS_OK:
            raise ValueError("Fail to enroll account, get error: {} {}".format(
                enroll_result.status_code, enroll_result.text))

        if 'mobile/welcome' in enroll_result.url.lower():
            get_logger().info('Enroll account {} success'.format(username))
        else:
            get_logger().error('Enroll to {}, detail: {}'.format(result.url, result.text))
            raise AssertionError('Error occurred when enroll account {}'.format(username))

    session, result = login_mobile_web(username, password)

    if 'mobile/beginnerquestionnaire' in result.url.lower():  # or 'mobile/beginnerquestionnairelv0' in result.url:
        response_questionnaire = submit_beginner_questionaire(level_code, session)
        if response_questionnaire.status_code == HTTP_STATUS_OK and response_questionnaire.json()[0]['isSuccess']:
            enroll_course_new_flow(username, password)
    else:
        enroll_course_new_flow(username, password)


def set_oc(student_id, level_code='0A', level_quantity=16):
    link = get_set_oc_url()
    session = no_ssl_requests()
    data = {'memberId': student_id, 'levelCode': level_code, 'levelQty': level_quantity}
    result = session.post(url=link, data=data)

    if result.text.strip() == 'True':
        get_logger().info('Set OC for student {} successfully'.format(student_id))
    else:
        raise ValueError('Fail to set OC for student {}! '.format(student_id) + result.text)


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

    if 'school_name' not in kwargs:
        kwargs['school_name'] = get_any_v1_school()['name']
    return activate_account_by_dict(kwargs)


def activate_s15_v1_student(**kwargs):
    kwargs['is_v2'] = False
    kwargs['is_s18'] = False
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_product(is_s18=False)['id']

    if 'school_name' not in kwargs:
        kwargs['school_name'] = get_any_v1_school()['name']
    return activate_account_by_dict(kwargs)


def activate_home_v1_student(**kwargs):
    kwargs['is_v2'] = False
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_home_product(is_s18=False)['id']

    if 'school_name' not in kwargs:
        kwargs['school_name'] = get_any_v1_school()['name']
    return activate_account_by_dict(kwargs)


def activate_school_v1_student(**kwargs):
    kwargs['is_v2'] = False
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_school_product(is_s18=False)['id']

    if 'school_name' not in kwargs:
        kwargs['school_name'] = get_any_v1_school()['name']
    return activate_account_by_dict(kwargs)


def activate_phoenix_student(**kwargs):
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_phoenix_product(**kwargs)['id']

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    if 'is_v1_pack' not in kwargs:
        kwargs['is_v1_pack'] = False

    if 'is_s18' not in kwargs:
        kwargs['is_s18'] = True

    if 'is_e19' not in kwargs:
        kwargs['is_e19'] = False
    return activate_account_by_dict(kwargs)


def activate_e19_phoenix_student(**kwargs):
    kwargs['is_s18'] = False
    kwargs['is_e19'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_phoenix_product(**kwargs)['id']

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    if 'is_v1_pack' not in kwargs:
        kwargs['is_v1_pack'] = False

    return activate_account_by_dict(kwargs)


def activate_e19_phoenix_student_with_eea(**kwargs):
    kwargs['is_s18'] = False
    kwargs['is_e19'] = True

    # create phoenix(except for PHX TS)for China partner, will add eea coupon, using different redemption code,
    # but, still use same product id. So using product name to get redemption code
    if 'product_id' in kwargs:
        kwargs['product_id'] = None

    if 'product_name' not in kwargs:
        kwargs['product_name'] = 'Phoenix - Socn - EEA'

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    if 'is_v1_pack' not in kwargs:
        kwargs['is_v1_pack'] = False

    return activate_account_by_dict(kwargs)


def activate_smart_plus_pro_student(**kwargs):
    kwargs['is_s18'] = False if config.domain == 'CN' else True
    kwargs['is_e19'] = True if config.domain == 'CN' else False
    kwargs['is_smart_plus'] = True

    # For Flex and Pro both use same product id but use different redemption code
    # so, create special account, all use pack name
    if 'product_id' in kwargs:
        kwargs['product_id'] = None

    if 'product_name' not in kwargs:
        kwargs['product_name'] = 'Smart Plus - Pro'

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    return activate_account_by_dict(kwargs)


def activate_smart_plus_flex_pl_student(**kwargs):
    kwargs['is_s18'] = False if config.domain == 'CN' else True
    kwargs['is_e19'] = True if config.domain == 'CN' else False
    kwargs['is_smart_plus'] = True

    # For Flex and Pro both use same product id but use different redemption code
    # so, create special account, all use pack name
    if 'product_id' in kwargs:
        kwargs['product_id'] = None

    if 'product_name' not in kwargs:
        kwargs['product_name'] = 'Smart Plus - Flex PL'

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    return activate_account_by_dict(kwargs)


def activate_smart_plus_flex_gl_student(**kwargs):
    kwargs['is_s18'] = False if config.domain == 'CN' else True
    kwargs['is_e19'] = True if config.domain == 'CN' else False
    kwargs['is_smart_plus'] = True

    # For Flex and Pro both use same product id but use different redemption code
    # so, create special account, all use pack name
    if 'product_id' in kwargs:
        kwargs['product_id'] = None

    if 'product_name' not in kwargs:
        kwargs['product_name'] = 'Smart Plus - Flex GL'

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    return activate_account_by_dict(kwargs)


def activate_smart_plus_flex_vip_student(**kwargs):
    kwargs['is_s18'] = False if config.domain == 'CN' else True
    kwargs['is_e19'] = True if config.domain == 'CN' else False
    kwargs['is_smart_plus'] = True

    # smart plus flex vip has different redemption code,
    # which can only get by the pack name
    if 'product_id' in kwargs:
        kwargs['product_id'] = None

    if 'product_name' not in kwargs:
        kwargs['product_name'] = 'Smart Plus - Flex VIP'

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    return activate_account_by_dict(kwargs)


def activate_smart_plus_school_vip_student(**kwargs):
    kwargs['is_s18'] = False if config.domain == 'CN' else True
    kwargs['is_e19'] = True if config.domain == 'CN' else False
    kwargs['is_smart_plus'] = True

    # smart plus school vip has different redemption code,
    # which can only get by the pack name
    if 'product_id' in kwargs:
        kwargs['product_id'] = None

    if 'product_name' not in kwargs:
        kwargs['product_name'] = 'Smart Plus - School VIP'

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    return activate_account_by_dict(kwargs)


def activate_smart_plus_gov_basic_student(**kwargs):
    kwargs['is_s18'] = True
    kwargs['is_e19'] = False
    kwargs['is_smart_plus'] = True

    # create smart plus student, use the pack name
    if 'product_id' in kwargs:
        kwargs['product_id'] = None

    if 'product_name' not in kwargs:
        kwargs['product_name'] = 'Smart Plus - Indo Basic'

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    return activate_account_by_dict(kwargs)


def activate_smart_plus_gov_premium_student(**kwargs):
    kwargs['is_s18'] = True
    kwargs['is_e19'] = False
    kwargs['is_smart_plus'] = True

    # create smart plus student, use the pack name
    if 'product_id' in kwargs:
        kwargs['product_id'] = None

    if 'product_name' not in kwargs:
        kwargs['product_name'] = 'Smart Plus - Indo Premium'

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    return activate_account_by_dict(kwargs)


def activate_smart_plus_gov_plus_student(**kwargs):
    kwargs['is_s18'] = True
    kwargs['is_e19'] = False
    kwargs['is_smart_plus'] = True

    # create smart plus student, use the pack name
    if 'product_id' in kwargs:
        kwargs['product_id'] = None

    if 'product_name' not in kwargs:
        kwargs['product_name'] = 'Smart Plus - Indo Plus'

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    return activate_account_by_dict(kwargs)


def activate_smart_plus_gov_pro_student(**kwargs):
    kwargs['is_s18'] = True
    kwargs['is_e19'] = False
    kwargs['is_smart_plus'] = True

    # create smart plus student, use the pack name
    if 'product_id' in kwargs:
        kwargs['product_id'] = None

    if 'product_name' not in kwargs:
        kwargs['product_name'] = 'Smart Plus - Indo Pro'

    if 'school_name' not in kwargs:
        is_online = not kwargs.get('center_pack', True)
        kwargs['school_name'] = get_any_phoenix_school(is_virtual=is_online)['name']

    return activate_account_by_dict(kwargs)


def activate_e19_student(**kwargs):
    kwargs['is_s18'] = False
    kwargs['is_e19'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_product(is_s18=False, is_e19=True)['id']

    return activate_account_by_dict(kwargs)


def activate_e19_home_student(**kwargs):
    kwargs['is_s18'] = False
    kwargs['is_e19'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_home_product(is_s18=False, is_e19=True)['id']
    return activate_account_by_dict(kwargs)


def activate_e19_school_student(**kwargs):
    kwargs['is_s18'] = False
    kwargs['is_e19'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_school_product(is_s18=False, is_e19=True)['id']
    return activate_account_by_dict(kwargs)


def activate_s18_student(**kwargs):
    kwargs['is_s18'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_product(is_s18=True)['id']
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
    kwargs['is_s18'] = False
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_product(is_s18=False)['id']
    if 'school_name' not in kwargs:
        kwargs['school_name'] = get_any_v2_school()['name']
    return activate_account_by_dict(kwargs)


def activate_home_v2_student(**kwargs):
    kwargs['is_s18'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_home_product(is_s18=True)['id']
    return activate_account_by_dict(kwargs)


def activate_school_v2_student(**kwargs):
    kwargs['is_s18'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_school_product(is_s18=True)['id']
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

    return activate_account_by_dict(kwargs)


def activate_onlineoc_school_student(**kwargs):
    kwargs['is_s18'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_school_product(is_s18=True)['id']
    return activate_onlineoc_student(**kwargs)


def activate_onlineoc_home_student(**kwargs):
    kwargs['is_s18'] = True
    if 'product_id' not in kwargs:
        kwargs['product_id'] = get_any_home_product(is_s18=True)['id']
    return activate_onlineoc_student(**kwargs)


def activate_student_with_random_level(min_level=1, max_level=16, **kwargs):
    level = get_random_level(min_level, max_level)
    kwargs['startLevel'] = level
    return activate_account_by_dict(kwargs)


def activate_school_student_with_random_level(min_level=1, max_level=16, **kwargs):
    level = get_random_level(min_level, max_level)
    kwargs['startLevel'] = level
    return activate_school_v2_student(**kwargs)


def activate_home_student_with_random_level(min_level=1, max_level=16, **kwargs):
    level = get_random_level(min_level, max_level)
    kwargs['startLevel'] = level
    return activate_home_v2_student(**kwargs)


def activate_phoenix_student_with_random_level(min_level=1, max_level=16, **kwargs):
    level = get_random_level(min_level, max_level)
    kwargs['startLevel'] = level
    return activate_phoenix_student(**kwargs)


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


def sf_set_hima_test(student_id, level_code='0A', ignore_if_already_set=True):
    try:
        sf_service_helper.set_hima_test(student_id, level_code)

    except SystemError as e:

        if ignore_if_already_set:
            assert str(e) == "Can't do this, please check student data if already done.", str(e)
        else:
            raise


def activate_oboe_package(student_id, package_product_ids):
    """
    Activate oboe package for the student, eg. career track, skills clinics, osc, spin etc.
    :param student_id:
    :param package_product_id: list of package_product_id, which is PackageProduct_id column of
    table oboe.dbo.PackageProduct, eg. 1001,1002,1020
    :return:
    """
    link = get_activate_oboe_package_link()
    session = no_ssl_requests()
    order_id = str(uuid.uuid1())
    data = {'memberId': student_id,
            'orderId': order_id,
            'packageProductIds': package_product_ids,
            'templateData': ''}
    result = session.post(url=link, data=data)

    if result.status_code == HTTP_STATUS_OK and 'Success,IsSuccess:True' in result.text:
        get_logger().info(
            'Activate oboe package {0} for student {1} successfully'.format(package_product_ids, student_id))
    else:
        raise ValueError(
            'Fail to activate oboe package {0} for student {1}! '.format(package_product_ids, student_id) + result.text)
