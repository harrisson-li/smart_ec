from datetime import datetime

import arrow
import pytz
from ectools.internal.business.enums import Partners
from ectools.internal.business.enums import Timezone


def get_current_utc_date_time():
    return datetime.now(pytz.timezone(Timezone.UTC))


def get_local_date_time(dt, tz):
    return dt.astimezone(tz)


def get_current_china_date_time():
    return get_current_local_date_time(Timezone.CHINA)


def get_current_moscow_date_time():
    return get_current_local_date_time(Timezone.MOSCOW)


def get_current_jakarta_date_time():
    return get_current_local_date_time(Timezone.JAKARTA)


def get_current_madrid_date_time():
    return get_current_local_date_time(Timezone.MADRID)


def get_current_boston_date_time():
    return get_current_local_date_time(Timezone.BOSTON)


def get_current_local_date_time(local_timezone):
    current_utc_time = get_current_utc_date_time()
    return get_local_date_time(current_utc_time, pytz.timezone(local_timezone))


def get_current_local_date_time_by_partner(partner=None):
    from ectools.config import config
    if not partner:
        partner = config.partner

    current_date_time = get_current_china_date_time()

    if partner == Partners.RUPE:
        current_date_time = get_current_moscow_date_time()
    elif partner == Partners.INDO:
        current_date_time = get_current_jakarta_date_time()
    elif partner == Partners.ECSP:
        current_date_time = get_current_madrid_date_time()

    return current_date_time


def convert_utc_to_target_timezone(target_timezone, utc_time):
    """
    Convert date time from utc to one target timezone.

    :param target_timezone: The timezone you want to convert to
           timezone format e.g TimeZone.BEIJING, "US/Pacific", "+07:00", "UTC"
           also can refer https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    :param utc_time: The original utc time you want to convert to other timezone
           utc_time can be string or datetime format
           if in string format, need to follow format "M/D/YYYY H:mm:ss A"
           e.g 1/7/2019 8:51:53 AM
    :return: time in arrow datetime type in target timezone
    """
    if isinstance(utc_time, str):
        time = (arrow.get(utc_time, "M/D/YYYY H:mm:ss A", tzinfo=Timezone.UTC))

        target_time = time.to(target_timezone)
    elif isinstance(utc_time, datetime) or isinstance(utc_time, arrow.Arrow):
        time = arrow.get(utc_time, tzinfo=Timezone.UTC)
        target_time = time.to(target_timezone)
    else:
        raise TypeError

    return target_time


def convert_time_slot_to_start_end_time_for_events(time_slot):
    start_end_time = time_slot.split("-")
    start_time = start_end_time[0].replace(":", "")
    end_time = start_end_time[1].replace(":", "")
    return start_time, end_time


def change_date_format(date, format_from='MM/DD/YYYY', format_to="YYYY-MM-DD"):
    local = arrow.get(date, format_from)
    return local.format(format_to)