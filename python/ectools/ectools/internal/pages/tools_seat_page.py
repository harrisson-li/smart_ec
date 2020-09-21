from ectools.config import config
from . import PageBase


class ToolsSeatPage(PageBase):
    STUDENT_ID_INPUT_XPATH = "//input[@id='memberId']"
    OPERATOR_INPUT_XPATH = "//input[@id='operator']"
    SCHOOL_VIP_BOOKING_BUTTON_XPATH = "//button[contains(text(),'SchoolVip Booking')]"
    SCHOOL_VIP_BOOKING_TOKEN_XPATH = "//a[@id='outputSchoolVip']"

    def __init__(self, browser):
        super(ToolsSeatPage, self).__init__(browser)
        self.url = "{}/services/ecsystem/Tools/Seat".format(config.etown_root)

    @property
    def element_student_id_input(self):
        return self.get_element(self.STUDENT_ID_INPUT_XPATH)

    @property
    def element_operator_input(self):
        return self.get_element(self.OPERATOR_INPUT_XPATH)

    @property
    def element_school_vip_booking_button(self):
        return self.get_element(self.SCHOOL_VIP_BOOKING_BUTTON_XPATH)

    @property
    def element_school_vip_booking_token(self):
        return self.get_element(self.SCHOOL_VIP_BOOKING_TOKEN_XPATH)
