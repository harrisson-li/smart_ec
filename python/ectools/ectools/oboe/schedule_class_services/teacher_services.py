from ectools.oboe.request_helper import post_request, TeacherServices, is_response_success


def is_teacher_exist(teacher_name):
    data = {
        'term': teacher_name
    }
    response = post_request(TeacherServices.GetTeacherList, data)
    return True if response else False


def create_teacher_by_school(school_id, teacher_name):
    data = {
        "Teacher_id": 0,
        "UserSchoolIds": school_id,
        "CurrentRoleCode": "",
        "CurrentTCRRoleStr": "TCR",
        "TeacherName": teacher_name,
        "AutoDeleteUnpublishedClass": 'False',
        "TeacherType_id": "2",
        "HomeSchool_id": school_id,
        "TeachingHourPerWeek": "0",
        "TeacherFeaturedClassType": ['5051'],
        "teacherFormData": '',
        "TeacherWorkingHours": ['', '', '', '', '', '', ''],
        "TeacherDayOff": []
    }
    final_data = {
        "Teacher_id": 0,
        "UserSchoolIds": school_id,
        "CurrentRoleCode": "",
        "CurrentTCRRoleStr": "TCR",
        "TeacherName": teacher_name,
        "AutoDeleteUnpublishedClass": 'False',
        "TeacherType_id": "2",
        "HomeSchool_id": school_id,
        "TeachingHourPerWeek": "0",
        "TeacherFeaturedClassType": ['5051'],
        "TeacherWorkingHours": ['', '', '', '', '', '', ''],
        "TeacherDayOff": [],
        'teacherFormData': str(data)}

    response = post_request(TeacherServices.InsertTeacher, final_data)
    assert is_response_success(response), response
