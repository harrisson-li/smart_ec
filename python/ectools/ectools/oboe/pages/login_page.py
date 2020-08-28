from time import sleep

from selenium.webdriver.common.by import By

from ectools.config import *
from ectools.constant import OBOE_USERNAME, OBOE_PASSWORD
from ectools.internal.pages.oboe_page_base import OboePageBase
from ectools.utility import wait_for


class LoginPage(OboePageBase):
    USERNAME_TEXT_ID = "username"
    PASSWORD_TEXT_ID = "password"
    SUBMIT_BUTTON_ID = "oboe-login-btn"
    LOGIN_ERROR_TEXT_ID = "oboe-login-error-message"
    TIPS_TEXT_ID = "oboe-login-tips"

    AWS_LOGIN_USERNAME_XPATH = "//input[@id='i0116']"
    AWS_LOGIN_PASSWORD_XPATH = "//input[@id='i0118']"
    AWS_SUBMIT_BUTTON_XPATH = "//input[@id='idSIButton9']"
    AWS_BACK_BUTTON_XPATH = "//input[@id='idBtn_Back']"

    TEXT_USERNAME = "Username"
    TEXT_PASSWORD = "Password"
    ATTRIBUTE_NAME_PLACEHOLDER = "placeholder"
    TEXT_LOGIN_ERROR = "Sorry, your username and/or password are incorrect.\nPlease try again."
    TEXT_TIPS = "TIPS:\nE.g. for sky.zhong@ef.com, please use sky.zhong as the username above"

    def __init__(self, browser):
        super(LoginPage, self).__init__(browser)
        self.url = config.oboe_root + "Login"

    @property
    def element_aws_username(self):
        return self.wait_until_xpath_visible(self.AWS_LOGIN_USERNAME_XPATH)

    @property
    def element_aws_password(self):
        return self.wait_until_xpath_visible(self.AWS_LOGIN_PASSWORD_XPATH)

    @property
    def element_aws_back(self):
        return self.wait_until_xpath_visible(self.AWS_BACK_BUTTON_XPATH)

    @property
    def element_aws_submit(self):
        return self.wait_until_xpath_visible(self.AWS_SUBMIT_BUTTON_XPATH)

    @property
    def element_username(self):
        return self.get_element_by(By.ID, self.USERNAME_TEXT_ID)

    @property
    def element_username_default_text(self):
        return self.element_username.get_attribute(self.ATTRIBUTE_NAME_PLACEHOLDER)

    @property
    def element_password(self):
        return self.get_element_by(By.ID, self.PASSWORD_TEXT_ID)

    @property
    def element_password_default_text(self):
        return self.element_password.get_attribute(self.ATTRIBUTE_NAME_PLACEHOLDER)

    @property
    def element_submit_button(self):
        return self.get_element_by(By.ID, self.SUBMIT_BUTTON_ID)

    @property
    def element_login_error(self):
        return self.get_element_by(By.ID, self.LOGIN_ERROR_TEXT_ID)

    @property
    def element_tips(self):
        return self.get_element_by(By.ID, self.TIPS_TEXT_ID)

    def login(self, username, password):
        self.element_username.send_keys(username)
        self.element_password.send_keys(password)
        self.element_submit_button.click()

    def wait_for_aws_redirect(self, timeout=30):
        def redirect_done():
            return '/oboe2/' in self.browser.current_url

        wait_for(redirect_done, timeout=timeout)

    def is_direct_login(self):
        try:
            self.wait_for_aws_redirect()
            return True
        except:
            return False

    def login_aws(self, username=OBOE_USERNAME, password=OBOE_PASSWORD):
        # Make case stable cause the login page may load very slowly
        sleep(1)
        # the login step may be skipped, which is control by other team
        # so we first try if it is direct login
        if self.is_xpath_visible(self.AWS_SUBMIT_BUTTON_XPATH):
            # login to microsoft online with username + password
            self.element_aws_username.send_keys(username + '@ef.com')
            self.element_aws_submit.click()
            self.element_aws_password.send_keys(password)
            self.element_aws_submit.click()

            # choose not keep login session to let the dialog always show up
            self.element_aws_back.click()

            # if prompt authentication required dialog, please update internet options as below
            # https://confluence.eflabs.cn/display/SMart/How+to+handle+Authentication+Required+dialog+in+chrome

        self.wait_for_aws_redirect()
        self.wait_for_ready()
