from ectools.config import set_environment, set_partner
from ectools.logger import get_logger
from ectools.oboe.schedule_class_helper import schedule_class_topic, schedule_class, get_year_week_code, \
    get_future_date, delete_class


def test_schedule_class_topic():
    set_environment('qa')
    set_partner('cool')

    schedule_date = get_future_date(7)  # e.g. 05/20/2018
    week_code = get_year_week_code(schedule_date)  # e.g. 1821

    topic = schedule_class_topic(week_code=week_code,
                                 class_category='F2F',
                                 class_type='F2F Beginner High')
    get_logger().info(topic)
    assert topic['School_id'] == 99
    assert topic['ClassCategory_id'] == 1


def test_schedule_class():
    set_environment('staging')
    set_partner('cool')

    schedule_date = get_future_date(1)  # tomorrow

    detail = schedule_class(schedule_date=schedule_date,
                            school_name='BJ_DFG',
                            class_category='LC')

    get_logger().info(detail)
    assert detail is not None

    # change partner
    set_partner('mini')
    detail = schedule_class(schedule_date=schedule_date,
                            school_name='CD_MCC',
                            class_category='Workshop')

    get_logger().info(detail)
    assert detail is not None


def test_delete_class():
    set_environment('qacn')
    set_partner('mini')

    schedule_date = get_future_date(1)  # tomorrow

    detail = schedule_class(schedule_date=schedule_date,
                            school_name='CD_MCC',
                            class_category='LC')

    delete_class(detail['ScheduledClass_id'], class_category='LC')

    # change partner
    set_partner('cool')
    detail = schedule_class(schedule_date=schedule_date,
                            school_name='BJ_DFG',
                            class_category='F2F')
    delete_class(detail['ScheduledClass_id'], class_category='F2F')


def test_schedule_class_F2F_VIP():
    set_environment('uatcn')
    set_partner('cool')

    schedule_date = get_future_date(1)  # tomorrow

    detail = schedule_class(schedule_date=schedule_date,
                            school_name='QA_T1C',
                            class_category='F2F',
                            is_vip_class=True)

    get_logger().info(detail)
    assert detail is not None

    # change partner
    set_partner('mini')
    detail = schedule_class(schedule_date=schedule_date,
                            school_name='QA_T2C',
                            class_category='F2F',
                            is_vip_class=True)

    get_logger().info(detail)
    assert detail is not None


def test_schedule_class_Teacher_Review():
    set_environment('uatcn')
    set_partner('cool')

    schedule_date = get_future_date(1)  # tomorrow

    detail = schedule_class(schedule_date=schedule_date,
                            school_name='QA_T1C',
                            class_category='1:1 Teacher Review')

    get_logger().info(detail)
    assert detail is not None


def test_schedule_class_with_capacity_reset():
    set_environment('staging')
    set_partner('cool')

    schedule_date = get_future_date(1)  # tomorrow
    detail = schedule_class(schedule_date=schedule_date,
                            school_name='SH_PSQ',
                            class_category='Workshop', capacity=0)

    get_logger().info(detail)
    assert detail is not None
