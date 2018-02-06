import ectools.ecdb_helper as db_helper
from ectools.account_helper import *
from ectools.config import get_logger, set_environment, set_partner
from ectools.internal.objects import *


def test_create_account():
    set_environment('staging')
    student = create_account_without_activation()
    get_logger().info(student)
    assert student is not None
    assert student['password'] == '1'

    student = {'member_id': student['member_id']}
    student = activate_account(student=student)
    assert student['member_id'] is not None

    # test save account via api
    original = db_helper._remote_db_dir

    try:
        db_helper._remote_db_dir = '//not/exist/path'
        student = create_account_without_activation(is_e10=True)
        get_logger().info(student)
        assert student is not None
        assert student['is_e10']

    finally:
        db_helper._remote_db_dir = original


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
    student = activate_account(startLevel=3, mainRedemptionQty=1, securityverified=False)
    assert student['startLevel'] == 3
    assert student['mainRedemptionQty'] == 1
    assert not student['securityverified']


def test_activate_s18_accounts():
    set_environment('staging')
    set_partner('cool')
    student = activate_s18_school_student()
    assert student['product']['main_code'] == 'S18SCHOOLMAIN'
    assert student['product']['id'] == 63


def test_get_s18_products():
    set_partner('cool')
    product = get_any_school_product()
    assert product['main_code'] == 'S15SCHOOLMAIN'

    product = get_any_school_product(is_s18=True)
    assert product['main_code'] == 'S18SCHOOLMAIN'

    product = get_any_home_product()
    assert product['main_code'] == 'S15HOMEPL20MAIN'

    product = get_any_home_product(is_s18=True)
    assert product['main_code'] == 'S18HOMEPL20MAIN'


def test_activate_eclite_account():
    # should raise error with message like mismatch school and product
    set_environment('staging')
    set_partner('mini')
    try:
        activate_account(65, 'WH_GGC')
    except AssertionError as e:
        assert e.args[0] == "Miss match product [65] and school [WH_GGC] for ECLite account!"

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
    set_environment('staging')
    set_partner('mini')

    student = activate_e10_student()
    assert student['is_e10']
    student = activate_school_v2_student()
    assert student['product']['product_type'] == 'School'
    assert student['is_v2']
    student = activate_home_student()
    assert student['product']['product_type'] == 'Home'
    assert not student['is_v2']
    student = activate_school_student_with_random_level(min_level=2, max_level=3)
    assert student['startLevel'] in ['0B', 1]


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


def test_set_hima_test():
    set_environment('uat')
    sf_service_helper.set_hima_test('23924331', '5')


def test_activate_onlineoc_student():
    set_environment('staging')
    activate_onlineoc_school_student(startLevel=3)


def test_activate_socn_student():
    set_environment('uat')
    set_partner('socn')
    activate_account(product_id=157, is_s18=True)


def test_activate_v1_student():
    set_environment('staging')
    set_partner('mini')
    activate_s15_student()
