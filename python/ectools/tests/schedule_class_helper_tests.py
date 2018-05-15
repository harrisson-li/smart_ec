from ectools.config import get_logger, set_environment, set_partner
from ectools.schedule_class_helper import *


def test_schedule_class_topic():
    set_environment('qa')
    set_partner('mini')

    schedule_date = get_future_date(7)  # e.g. 05/20/2018
    week_code = get_year_week_code(schedule_date)  # e.g. 1821

    topic = schedule_class_topic(week_code=week_code,
                                 class_category='F2F',
                                 class_type='F2F High')
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
    schedule_class(schedule_date=schedule_date,
                   school_name='CD_MCC',
                   class_category='Workshop')

    get_logger().info(detail)
    assert detail is not None
