"""
Use this module to schedule class topic.

The major method you can use:

 - schedule_class_topic
   will schedule class topic with provided parameters, skipped when topic already scheduled.

 - schedule_class_topic_if_needed
   will not schedule new topic if matched topic for the category and type already scheduled.


"""
from random import choice

from assertpy import assert_that
from lxml import etree

from ectools.config import *
from ectools.internal.business.enums import Partners, ClassCategory
from ectools.logger import get_logger
from ectools.oboe.utils import get_partner_school_id, get_class_category_id, ScheduleClassServices
from ..request_helper import post_request, is_response_success, JsonResponse


def schedule_class_topic(week_code, class_category, class_type=None, class_topic=None,
                         available_week_type=None):
    """
    method to schedule a class topic, will raise error if scheduled failed.

    :param available_week_type: 1: Mon/Wed/Fri/Sun, 2: Tue/Thu/Sat
    :param week_code: week info in format like: 1752, 1801 [year+week]
    :param class_category: class category like: F2F, Workshop
    :param class_type: optional, if not given will randomly pick one.
    :param class_topic: optional- partial matching rule, if not given will randomly pick one.
    :return:
    """
    info = [config.env, config.partner, class_category,
            class_type, class_topic, 'week {}'.format(week_code)]
    get_logger().info('Schedule class topic @ {}'.format(' / '.join([x for x in info if x])))

    school_id = get_partner_school_id(config.partner)
    category_id = get_class_category_id(class_category)
    class_type_id = _get_class_type_id(category_id, class_type)
    class_topic_id = _get_class_topic_id(class_type_id, class_topic)

    data = {
        "School_id": school_id,
        "ClassCategory_id": category_id,
        "ClassType_id": class_type_id,
        "ClassTopic_id": class_topic_id,
        "WeekCode": week_code,
        "AvailableWeekDayType": 0
    }

    msg = _schedule_handler(data)

    if config.partner in ('Cool', 'Mini', 'Cehk') and class_category == ClassCategory.F2F:
        data['AvailableWeekDayType'] = available_week_type
        msg = _schedule_handler(data)

    # return the schedule detail for troubleshooting
    data['Message'] = msg
    return data


def schedule_class_topic_if_needed(week_code, class_category, class_type=None, class_topic=None,
                                   available_week_type=None):
    """
     this method is mainly for checking matched F2F class topic and Workshop preview class
    """
    if class_category == ClassCategory.APPLY:
        get_logger().info('No need to schedule topic for Apply')
        return

    school_id = get_partner_school_id(config.partner)
    topics = _get_scheduled_class_topics(school_id, week_code)

    matched = [x for x in topics if x['ClassCategory'] == class_category]

    if available_week_type:
        matched = [x for x in matched if x['AvailableWeekType'] == available_week_type]

    if class_type:
        matched = [x for x in matched if x['ClassType'] == class_type]

    if class_topic:
        matched = [x for x in matched if class_topic in x['ClassTopic']]

    if not matched:
        if config.env.lower() == 'live':
            get_logger().warn('Cannot schedule class topic in Live env.')
            return
        Cache.oboe_service_session = None  # clear cache to re-login oboe
        schedule_class_topic(week_code, class_category, class_type, class_topic, available_week_type)
        Cache.oboe_service_session = None  # clear cache to make schedule topic available

    else:
        get_logger().info('No need to schedule new topic.')


def _schedule_handler(data):
    SAME_TOPIC_SCHEDULED = "Unable to schedule this class topic in this week, since the same class " \
                           "topic has been scheduled already."

    response = post_request(ScheduleClassServices.ScheduleClassTopic, data)

    if not is_response_success(response):
        if response[JsonResponse.ErrorMsg] == SAME_TOPIC_SCHEDULED:
            get_logger().warn('Already scheduled, ignore.')
        else:
            raise ValueError("Error: {}".format(response[JsonResponse.ErrorMsg]))

    return response[JsonResponse.ErrorMsg]


def _get_class_type_id(category_id, class_type_name):
    class_types = _get_class_types(category_id)
    found = class_types[0]

    if class_type_name:
        found = [x for x in class_types if x['ClassTypeName'] == class_type_name]
        assert_that(found, 'Class type name not found: {}'.format(class_type_name)).is_length(1)
        found = found[0]

    return found['ClassType_id']


def _get_class_topic_id(class_type_id, class_topic_name):
    class_topics = _get_class_topics(class_type_id)

    if len(class_topics) > 0:
        found = class_topics[0]

        if class_topic_name:
            matched = [x for x in class_topics if class_topic_name in x['ClassTopicName']]
            assert_that(len(matched), 'Class type name not found: {}'.format(class_topic_name)).is_not_zero()
            found = choice(matched)
        get_logger().info("Get class topic id: {}".format(found['ClassTopic_id']))
        return found['ClassTopic_id']
    else:
        raise ValueError("No class topic found with class type id = {}".format(class_type_id))


def _get_class_types(category_id):
    return post_request(ScheduleClassServices.LoadClassType, {
        'classCategory_id': category_id
    })


def _get_class_topics(class_type_id):
    get_logger().info("Try to get class topic id for class type {}".format(class_type_id))
    return post_request(ScheduleClassServices.LoadClassTopic, {
        'classType_id': class_type_id
    })


def _get_scheduled_class_topics(school_id, week_code):
    get_logger().info("Try to get scheduled class topic for school {} in week {}".format(school_id, week_code))
    dict_data = {
        'currentSchoolId': school_id,
        'currentWeekCode': week_code
    }
    response = post_request(ScheduleClassServices.GetScheduledClassTopic, dict_data, None, False)

    page = etree.HTML(response)
    matched = page.xpath(u"//td")
    scheduled_class_topic_ids = page.xpath(u"//span[contains(@class, 'editBtn')]/@cursctid")

    cells = [href.text for href in matched if str(href.text).strip()]

    columns, index = 6, 0
    rows = int(len(cells) / columns)
    topics = []

    for i in range(rows):
        category = cells[index]
        available_week_type = None
        if category == ClassCategory.F2F and \
                config.partner in (Partners.COOL,
                                   Partners.MINI,
                                   Partners.SOCN,
                                   Partners.CEHK):
            data = {
                'scheduledClassTopic_id': scheduled_class_topic_ids[i]
            }

            response = post_request(ScheduleClassServices.EditScheduledClassTopic, data, None, False)
            page_edit_scheduled_class_topic = etree.HTML(response)
            available_week_types = page_edit_scheduled_class_topic.xpath(
                u"//select[@id='AvailableWeekDayType']/option[@selected='selected']/@value")
            if len(available_week_types) == 0:
                available_week_type = '1'
            else:
                available_week_type = available_week_types[0]

        topics.append({'ClassCategory': cells[index],
                       'ClassType': cells[index + 1],
                       'ClassTopic': cells[index + 2],
                       'StartDate': cells[index + 3],
                       'EndDate': cells[index + 4],
                       'AvailableWeekType': available_week_type})
        index += columns
    if len(topics) == 0:
        get_logger().info("No scheduled class topic found, need to schedule a new one.")
    return topics
