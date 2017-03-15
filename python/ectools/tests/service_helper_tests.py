from ectools.config import get_logger, set_environment
from ectools.service_helper import *


def test_get_member_site_settings():
    set_environment('qa')
    student_id = 10806560
    settings = get_member_site_settings(student_id)
    get_logger().info(settings)


def test_is_v2_student():
    set_environment('qa')
    student_id = 10806560
    assert is_v2_student(student_id)


def test_get_student_name_and_email():
    set_environment('uat')
    student_id = 23904718
    name, email = get_student_name_and_email(student_id)
    assert name == 'stest24561'
    assert email == "te636251605203525074@qp1.org"


def test_load_student_via_ecplatform_service():
    set_environment('uat')
    student_id = 23904718
    result = load_student(student_id)
    assert result['CourseVersion'] == 1
    assert result['CurrentLevelCode'] == '1'

    result = load_student_basic_info(student_id)
    assert result['StudentBasicInfo'][0]['Key'] == 'UserName'
    assert result['StudentBasicInfo'][0]['Value'] == 'stest24561'


def test_load_status_flag():
    set_environment('uat')
    student_id = 23904718
    result = load_student_status_flag(student_id)
    assert result['StatusFlags'][0]['Key'] == 5
    assert result['StatusFlags'][0]['Value'] == 'True'


def test_load_student_via_score_helper():
    set_environment('uat')
    student_id = 23904718
    result = load_student_info_via_score_helper(student_id)
    assert result['username'] == 'stest24561'
    assert result['member_id'] == student_id
    assert result['partner'] == 'Mini'
    assert result['current_level'] == 'GE2013 Level3'
    assert result['current_unit'] == 'Unit 6'
