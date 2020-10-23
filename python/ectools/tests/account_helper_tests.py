from ectools.account_helper import *
from ectools.config import set_environment, set_partner
from ectools.internal.objects import *
from ectools.logger import get_logger


def test_reactivate_account():
    set_environment('uat')
    member_id = 23978355

    student = {'member_id': member_id}
    student = activate_account(student=student)

    assert student['member_id'] == member_id


def test_create_account():
    set_environment('staging')
    student = create_account_without_activation()
    get_logger().info(student)
    assert student is not None
    assert student['password'] == '1'

    student = {'member_id': student['member_id']}
    student = activate_account(student=student)
    assert student['member_id'] is not None

    # test save account via sql
    original = config.remote_api

    try:
        config.remote_api = 'http://not/exist/'
        student = create_account_without_activation(is_e10=True)
        get_logger().info(student)
        assert student is not None
        assert student['is_e10']

    finally:
        config.remote_api = original


def test_activate_account_default():
    set_environment('staging')
    student = activate_account(is_v2=True, mainRedemptionQty=60)
    get_logger().info(student)
    assert student is not None
    student = create_account_without_activation()
    student = activate_account(product_id=63, school_name='SH_ZJC', student=student)
    assert student['is_v2']
    assert student['school']['name'] == 'SH_ZJC'


def test_activate_account_kwargs():
    set_environment('staging')
    student = activate_account(startLevel=3, mainRedemptionQty=1, securityverified=False, includesenroll=False)
    assert student['activation_data']['startLevel'] == 3
    assert student['activation_data']['mainRedemptionQty'] == 1
    assert not student['activation_data']['securityverified']
    assert not student['activation_data']['includesenroll']


def test_activate_s18_accounts():
    set_environment('staging')
    set_partner('cool')
    student = activate_s18_school_student()
    assert student['product']['main_code'] == 'S18SCHOOLMAIN'
    assert student['product']['id'] == 63


def test_get_s18_products():
    set_partner('cool')
    product = get_any_school_product(is_s18=False)
    assert product['main_code'] == 'S15SCHOOLMAIN'

    product = get_any_school_product(is_s18=True)
    assert product['main_code'] == 'S18SCHOOLMAIN'

    product = get_any_home_product(is_s18=False)
    assert product['main_code'] == 'S15HOMEPL20MAIN'

    product = get_any_home_product(is_s18=True)
    assert product['main_code'] == 'S18HOMEPL20MAIN'


def test_activate_eclite_account():
    # should raise error with message like mismatch school and product
    set_environment('staging')
    set_partner('mini')

    activate_account(143)

    try:
        activate_account(143, 'FS_ZUM')
    except AssertionError as e:
        assert e.args[0] == "Miss match product [143] and school [FS_ZUM] for ECLite account!"

    try:
        set_partner('cool')
        activate_eclite_student()
    except Exception as e:
        assert e.args[0] == "Cannot choose from an empty sequence"

    set_partner('mini')
    assert is_lite_product(143)
    assert is_lite_product('143')

    account = activate_eclite_student()
    assert "EC Lite" in account["product"]["name"]


def test_ignore_eclite_school():
    school_tags = [s['tags'] for s in get_all_normal_v2_schools('mini')]
    for tag in school_tags:
        assert 'ECLite' not in tag


def test_activate_account_more():
    set_environment('qa')
    set_partner('mini')

    student = activate_e10_student()
    assert student['is_e10']
    student = activate_school_v2_student()
    assert student['product']['product_type'] == 'School'
    assert student['is_v2']
    student = activate_home_v1_student()
    assert student['product']['product_type'] == 'Home'
    assert not student['is_v2']
    student = activate_school_student_with_random_level(min_level=2, max_level=3)
    assert student['activation_data']['startLevel'] in ['0B', 1]


# noinspection PyUnresolvedReferences
def test_convert_student_to_object():
    set_environment('staging')
    student = get_or_activate_account(tag='UnitTest')

    class Student(Base):
        pass

    class School(Base):
        pass

    student_obj = convert_account_to_object(student, account_object_type=Student, school_object_type=School)
    get_logger().info(student_obj)
    assert isinstance(student_obj, Student)
    assert isinstance(student_obj.product, dict)
    assert student_obj.is_e10 == student['is_e10']
    assert student['member_id'] == student_obj.member_id


