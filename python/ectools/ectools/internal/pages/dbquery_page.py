from lxml import etree

from . import PageBase
from ..constants import ELEMENT_TIMEOUT_DEFAULT


class DbQueryPage(PageBase):
    TEXT_QUERY = "//textarea[@id='TxtQuery']"
    BUTTON_EXE = "//input[@id='BtnExecute']"
    RESULT_TABLE = "//table[4]"
    QUERY_ERROR_INFO = "Query Error"
    QUERY_MESSAGE_TEXT = "//*[@id='Form1']/text()"
    LOGIN_NAME = "//input[@id='i0116']"
    LOGIN_PASS = "//input[@id='i0118']"
    LOGIN_NEXT = "//input[@id='idSIButton9']"
    LOGIN_USER = ('qa.testauto@ef.com', 'test@456')

    def __init__(self, browser, env):
        super().__init__(browser)
        assert env != 'UAT', 'DbQuery page not support UAT!'

        self.env = env.lower()
        self.url_base = "https://{}deepblue2.englishtown.com/dbquery/{}"

        e = '' if self.env == 'live' else self.env
        self.url = self.url_base.format(e, 'dbquery.aspx')

    def login(self, username=None, password=None):
        if not username:
            username, password = self.LOGIN_USER

        self.get()
        if self.is_xpath_present(self.LOGIN_NAME):
            self.get_element(self.LOGIN_NAME).send_keys(username)
            self.get_element(self.LOGIN_NEXT).click()

            self.wait_until_xpath_clickable(self.LOGIN_PASS)
            self.get_element(self.LOGIN_PASS).send_keys(password)
            self.get_element(self.LOGIN_NEXT).click()

            if self.is_xpath_present(self.LOGIN_NEXT):
                self.get_element(self.LOGIN_NEXT).click()

        self.wait_until_xpath_visible(self.TEXT_QUERY)

    def update_query_page(self):
        """Update action will use config qa page."""
        if self.env == 'qa':
            url = self.url_base.format(self.env, 'configqa.aspx')
            self.browser.get(url)

    def execute_query(self, query_text):
        self.get_element(self.TEXT_QUERY).send_keys(query_text)
        self.get_element(self.BUTTON_EXE).click()
        self.wait_for_ready()

    def parse_value(self, v):
        """
        parse value in web page in some cases, will make life better.
        '' => None
        'True' => True
        'False' => False
        """
        v = v.strip()

        if v == '':
            return None
        if v == 'True':
            return True
        if v == 'False':
            return False

        return v

    def get_result(self, as_dict=True):
        self.check_query_error()

        # no result in query, return an empty list
        if '-1 rows affected.' in self.browser.page_source:
            return []

        # analyze the table in page source to get result
        doc = etree.HTML(self.browser.page_source)
        element_rows = doc.xpath('//table')[4].find('tbody').findall('tr')

        # first row is header
        element_header = element_rows.pop(0)
        headers = []
        for e in element_header.findall('td'):
            v = etree.tostring(e, encoding='utf8', method='text').decode()
            headers.append(v.strip())  # header might be empty

        rows_as_list = []
        for element_row in element_rows:
            row = []

            for e in element_row.findall('td'):
                v = etree.tostring(e, encoding='utf8', method='text').decode()
                row.append(self.parse_value(v))

            rows_as_list.append(row)

        if as_dict:
            return [dict(zip(headers, r)) for r in rows_as_list]
        else:
            return rows_as_list

    def check_query_error(self):
        if self.QUERY_ERROR_INFO in self.browser.page_source:
            doc = etree.HTML(self.browser.page_source)
            message = [t.strip() for t in doc.xpath(self.QUERY_MESSAGE_TEXT) if t.strip()]
            raise ValueError(self.QUERY_ERROR_INFO + ''.join(message))

    def get_message(self):
        doc = etree.HTML(self.browser.page_source)
        message = [t.strip() for t in doc.xpath(self.QUERY_MESSAGE_TEXT) if t.strip()]
        return ''.join(message)
