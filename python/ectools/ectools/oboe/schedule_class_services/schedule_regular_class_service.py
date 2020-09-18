"""
Use this module to schedule normal class, e.g. F2F, WS, BB ...

The major method you can use:

 - schedule_regular_class
   will schedule a class with provided parameter
   if not class topic scheduled ahead will schedule a new one for you

"""
from random import choice, randint

from assertpy import assert_that

from ectools.config import *
from ectools.internal.business.enums import Partners, ClassCategory, Environments
from ectools.internal.data_helper import get_school_by_name
from ectools.logger import get_logger
from ectools.oboe.request_helper import post_request, ScheduleClassServices, is_response_success
from ectools.oboe.utils import get_future_date, get_year_week_code, get_week_day, get_available_week_type
from ectools.oboe.utils import search_html_strings, parse_timeslot_format, get_class_category_id
from .schedule_class_topic_service import schedule_class_topic_if_needed

SCHEDULE_CONFLICT_ERROR = "Another class has been scheduled"
TEACHER_CONFLICT_ERROR = "for the selected teacher."
CLASSROOM_CONFLICT_ERROR = "in the classroom selected."


# @retry_for_error(error=AssertionError)  # to improve schedule class rate, add retry mechanism
def schedule_regular_class(schedule_date, school_name, class_category,
                           class_type=None, class_topic=None, is_preview=False,
                           is_online_attending=False, is_vip_class=False):
    """
    method to schedule normal class: f2f, ws, apply etc.
    """
    if is_preview and not class_type:
        class_type = 'Beginner A'  # default to Beginner A to make things simple

    if class_category == 'F2F' and not class_type:
        if config.partner == 'Cehk':
            class_type = 'F2F Low'
        elif config.partner in ('Cool', 'Mini'):
            class_type = 'F2F Beginner Starter'
        else:
            class_type = 'F2F Beginner'

    info = [config.env, config.partner, school_name,
            class_category, class_type, class_topic, schedule_date]
    get_logger().info('Schedule class @ {}'.format(' / '.join([x for x in info if x])))

    week_code = get_year_week_code(schedule_date)

    available_week_type = None
    if class_category == ClassCategory.F2F and config.partner in (Partners.COOL,
                                                                  Partners.MINI,
                                                                  Partners.SOCN,
                                                                  Partners.CEHK):
        week_day = get_week_day(schedule_date)
        available_week_type = get_available_week_type(week_day)

    school_id = get_school_by_name(school_name, ignore_socn=True)['id']

    # skip when in live environment
    if config.env != Environments.LIVE:
        schedule_class_topic_if_needed(week_code, class_category,
                                       class_type, class_topic,
                                       available_week_type)

    html_response = _read_scheduled_class_form(school_id, week_code)
    teacher_ids = search_html_strings(html_response, 'select',
                                      attr={'name': 'Teacher_id'},
                                      regex=r'<option value="(.*?)">')
    classroom_ids = search_html_strings(html_response, 'div',
                                        attr={'id': 'scheduledClassHeaderContainer'},
                                        regex=r'classroomid="(.*?)"')

    time_slots = search_html_strings(html_response, 'td', {'class': 'timeSlot'}, r'>(\d.*?)<a ')

    # if is today, will always use last time slot to avoid schedule class at passed slot
    is_today = schedule_date == get_future_date()
    time_slot = time_slots[-1] if is_today else choice(time_slots)
    time_slot = parse_timeslot_format(time_slot)

    class_category_id = get_class_category_id(class_category)
    types_info = _read_available_types(schedule_date, school_id, class_category_id)
    type_info = _select_class_type_info(types_info, class_type)
    get_logger().debug(
        'Use class type: {} (class_type_id={})'.format(type_info['ClassTypeName'], type_info['ClassType_id']))

    topics_info = _read_available_topics(schedule_date, school_id, type_info['ClassType_id'])
    topic_info = _select_scheduled_class_topic_info(topics_info, class_topic)

    data = {
        'ScheduledClass_id': 0,
        'EndDate': schedule_date,
        'School_id': school_id,
        'LastUpdateUTCDateTicks': '',
        'StartDate': schedule_date,
        'StartTime': time_slot[0],
        'EndTime': time_slot[1],
        'ClassRoom_id': classroom_ids.pop(),
        'Capacity': randint(4, 10),
        'ClassCategory_id': class_category_id,
        'ClassType_id': type_info['ClassType_id'],
        'Teacher_id': teacher_ids.pop(),
        'LCDescription': '',
        'EnterableClassTopic': '',
        'IsOnlineAttending': False,
        'IsPreview': False,
        'PreviewTimePeriodIndex': 0,
        'AutoScheduledClassNeedToReview': '',
        'IsVipClass': False
    }

    if topic_info:
        get_logger().debug(
            'Use scheduled class topic: {} / {} / {} / {} / {} with AvailableWeekDayType={}'.format(
                topic_info['ScheduledClassTopic_id'],
                topic_info['ClassCategory_id'],
                topic_info['ClassType_id'],
                topic_info['ClassTopic_id'],
                topic_info['ClassTopicName'],
                topic_info['AvailableWeekDayType']))
        data['ScheduledClassTopic_id'] = topic_info['ScheduledClassTopic_id']
        data['ClassTopic_id'] = topic_info['ClassTopic_id']

    if is_preview:
        get_logger().debug('Schedule as preview class')
        assert_that(class_category).is_equal_to('Workshop')
        data['IsPreview'] = True
        data['PreviewTimePeriodIndex'] = randint(1, 2)

    if class_category == 'Apply':
        data.update({'LCDescription': 'Apply Topic Detail',
                     'EnterableClassTopic': 'Apply Test Topic'})

    if is_online_attending:
        get_logger().debug('Schedule online attending class')
        data['IsOnlineAttending'] = True

    if is_vip_class:
        get_logger().debug('Schedule VIP F2F class')
        assert_that(class_category).is_equal_to('F2F')
        data['IsVipClass'] = True

    get_logger().debug('detail = {}'.format(data))
    while True:
        response = post_request(ScheduleClassServices.ScheduleSpecifiedClass, data)
        if is_response_success(response):
            scheduled_class_id = response['ScheduledClass']['ScheduledClass_id']
            break

        elif SCHEDULE_CONFLICT_ERROR in str(response):

            try:

                if TEACHER_CONFLICT_ERROR in str(response):
                    get_logger().debug('Retry due to teacher conflict...')
                    data['Teacher_id'] = teacher_ids.pop()

                if CLASSROOM_CONFLICT_ERROR in str(response):
                    get_logger().debug('Retry due to classroom conflict...')
                    data['ClassRoom_id'] = classroom_ids.pop()

            except IndexError:
                raise ValueError('No available teacher or classroom to schedule class.')

        else:
            raise ValueError(response)

    # after schedule class success, we should publish the class
    _publish_class(school_id, week_code)
    get_logger().info('The scheduled class id is: {}'.format(scheduled_class_id))

    # return the whole schedule class detail
    data['ScheduledClass_id'] = scheduled_class_id
    data['WeekCode'] = week_code
    return data