def test_sf_suspend_student():
    set_environment('qa')
    import datetime
    now = datetime.datetime.now()
    further = now + timedelta(days=5)
    suspend_date = now.strftime('%Y-%m-%d')
    resume_date = further.strftime('%Y-%m-%d')

    sf_service_helper.suspend_student('11276463', suspend_date, resume_date)
    sf_service_helper.resume_student('11276463')


def test_get_or_activate_account():
    set_environment('staging')
    account1 = get_or_activate_account(tag='UnitTest')
    account2 = get_or_activate_account(tag='UnitTest')

    for key in ['member_id', 'partner', 'environment']:
        assert account1[key] == account2[key]

    assert account2.get('found_by_tag'), 'second account always has the key: found_by_tag'


def test_get_account_by_tag():
    set_environment('live')
    accounts = get_accounts_by_tag('indo')
    assert len(accounts) > 0

    set_environment('qa')
    accounts = get_accounts_by_tag('ectools', expiration_days=14)
    assert len(accounts) > 0

    # get account method
    account = get_account(accounts[0]['member_id'])
    assert account is not None
    assert account['username'] == accounts[0]['username']


def test_or_activate_onlineoc_student():
    set_environment('staging')
    account = get_or_activate_account(tag='OnlineOC_UT', method='activate_onlineoc_student')
    assert account['is_onlineoc']


def test_set_hima_test_success():
    set_environment('uat')
    sf_service_helper.set_hima_test('23924331', '5')


def test_set_hima_test_failed():
    set_environment('uat')
    student_id = 23955169
    msg = "Can't do this, please check student data if already done."

    try:
        sf_service_helper.set_hima_test(student_id, '5')

    except SystemError as e:
        assert str(e) == msg

    else:
        assert False, 'Did not raise error!'

    sf_set_hima_test(student_id)

    try:
        sf_set_hima_test(student_id, ignore_if_already_set=False)

    except SystemError as e:
        assert str(e) == msg

    else:
        assert False, 'Did not raise error!'


def test_activate_onlineoc_student():
    set_environment('staging')
    activate_onlineoc_school_student(startLevel=3)


def test_activate_socn_student():
    set_environment('uat')
    set_partner('socn')
    activate_account(product_id=157, school_name='CN_TSC')

    # activate data with phoenix pack should not hurt
    activate_account(product_id=157, school_name='CN_TSC', center_pack=True, online_pack=True)


def test_activate_v1_student():
    set_environment('staging')
    set_partner('mini')
    activate_s15_v1_student()


def test_activate_phoenix_student():
    set_environment('uat')
    set_partner('rupe')

    activate_phoenix_student()
    activate_phoenix_student(center_pack=False, startLevel='4')
    activate_phoenix_student(online_pack=False)
    activate_phoenix_student(includesenroll=False)


def test_activate_phoenix_pack():
    set_environment('uat')
    set_partner('rupe')

    activate_phoenix_student(phoenix_packs=['Center Pack Basic', 'Intensive Center Fee'])


def test_activate_live_student():
    set_environment('live')
    set_partner('cool')
    activate_s18_student(school_name='QA_T1C')


def test_activate_phoenix_socn():
    set_environment('staging')
    set_partner('socn')
    activate_phoenix_student(school_name='HZ_CXC')

    set_environment('qacn')
    set_partner('socn')
    activate_phoenix_student(school_name='HZ_CXC')


def test_activate_phoenix_trial():
    set_environment('uat')
    set_partner('socn')
    activate_phoenix_student(product_id=165)

    set_partner('rupe')
    activate_phoenix_student(product_id=163)

    set_partner('ecsp')
    activate_phoenix_student(product_id=164)


def test_activate_default_account():
    set_environment('staging')
    for partner, prod in [('Cool', 63), ('Mini', 65), ('Rupe', 159), ('Cehk', 127)]:
        set_partner(partner)
        account = activate_account()
        assert account['product']['id'] == prod


