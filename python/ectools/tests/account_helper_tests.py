from ectools.account_helper import *
from ectools.config import get_logger, set_environment
from ectools.internal.objects import *


def test_create_account():
    student = create_account_without_activation()
    get_logger().info(student)
    assert student is not None
    assert student['password'] == '1'

    student = {'member_id': student['member_id']}
    student = activate_account(student=student)
    assert student['member_id'] is not None

    # test save account via api
    import ectools.ecdb_helper as db_helper
    db_helper._remote_db_dir = '//not/exist/path'
    student = create_account_without_activation(is_e10=True)
    get_logger().info(student)
    assert student is not None
    assert student['is_e10']


def test_activate_account_default():
    set_environment('qa')
    student = activate_account(is_v2=True, mainRedemptionQty=60)
    get_logger().info(student)
    assert student is not None
    student = create_account_without_activation()
    student = activate_account(product_id=63, school_name='SH_ZJC', student=student)
    assert student['is_v2']
    assert student['school']['name'] == 'SH_ZJC'


def test_activate_account_kwargs():
    student = activate_account(startLevel=3, mainRedemptionQty=1, securityverified=False)
    assert student['startLevel'] == 3
    assert student['mainRedemptionQty'] == 1
    assert not student['securityverified']


def test_activate_account_more():
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
    student = activate_account()

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