def _read_scheduled_class_form(school_id, week_code):
    """api = ScheduledClass"""
    return post_request(
        ScheduleClassServices.ScheduleClass,
        {
            "currentSchoolId": school_id,
            "currentWeekCode": week_code,
        }, None, False)


def _read_available_types(schedule_date, school_id, class_category_id):
    """api = ScheduledClass/GetClassTypeAndScheduledClassTopicByClassCategory"""

    data = {
        "school_id": school_id,
        "classCategory_id": class_category_id,
        "classDate": schedule_date,
        "classType_id": 0
    }

    return post_request(ScheduleClassServices.GetClassType, data)


def _read_available_topics(schedule_date, school_id, class_type_id):
    """api =  ScheduledClass/GetClassTopicByClassTypeId"""

    data = {
        "school_id": school_id,
        "curDate": schedule_date,
        "classType_id": class_type_id,
    }

    return post_request(ScheduleClassServices.GetClassTopic, data)


def _select_class_type_info(info, class_type_name):
    """method to select proper class type id."""
    assert isinstance(info, dict) and 'ClassTypes' in info
    types = [t for t in info['ClassTypes']]

    if class_type_name:
        get_logger().info("Try to get class type with name: {}".format(class_type_name))
        types = [t for t in types if t['ClassTypeName'] == class_type_name]

    if len(types) > 0:
        return choice(types)
    else:
        raise Exception("Unable to get class type with name.")


def _select_scheduled_class_topic_info(info, class_topic_name):
    """method to select proper class topic id."""
    assert isinstance(info, list)
    if class_topic_name:
        info = [x for x in info if class_topic_name in x['ClassTopicName']]

    return choice(info) if info else None


def _publish_class(school_id, week_code):
    data = {
        "currentSchoolId": school_id,
        "currentWeekCode": week_code
    }

    response = post_request(ScheduleClassServices.ScheduleClassPublish, data)
    assert is_response_success(response), response
    get_logger().debug('Publish class success')


def delete_class(class_id):
    """
    Delete class whatever with student booked.
    :param class_id:
    :return:
    """
    data = {'scheduledclass_id': class_id,
            'isMandatory': True
    }
    response = post_request(ScheduleClassServices.DeleteScheduledClass, data)
    assert is_response_success(response), response
    get_logger().debug('Delete class success')
