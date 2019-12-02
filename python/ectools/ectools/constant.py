class Memcached(object):
    # cache time = 6 hours
    STUDENT_FEATURE_ACCESS_GRANTS = 'ec_platform_oboe_studentfeatureaccessgrants_bystudent_primitive_{student_id}'

    # cache time = 24 hours
    META_COUPON_DISPLAY = 'ec_platform_oboe_metacoupongroupdisplay_{site_version}_partner_{partner_code}'

    # cache time = 1 hour
    SF_LOGIN = 'ec_platform_SFLoginInfo'

    # cache time = 12 hours
    CLASS_TOKEN = 'ec_platform_ClassToken_{scheduled_class_id}'

    # cache time = 12 hours
    CLASS_BIZ = 'ec_platform_classbiz_{site_version}_product_{product_id}'

    # cache time = 48 hours
    NPS_ONLINE_STATUS_BY_STUDENT = 'ec_platform_oboe_npsonlinestatus_bystudentid_{student_id}'

    # cache time = 2 hours
    STUDENT_BASIC_INFO = 'ec_platform_oboe_studentbasicinfo_bystudent_primitive_V3_{student_id}'

    # cache time = 6 hours
    STUDENT_PRODUCT_FEATURE = 'ec_platform_oboe_studentproductfeature_bystudent_primitive_{student_id}'

    # cache time = 12 hours
    STUDENT_PACKAGE_FEATURE = 'ec_platform_studentpackagefeature_{student_id}'

    # cache time = 6 hours
    STUDENT_INFO = 'ec_platform_ec_student_by_studentid_{student_id}'

    # ClassTaken for offline class, cache = 2 hours
    CLASS_TAKEN_OFFLINE = 'ec_platform_{site_version}_ClassTaken_{student_id}'

    # class attendance for online class, cache = 2 hours
    CLASS_ATTENDANCE_ONLINE = 'student_totalclassattendance_{student_id}'
