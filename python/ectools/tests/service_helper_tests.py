from assertpy import assert_that

from ectools.account_helper import activate_e19_student
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
    assert result['course_version'] == 'E12'
    assert result['current_level'] == '3'


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
    expected = '{"member_id": 23904718, "user_name": "stest24561", "first_name": "s14hz", "last_name": "test", ' \
               '"password": "1", "email": "te636251605203525074@qp1.org", "home_phone": "", "country_code": "cn", ' \
               '"partner_code": "Mini", "state_code": "", "city_code": "", "address1": "", "address2": "", ' \
               '"postal_code": "", "email_language_code": "en", "e_tag": "", "member_type_code": "M", ' \
               '"date_of_birth": "2017-03-15 03:42:00", "local_name": "s14hz test", "gender_code": "", ' \
               '"mobile_phone": null, "display_name": null, "language_code": "en", "address": "", ' \
               '"occupation": "", "omniture_friendly_name": "", "data_store": "US1", ' \
               '"creation_date": "2017-03-15 03:43:10", "success": false, "error_code": null}'

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
        assert '"IsSuccess":false' in str(e)
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


def test_adjust_coupon():
    set_environment('uat')
    student_id = 24006538
    adjust_coupon(student_id, 'F2F', 5)
    adjust_coupon(student_id, 'F2F', -3)
    adjust_coupon(student_id, 'WS', 5)
    adjust_coupon(student_id, 'WS', -3)
    adjust_coupon(student_id, 'LC', 5)
    adjust_coupon(student_id, 'LC', -3)
    adjust_coupon(student_id, 'PL40', 5)
    adjust_coupon(student_id, 'PL40', -3)
    adjust_coupon(student_id, 'GL', 5)
    adjust_coupon(student_id, 'GL', -3)


def test_update_student_password():
    set_environment('uat')
    student_name = 'stest55675'
    student = account_service_load_student(23973971)
    old_password = student['password']
    new_password = password_generator()

    update_student_password(student_name, old_password, new_password)
    student = account_service_load_student(23973971)

    assert student['password'] == new_password


def test_clear_memcached_by_type():
    set_environment('uat')
    assert clear_memcached_by_type(ClearCacheType.BOOKING_MEM_CACHE_BY_DATE_RANGE, 24001345) == 'success'


def test_clear_booking_mem_cached():
    set_environment('uat')
    assert clear_booking_mem_cache_by_date_range(24001345) == 'success'


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
    assert student_active_subscription[0]['is_active']

    # expired student
    expired_student_id = 23999880
    student_subscription = get_student_active_subscription(expired_student_id)
    assert len(student_subscription) == 0


def test_get_student_basics():
    set_environment('uat')

    url1 = config.etown_root + STUDENT_BASICS["URL"]
    result1 = requests.post(url1, data={STUDENT_BASICS["DATA"]: "23990631"})
    assert_that(result1.json()['Email']).is_equal_to('637019489788342643@qp1.org')

    url2 = config.etown_root + STUDENT_PRODUCTS["URL"]
    result2 = requests.post(url2, data={STUDENT_PRODUCTS["DATA"]: "23990631"})
    assert_that(result2.json()['StudentId']).is_equal_to(23990631)


def test_get_student_coupon_info():
    set_environment('uat')
    coupon_info = get_student_coupon_info(24006538)
    assert_that(coupon_info['IsSuccess']).is_true()


def test_get_student_feature_access_grants():
    set_environment('uatcn')
    feature_info = get_student_feature_access_grants(24123877)
    assert_that(
        len([feature for feature in feature_info if feature['FeatureAccess'] == 'SelfStudy_Extendable'])).is_equal_to(1)


def test_get_EEA_coupon():
    set_environment('uatcn')
    coupon_info = get_EEA_coupon(24123877)

    # Check total coupon count
    assert_that(coupon_info[0]).is_equal_to(360)
    # Check remaining coupon count
    assert_that(coupon_info[1]).is_equal_to(360)


def test_get_student_enrollments_info():
    set_environment('uat')
    current_enrollment = get_current_level_unit(24010365)
    current_level = current_enrollment[0]
    current_unit = current_enrollment[1]
    assert_that(current_level).is_equal_to(2)
    assert_that(current_unit).is_equal_to(1)


def test_cancel_student():
    set_environment('qa')
    student_id = 11580650
    account_service_cancel_student(student_id)


def test_get_student_top_level_code():
    set_environment('uat')
    student_id = 24013927

    assert get_student_top_level_code(student_id) == '10'


def test_change_expiration_date():
    set_environment('uat')

    # active student gets exception
    student_id = 24015038

    try:
        change_expiration_date(student_id, -10)
    except AssertionError as e:
        assert e.args[0] == '{"Success":false,"ErrorCode":"HasActiveSubscription"}'

    # expired & reactivated student get exception
    student_id = 24014999

    try:
        change_expiration_date(student_id, -10)
    except AssertionError as e:
        assert e.args[0] == '{"Success":false,"ErrorCode":"HasActiveSubscription"}'

    # offset >= 0 gets exception
    student_id = 24015046
    try:
        change_expiration_date(student_id, 0)
    except AssertionError as e:
        assert e.args[0] == '{"Success":false,"ErrorCode":"NegativeDayOffsetExpected"}'

    # expired student & days_offset < 0
    student_id = 24015046
    change_expiration_date(student_id, -10)


def test_convert_to_smart_plus():
    set_environment('uat')
    student = activate_e19_student()
    convert_to_smart_plus(student['member_id'])

def test_update_student_address():
    set_environment('uatcn')
    student = activate_e19_student()
    student_name = student['username']
    student_password = student['password']
    updated_address = 'Test Address2'
    update_student_address(student_name, student_password,
                           billing_address=updated_address)
    student_info = account_service_load_student(student['username'])
    assert_that(student_info['address1']).is_equal_to(updated_address)
