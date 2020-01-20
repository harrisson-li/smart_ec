"""
This module will provide functions to schedule EC class via oboe service. Example usage::

  from ectools.schedule_class_helper import *
  from ectools.config import set_environment, set_partner

  # set smart repo, required for Mac / Linux system
  set_smart_repo('/path/to/smart')

  # first of all, you have to set environment and partner
  set_environment('qa')
  set_partner('mini')

  # choose the date and week
  schedule_date = get_future_date(7)  # e.g. 05/20/2018
  week_code = get_year_week_code(schedule_date)  # e.g. 1821

  # then schedule a class topic (optional)
  topic_info = schedule_class_topic(week_code=week_code,
                                   class_category='F2F',
                                   class_type='F2F High')

  # or schedule a class directly, if no topic scheduled it will auto schedule one
  # schedule_class() support offsite class and center class, see below examples

  # offsite class and supported arguments
  detail = schedule_class(schedule_date=schedule_date,
                          school_name='BJ_DFG',
                          class_category='LC'
                          # center_type = 'InCenter' / 'OutCenter'
                          # capacity
                          # start_time e.g. '1100'
                          # end_time e.g. '1200'
                          # address_en
                          # address_local
                          # topic_en
                          # topic_local
                          # notes_en
                          # notes_local
                          # fee
                          # friends_allowed
                          # friends_total
                          )

  # center class and supported arguments
  set_partner('mini')
  schedule_class(schedule_date=schedule_date,
                 school_name='CD_MCC',
                 class_category='Workshop'
                 # class_type=None => optional
                 # class_topic=None => optional, partial match
                 # is_preview => optional, for Beginner Workshop
                 )

For more detail about schedule class topic and schedule topic, please refer to smart automation repo.

 -  ``smart\\business\oboe\service\schedule_class_services\``

"""

from ectools.config import config

from ectools.oboe import _import_smart


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
    _import_smart()
    from data import utilities as i
    return i.get_future_date(days_delta, date_format)


def get_year_week_code(date_str):
    """
    Convert date string into week code.

    :param date_str: format in ``mm/dd/year``, e.g. 1/21/2017
    :return: e.g. ``1703`` ==> year 2017, third week
    """
    _import_smart()
    from data import utilities as i
    return i.get_year_week_code(date_str)


def schedule_class_topic(**kwargs):
    """
    Schedule class topic via OBOE service, for more detail please refer to:

        - ``smart\\business\oboe\service\schedule_class_services\schedule_class_topic_service.py``

    :return: class topic info, dict data type.
    """
    _import_smart()
    # config should be backup before importing 'setting', to avoid overridden by default value in setting init
    env, partner = config.env, config.partner
    from business.oboe.service import schedule_class_services as smart_oboe_svc
    from settings import helper as smart_helper

    smart_helper.set_environment(env)
    smart_helper.set_partner(partner)
    return smart_oboe_svc.schedule_class_topic(**kwargs)


def schedule_class(**kwargs):
    """
    Schedule class via OBOE service, for more detail please refer to:

        - ``smart\\business\oboe\service\schedule_class_services\__init__.py``
        - ``smart\\business\oboe\service\schedule_class_services\schedule_offsite_class_service.py``
        - ``smart\\business\oboe\service\schedule_class_services\schedule_regular_class_service.py``

    :return: class info, dict data type.
    """
    _import_smart()
    # config should be backup before importing 'setting', to avoid overridden by default value in setting init
    env, partner = config.env, config.partner
    from business.oboe.service import schedule_class_services as smart_oboe_svc
    from settings import helper as smart_helper

    smart_helper.set_environment(env)
    smart_helper.set_partner(partner)
    return smart_oboe_svc.schedule_class(**kwargs)
