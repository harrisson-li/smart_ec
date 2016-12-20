from ectools.utility import *


def test_get_browser():
    browser = get_browser()
    assert browser.name == 'chrome'
    close_browser()
    browser = get_browser(browser_type='Chrome', browser_id='my')
    assert browser.name == 'chrome'
    close_browser(browser_id='my')
