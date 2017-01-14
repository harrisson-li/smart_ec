from selenium.webdriver.common.keys import Keys

from ectools.config import get_logger
from ectools.token_helper import get_token
from ectools.utility import get_score, get_browser, retry_for_error
from ..objects import *
from ..pages import TIMEOUT_FOR_ELEMENT_WAITING
from ..pages.score_helper_page_v1 import SubmitScoreHelperS15Page as CurrentPage

"""
Score submit tools for S15 students.
You must call load_student() method before any action.
"""


def _open_page():
    Cache.page = CurrentPage(get_browser(), get_token())
    Cache.page.get()
    Cache.page.wait_for_ready()


def _page():
    assert isinstance(Cache.page, CurrentPage)
    return Cache.page


def load_student(student_id, reload_page=True):
    if reload_page:
        _open_page()

    _page().element_member_textbox.clear()
    _page().element_member_textbox.send_keys(student_id)
    _page().element_member_textbox.send_keys(Keys.TAB)
    _page().wait_for_option_selector(CurrentPage.CURRENT_UNIT_SELECTOR_XPATH)


def wait_for_submit_ready():
    _page().wait_until_xpath_clickable(CurrentPage.BATCH_SUBMIT_BUTTON_XPATH)


def submit_current_unit(score=get_score(), skip_activity=0):
    _page().element_load_unit_progress_button.click()
    wait_for_submit_ready()

    _page().select_option_by_text(CurrentPage.EXCEPT_ACTIVITY_SELECTOR_XPATH, skip_activity)
    _page().element_level_test_score_textbox.clear()
    _page().element_level_test_score_textbox.send_keys(score)
    _page().element_level_test_batch_submit_score_button.click()
    _page().close_alert_and_get_its_text()
    _page().wait_for_ready()


def submit_for_unit(unit_id, score=get_score(), skip_activity=0):
    enroll_to_unit(unit_id=unit_id)

    _page().select_option_by_text(CurrentPage.EXCEPT_ACTIVITY_SELECTOR_XPATH, skip_activity)
    _page().element_level_test_score_textbox.clear()
    _page().element_level_test_score_textbox.send_keys(score)
    _page().element_level_test_batch_submit_score_button.click()
    _page().close_alert_and_get_its_text()
    _page().wait_for_ready()


def pass_to_unit(unit_id, score=get_score(), skip_activity=0):
    get_logger().info("Pass to unit {} and except {} activities".format(unit_id, skip_activity))
    _page().element_load_all_unit_progress.click()
    wait_for_submit_ready()

    _page().element_score_to_unit_textbox.send_keys(score)
    _page().select_option_by_index(CurrentPage.TARGET_UNIT_SELECTOR_XPATH, unit_id - 2)
    _page().select_option_by_text(CurrentPage.EXCEPT_ACTIVITY_SELECTOR_XPATH, 0)
    _page().element_batch_submit_all_unit_score_button.click()
    _page().close_alert_and_get_its_text(TIMEOUT_FOR_ELEMENT_WAITING)
    _page().wait_for_ready()
    submit_for_unit(unit_id=unit_id, score=score, skip_activity=skip_activity)


def pass_six_units(score=get_score()):
    pass_to_unit(6, score)


def pass_level_test(score=get_score()):
    get_logger().info("Pass level test")
    _page().select_option_by_index(CurrentPage.CURRENT_UNIT_SELECTOR_XPATH, 6)
    _page().element_load_unit_progress_button.click()
    wait_for_submit_ready()

    _page().element_level_test_score_textbox.send_keys(score)
    _page().element_level_test_batch_submit_score_button.click()
    _page().close_alert_and_get_its_text()
    _page().wait_for_ready()


def pass_six_units_and_level_test(score=get_score()):
    pass_to_unit(6, score)
    pass_level_test(score)


@retry_for_error(error=AssertionError)
def enroll_to_unit(unit_id, course_level=None):
    get_logger().info("Enroll to unit {}".format(unit_id))
    if course_level is not None:
        _page().select_option_by_text(CurrentPage.COURSE_NAME_SELECTOR_XPATH, course_level)

    _page().select_option_by_index(CurrentPage.CURRENT_UNIT_SELECTOR_XPATH, unit_id - 1)
    _page().element_enroll_to_selected_unit_button.click()
    wait_for_submit_ready()

    # reload to ensure enrollment changed
    student_id = _page().element_member_textbox.get_attribute('value')
    load_student(student_id, reload_page=False)
    current_unit = _page().first_selected_option(CurrentPage.CURRENT_UNIT_SELECTOR_XPATH)
    assert "Unit {}".format(unit_id) in current_unit.text
