from time import sleep

from assertpy import assert_that
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from ectools.internal.business.enums import Attribute
from ectools.internal.constants import TIMEOUT_SECONDS, TIMEOUT_FOR_ELEMENT_WAITING, TIMEOUT_FOR_ELEMENT_PRESENT, \
    TIMEOUT_FOR_ELEMENT_VISIBLE
from ectools.logger import get_logger
from ectools.utility import detail_on_failure, retry_for_error, convert_to_str, get_random_item


class PageBase(object):
    def __init__(self, browser, url=''):
        assert isinstance(browser, WebDriver)
        self.browser = browser
        self.url = url

    def get(self):
        """Open the page according to self.url"""
        self.get_page(self.url)
        self.wait_for_ready()

    def get_page(self, custom_url):
        """Open a custom page by passing in url."""
        get_logger().debug("Open {}".format(custom_url))
        self.browser.get(custom_url)
        self.wait_for_ready()

    def get_url(self, custom_url):
        """Open a custom page by passing in url."""
        get_logger().debug("Open {}".format(custom_url))
        self.browser.get(custom_url)

    def open_new_window(self):
        self.browser.execute_script("window.open('')")

    def switch_to_new_window(self, new_window_handler=None):
        """
        Switch to a new browser window.
        :param new_window_handler: If not specified will switch another existed window.
        :return: The new window handler.
        """
        if not new_window_handler:
            handlers = self.browser.window_handles

            # only 1 window exist, switch to it
            if len(handlers) == 1:
                new_window_handler = handlers[0]
            else:
                # multiple windows found, pick the first one in list
                current_window_handler = self.browser.current_window_handle

                for handler in self.browser.window_handles:
                    if handler != current_window_handler:
                        new_window_handler = handler
                        break

        self.browser.switch_to.window(new_window_handler)
        get_logger().debug("Switch to: {} ({})".format(self.browser.title, self.browser.current_url))
        return new_window_handler

    def close_current_window(self):
        """Close current browser window."""
        get_logger().debug("Close: {} ({})".format(self.browser.title, self.browser.current_url))
        self.browser.close()

    def refresh(self):
        """Reload current page."""
        self.browser.refresh()

    def wait_for_ready(self):
        """Wait for current page loaded completed."""

        def is_ready(browser):
            return browser.execute_script("return document.readyState") == "complete"

        self.wait_until(is_ready, "Timeout while waiting for {} ready!".format(type(self).__name__))

    def wait(self, timeout=TIMEOUT_SECONDS):
        """Get a WebDriverWait object with specific timeout, default to 60 seconds."""
        return WebDriverWait(driver=self.browser, timeout=timeout)

    def sleep(self, seconds):
        """Shortcut to sleep function."""
        sleep(seconds)

    @detail_on_failure
    def wait_until(self, method, message=None, timeout=TIMEOUT_SECONDS):
        """
        Calls the method provided with the driver as an argument until the \
        return value is not False. Default to 60 seconds.
        """

        return self.wait(timeout).until(method, message)

    @detail_on_failure
    def wait_until_not(self, method, message=None, timeout=TIMEOUT_SECONDS):
        """
        Calls the method provided with the driver as an argument until the \
        return value is False. Default to 60 seconds.
        """

        return self.wait(timeout).until_not(method, message)

    def get_option_selector(self, selector_xpath):
        """Get a Select control by xpath."""
        return self.get_option_selector_by(By.XPATH, selector_xpath)

    @detail_on_failure
    def get_option_selector_by(self, by, by_value):
        """Get a Select control."""
        element = self.get_element_by(by, by_value)
        return Select(element)

    @detail_on_failure
    def wait_for_option_selector_by(self, by, by_value, timeout=TIMEOUT_SECONDS):
        self.wait_until(lambda x: len(self.get_all_option_elements_by(by, by_value)) > 0, timeout=timeout)

    def wait_for_option_selector(self, selector_xpath, timeout=TIMEOUT_SECONDS):
        self.wait_for_option_selector_by(By.XPATH, selector_xpath, timeout=timeout)

    @detail_on_failure
    def get_all_option_elements_by(self, by, by_value):
        """Get all options from a Select control."""
        options = self.get_option_selector_by(by, by_value).options
        return options

    def get_all_option_text(self, selector_xpath):
        """Get all option text from a Select control."""
        options = self.get_all_option_elements(selector_xpath)
        return [o.text for o in options]

    def get_all_option_value(self, selector_xpath):
        """Get all option value from a Select control."""
        options = self.get_all_option_elements(selector_xpath)
        return [o.get_attribute('value') for o in options]

    @detail_on_failure
    def get_all_option_elements(self, selector_xpath):
        """Get all options from a Select control by xpath."""
        return self.get_all_option_elements_by(By.XPATH, selector_xpath)

    @detail_on_failure
    @retry_for_error(error=StaleElementReferenceException)
    def select_option_value_by(self, by, by_locator_value, option_value):
        """Select option by value attribute with locator."""
        self.wait_for_option_selector_by(by, by_locator_value)
        option = self.get_option_selector_by(by, by_locator_value)

        option_value = convert_to_str(option_value)
        option.select_by_value(option_value)

    def select_option_by_value(self, selector_xpath, value):
        """Select option by value attribute."""
        self.select_option_value_by(By.XPATH, selector_xpath, value)

    @detail_on_failure
    @retry_for_error(error=StaleElementReferenceException)
    def select_option_partial_value_by(self, by, by_locator_value, option_value):
        """Select option by value attribute with locator."""
        self.wait_for_option_selector_by(by, by_locator_value)
        option = self.get_option_selector_by(by, by_locator_value)

        option_value = convert_to_str(option_value)
        option.select_by_partial_value(option_value)

    def select_option_by_partial_value(self, selector_xpath, value):
        """Select option by partial value."""
        self.select_option_partial_value_by(By.XPATH, selector_xpath, value)

    @detail_on_failure
    @retry_for_error(error=StaleElementReferenceException)
    def select_option_by_text(self, selector_xpath, text):
        """Select option by visible text."""
        self.wait_for_option_selector(selector_xpath)
        option = self.get_option_selector(selector_xpath)

        text = convert_to_str(text)
        option.select_by_visible_text(text)

    @detail_on_failure
    @retry_for_error(error=StaleElementReferenceException)
    def select_option_by_index(self, selector_xpath, index=0):
        """Select option by index, starts from 0."""
        self.wait_for_option_selector(selector_xpath)
        option = self.get_option_selector(selector_xpath)
        option.select_by_index(index)

    @detail_on_failure
    @retry_for_error(error=StaleElementReferenceException)
    def select_option_randomly(self, selector_xpath, start_index=0):
        """Select option randomly, starts select from start_index to the last one"""
        self.wait_for_option_selector(selector_xpath)
        all_options = self.get_all_option_text(selector_xpath)[start_index:]
        random_option = get_random_item(all_options)
        get_logger().debug("Select random option: {}".format(random_option))
        self.select_option_by_text(selector_xpath, random_option)

    @detail_on_failure
    def first_selected_option(self, selector_xpath):
        self.wait_for_option_selector(selector_xpath)
        return self.get_option_selector(selector_xpath).first_selected_option

    @detail_on_failure
    def get_element_by(self, by, by_value, timeout=TIMEOUT_FOR_ELEMENT_WAITING):
        try:
            element = self.wait(timeout).until(conditions.presence_of_element_located((by, by_value)))
            assert isinstance(element, WebElement)
            return element
        except:
            get_logger().error("Failed to get element by {}: {}".format(by, by_value))
            raise

    @detail_on_failure
    def get_element(self, xpath, timeout=TIMEOUT_FOR_ELEMENT_WAITING):
        return self.get_element_by(By.XPATH, xpath, timeout)

    @detail_on_failure
    def get_elements(self, xpath, timeout=TIMEOUT_FOR_ELEMENT_WAITING):
        try:
            return self.wait(timeout).until(conditions.presence_of_all_elements_located((By.XPATH, xpath)))
        except:
            get_logger().error("Failed to get elements for :{} in {} seconds".format(xpath, timeout))
            raise

    @detail_on_failure
    def get_child_elements(self, parent_xpath_or_element, html_tag=None):
        """
        To get all child elements under specific xpath or element.
        :param parent_xpath_or_element: Parent element or xpath.
        :param html_tag: Specify child tag or else return all children.
        :return: All child elements.
        """
        return self.get_descendant_elements(parent_xpath_or_element, html_tag, search_level='/')

    @detail_on_failure
    def get_descendant_elements(self, parent_xpath_or_element, html_tag=None, search_level="//"):
        """
        To get all descendants under specific xpath or element.
        :param parent_xpath_or_element: Parent element or xpath.
        :param html_tag: Specify child tag or else return all children.
        :param search_level: Level to search element, you should not change it.
        :return: All descent elements.
        """
        by_element = isinstance(parent_xpath_or_element, WebElement)
        target_xpath = parent_xpath_or_element if not by_element else "."
        target_xpath += search_level

        if html_tag is not None:
            target_xpath += html_tag
        else:
            target_xpath += "*"

        if by_element:
            parent = parent_xpath_or_element
        else:
            parent = self.browser

        return parent.find_elements_by_xpath(target_xpath)

    @detail_on_failure
    def get_table_data(self, table_xpath, first_row_as_header=True):
        """
        Gets the html table data, if first_row_as_header will return as dict, else return as list.
        """
        element_rows = self.get_descendant_elements(table_xpath, html_tag='tr')
        result = []

        if first_row_as_header:
            element_first_row = element_rows[0]
            is_th = self.is_xpath_present('{}//tr/th'.format(table_xpath), timeout=1)

            if is_th:
                search_by = './th'
            else:
                search_by = './td'

            columns = [x.text for x in element_first_row.find_elements_by_xpath(search_by)]

            for element_row in element_rows[1:]:
                values = [x.text for x in element_row.find_elements_by_xpath('./td')]
                result.append(dict(zip(columns, values)))
        else:
            for element_row in element_rows:
                values = [x.text for x in element_row.find_elements_by_xpath('./td')]
                result.append(values)

        return result

    @detail_on_failure
    def wait_until_title_is(self, title, timeout=TIMEOUT_SECONDS):
        """Wait for page title match to expected value."""
        return self.wait_until(conditions.title_is(title), timeout=timeout)

    @detail_on_failure
    def wait_until_title_contains(self, text, timeout=TIMEOUT_SECONDS):
        """Wait for page title contains text."""
        return self.wait_until(conditions.title_contains(text), timeout=timeout)

    @detail_on_failure
    def wait_until_element_clickable_by(self, by, by_value, timeout=TIMEOUT_SECONDS):
        """Wait for xpath element clickable."""
        return self.wait_until(conditions.element_to_be_clickable((by, by_value)), timeout=timeout)

    @detail_on_failure
    def wait_until_xpath_clickable(self, xpath, timeout=TIMEOUT_SECONDS):
        """Wait for xpath element clickable."""
        return self.wait_until_element_clickable_by(By.XPATH, xpath, timeout=timeout)

    @detail_on_failure
    def wait_until_xpath_not_clickable(self, xpath, timeout=TIMEOUT_SECONDS):
        """Wait for xpath element not clickable."""
        return self.wait_until_not(conditions.element_to_be_clickable((By.XPATH, xpath)), timeout=timeout)

    @detail_on_failure
    def wait_until_xpath_presence(self, xpath, timeout=TIMEOUT_SECONDS):
        """Wait for xpath element presence in DOM."""
        return self.wait_until(conditions.presence_of_element_located((By.XPATH, xpath)), timeout=timeout)

    @detail_on_failure
    def wait_until_xpath_not_presence(self, xpath, timeout=TIMEOUT_SECONDS):
        """Wait for xpath element not presence in DOM."""
        return self.wait_until_not(conditions.presence_of_element_located((By.XPATH, xpath)), timeout=timeout)

    @detail_on_failure
    def wait_until_xpath_visible(self, xpath, timeout=TIMEOUT_SECONDS):
        """Wait for xpath element is visible on page."""
        return self.wait_until(conditions.visibility_of_element_located((By.XPATH, xpath)), timeout=timeout)

    @detail_on_failure
    def wait_until_xpath_text_present(self, xpath, text, timeout=TIMEOUT_SECONDS):
        """Wait for text present in element find by xpath."""
        return self.wait_until(conditions.text_to_be_present_in_element((By.XPATH, xpath), text), timeout=timeout)

    @detail_on_failure
    def wait_until_xpath_value_present(self, xpath, value, timeout=TIMEOUT_SECONDS):
        """Wait for value attribute present in element find by xpath."""
        return self.wait_until(conditions.text_to_be_present_in_element_value((By.XPATH, xpath), value),
                               timeout=timeout)

    @detail_on_failure
    def wait_until_xpath_to_be_selected(self, xpath, timeout=TIMEOUT_SECONDS):
        """Wait for xpath element is selected."""
        return self.wait_until(conditions.element_located_to_be_selected((By.XPATH, xpath)), timeout=timeout)

    @detail_on_failure
    def wait_until_xpath_invisible(self, xpath, timeout=TIMEOUT_SECONDS):
        """Wait for xpath element is invisible on page."""
        self.wait_until(conditions.invisibility_of_element_located((By.XPATH, xpath)), timeout=timeout)

    @retry_for_error(error=StaleElementReferenceException)
    @detail_on_failure
    def wait_until_element_visible(self, element, timeout=TIMEOUT_SECONDS):
        """Wait for element visible, use xpath method if you want to re-get the element."""
        return self.wait_until(conditions.visibility_of(element), timeout=timeout)

    @detail_on_failure
    def wait_until_element_to_be_selected(self, element, timeout=TIMEOUT_SECONDS):
        """Wait for element is selected, use xpath method if you want to re-get the element."""
        return self.wait_until(conditions.element_to_be_selected(element), timeout=timeout)

    @detail_on_failure
    def wait_until_element_to_be_not_selected(self, element, timeout=TIMEOUT_SECONDS):
        """Wait for element unselected."""
        return self.wait_until(conditions.element_located_selection_state_to_be(element, False), timeout=timeout)

    @detail_on_failure
    def wait_until_alert_is_present(self, timeout=TIMEOUT_SECONDS):
        """Wait and return the alert on page."""
        return self.wait(timeout).until(conditions.alert_is_present())

    def handle_alert(self, accept=True):
        if self.browser.name == 'phantomjs':
            self.js_handle_alert(accept)
        else:
            alert = self.wait_until_alert_is_present()
            if accept:
                alert.accept()
            else:
                alert.dismiss()

    def js_handle_alert(self, accept=True):
        get_logger().warn("Close alert via javascript...")
        self.browser.execute_script("window.original_confirm_function = window.confirm")
        self.browser.execute_script("window.confirm = function(msg) { return %s; }" % str(accept).lower())
        self.browser.execute_script("window.confirm = window.original_confirm_function")

    def close_alert_and_get_its_text(self, accept=True, timeout=TIMEOUT_SECONDS):
        if self.browser.name == 'phantomjs':
            self.js_handle_alert(accept)
            return "no way to get alert text from phantomjs!"
        else:
            alert = self.wait_until_alert_is_present(timeout)
            alert_text = alert.text
            if accept:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text

    def mouse_over(self, web_element):
        self.wait_until_element_visible(web_element)
        ActionChains(self.browser).move_to_element(web_element).perform()

    def is_alert_present(self, timeout=TIMEOUT_FOR_ELEMENT_PRESENT):
        """Determine if alert dialog present."""
        try:
            alert = self.wait_until_alert_is_present(timeout)
            return alert is not None
        except TimeoutException:
            return False

    @detail_on_failure
    def is_option_value_loaded(self, selector_xpath, value, timeout=TIMEOUT_SECONDS):
        """Determine if option value is loaded."""
        self.wait_for_option_selector(selector_xpath, timeout=timeout)
        options = self.get_all_option_elements(selector_xpath)
        return value in [o.get_attribute("value") for o in options]

    @detail_on_failure
    def is_option_text_loaded(self, selector_xpath, value, timeout=TIMEOUT_SECONDS):
        """Determine if option text is loaded."""
        self.wait_for_option_selector(selector_xpath, timeout=timeout)
        options = self.get_all_option_elements(selector_xpath)
        return value in [o.text for o in options]

    @detail_on_failure
    def is_xpath_present(self, xpath, timeout=TIMEOUT_FOR_ELEMENT_PRESENT):
        """Determine if xpath present, default timeout in 10 seconds."""
        try:
            self.wait(timeout).until(conditions.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            get_logger().warn("Timeout while waiting for '{}' in {} seconds.".format(xpath, timeout))
            return False
        except Exception as e:
            get_logger().warn("Error occurred while waiting for '{}': {}".format(xpath, e.args))
            return False

    @detail_on_failure
    def is_xpath_visible(self, xpath, timeout=TIMEOUT_FOR_ELEMENT_VISIBLE):
        """Determine if xpath visible, default timeout in 10 seconds."""
        try:
            self.wait(timeout).until(conditions.visibility_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            get_logger().warn("Timeout while waiting for '{}' in {} seconds.".format(xpath, timeout))
            return False
        except Exception as e:
            get_logger().warn("Error occurred while waiting for '{}': {}".format(xpath, e.args))
            return False

    @detail_on_failure
    def is_xpath_clickable(self, xpath, timeout=TIMEOUT_FOR_ELEMENT_VISIBLE):
        """Determine if xpath clickable, default timeout in 10 seconds."""
        try:
            self.wait(timeout).until(conditions.element_to_be_clickable((By.XPATH, xpath)))
            return True
        except TimeoutException:
            get_logger().warn("Timeout while waiting for '{}' in {} seconds.".format(xpath, timeout))
            return False
        except Exception as e:
            get_logger().warn("Error occurred while waiting for '{}': {}".format(xpath, e.args))
            return False

    @detail_on_failure
    def is_checkbox_checked(self, checkbox_xpath):
        """Determine if the checkbox is checked."""
        return self.get_element(checkbox_xpath).get_attribute(Attribute.CHECKED)

    @detail_on_failure
    def verify_current_page_url(self, page_url=None, exact_match=False):
        """
        Verify browser url contains or equal to current page url.
        If page_url is not specified, will use self.url.
        """

        def ignore_https(url):
            if url.startswith('https'):
                return 'http' + url[5:]
            else:
                return url

        if page_url is None:
            page_url = self.url

        expected_url = ignore_https(page_url)
        actual_url = ignore_https(self.browser.current_url)

        if exact_match:
            assert_that(actual_url).is_equal_to_ignoring_case(expected_url)
        else:
            assert_that(actual_url).contains_ignoring_case(expected_url)

    @detail_on_failure
    def verify_xpath_presence(self, *xpath_items):
        """
        Verify all given xpath items are present.
        Will throw TimeoutException if given xpath not found in default timeout seconds.
        """
        for xpath in xpath_items:
            self.wait_until_xpath_presence(xpath)

    @detail_on_failure
    def verify_xpath_not_presence(self, *xpath_items):
        """
        Verify all given xpath items are not present.
        Will throw TimeoutException if given xpath found in default timeout seconds.
        """
        for xpath in xpath_items:
            self.wait_until_xpath_not_presence(xpath)

    @detail_on_failure
    def verify_elements_visible(self, *elements):
        """
        Verify all given elements are in visible state.
        """
        for element in elements:
            self.wait_until_element_visible(element)

    @detail_on_failure
    def wait_until_text_is_not_empty_on_element(self, element, timeout=TIMEOUT_SECONDS):
        """
        Used for the situation that the text is loaded several seconds later than text_object
        """

        def text_not_empty(x):
            text = element.text.strip()
            return text != ""

        self.wait_until(text_not_empty, timeout=timeout)
        return element.text

    @detail_on_failure
    def wait_until_text_is_not_empty_on_xpath(self, xpath, timeout=TIMEOUT_SECONDS):
        """
        Used for the situation that the text is loaded several seconds later than text_object
        """

        def text_not_empty(x):
            text = self.get_element(xpath).text.strip()
            return text != ""

        self.wait_until(text_not_empty, timeout=timeout)
        return self.get_element(xpath).text

    @staticmethod
    def clear_and_input(element, text):
        element.clear()
        element.send_keys(text)

    @staticmethod
    def is_element_disabled_by_attribute(element, attribute_name):
        return "disabled" in element.get_attribute(attribute_name)

    @detail_on_failure
    def wait_until_value_in_attribute(self, element, attribute, value, timeout=TIMEOUT_SECONDS):
        """
        Wait until the attribute of an element has a given value
        """

        def value_in_attribute(x):
            return value in element.get_attribute(attribute)

        self.wait_until(value_in_attribute, timeout=timeout)
        return element.get_attribute(attribute)
