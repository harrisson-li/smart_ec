from account_helper import *
from config import get_logger


def test_create_account():
    student = create_account_without_activation()
    get_logger().info(student)
    assert student is not None
    assert student['password'] == '1'
    student = create_account_without_activation(is_e10=True)
    get_logger().info(student)
    assert student is not None
    assert student['is_e10']


def test_activate_account():
    student = activate_account()
    get_logger().info(student)
