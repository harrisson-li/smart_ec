import json
import re
from datetime import timedelta, date, datetime
from random import choice, randint

from bs4 import BeautifulSoup as bs

from ectools.internal.business.enums import ClassCategory
from ectools.internal.business.time_helper import get_current_local_date_time_by_partner
from ectools.logger import get_logger


class ScheduleClassServices:
    ScheduleClass = "ScheduledClass"
    GetClassType = "ScheduledClass/GetClassTypeAndScheduledClassTopicByClassCategory"
    GetClassTopic = "ScheduledClass/GetClassTopicByClassTypeId"
    GetTeacher = "ScheduledClass/GetTeacherListFilteredByClassTypeAndClassCategory"
    GetScheduledClassTopic = "ScheduledClassTopic"
    ScheduleClassTopic = "ScheduledClassTopic/Insert"
    ScheduleSpecifiedClass = "ScheduledClass/Insert"
    ScheduleClassPublish = "ScheduledClass/Publish"
    LCOffSitePublish = "LCOffSite/Publish"
    LoadClassType = "ScheduledClassTopic/LoadClassTypeByClassCategory_id"
    LoadClassTopic = "ScheduledClassTopic/LoadClassTopicByClassType_id"
    ScheduleOffSite = "LCOffSite"
    ScheduleOffSiteCA = "LCOffSite/IndexCA"
    ScheduleOffSiteNew = "LCOffSite/New"
    ScheduleLCOffSiteClass = "LCOffSite/Insert"
    EditScheduledClassTopic = "ScheduledClassTopic/Edit"
    DeleteScheduledClass = "ScheduledClass/Delete"
    DeleteOffSiteClass = "LCOffSite/Delete"


class TeacherServices:
    InsertTeacher = "Smart/Teacher/Insert"
    GetTeacherList = "Smart/Teacher/GetTeacherList"


class ClassInfoServices:
    GetClassroomBySchoolId = "Common/GetClassroomBySchool_id"


class ChangePartner:
    ChangePartner = "PartnerCode/ChangePartner"


class OffPeakServices:
    OffPeakSave = "Offpeak/Save"


class ManageClassStatusServices:
    ClassStatusSave = "BookingStatus/SaveForAdmin"


class AdminToolsServices:
    TechSupport = "/techsupport"
    GetToken = "AdminTools/MemberSiteSetting"


class StatusCode:
    Success = 200


class ResponseStatus:
    Success = True
    Failed = False


def string_to_json(data):
    return json.loads(data)


class JsonResponse:
    IsSuccess = "IsSuccess"
    Success = "Success"
    ErrorCode = "ErrorCode"
    ErrorMessage = "ErrorMessage"
    ErrorMsg = "ErrorMsg"


partner_school_id_mapping = {'Cool': 99, 'Mini': 106, 'Cehk': 910,
                             'Rupe': 1000, 'Indo': 2000, 'Ecsp': 3000, 'Socn': 3017,
                             'cool': 99, 'mini': 106, 'cehk': 910,
                             'rupe': 1000, 'indo': 2000, 'ecsp': 3000, 'socn': 3017
                             }

class_category_id_name_mapping = {1: ClassCategory.F2F,
                                  2: ClassCategory.WORKSHOP,
                                  3: ClassCategory.APPLY,
                                  4: ClassCategory.LIFE_CLUB,
                                  38: ClassCategory.CA_SEMINAR,
                                  41: ClassCategory.SKILL_WORKSHOP,
                                  42: ClassCategory.BUSINESS_ENGLISH,
                                  49: ClassCategory.BEGINNER_BASICS,
                                  43: ClassCategory.BEGINNER_LC,
                                  203: ClassCategory.ENGLISH_CORNER,
                                  205: ClassCategory.TEACHER_REVIEW,
                                  300: ClassCategory.BUSINESS_ENGLISH_WORKSHOP,
                                  503: ClassCategory.CAREER_TRACK,
                                  504: ClassCategory.SKILLS_CLINICS,
                                  507: ClassCategory.BEGINNER_BASICS_v2}


def get_partner_school_id(partner):
    return partner_school_id_mapping[partner]


def get_class_category_id(category_name):
    for k, v in class_category_id_name_mapping.items():
        if v == category_name:
            return k

    raise ValueError('Cannot find matched id for class category: {}'.format(category_name))


def get_class_category_name(category_id):
    return class_category_id_name_mapping[category_id]


def filter_json_data(data, filter_string1, filter_string2=None):
    if isinstance(data, str):
        data = string_to_json(data)
    if not data:
        raise ValueError("data cannot be empty.")

    filter_info = []

    for dic in data:
        for k, v in dic.items():
            if k.startswith(filter_string1):
                filter_info.append(v if filter_string2 is None else {dic[filter_string2]: v})

    return filter_info


def search_in_dict(data, filter_key, filter_value):
    if isinstance(data, str):
        data = string_to_json(data)

    filter_info = []

    for dic in data:
        for k, v in dic.items():
            if k.startswith(filter_key) and v.startswith(filter_value):
                filter_info.append(dic)

    if not filter_info:
        get_logger().info("No proper data found in the data {}.".format(data))
        return False
    else:
        return filter_info


def get_value_by_dict(dict_data, key=None):
    assert isinstance(dict_data, dict)

    for k, v in dict_data.items():
        # if no key given, then return the first value directly
        if key is None:
            return v

        # if k in dict_data is tuple or string, and given key in the tuple or string
        if isinstance(k, (tuple, str)) and key in k:
            return v


