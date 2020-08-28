from ectools.logger import get_logger
from ectools.oboe.request_helper import post_request, is_response_success
from ectools.oboe.utils import ManageClassStatusServices


def manage_class_status(student_id, booking_id, schedule_class_id, status_from, status_to):
    """
    :param student_id:
    :param booking_id:
    :param schedule_class_id:
    :param status_from: using statusName like 'Standby', 'Checkin', can refer enums.ClassStatus
            class ClassStatus:
            CHECK_IN = 'Checkin'
            NO_SHOW = 'NoShow'
            NO_SHOW_LATE = 'NoShowLate'
            CANCELLED = 'Cancelled'
            WAITING = 'Waiting'
            BOOKED = 'Booked'
            WAIT_FAILED = 'WaitFailed'
            STANDBY = 'Standby'
            TENTATIVELY_BOOKED = 'TentativelyBooked'
    :param status_to: using statusFlag, like 2, 4, ...., can refer enums.ClassBookingStatusId
            class ClassBookingStatusId:
            EMPTY = "0"
            BOOKED = "1"
            CHECK_IN = "2"
            NO_SHOW = "3"
            CANCELLED = "4"
            WAITING = "6"
            NO_SHOW_LATE = "8"
            TENTATIVELY_BOOKED = "11"
            STAND_BY = "12"
    :return:
    """
    data = {
        'StudentId': student_id,
        'BookingId': booking_id,
        'ScheduleClassId': schedule_class_id,
        'StatusFrom': status_from,
        'StatusTo': status_to
    }

    response = post_request(ManageClassStatusServices.ClassStatusSave, data)
    assert is_response_success(response), response
    get_logger().info("manage class status from {} to {} success.".format(status_from, status_to))
