from service_helper import get_member_site_settings
from config import get_logger


def test_get_member_site_settings():
    student_id = 23881835
    settings = get_member_site_settings(student_id)
    get_logger().info(settings)
