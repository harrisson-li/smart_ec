from ectools.account_helper import activate_school_v2_student
from ectools.config import set_environment
from ectools.offline_class_helper import *
from ectools.score_helper import *


def test_submit_score_helper_v2():
    set_environment('uat')
    student = activate_school_v2_student()
    student_id = student['member_id']
    get_logger().info(student)

    with submit_score_helper(student_id=student_id):
        submit_current_unit()
        pass_six_units_and_level_test()

    achieve_minimum_class_taken(student_id=student_id)
