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
You can quickly start with following call:
from ectools.manage_class_status_helper import *

# set smart repo, required for Mac / Linux system, default value only for windows system
set_smart_repo('/path/to/smart')

ClassStatus = class_status_name()
ClassFlag = class_status_flag()

manage_class_status(student_id, booking_id, schedule_class_id, ClassStatus.CHECK_IN, ClassFlag.CANCELLED)

"""

from ectools.config import config

from ectools.oboe import _import_smart


def class_status_name():
    _import_smart()
    from data.enums import ClassStatus
    return ClassStatus


def class_status_flag():
    _import_smart()
    from data.enums import ClassBookingStatusId
    return ClassBookingStatusId


def manage_class_status(student_id, booking_id, schedule_class_id, status_from, status_to):
    """
     Manage class status via OBOE service, for more detail please refer to:

        - smart\\business\oboe\service\manage_class_status_services\__init__.py
    """

    # config should be backup before importing 'setting', to avoid overridden by default value in setting init
    env, partner = config.env, config.partner

    _import_smart()
    from business.oboe.service import manage_class_status_services
    from settings import helper as smart_helper

    smart_helper.set_environment(env)
    smart_helper.set_partner(partner)
    manage_class_status_services.manage_class_status(student_id, booking_id, schedule_class_id,
                                                     status_from, status_to)
