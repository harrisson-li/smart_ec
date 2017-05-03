from ectools.config import get_logger, set_environment
from ectools.service_helper import *


def test_get_member_site_settings():
    set_environment('qa')
    student_id = 10806560
    settings = get_member_site_settings(student_id)
    get_logger().info(settings)

    set_environment('uat')
    student_id = 23908427
    settings = get_member_site_settings(student_id)
    get_logger().info(settings)


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
    assert result['current_level_code'] == 3
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
    assert result['current_level_code'] == 3
    assert result['current_unit'] == 6
    assert result['partner'] == 'Mini'

    set_environment('qa')
    student_id = 11257646
    result = score_helper_load_student(student_id)
    assert result['username'] == 'stest79207'
    assert result['current_level_name'] == 'A'
    assert result['current_level_code'] == 1
    assert result['current_unit'] == 3

    set_environment('qa')
    student_id = 11260074
    result = score_helper_load_student(student_id)
    assert result['username'] == 'stest80717'
    assert result['current_level_name'] == 'EFEC Industry Spins'
    assert result['current_level_code'] == 'EFEC Industry Spins'
    assert result['current_unit'] == 'Pharmacy'
    assert result['partner'] == 'Mini'


def test_load_student_via_ecplatform_service():
    set_environment('uat')
    student_id = 23904718
    result = ecplatform_load_student(student_id)
    assert result['CourseVersion'] == 1
    assert result['CurrentLevelCode'] == '1'

    result = ecplatform_load_student_basic_info(student_id)
    assert result['StudentBasicInfo'][0]['Key'] == 'UserName'
    assert result['StudentBasicInfo'][0]['Value'] == 'stest24561'


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
