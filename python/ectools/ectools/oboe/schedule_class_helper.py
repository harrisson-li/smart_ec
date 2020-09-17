"""
This module will provide functions to schedule EC class via oboe service.
"""

from ectools.oboe import utils, schedule_class_services
from ectools.oboe.schedule_class_services import schedule_class_topic_service


def get_future_date(days_delta=0, date_format='%m/%d/%Y'):
    """
    Get a date in specified format. for example::

      today = get_future_date()
      tomorrow = get_future_date(1)
      yesterday = get_future_date(-1)

    :param days_delta: any integer number.
    :param date_format: default = ``%m/%d/%Y``
    :return: date string in format.
    """
    return utils.get_future_date(days_delta, date_format)


def get_year_week_code(date_str):
    """
    Convert date string into week code.

    :param date_str: format in ``mm/dd/year``, e.g. 1/21/2017
    :return: e.g. ``1703`` ==> year 2017, third week
    """
    return utils.get_year_week_code(date_str)


def schedule_class_topic(**kwargs):
    """
    Schedule class topic
    :return: class topic info, dict data type.
    """

    return schedule_class_topic_service.schedule_class_topic(**kwargs)


def schedule_class(**kwargs):
    """
    Schedule class
    :return: class info, dict data type.
    """
    return schedule_class_services.schedule_class(**kwargs)


def delete_class(class_id, class_category):
    schedule_class_services.delete_class(class_id, class_category)
