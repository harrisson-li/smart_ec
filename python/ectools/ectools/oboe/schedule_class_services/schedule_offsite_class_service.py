"""
Use this module to schedule LC and CAE class.

The major method you can use:

 - schedule_offsite_class
   will schedule LC / CAE class with provided parameters.

"""
from assertpy import assert_that

from ectools.config import *
from ectools.internal.business.enums import CenterType
from ectools.internal.data_helper import get_school_by_name
from ectools.logger import get_logger
from ..request_helper import *


def schedule_offsite_class(schedule_date, school_name, class_category=ClassCategory.LC,
                           center_type=CenterType.INCENTER, **kwargs):
    """
    Schedule LC / CAE class.
    :param schedule_date: date in format MM/DD/YYYY
    :param school_name: e.g. SH_PSQ
    :param class_category: LC or CAE
    :param center_type: InCenter or OutCenter
    :param kwargs: capacity/start_time/end_time/address_en/address_local
                   topic_en/topic_local/notes_en/notes_local
                   fee/friends_allowed/friends_total
    :return:
    """
    get_logger().info('Schedule class for {} / {} / {} @ {}'
                .format(school_name, class_category, center_type, schedule_date))

    assert_that(config.env.lower()).is_not_equal_to('live')
    week_code = get_year_week_code(schedule_date)
    capacity = kwargs.get('capacity', 100)

    is_today = schedule_date == get_future_date()
    start_time, end_time = get_random_time_for_lc(is_today)

    start_time = kwargs.get('start_time', start_time)
    end_time = kwargs.get('end_time', end_time)

    address_en = kwargs.get('address_en', 'auto address')
    address_local = kwargs.get('address_local', 'local address')
    topic_en = kwargs.get('topic_en', 'auto topic')
    topic_local = kwargs.get('topic_local', 'local topic')
    notes_en = kwargs.get('notes_en', None)
    notes_local = kwargs.get('notes_local', None)

    fee = kwargs.get('fee', None)
    friends_allowed = kwargs.get('friends_allowed', 0)
    friends_total = kwargs.get('friends_total', 0)

    school_partner = get_school_by_name(school_name)['partner']
    virtual_citywide_school_id = _get_citywide_school_id(school_name)

    data = {
        'ScheduledClass_id': 0,
        'VirtualSchool_id': virtual_citywide_school_id,
        'StartDate': schedule_date,
        'EndDate': schedule_date,
        'LastUpdateUTCDateTicks': 0,
        'SchoolPartnerCode': school_partner,
        'ClassType_id': 371,
        'StartTime': start_time,
        'EndTime': end_time,
        'BookingCutOffDate': '',
        'EventType_id': 120,
        'PersonaType_id': 161,  # Career Focus
        'genreExt': '',
        'Genre_id': '',
        'CenterType': center_type,
        'InCenterSchool_id': '',
        'InCenterClassroom_id': '',
        'Capacity': capacity,
        'Teacher_id': '',
        'Coordinator_id': '',
        'Address_en': address_en,
        'Address_local': address_local,
        'Topic_en': topic_en,
        'Topic_en_source': '',
        'Topic_local': topic_local,
        'Notes_en': notes_en,
        'Notes_local': notes_local,
        'Fee': fee,
        'TotalFriendsAllowed': friends_total,
        'FriendsAllowed': friends_allowed,
        'Material': ''
    }

    if center_type == CenterType.INCENTER:
        school_id = get_school_by_name(school_name)['id']
        classrooms = _get_classrooms_by_school_id(school_id, schedule_date)
        classroom = choice(classrooms)

        data.update({'InCenterSchool_id': school_id,
                     'InCenterClassroom_id': classroom['Classroom_id']})
        if not kwargs.get('ignore_classroom_capacity', False):
            data.update({'Capacity': classroom['Capacity']})

    if class_category == ClassCategory.CAE:
        data['ClassType_id'] = 3016
    if class_category == ClassCategory.EEA:
        data['ClassType_id'] = 5051

    get_logger().debug('detail = {}'.format(data))
    response = post_request(ScheduleClassServices.ScheduleLCOffSiteClass, data)
    assert is_response_success(response), response
    scheduled_class_id = response['ScheduledClass']['ScheduledClass_id']

    _publish_class(virtual_citywide_school_id, week_code)
    get_logger().info('The scheduled class id is: {}'.format(scheduled_class_id))

    # return the whole schedule class detail
    data['ScheduledClass_id'] = scheduled_class_id
    data['WeekCode'] = week_code
    return data


def _publish_class(school_id, week_code):
    """publish LC class"""
    data = {
        "pageScroll": '',
        'PageStatus': None,
        'PageMessage': '',
        'currentVirtualSchool_id': school_id,
        "currentSchool_id": 0,
        "currentWeekCode": week_code
    }

    response = post_request(ScheduleClassServices.LCOffSitePublish, data)
    assert is_response_success(response), response
    get_logger().debug("Publish class success")


def _read_schedule_offsite_form():
    """api = LCOffSite"""
    return get_request(ScheduleClassServices.ScheduleOffSite, False)


def _get_citywide_school_id(school_name):
    response = _read_schedule_offsite_form()
    city_name = get_school_by_name(school_name)['lc_city']
    school_ids = search_html_strings(response, 'select',
                                     attr={'name': 'currentVirtualSchool_id'},
                                     regex=r'<option .*value="(.*?)">{}<'.format(city_name))
    return choice(school_ids)


def _read_schedule_offsite_new_form(citywide_school_id, schedule_date):
    """
    post /oboe2/LCOffSite/New
    """
    return post_request(
        ScheduleClassServices.ScheduleOffSiteNew,
        {
            "school_id": citywide_school_id,
            "classDate": schedule_date,
        }, None, False)


def _get_classrooms_by_school_id(school_id, schedule_date):
    data = {
        "school_id": school_id,
        "classDate": schedule_date,
    }

    return post_request(ClassInfoServices.GetClassroomBySchoolId, data)


def delete_class(class_id):
    """
    Delete class without student booked.
    :param class_id:
    :return:
    """
    data = {'scheduledclass_id': class_id}
    response = post_request(ScheduleClassServices.DeleteOffSiteClass, data)
    assert is_response_success(response), response
    get_logger().debug('Delete class success')
