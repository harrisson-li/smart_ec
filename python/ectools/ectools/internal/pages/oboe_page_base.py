import time

import requests
from assertpy import assert_that
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from ectools.config import *
from ectools.internal.business.enums import PageResponseStatus
from ectools.internal.constants import TIMEOUT_FOR_ELEMENT_WAITING, NORMAL_ELEMENT_POLLING_TIME
from ectools.internal.pages import PageBase
from ectools.logger import get_logger
from ectools.oboe.utils import get_future_date, get_day_from_date, get_month_from_date
from ectools.utility import get_random_item
from ectools.utility import wait_for


class OboePageBase(PageBase):
    OBOE_USER_IMAGE_XPATH = "//div[contains(@class, 'oboe-user-image')]"
    LOADING_ICON_XPATH = "//*[@id='divLoadingContainer']"
    PARTNER_TEXT_XPATH = "/html/body/div[@class='l-topbar']/div/div[@class='oboe-user-bar']/b[2]"
    PARTNER_LIST_XPATH = "/html/body/div[@class='l-topbar']/div/div[@class='oboe-user-bar']/ul/li[1]/ul/li"
    CHANGE_PARTNER_XPATH = "/html/body/div[@class='l-topbar']/div/div[@class='oboe-user-bar']/ul/li[1]/a"
    PROMPT_MESSAGE_XPATH = "//*[@id='promptMessage']"
    SEARCH_TYPE_XPATH = "//*[@id='SearchType']"
    SEARCH_CONTENT_XPATH = "//*[@id='SearchContent']"
    QUERY_CONTENT_XPATH = '//*[@id="Query_SearchContent"]'
    SEARCH_BUTTON_XPATH = "//*[@id='btnSearch']"
    SELECT_TYPE_DROPBOX_ID = "SearchType"
    SEARCH_CONTEXT_TEXT_ID = "SearchContent"
    SEARCH_DATE_XPATH = '//*[@id="Query_SearchDate"]'
    SEARCH_BUTTON_ID = "btnSearch"
    SEARCH_DATE_PICKER_NEXT_XPATH = "//span[@innertext='Next']"
    SEARCH_DATE_PICKER_PREV_XPATH = "//span[@innertext='Prev']"
    VALUE_USER_NAME_TEXT_OPTION = "UserName"
    VALUE_ELITE_CODE_TEXT_OPTION = "EliteCode"
    TEXT_CHANGE_PARTNER_MENU_LINK = "Change Partner"
    TEXT_LOGOUT_MENU_LINK = "Logout"
    EXPECTED_DAY = ''

    def __init__(self, browser, url=''):
        super(OboePageBase, self).__init__(browser, url)

    @property
    def element_oboe_user_image(self):
        return self.wait_until_xpath_clickable(self.OBOE_USER_IMAGE_XPATH)

    @property
    def element_change_partner_menu(self):
        return self.get_element_by(By.LINK_TEXT, self.TEXT_CHANGE_PARTNER_MENU_LINK)

    @property
    def element_logout_menu(self):
        return self.get_element_by(By.LINK_TEXT, self.TEXT_LOGOUT_MENU_LINK)

    @property
    def element_partner_text(self):
        return self.get_element(self.PARTNER_TEXT_XPATH)

    @property
    def current_partner(self):
        return self.get_element(self.PARTNER_TEXT_XPATH).text

    @property
    def element_change_partner(self):
        return self.get_element(self.CHANGE_PARTNER_XPATH)

    @property
    def element_search_type(self):
        return self.get_element(self.SEARCH_TYPE_XPATH)

    @property
    def element_search_content(self):
        return self.get_element(self.SEARCH_CONTENT_XPATH)

    @property
    def element_search_button(self):
        return self.get_element(self.SEARCH_BUTTON_XPATH)

    @property
    def element_search_date(self):
        return self.get_element(self.SEARCH_DATE_XPATH)

    @property
    def element_search_content_text(self):
        return self.get_element_by(By.ID, self.SEARCH_CONTEXT_TEXT_ID)

    @property
    def element_query_search_content(self):
        return self.get_element(self.QUERY_CONTENT_XPATH)

    @property
    def element_selected_date_link_text(self):
        return self.get_element_by(By.LINK_TEXT, self.EXPECTED_DAY)

    @property
    def element_selected_date_pick_next_button(self):
        return self.get_element(self.SEARCH_DATE_PICKER_NEXT_XPATH)

    @property
    def element_selected_date_pick_prev_button(self):
        return self.get_element(self.SEARCH_DATE_PICKER_PREV_XPATH)

    def logout(self):
        self.element_oboe_user_image.click()
        self.element_logout_menu.click()

    def wait_until_page_response_status(self, url, status_code):
        end_time = time.time() + TIMEOUT_FOR_ELEMENT_WAITING
        while time.time() < end_time:
            response = requests.get(url, verify=False)
            if response.status_code == status_code:
                get_logger().info("Get status code {} for url: {} within {} seconds".format(
                    status_code, url, TIMEOUT_FOR_ELEMENT_WAITING))
                return True
            time.sleep(NORMAL_ELEMENT_POLLING_TIME)
        raise TimeoutException("Can NOT get status code {} for url: {} within {} seconds".format(
            status_code, url, TIMEOUT_FOR_ELEMENT_WAITING))

    def get_table_row_count(self, table_xpath):
        row_xpath = table_xpath + "/tbody/tr"
        return len(self.browser.find_elements_by_xpath(row_xpath))

    def get_table_column_count(self, table_xpath, has_header=True):
        if has_header:
            column_xpath = table_xpath + "/tbody/tr[1]/th"
        else:
            column_xpath = table_xpath + "/tbody/tr[1]/td"
        return len(self.browser.find_elements_by_xpath(column_xpath))

    def get_table_cell_xpath(self, table_xpath, row, column, has_header=True):
        if has_header:
            cell_xpath = table_xpath + "/tbody/tr[{}]/td[{}]".format(row + 1, column)
        else:
            cell_xpath = table_xpath + "/tbody/tr[{}]/td[{}]".format(row, column)
        return cell_xpath

    def get_table_cell_value(self, table_xpath, row, column, has_header=True):
        cell_xpath = self.get_table_cell_xpath(table_xpath, row, column, has_header)
        return self.browser.find_element_by_xpath(cell_xpath).text

    def get_available_week_day_type(self, class_date):
        class_date = time.strptime(class_date, '%Y-%m-%d')
        week_day = time.strftime('%w', class_date)
        if week_day in ['2', '4', '6']:
            return 'Tue/Thu/Sat'
        else:
            return 'Mon/Wed/Fri/Sun'

    def select_available_week_day_type(self, class_date, select_xpath):
        week_day_type = self.get_available_week_day_type(class_date)
        self.select_option_by_text(select_xpath, week_day_type)

    def select_week(self, class_date, select_xpath):
        class_date = time.strptime(class_date, '%Y-%m-%d')
        all_weeks = self.get_all_option_elements(select_xpath)

        for week in all_weeks:
            space_index = week.text.index(' ')
            dash_index = week.text.index('-')
            first_day = time.strptime(week.text[space_index + 1:dash_index], '%m/%d/%Y')
            last_day = time.strptime(week.text[dash_index + 1:], '%m/%d/%Y')
            if first_day <= class_date <= last_day:
                self.select_option_by_text(select_xpath, week.text)
                return week.text

        raise Exception("Cannot find a proper week for the given date {}".format(class_date))

    def wait_for_page_load(self):
        self.wait_until_xpath_invisible(self.LOADING_ICON_XPATH)

    def wait_for_page_load_change_partner(self):
        self.wait_until_xpath_invisible(self.LOADING_ICON_XPATH)
        self.wait_until_xpath_invisible(self.PROMPT_MESSAGE_XPATH)

    def wait_for_sub_dropdown_loaded(self, xpath, sub_xpath, expected_value=None):
        """
        This method is waiting for sub dropdown loaded after above dropdown selected.
        :param expected_value: the given text, if None, will select randomly from dropdown list
        :param xpath: the first dropdown xpath
        :param sub_xpath: the second dropdown xpath
        """
        original_value = self.first_selected_option(xpath).text
        get_logger().info("The first value under dropdown is: {}".format(original_value))

        if expected_value is None:
            all_options = self.get_all_option_elements(xpath)
            random_index = get_random_item(range(len(all_options)))
            expected_value = self.get_all_option_text(xpath)[random_index]

        if expected_value != original_value:
            original_sub_options = self.get_all_option_text(sub_xpath)
            get_logger().info("Original_sub_options are: {}".format(original_sub_options))
            self.select_option_by_text(xpath, expected_value)

            def loaded():
                new_sub_options = self.get_all_option_text(sub_xpath)
                return new_sub_options != original_sub_options

            wait_for(loaded)
            get_logger().info("After select the expected value {}, new_sub_options: {}"
                        .format(expected_value, self.get_all_option_text(sub_xpath)))

    def select_option_delay(self, select_xpath, option_value, tag_name="option"):
        option_xpath = select_xpath + "/{}[contains(text(), '{}')]".format(tag_name, option_value)
        option = self.get_element(option_xpath)
        option.click()
        get_logger().info("Select [{}]".format(option.text))

    def change_partner(self, to_partner=None):
        if not to_partner:
            to_partner = config.partner

        if self.current_partner != to_partner:
            original_partner = self.current_partner
            partner_list_number = len(self.browser.find_elements_by_xpath(self.PARTNER_LIST_XPATH))
            current_url = self.browser.current_url

            self.element_oboe_user_image.click()
            # Because this web element is popped up after clicking the image above
            # So we have to give a fixed time to wait until the it is shown completely
            time.sleep(NORMAL_ELEMENT_POLLING_TIME)
            self.mouse_over(self.element_change_partner)

            for partner_number in range(1, partner_list_number + 1):
                partner_xpath = self.PARTNER_LIST_XPATH + '[{}]/a'.format(partner_number)
                partner_text = self.get_element(partner_xpath).get_attribute('data-partner')

                if partner_text == to_partner:
                    self.wait_until_xpath_clickable(partner_xpath)
                    self.get_element(partner_xpath).click()
                    # The loading icon and prompt message may appear slow, so wait a second
                    time.sleep(NORMAL_ELEMENT_POLLING_TIME)
                    self.wait_for_page_load_change_partner()
                    self.wait_until_page_response_status(current_url, PageResponseStatus.SUCCESS)
                    break

            changed_partner = self.get_element(self.PARTNER_TEXT_XPATH).text
            get_logger().info("The partner is changed from {} to {}".format(original_partner, to_partner))
            assert_that(changed_partner, "Failed to change partner.").is_equal_to(to_partner)

    def search_student_by_username(self, username):
        get_logger().info("Search student by username: {}".format(username))
        self.select_option_value_by(By.ID, self.SELECT_TYPE_DROPBOX_ID, self.VALUE_USER_NAME_TEXT_OPTION)
        self.element_search_content_text.clear()
        self.element_search_content_text.send_keys(username)
        self.element_search_button.click()

    def choose_selected_day_from_date_picker(self, selected_date):
        """
        If selected date is not in the same month with current date,
        need click next or prev button of date picker to selected special day
        for example: today is 2019-12-30, selected_date is 2020-01-01,
        need click next button of date picker to click 01

        And this method only can selected month from [current month-1, current month +1]
        :param selected_date:
        :return:
        """
        today = get_future_date(0)
        current_month = get_month_from_date(today)
        selected_month = get_month_from_date(selected_date)
        selected_day = get_day_from_date(selected_date)
        self.element_search_date.click()

        if current_month != selected_month and today < selected_date:
            self.element_selected_date_pick_next_button.click()
        elif current_month != selected_month and today > selected_date:
            self.element_selected_date_pick_prev_button.click()

        self.EXPECTED_DAY = str(selected_day)
        self.element_selected_date_link_text.click()
        self.element_search_button.click()

    def search_operated_class_by_username_and_date(self, username, selected_date):
        get_logger().info("Search class by username:{0} and date:{1}".format(username, selected_date))
        self.element_query_search_content.clear()
        self.element_query_search_content.send_keys(username)
        self.choose_selected_day_from_date_picker(selected_date)
