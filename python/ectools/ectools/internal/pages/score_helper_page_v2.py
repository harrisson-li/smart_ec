from ectools.config import config

from . import PageBase


class SubmitScoreHelperS15V2Page(PageBase):
    MEMBER_ID_TEXTBOX_XPATH = "//*[@id='txtMemberId']"
    LOAD_BUTTON_XPATH = "//*[@id='btnLoad']"
    COURSE_LIST_SELECTOR_XPATH = "//*[@id='dpCourseList']"
    LEVEL_LIST_SELECTOR_XPATH = "//*[@id='dpLevelList']"
    UNIT_LIST_SELECTOR_XPATH = "//*[@id='dpUntiList']"
    UNIT_SCORE_TEXTBOX_XPATH = "//*[@id='txtUnitScore']"
    ACTIVITY_SKIP_SELECTOR_XPATH = "//*[@id='dpActivitySkip']"
    ENROLL_BUTTON_XPATH = "//*[@id='btnEnroll']"
    UNIT_SCORE_SUBMIT_BUTTON_XPATH = "//*[@id='btnUnitScore']"
    UNIT_INFO_TEXT_XPATH = "//*[@id='lbUnitInfo']"
    MERGED_LESSON_SCORE_TEXTBOX_XPATH = "//*[@id='lessonProgressRepeater_txtLessonScore_%s']"
    MERGED_LESSON_SUBMIT_SCORE_BUTTON_XPATH = "//*[@id='lessonProgressRepeater_btnMergedLesson_%s']"
    MERGER_LESSON_STATUS_TEXT_XPATH = "//*[@id='plLessonProgress']/table[%s]/tbody/tr[1]/td[1]"
    PC_LESSON_SCORE_TEXTBOX_XPATH = "//*[@id='lessonProgressRepeater_txtPCLessonScore_%s']"
    PC_LESSON_SUBMIT_SCORE_BUTTON_XPATH = "//*[@id='lessonProgressRepeater_btnPCLesson_%s']"
    PC_LESSON_STATUS_TEXT_XPATH = "//*[@id='plLessonProgress']/table[%s]/tbody/tr[2]/td[1]"
    MOBILE_LESSON_SCORE_TEXTBOX_XPATH = "//*[@id='lessonProgressRepeater_txtMOBLessonScore_%s']"
    MOBILE_LESSON_SUBMIT_SCORE_BUTTON_XPATH = "//*[@id='lessonProgressRepeater_btnMOBLesson_%s']"
    MOBILE_LESSON_STATUS_TEXT_XPATH = "//*[@id='plLessonProgress']/table[%s]/tbody/tr[2]/td[3]"

    UNIT_ID = "UNIT_ID"
    UNIT_NAME = "NAME"
    UNIT_HAS_PASSED = "HAS_PASSED"
    SCORE = "SCORE"
    STATUS = "STATUS"

    def __init__(self, browser, token=''):
        super(SubmitScoreHelperS15V2Page, self).__init__(browser)
        self.url = "{}/services/api/school/_tools/SubmitScoreHelper.aspx?token={}".format(config.etown_root, token)

    @property
    def element_member_id_textbox(self):
        return self.get_element(self.MEMBER_ID_TEXTBOX_XPATH)

    @property
    def element_load_button(self):
        return self.get_element(self.LOAD_BUTTON_XPATH)

    @property
    def element_course_list_selector(self):
        return self.get_element(self.COURSE_LIST_SELECTOR_XPATH)

    @property
    def element_level_list_selector(self):
        return self.get_element(self.LEVEL_LIST_SELECTOR_XPATH)

    @property
    def element_unit_list_selector(self):
        return self.get_element(self.UNIT_LIST_SELECTOR_XPATH)

    @property
    def element_unit_score_textbox(self):
        return self.get_element(self.UNIT_SCORE_TEXTBOX_XPATH)

    @property
    def element_activity_skip_selector(self):
        return self.get_element(self.ACTIVITY_SKIP_SELECTOR_XPATH)

    @property
    def element_enroll_button(self):
        return self.get_element(self.ENROLL_BUTTON_XPATH)

    @property
    def element_unit_score_submit_button(self):
        return self.get_element(self.UNIT_SCORE_SUBMIT_BUTTON_XPATH)

    @property
    def element_unit_info_text(self):
        return self.get_element(self.UNIT_INFO_TEXT_XPATH)

    def element_merged_lesson_score_textbox(self, lesson_sequence):
        return self.get_element(self.MERGED_LESSON_SCORE_TEXTBOX_XPATH % (lesson_sequence - 1))

    def element_merged_lesson_submit_score_button(self, lesson_sequence):
        return self.get_element(self.MERGED_LESSON_SUBMIT_SCORE_BUTTON_XPATH % (lesson_sequence - 1))

    def element_merged_lesson_status_text(self, lesson_sequence):
        lesson_status_text = self.get_element(
            self.MERGER_LESSON_STATUS_TEXT_XPATH % lesson_sequence).text.strip().split(' ')
        return {self.SCORE: lesson_status_text[-3], self.STATUS: lesson_status_text[-1]}

    def get_merged_lesson(self, lesson_sequence):
        merged_lesson_score_text_box = self.element_merged_lesson_score_textbox(lesson_sequence)
        merged_lesson_submit_score_button = self.element_merged_lesson_submit_score_button(lesson_sequence)
        merged_lesson_status_text = self.element_merged_lesson_status_text(lesson_sequence)

        return merged_lesson_score_text_box, merged_lesson_submit_score_button, merged_lesson_status_text

    def element_pc_lesson_score_textbox(self, lesson_sequence):
        return self.get_element(self.PC_LESSON_SCORE_TEXTBOX_XPATH % (lesson_sequence - 1))

    def element_pc_lesson_submit_score_button(self, lesson_sequence):
        return self.get_element(self.PC_LESSON_SUBMIT_SCORE_BUTTON_XPATH % (lesson_sequence - 1))

    def element_pc_lesson_status_text(self, lesson_sequence):
        return self.get_element(self.PC_LESSON_STATUS_TEXT_XPATH % lesson_sequence)

    def get_pc_lesson(self, lesson_sequence):
        pc_lesson_score_text_box = self.element_pc_lesson_score_textbox(lesson_sequence)
        pc_lesson_submit_score_button = self.element_pc_lesson_submit_score_button(lesson_sequence)
        pc_lesson_status_text = self.element_pc_lesson_status_text(lesson_sequence)

        return pc_lesson_score_text_box, pc_lesson_submit_score_button, pc_lesson_status_text

    def element_mobile_lesson_score_textbox(self, lesson_sequence):
        return self.get_element(self.MOBILE_LESSON_SCORE_TEXTBOX_XPATH % (lesson_sequence - 1))

    def element_mobile_lesson_submit_score_button(self, lesson_sequence):
        return self.get_element(self.MOBILE_LESSON_SUBMIT_SCORE_BUTTON_XPATH % (lesson_sequence - 1))

    def element_mobile_lesson_status_text(self, lesson_sequence):
        return self.get_element(self.MOBILE_LESSON_STATUS_TEXT_XPATH % lesson_sequence)

    def get_mobile_lesson(self, lesson_sequence):
        mobile_lesson_score_text_box = self.element_mobile_lesson_score_textbox(lesson_sequence)
        mobile_lesson_submit_score_button = self.element_mobile_lesson_submit_score_button(lesson_sequence)
        mobile_lesson_status_text = self.element_mobile_lesson_status_text(lesson_sequence)

        return mobile_lesson_score_text_box, mobile_lesson_submit_score_button, mobile_lesson_status_text
