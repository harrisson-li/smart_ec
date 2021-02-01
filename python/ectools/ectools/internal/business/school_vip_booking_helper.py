from ectools.internal.constants import OBOE_USER_EMAIL
from ectools.internal.objects import Cache
from ectools.internal.pages.school_vip_class_booking_page import SchoolVipClassBookingPage
from ectools.internal.pages.tools_seat_page import ToolsSeatPage
from ectools.logger import get_logger
from ectools.utility import get_browser


def get_school_vip_booking_token(student_id):
    tools_seat_page = ToolsSeatPage(get_browser())
    tools_seat_page.get()
    tools_seat_page.wait_for_ready()

    tools_seat_page.element_student_id_input.clear()
    tools_seat_page.element_student_id_input.send_keys(student_id)

    tools_seat_page.element_operator_input.clear()
    tools_seat_page.element_operator_input.send_keys(OBOE_USER_EMAIL)

    tools_seat_page.element_school_vip_booking_button.click()

    token = tools_seat_page.element_school_vip_booking_token.text

    return token


def _open_page(student_id):
    token = get_school_vip_booking_token(student_id)

    Cache.page = SchoolVipClassBookingPage(get_browser(), token)
    Cache.page.get()
    Cache.page.wait_for_ready()


def _page():
    assert isinstance(Cache.page, SchoolVipClassBookingPage)
    return Cache.page


def search_school_vip_class(student_id, school_name, class_category, class_date):
    get_logger().info("Search class with {} / {} / {}".format(school_name, class_category, class_date))
    _open_page(student_id)

    _page().select_option_by_text(_page().SCHOOL_SELECTOR_XPATH, school_name)
    _page().select_option_by_text(_page().CLASS_CATEGORY_SELECTOR_XPATH, class_category)
    _page().element_class_date_input.clear()
    _page().element_class_date_input.send_keys(class_date)
    _page().element_search_button.click()


def has_class_searched():
    return _page().is_xpath_present(_page().SEARCHED_CLASS_LIST_XPATH)


def book_school_vip_class(student_name, scheduled_class_id):
    get_logger().info("Book class (class_id={}) for student {}".format(scheduled_class_id, student_name))
    if has_class_searched():
        student_field = _page().get_student_name(scheduled_class_id)
        if student_field != student_name:
            _page().element_student_name(scheduled_class_id).clear()
            _page().element_student_name(scheduled_class_id).send_keys(student_name)

        _page().wait_until_xpath_visible(_page().BOOK_BUTTON_XPATH.format(scheduled_class_id))
        _page().get_element_book_button(scheduled_class_id).click()
        _page().wait_until_xpath_visible(_page().CONFIRM_BOOK_POPUP_XPATH)
        _page().element_popup_confirm_button.click()
    else:
        raise ValueError("No classes searched.")


def book_school_vip_class_failed(student_name, scheduled_class_id):
    get_logger().info("Book class failed (class_id={}) for student {}".format(scheduled_class_id, student_name))
    if has_class_searched():
        student_field = _page().get_student_name(scheduled_class_id)
        if student_field != student_name:
            _page().element_student_name(scheduled_class_id).clear()
            _page().element_student_name(scheduled_class_id).send_keys(student_name)

        _page().wait_until_xpath_visible(_page().BOOK_BUTTON_XPATH.format(scheduled_class_id))
        _page().get_element_book_button(scheduled_class_id).click()
        _page().wait_until_xpath_visible(_page().CONFIRM_BOOK_POPUP_XPATH)
        _page().element_popup_confirm_button.click()
        _page().wait_until_xpath_visible(_page().ERROR_MESSAGE_POPUP_XPATH)
        _page().element_popup_close.click()
    else:
        raise ValueError("No classes searched.")
