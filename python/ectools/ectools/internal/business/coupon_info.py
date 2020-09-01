from ectools.db_query import fetch_all
from ectools.internal.business.enums import CouponType
from ectools.internal.constants import E19_LEVEL_STAGE_MAPPING, S18_LEVEL_STAGE_MAPPING
from ectools.internal.data_helper import get_move_on_info
from ectools.oboe.utils import level_code_map
from ectools.service_helper import get_EEA_coupon, get_basic_offline_coupon_info, get_special_offline_coupon_info, \
    is_e19_student
from ectools.utility import xml_to_dict

PRODUCT_INITIAL_COUPON_MAPPING = {
    63: {
        'PL20': 1,
        'GL': 0,
        'Face to Face': 1,
        'Workshop': 1,
        'Life Club': 1
    },
    64: {
        'PL20': 1,
        'GL': 0
    },
    65: {
        'PL20': 1,
        'GL': 0,
        'Face to Face': 1,
        'Workshop': 1,
        'Life Club': 1
    },
    66: {
        'PL20': 1,
        'GL': 0
    },
    67: {'GL': 0},
    68: {'GL': 0},
    127: {
        'PL20': 1,
        'GL': 360,  # 1/day
        'Face to Face': 1,
        'Workshop': 1,
        'Life Club': 1
    },
    128: {
        'PL20': 1,
        'GL': 360  # 1/day
    },
    129: {
        'GL': 360  # 1/day
    },
    130: {},
    135: {
        'GL': 0,
        'Face to Face': 1,
        'Workshop': 1,
        'Life Club': 1
    },
    136: {
        'GL': 0
    },
    139: {
        'PL40': 156,  # 13/month
        'GL': 0
    },
    142: {
        'PL20': 1,
        'GL': 0,
        'F2F/PL20': 1,
        'Workshop': 2,
        'Life Club': 1
    },
    143: {
        'PL20': 12,  # 1/month
        'GL': 0,
        'Life Club': 1
    },
    147: {
        'PL20': 1,
        'GL': 0,
        'Face to Face': 1,
        'Workshop': 1,
        'Life Club': 1
    },
    158: {
        'GL': 0
    },
    # Online Pack Basic
    162: {
        'GL': 18,
        'PL40': 12
    },
    'Beginner Basics': {'Beginner Basics': 10},
    'Skills Clinics': {'Skills Clinics': 6},
    'Career Track': {'Career Track': 4}
}

COUPON_CODE_NAME_MAPPING = {
    'f2f': CouponType.Face2Face,
    'workshop': CouponType.WORKSHOP,
    'lifeclub': CouponType.Life_Club,
    'pl20': CouponType.PL20,
    'pl40': CouponType.PL40,
    'bbpl': CouponType.BBPL,
    'bbv2': CouponType.Beginner_Basics_v2,
    'gl': CouponType.GL,
    '1:1 teacher review': CouponType.TeacherReview,
    'eea': CouponType.EEA
}


def is_offline_coupon(coupon_type):
    return coupon_type in (CouponType.Face2Face, CouponType.F2F,
                           CouponType.WORKSHOP, CouponType.WS,
                           CouponType.APPLY, CouponType.EF_EVENTS,
                           CouponType.Life_Club, CouponType.LC,
                           CouponType.Beginner_Basics, CouponType.BB,
                           CouponType.Beginner_Basics_v2, CouponType.BBv2,
                           CouponType.TeacherReview)


def get_initial_coupon(product_id, has_beginner_basics):
    initial_coupon = PRODUCT_INITIAL_COUPON_MAPPING[product_id]

    if has_beginner_basics:
        initial_coupon.update(PRODUCT_INITIAL_COUPON_MAPPING['Beginner Basics'])

    return initial_coupon


def get_stage_coupon_info(product_id, stage, tag):
    coupon_info = get_move_on_info(product_id=product_id, tag=tag)

    info = {}
    if len(coupon_info):
        info = eval(coupon_info['stage_move_on_coupon_info'])[stage]

    return info


def get_initial_coupon_for_smart_plus(product_id, stage, tag):
    stage_coupon_info = get_stage_coupon_info(product_id, stage, tag)
    coupons = {}
    for k, v in stage_coupon_info.items():
        coupons[COUPON_CODE_NAME_MAPPING[k]] = v
    return coupons


def get_level_move_on_criteria_info(product_id):
    coupon_info = get_move_on_info(product_id=product_id)
    info = {}
    if len(coupon_info):
        info = eval(coupon_info['level_move_on_criteria'])

    return info


def get_initial_offline_coupon_for_smart_plus(product_id, stage, tag):
    coupon_info = get_initial_coupon_for_smart_plus(product_id, stage, tag)

    offline_coupon = {}
    for name, count in coupon_info.items():
        if is_offline_coupon(name):
            offline_coupon[name] = count

    return offline_coupon


def get_unit_move_on_coupon_grant_pl20_history(student_id):
    sql = "SELECT * FROM Oboe.dbo.CouponGrantHistory " \
          "WHERE Student_id = {} AND CouponType_id = 2 AND GrantType_id = 2"  # PL20 unit move on grant type
    return fetch_all(sql.format(student_id), as_dict=True)


def get_unit_move_on_released_coupon_info(student_id):
    grant_history = get_unit_move_on_coupon_grant_pl20_history(student_id)

    for info in grant_history:
        coupon_grant_context = xml_to_dict(info['ContextData'])

        grant_items = coupon_grant_context['CouponGrantContextData']['Items']['CouponGrantContextDataItem']

        # get level unit info from grant context data
        # {'levelcode': '5', 'unit': '2', 'event': 'UnitMoveOn'}
        for grant_item in grant_items:
            item_name = grant_item['Name']
            item_value = grant_item['Value']

            info[item_name] = item_value

    return grant_history


def get_unit_move_on_released_coupon_count_in_stage(student_id, stage_name):
    coupon_info = get_unit_move_on_released_coupon_info(student_id)
    stage_mapping = E19_LEVEL_STAGE_MAPPING if is_e19_student(student_id) else S18_LEVEL_STAGE_MAPPING

    count = 0
    for info in coupon_info:
        level_number = level_code_map(info['levelcode'])

        if stage_mapping[level_number] == stage_name:
            count = count + int(info['GrantQuantities'])

    return count


def get_student_left_offline_coupon(student_id):
    left_offline_coupon = get_basic_offline_coupon_info(student_id)
    left_special_offline_coupon = get_special_offline_coupon_info(student_id)
    left_offline_coupon.update(left_special_offline_coupon)
    student_left_eea_coupon = get_EEA_coupon(student_id)[1]
    if student_left_eea_coupon > 0:
        left_offline_coupon[CouponType.EEA] = student_left_eea_coupon

    return left_offline_coupon
