from ectools.account_helper import *
from ectools.logger import get_logger
from ectools.oboe.request_helper import *


def configure_offpeak_by_center(school_name, offpeak_date, timeslot):
    """

    :param school_name: like 'SH_PSQ'
    :param offpeak_date: format like 'mm/dd/yyyy'
    :param timeslot: format like: '1000-1700'
    """
    school_id = get_school_by_name(school_name)['id']
    week_day_index = time.strptime(offpeak_date, "%m/%d/%Y").tm_wday
    week_index = week_day_index + 1

    if week_index == 7:
        week_index = 0

    timeslot_format = parse_timeslot_format(timeslot, '')

    json_data = {
        "SchoolId": school_id,
        "WeekOffpeakInfos": [{"WeekDay": week_index,
                              "OffpeakInfoShowString": timeslot_format}]
    }

    response = post_request(OffPeakServices.OffPeakSave, None, json_data)
    assert is_response_success(response), response
    get_logger().info("Configure offpeak timeslot {} for {} at {} success.".format(timeslot, school_name, offpeak_date))