def test_activate_e19_account():
    set_environment('uat')
    set_partner('Cool')
    student_beginner_low = activate_account(is_s18=False, is_e19=True, includesenroll=True)
    student_beginner_high_0b = activate_account(is_s18=False, is_e19=True, includesenroll=True, startLevel='0B')
    student_beginner_high_1 = activate_account(is_s18=False, is_e19=True, includesenroll=True, startLevel='1')
    student_elementary = activate_account(is_s18=False, is_e19=True, includesenroll=True, startLevel='2')

    assert student_beginner_low['is_e19'] is True
    assert student_beginner_low['level_code'] == '0A'
    assert student_beginner_high_0b['is_e19'] is True
    assert student_beginner_high_0b['level_code'] == '0B'
    assert student_beginner_high_1['is_e19'] is True
    assert student_beginner_high_1['level_code'] == '1'
    assert student_elementary['is_e19'] is True
    assert student_elementary['level_code'] == '2'


def test_activate_s18_legacy_account():
    set_environment('uat')

    student_legacy = activate_account(is_s18=True, is_e19=False, includeenroll=True)
    assert student_legacy['member_id'] is not None


def test_activate_smart_plus_pro_account():
    set_environment('qa')
    set_partner('socn')
    activate_smart_plus_pro_student(includeenroll=True, product_id=173)


def test_activate_smart_plus_flex_pl_account():
    set_environment('qacn')
    set_partner('socn')
    activate_smart_plus_flex_pl_student(includeenroll=True, product_id=173)
    activate_smart_plus_flex_pl_student(includeenroll=True)
    activate_account(is_s18=False, is_e19=True, is_smart_plus=True, school_name='HZ_CXC',
                     product_name='Smart Plus - Flex PL')


def test_activate_smart_plus_flex_gl_account():
    set_environment('uat')
    set_partner('socn')
    activate_smart_plus_flex_gl_student(includeenroll=True, product_id=173, school_name='HZ_CXC')
    activate_smart_plus_flex_gl_student(includeenroll=True)


def test_activate_smart_plus_flex_vip_account():
    set_environment('uat')
    set_partner('socn')
    activate_smart_plus_flex_vip_student(includeenroll=True, product_id=173)
    activate_smart_plus_flex_vip_student(includeenroll=True)
    activate_account(is_s18=False, is_e19=True, is_smart_plus=True, school_name='HZ_CXC',
                     product_name='Smart Plus - Flex VIP')


def test_activate_phoenix_with_dict_coupon_info():
    pack_info = {'Center Pack Basic': {
        "coupons": [
            {
                "name": "F2F",
                "count": 1
            },
            {
                "name": "WS",
                "count": 1
            },
            {
                "name": "LC",
                "count": 1
            }
        ]
    }}

    set_environment('uat')
    set_partner('rupe')
    activate_phoenix_student(school_name='QA_RUC', is_s18=True, is_e19=False, phoenix_packs=pack_info)


def test_activate_phoenix_with_string_coupon_info():
    pack_info = {
        '1 Year Basic': '{"coupons":[{"name":"PL40","count":1},{"name":"GL","count":1},{"name":"LC","count":1}]}'}

    set_environment('uat')
    set_partner('socn')
    activate_phoenix_student(school_name='QA_T1C', is_s18=False, is_e19=True, phoenix_packs=pack_info)


def test_activate_phoenix_with_eea():
    set_environment('uat')
    set_partner('socn')
    activate_account(is_s18=False, is_e19=True, is_smart_plus=False, is_phoenix=True, school_name='HZ_CXC',
                     product_name='Phoenix - Socn - EEA')
    activate_e19_phoenix_student_with_eea()
    activate_e19_phoenix_student_with_eea(phoenix_packs=['1 Year Basic'])


def test_activate_phoenix_without_eea():
    set_environment('uat')
    set_partner('socn')
    activate_account(is_s18=False, is_e19=True, is_smart_plus=False, is_phoenix=True, school_name='CN_TSC',
                     product_name='Phoenix - Socn', online_pack=True, center_pack=False)


def test_activate_s18_using_product_name():
    set_environment('uat')
    set_partner('cool')
    activate_account(is_s18=False, is_e19=True, school_name='SH_JAT', product_name='Smart 18 - School - E19')


def test_activate_indo_smart_plus_pro():
    set_environment('uat')
    set_partner('indo')
    student = activate_smart_plus_pro_student()

    assert student['partner'] == 'Indo'
    assert student['is_smart_plus']
    assert not student['is_e19']
    assert student['is_s18']
