import ectools.internal.business.score_helper_v1 as s15_submit_tool
from assertpy import assert_that
from ectools.config import config, get_logger
from ectools.token_helper import get_token
from ectools.utility import get_browser, get_score, retry_for_error

from ..objects import *
from ..pages.score_helper_page_v2 import SubmitScoreHelperS15V2Page as CurrentPage

"""
Score submit tools for S15 Platform 2.0 students.
You must call load_student() method before any action.
"""

NOT_STARTED = "NotStarted"
ONGOING = "OnGoing"
PASSED = "Passed"
MAX_UNIT_NUMBER = 6


def _health_check():
    Cache.page = CurrentPage(get_browser())
    Cache.page.get_page(config.etown_root + "/services/api/ecplatform/_tools/health.aspx")
    assert_that(get_browser().page_source).contains("Overall Health:Ok")


def _open_page():
    _health_check()
    Cache.page = CurrentPage(get_browser(), get_token())
    Cache.page.get()


def _page():
    assert isinstance(Cache.page, CurrentPage)
    return Cache.page


def load_student(student_id, reload_page=True):
    if reload_page:
        _open_page()

    Cache.current_student = student_id
    _page().element_member_id_textbox.clear()
    _page().element_member_id_textbox.send_keys(student_id)
    _page().element_load_button.click()
    _page().wait_until_element_visible(_page().element_unit_info_text)


def submit_current_unit(score=get_score(), skip_activity=0):
    _page().wait_until_element_visible(_page().element_unit_score_textbox)
    _page().element_unit_score_textbox.clear()
    _page().element_unit_score_textbox.send_keys(score)
    _page().select_option_by_text(CurrentPage.ACTIVITY_SKIP_SELECTOR_XPATH, skip_activity)
    _page().element_unit_score_submit_button.click()

    if skip_activity == 0:
        verify_unit_status(expected_status=PASSED)
    else:
        verify_unit_status(expected_status=ONGOING)


def submit_for_unit(unit_id, score=get_score(), skip_activity=0):
    enroll_to_unit(target_unit_id=unit_id)
    submit_current_unit(score=score, skip_activity=skip_activity)


@retry_for_error(error=AssertionError)
def enroll_to_unit(target_unit_id):
    get_logger().info("Enroll to unit {}".format(target_unit_id))
    _page().select_option_by_index(CurrentPage.UNIT_LIST_SELECTOR_XPATH, target_unit_id - 1)
    _page().wait_until_xpath_clickable(_page().ENROLL_BUTTON_XPATH)
    _page().element_enroll_button.click()

    load_student(Cache.current_student, reload_page=False)
    current_unit = get_current_unit_id()
    assert current_unit == target_unit_id


def get_current_unit_id():
    current_unit = _page().first_selected_option(CurrentPage.UNIT_LIST_SELECTOR_XPATH)
    unit_id = current_unit.text.split('-')[0].split(' ')[1]
    return int(unit_id)


def pass_to_unit(unit_id, score=get_score(), skip_activity=0):
    get_logger().info("Pass to unit {} and except {} activities".format(unit_id, skip_activity))
    current_unit = get_current_unit_id()
    assert_that(current_unit).is_less_than_or_equal_to(unit_id)

    for unit in range(int(current_unit), unit_id + 1):

        if unit == unit_id:
            submit_for_unit(unit_id=unit, score=score, skip_activity=skip_activity)
        else:
            submit_for_unit(unit_id=unit, score=score)


def pass_six_units(score=get_score()):
    pass_to_unit(6, score)


def submit_merged_score_for_one_lesson(lesson_sequence, score=get_score()):
    merged_lesson = _page().get_merged_lesson(lesson_sequence)
    merged_lesson[0].clear()
    merged_lesson[0].send_keys(score)
    merged_lesson[1].click()


def submit_pc_score_for_one_lesson(lesson_sequence, score=get_score()):
    pc_lesson = _page().get_pc_lesson(lesson_sequence)
    pc_lesson[0].clear()
    pc_lesson[0].send_keys(score)
    pc_lesson[1].click()


def submit_mobile_score_for_one_lesson(lesson_sequence, score=get_score()):
    mobile_lesson = _page().get_mobile_lesson(lesson_sequence)
    mobile_lesson[0].clear()
    mobile_lesson[0].send_keys(score)
    mobile_lesson[1].click()


def verify_merged_lesson_status(lesson_sequence, expected_status):
    merged_lesson = _page().get_merged_lesson(lesson_sequence)
    get_logger().info(
        "Actual status is: %s; Expected status is: %s" % (merged_lesson[2][_page().STATUS], expected_status))
    return merged_lesson[2][_page().STATUS] == expected_status


def verify_pc_lesson_status(lesson_sequence, expected_status):
    pc_lesson = _page().get_pc_lesson(lesson_sequence)
    get_logger().info(
        "Actual status is: %s; Expected status is: %s" % (pc_lesson[2][_page().STATUS], expected_status))
    return pc_lesson[2][_page().STATUS] == expected_status


def verify_mobile_lesson_status(lesson_sequence, expected_status):
    mobile_lesson = _page().get_mobile_lesson(lesson_sequence)
    get_logger().info(
        "Actual status is: %s; Expected status is: %s" % (mobile_lesson[2][_page().STATUS], expected_status))
    return mobile_lesson[2][_page().STATUS] == expected_status


def get_unit_info():
    unit_info_text = _page().element_unit_info_text.text.split(',')
    unit_info = {_page().UNIT_ID: get_current_unit_id(), _page().UNIT_NAME: unit_info_text[1].split(':')[-1],
                 _page().SCORE: int(unit_info_text[2].split(':')[-1]),
                 _page().UNIT_HAS_PASSED: bool(unit_info_text[3].split(':')[-1]),
                 _page().STATUS: unit_info_text[4].split(':')[-1]}
    return unit_info


def verify_unit_status(expected_status):
    unit_info = get_unit_info()
    return unit_info[_page().STATUS] == expected_status


def pass_level_test(score=get_score()):
    student = Cache.current_student
    s15_submit_tool.load_student(student)
    s15_submit_tool.pass_level_test(score)


def pass_six_units_and_level_test(score=get_score()):
    pass_six_units(score=score)
    pass_level_test(score=score)
