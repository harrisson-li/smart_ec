from ectools.config import config
from . import PageBase


class SchoolVipClassBookingPage(PageBase):
    SCHOOL_SELECTOR_XPATH = "//select[@name='schoolId']"
    CLASS_CATEGORY_SELECTOR_XPATH = "//select[@name='classCategoryId']"
    CLASS_DATE_INPUT_XPATH = "//input[@name='classDate']"
    SEARCH_BUTTON_XPATH = "//button[@id='search-submit']"
    STUDENT_NAME_INPUT_XPATH = "//input[@id='input-user-{}']"
    BOOK_BUTTON_XPATH = "//input[@id='input-user-{}']/../../following-sibling::td[@class='nextAction']/button"
    SEARCHED_CLASS_LIST_XPATH = "//table[@class='class-list-table']/tbody/tr"
    NO_CLASS_MESSAGE_XPATH = "//table[@class='class-list-table]/div"
    NO_CLASS_MESSAGE = "classes not found !"

    CONFIRM_BOOK_POPUP_XPATH = "//div[@class='popup-book']"
    POPUP_CLOSE_BUTTON_XPATH = "//button[@class='close']"
    POPUP_CONFIRM_BUTTON_XPATH = "//button[@id='popup-book-confirm-button']"

    def __init__(self, browser, token):
        super(SchoolVipClassBookingPage, self).__init__(browser)
        self.url = "{}/ecplatform/mvc/schoolvip/classbooking?token={}&lng=en".format(config.etown_root, token)

    @property
    def element_school_selector(self):
        return self.get_element(self.SCHOOL_SELECTOR_XPATH)

    @property
    def element_class_category_selector(self):
        return self.get_element(self.CLASS_CATEGORY_SELECTOR_XPATH)

    @property
    def element_class_date_input(self):
        return self.get_element(self.CLASS_DATE_INPUT_XPATH)

    @property
    def element_search_button(self):
        return self.get_element(self.SEARCH_BUTTON_XPATH)

    def element_student_name(self, scheduled_class_id):
        return self.get_element(self.STUDENT_NAME_INPUT_XPATH.format(scheduled_class_id))

    def get_student_name(self, scheduled_class_id):
        return self.element_student_name(scheduled_class_id).text

    def get_element_book_button(self, scheduled_class_id):
        return self.get_element(self.BOOK_BUTTON_XPATH.format(scheduled_class_id))

    @property
    def element_popup_confirm_button(self):
        return self.get_element(self.POPUP_CONFIRM_BUTTON_XPATH)
