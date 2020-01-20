from ectools.config import set_environment, set_partner

from ectools.oboe.manage_class_status_helper import *


def test_manage_class_status():
    set_environment('uat')
    set_partner('cool')
    ClassStatus = class_status_name()
    ClassFlag = class_status_flag()
    student_id = 24002888
    booking_id = 582581
    schedule_class_id = 3137059
    manage_class_status(student_id, booking_id, schedule_class_id, ClassStatus.BOOKED, ClassFlag.CANCELLED)
