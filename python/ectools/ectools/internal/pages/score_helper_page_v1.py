from config import config
from internal.pages import PageBase


class SubmitScoreHelperS15Page(PageBase):
    MEMBER_TEXTBOX_XPATH = "//input[@id='tbMemberId']"
    LOAD_UNIT_PROGRESS_BUTTON_XPATH = "//*[@id='btnLoad']"
    LOAD_ALL_UNIT_PROGRESS_XPATH = "//*[@id='btnLoadLevel']"
    TARGET_UNIT_SELECTOR_XPATH = "//*[@id='toUnits']"
    EXCEPT_ACTIVITY_SELECTOR_XPATH = "(//*[@class='ddlKeepUnfinish'])[1]"
    BATCH_SUBMIT_BUTTON_XPATH = "(//*[@id='result']//input[@type='button'])[1]"
    USERNAME_TEXT_XPATH = "//*[@id='tbUserName']"
    CURRENT_UNIT_SELECTOR_XPATH = "//*[@id='ddlUnits']"
    ENROLL_TO_SELECTED_UNIT_XPATH = "//*[@id='btnEnroll']"
    SCORE_TEXTBOX_XPATH = "(//input[@class='txtBatchScore'])[1]"
    UNIT_PROGRESS_TEXT_XPATH = "//*[@id='form1']/div[3]/h3[2]"
    LOADING_FLAG_TEXT_XPATH = ".//*[@id='loadingFlag']"
    COURSE_NAME_SELECTOR_XPATH = "//select[@id='ddlCourses']"

    def __init__(self, browser, token=''):
        super(SubmitScoreHelperS15Page, self).__init__(browser)
        self.url = "{}/services/school/_tools/progress/SubmitScoreHelper.aspx?newengine=true&token={}".format(
            config.etown_root, token)

    @property
    def element_member_textbox(self):
        return self.get_element(self.MEMBER_TEXTBOX_XPATH)

    @property
    def element_load_unit_progress_button(self):
        return self.get_element(self.LOAD_UNIT_PROGRESS_BUTTON_XPATH)

    @property
    def element_load_all_unit_progress(self):
        return self.get_element(self.LOAD_ALL_UNIT_PROGRESS_XPATH)

    @property
    def element_score_to_unit_textbox(self):
        return self.get_element(self.SCORE_TEXTBOX_XPATH)

    @property
    def element_target_unit_selector(self):
        return self.get_element(self.TARGET_UNIT_SELECTOR_XPATH)

    @property
    def element_except_activity_selector(self):
        return self.get_element(self.EXCEPT_ACTIVITY_SELECTOR_XPATH)

    @property
    def element_batch_submit_all_unit_score_button(self):
        return self.get_element(self.BATCH_SUBMIT_BUTTON_XPATH)

    @property
    def element_username_text(self):
        return self.get_element(self.USERNAME_TEXT_XPATH)

    @property
    def element_enroll_to_selected_unit_button(self):
        return self.get_element(self.ENROLL_TO_SELECTED_UNIT_XPATH)

    @property
    def element_level_test_score_textbox(self):
        return self.get_element(self.SCORE_TEXTBOX_XPATH)

    @property
    def element_level_test_batch_submit_score_button(self):
        return self.get_element(self.BATCH_SUBMIT_BUTTON_XPATH)

    @property
    def element_unit_progress_text(self):
        return self.get_element(self.UNIT_PROGRESS_TEXT_XPATH)

    @property
    def element_loading_flag_text(self):
        return self.get_element(self.LOADING_FLAG_TEXT_XPATH)

    @property
    def element_course_name_selector(self):
        return self.get_element(self.COURSE_NAME_SELECTOR_XPATH)
