"""
This method will provide feature to update class status.
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
"""
from ectools.internal.business.enums import ClassBookingStatusId
from ectools.internal.business.enums import ClassStatus
from ectools.oboe import manage_class_status_services


def class_status_name():
    return ClassStatus


def class_status_flag():
    return ClassBookingStatusId


def manage_class_status(student_id, booking_id, schedule_class_id, status_from, status_to):
    manage_class_status_services.manage_class_status(student_id, booking_id, schedule_class_id, status_from, status_to)
