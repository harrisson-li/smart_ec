from config import get_logger, set_environment
from student_settings_helper import get_member_site_settings, is_v2_student


def test_get_member_site_settings():
    set_environment('qa')
    student_id = 10806560
    settings = get_member_site_settings(student_id)
    get_logger().info(settings)


def test_is_v2_student():
    set_environment('qa')
    student_id = 10806560
    assert is_v2_student(student_id)
