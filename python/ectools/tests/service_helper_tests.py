from ectools.config import set_environment
from ectools.logger import get_logger
from ectools.service_helper import *
from ectools.utility import password_generator


def test_get_member_site_settings():
    set_environment('qa')
    student_id = 10806560
    settings = get_member_site_settings(student_id)
    get_logger().info(settings)

    set_environment('uat')
    student_id = 23908427
    settings = get_member_site_settings(student_id)
    get_logger().info(settings)


def test_set_member_site_settings():
    set_environment('uat')
    student_id = 23908427

    set_member_site_settings(student_id, 'test_key', 'test_value')
    set_member_site_settings(student_id, 'test_time', '2017-10-1', is_time_value=True)

    settings = get_member_site_settings(student_id)
    assert settings['test_key'] == 'test_value'
    assert settings['test_time'] == '10/1/2017 12:00:00'

    set_environment('staging')
    student_id = 14890056

    set_member_site_settings(student_id, 'test_key', 'test_value', site_area='school_ec')
    settings = get_member_site_settings(student_id, site_area='school_ec')
    assert settings['test_key'] == 'test_value'

def test_is_v2_student():
    set_environment('qa')
    student_id = 10806560
    assert is_v2_student(student_id)

    set_environment('uat')
    student_id = 23908427
    assert is_v2_student(student_id)


def test_get_student_info():
    set_environment('uat')
    student_id = 23904718
    result = get_student_info(student_id)
    assert result['username'] == 'stest24561'
    assert result['email'] == "te636251605203525074@qp1.org"
    assert result['member_id'] == student_id
    assert result['partner'] == 'Mini'
    assert result['current_unit'] == 6
    assert result['current_level_name'] == '1'
    assert result['current_level_code'] == '3'
    assert result['elite_code'] == 'te23904718'
    assert result['school_id'] == 143
    assert result['product_id'] == 65
    assert result['division_code'] == 'CNMNCD5'
    assert result['is_home'] == False


def test_score_helper_load_student():
    set_environment('uat')
    student_id = 23904718
    result = score_helper_load_student(student_id)
    assert result['username'] == 'stest24561'
    assert result['current_level_name'] == '1'
    assert result['current_level_code'] == '3'
    assert result['current_unit'] == 6
    assert result['partner'] == 'Mini'

    set_environment('qa')
    student_id = 11257646
    result = score_helper_load_student(student_id)
    assert result['username'] == 'stest79207'
    assert result['current_level_name'] == 'A'
    assert result['current_level_code'] == '1'
    assert result['current_unit'] == 3

    set_environment('qa')
    student_id = 11260074
    result = score_helper_load_student(student_id)
    assert result['username'] == 'stest80717'
    assert result['current_level_name'] == 'EFEC Industry Spins'
    assert result['current_level_code'] == 'EFEC Industry Spins'
    assert result['current_unit'] == 'Pharmacy'
    assert result['partner'] == 'Mini'

    result = score_helper_load_student('ctest2515')
    assert result['current_level_name'] == 'A'
    assert result['current_level_code'] == 'A'


def test_load_student_via_ecplatform_service():
    set_environment('uat')
    student_id = 23904718
    result = ecplatform_load_student(student_id)
    assert result['CourseVersion'] == 1
    assert result['CurrentLevelCode'] == '1'

    result = ecplatform_load_student_basic_info(student_id)
    assert result['StudentBasicInfo'][0]['Key'] == 'EliteCode'
    assert result['StudentBasicInfo'][0]['Value'] == 'te23904718'


def test_load_status_flag():
    set_environment('uat')
    student_id = 23904718
    result = ecplatform_load_student_status_flag(student_id)
    assert result['StatusFlags'][0]['Key'] == 5
    assert result['StatusFlags'][0]['Value'] == 'True'


def test_troop_load_student():
    set_environment('qa')
    student_name = 'stest82330'
    result = troop_service_load_student(student_name)
    assert result['lastName'] == 'test'
    assert result['firstName'] == 's14hz'
    assert result['userName'] == 'stest82330'
    assert result['email'] == 'te636257602331089480@qp1.org'
    assert result['lastName'] == 'test'
    assert result['partnerCode'] == 'Cool'
    assert result['divisionCode'] == 'SSCNBJ5'


def test_troop_translate_blurb():
    blurb_id = '498117'
    result = troop_service_translate_blurb(blurb_id)
    assert result == 'Live Teacher Feedback'
    result = troop_service_translate_blurb(blurb_id, 'es')
    assert result == 'Comentarios de un Profesor'


def test_account_service_load_student():
    set_environment('uat')
    student_id = '23904718'
    expected = '{"last_name": "test", "local_name": "s14hz test", ' \
               '"first_name": "s14hz", "user_name": "stest24561", ' \
               '"partner_code": "Mini", "email": "te636251605203525074@qp1.org", ' \
               '"country_code": "cn", "member_type": "M", "password": "1", ' \
               '"member_id": "23904718", "creation_date": "2017-03-15T03:43:10.69", ' \
               '"date_of_birth": "2017-03-15T03:42:00.353", "language_code": "en", ' \
               '"email_language_code": "en", "data_store": "US1"}'

    result = account_service_load_student(student_id)
    assert result == json.loads(expected)

    student_name = 'stest24561'
    result = account_service_load_student(student_name)
    assert result == json.loads(expected)


def test_account_service_update_phone2():
    set_environment('uat')
    student_id = '23956735'
    account_service_update_phone2(student_id, 666666666)

    try:
        account_service_update_phone2(123, 66666666)
    except Exception as e:
        assert 'no such member' in str(e)
    else:
        assert False, 'should raise error!'


def test_account_service_update_name():
    set_environment('uat')
    student_id = '23958712'
    account_service_update_info(student_id, {'FirstName': 'unit.test'})


def test_adjust_level():
    set_environment('staging')
    student_id = 14896006

    adjust_level(student_id, to_level_code='0A')
    adjust_level(student_id, to_level_code=5)

    try:
        adjust_level(student_id, to_level_code=5)
    except SystemError as e:
        assert str(e) == 'Can not change to same unit!'


def test_add_offline_coupon():
    set_environment('staging')
    student_id = 14896006

    add_offline_coupon(student_id, 'F2F', 2)
    add_offline_coupon(student_id, 'WS', 2)


def test_update_student_password():
    set_environment('uat')
    student_name = 'stest55675'
    student = account_service_load_student(23973971)
    old_password = student['password']
    new_password = password_generator()

    update_student_password(student_name, old_password, new_password)
    student = account_service_load_student(23973971)

    assert student['password'] == new_password


def test_clear_memcached():
    set_environment('uat')
    cache_key = get_memcached_key(Memcached.CLASS_ATTENDANCE_ONLINE, student_id=23998728)

    assert clear_memcached(cache_key) == 'success'


def test_get_student_active_subscription():
    set_environment('uat')

    # active student
    active_student_id = 23999956
    student_active_subscription = get_student_active_subscription(active_student_id)
    assert len(student_active_subscription) > 0, "The student is not active"
    assert student_active_subscription['is_active']

    # expired student
    expired_student_id = 23999880
    student_subscription = get_student_active_subscription(expired_student_id)
    assert len(student_subscription) == 0
