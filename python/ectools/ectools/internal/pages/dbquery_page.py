from lxml import etree

from . import PageBase


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

        env = '' if env == 'Live' else env
        page = 'configqa.aspx' if env == 'QA' else 'dbquery.aspx'
        self.url = "https://{}deepblue2.englishtown.com/dbquery/{}".format(env.lower(), page)

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

            if self.is_xpath_present(self.LOGIN_NEXT, timeout=5):
                self.get_element(self.LOGIN_NEXT).click()

        self.wait_until_xpath_visible(self.TEXT_QUERY)

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

        doc = etree.HTML(self.browser.page_source)
        element_rows = doc.xpath('//table')[4].find('tbody').findall('tr')

        # first row is header
        element_header = element_rows.pop(0)
        headers = []
        for e in element_header.findall('td'):
            headers.append(e.text)

        rows_as_list = []
        for element_row in element_rows:
            row = []

            for e in element_row.findall('td'):
                row.append(self.parse_value(e.text))

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