def search_from_html(html_response, tag, attr, regex, is_today=False):
    """
    this method filter out random required info from html response
    :param html_response: html format response
    :param tag: html tag like td, select...
    :param attr: format like {attrName: attrValue}
    :param regex: regular expression
    :param is_today: check if today
    :return: random required info
    """
    if html_response:
        doc = bs(html_response, 'html.parser')
        match_info = doc.find_all(tag, attr)
        strings = re.findall(regex, str(match_info))
        if is_today:
            return strings[-1]
        else:
            return choice(strings)


def search_html_strings(html_content, tag, attr, regex):
    assert isinstance(html_content, str), 'html content should be provided!'
    doc = bs(html_content, 'html.parser')
    match_info = doc.find_all(tag, attr)
    return re.findall(regex, str(match_info))


def get_class_category_id_by_name(class_category):
    class_category_id = None
    for k, v in class_category_id_name_mapping.items():
        if v == class_category:
            class_category_id = k
            break

    if class_category_id:
        return class_category_id
    else:
        raise ValueError("Cannot find mapped class category id by "
                         "class category {}.".format(class_category))


def parse_timeslot_format(timeslot, split_mode='-'):
    """
    this method parse timeslot format from "16:00-17:00" to "[1600, 1700]"
    """
    if split_mode == '-':
        return timeslot.replace(':', '').split('-')
    elif split_mode == '':
        return timeslot.replace(':', '')


def get_future_date(days_delta=0, date_format="%m/%d/%Y"):
    """this method gets today's date by default"""

    current_time = get_current_local_date_time_by_partner()
    today = current_time.date()
    future_date = today + timedelta(days=days_delta)
    return future_date.strftime(date_format)


def get_future_hour(days_delta=0, hours_delta=0, date_format="%m/%d/%Y %H:%M:%S"):
    """this method gets current hour by default"""

    current_time = get_current_local_date_time_by_partner()
    minutes_delta = -current_time.minute
    seconds_delta = -current_time.second
    future_time = current_time + timedelta(days=days_delta, hours=hours_delta,
                                           minutes=minutes_delta, seconds=seconds_delta)
    return future_time.strftime(date_format)


def get_future_time(days_delta=0, hours_delta=0, minutes_delta=0, seconds_delta=0, date_format="%m/%d/%Y %H:%M:%S"):
    """this method gets current time by default"""

    current_time = get_current_local_date_time_by_partner()
    future_time = current_time + timedelta(days=days_delta, hours=hours_delta,
                                           minutes=minutes_delta, seconds=seconds_delta)
    return future_time.strftime(date_format)


def get_year_week_code(date_str=None):
    """
    get the exact week code in year from given date_str
    :param date_str: format 'mm/dd/year', e.g. 1/21/2017
    :return: e.g. 1703 ===> 2017 year, third week
    """
    if not date_str:
        date_str = str(get_future_date(1))

    # oboe system week number does not same to iso week number
    # week the first day of the year place in year before, than that week will be first week
    date_time = datetime.strptime(date_str, '%m/%d/%Y').date()
    first_day_of_the_year = date(date_time.year, 1, 1).isocalendar()
    should_adjust = first_day_of_the_year[0] != date_time.year

    week_info = date(date_time.year, date_time.month, date_time.day).isocalendar()
    if should_adjust:
        if week_info[0] == date_time.year:
            year = str(week_info[0])[2:]
            week = week_info[1] + 1
        else:
            year = str(week_info[0] + 1)[2:]
            week = 1
    else:
        year = str(week_info[0])[2:]
        week = week_info[1]

    return "{0}{1:02d}".format(year, week)


def get_week_day(date_str=None):
    """
    get the week day of the given date_str
    :param date_str: format 'mm/dd/year', e.g. 3/22/2020
    :return: 0, 1, 2, 3, 4, 5, 6 represents to Mon, Tue, Wed, Thu, Fri, Sat, Sun
    """
    if not date_str:
        date_str = str(get_future_date(1))

    date_time = datetime.strptime(date_str, '%m/%d/%Y').date()

    return date_time.weekday()


def get_available_week_type(week_day):
    """
    get the available week type, Mon/Wed/Fri/Sun or Tue/Thu/Sat
    :param week_day: 0 to 6
    :return: 1 means Mon/Wed/Fri/Sun, 2 means Tue/Thu/Sat
    """
    if 0 <= week_day <= 6:
        if week_day % 2 == 0:
            return 1
        else:
            return 2
    else:
        raise ValueError("Please pass correct week_day 0 to 6")


def get_day_from_date(date_time):
    """
    this method gets selected day from date
    for example: date_time is 2019-12-25, then method returns 25
    """

    future_date = datetime.strptime(date_time, '%m/%d/%Y')
    return future_date.day


def get_month_from_date(date_time):
    """
    this method gets selected month from date
    for example: date_time is 2019-12-25, then method returns 12
    """

    future_date = datetime.strptime(date_time, '%m/%d/%Y')
    return future_date.month


def get_random_time_for_lc(today=False):
    if not today:
        hour = randint(8, 22)
        minute = randint(0, 59)
        start_time = hour * 100 + minute
        end_time = start_time + 100
    else:
        start_time = 2100
        end_time = 2200

    return start_time, end_time


def level_code_map(level_code='0A'):
    if level_code == 'L0':
        return 0
    elif level_code == '0A':
        return 1
    elif level_code == '0B':
        return 2
    else:
        return int(level_code) + 2


def level_number_map(level_number=1):
    if level_number < 0 or level_number > 16:
        raise ValueError("Level number {} is invalid, please pass value between 0 to 16.".format(level_number))

    if level_number in (0, 1):
        return '0A'
    elif level_number == 2:
        return '0B'
    else:
        return str(level_number - 2)
