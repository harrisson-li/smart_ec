from ectools.student_settings_helper import is_v2_student
from ectools.utility import get_score
from .internal.business import score_helper_v1 as v1
from .internal.business import score_helper_v2 as v2
from .internal.objects import *
import ectools.utility


def _is_submit_for_v2():
    return getattr(Cache, 'submit_for_v2', False)


def load_student(student_id, reload_page=True):
    Cache.submit_for_v2 = is_v2_student(student_id)
    if _is_submit_for_v2():
        v2.load_student(student_id, reload_page)
    else:
        v1.load_student(student_id, reload_page)


def submit_current_unit(score=get_score(), skip_activity=0):
    if _is_submit_for_v2():
        v2.submit_current_unit(score, skip_activity)
    else:
        v1.submit_current_unit(score, skip_activity)


def pass_to_unit(unit_id, score=get_score(), skip_activity=0):
    if _is_submit_for_v2():
        v2.pass_to_unit(unit_id, score, skip_activity)
    else:
        v1.pass_to_unit(unit_id, score, skip_activity)


def pass_six_units(score=get_score()):
    if _is_submit_for_v2():
        v2.pass_six_units(score)
    else:
        v1.pass_six_units(score)


def enroll_to_unit(unit_id):
    if _is_submit_for_v2():
        v2.enroll_to_unit(unit_id)
    else:
        v1.enroll_to_unit(unit_id)


def pass_level_test(score=get_score()):
    if _is_submit_for_v2():
        v2.pass_level_test(score)
    else:
        v1.pass_level_test(score)


def pass_six_units_and_level_test(score=get_score()):
    if _is_submit_for_v2():
        v2.pass_six_units_and_level_test(score)
    else:
        v1.pass_six_units_and_level_test(score)


def close_browser():
    """To close browser for score helper."""
    ectools.utility.close_browser()
