from ectools.config import *
from ectools.internal.data_helper import get_online_teacher_by_display_name
from ectools.online_class_helper import OnlineClassHelper, classTypeGroup, get_teacher_center


def test_get_class_type():
    class_type = OnlineClassHelper().get_class_type()
    print(class_type)


def test_allocate_class():
    service_type = "PL"
    service_subtype = "Unspecific"
    level = "Any"
    partner = "Any"
    market = "Any"
    language = "en"
    teaching_item = "en"
    evc_server = "EvcUS1"
    duration = "30"
    start_time = "2020-03-05T11:00:00Z"
    end_time = "2020-03-05T11:30:00Z"
    center_code = "FWW"
    source_type_Code = "Allocated"
    class_info = OnlineClassHelper().allocate_class(service_type, service_subtype, level, partner, market, language,
                                                    teaching_item,
                                                    evc_server, duration, start_time, end_time, center_code,
                                                    source_type_Code)
    print(class_info)
    print(class_info[0]['classId'])


def test_set_availability():
    teacher_member_id = 10708789
    start_time = "2020-03-05T11:00:00Z"
    end_time = "2020-03-05T11:30:00Z"
    OnlineClassHelper().set_availability(teacher_member_id, start_time, end_time)


def test_assign_class():
    class_id = 1130787
    teacher_id = 10708789
    OnlineClassHelper().assign_class(class_id, teacher_id)


def test_schedule_class():
    set_environment('staging')
    teacher_id = 14830955
    class_type = classTypeGroup['Common']['GL-General-EvcCN1 for all levels']
    start_time = "2020-03-10 18:00:00"
    OnlineClassHelper().schedule_class(teacher_id, class_type, start_time, 1)


def test_get_teacher_center_code():
    set_environment('stagingcn')
    teacher_id = 14828995
    center_code = get_teacher_center(teacher_id)
    print(center_code)


def test_get_teacher_by_display_name():
    set_environment('qacn')
    teacher_name = get_online_teacher_by_display_name('Candy E.')
    print(teacher_name)
