import requests
import urllib3

from ectools.config import *
from ectools.constant import OBOE_USERNAME, OBOE_PASSWORD
from .utils import *

headers = {
    "Content-type": "application/x-www-form-urlencoded",
    "Accept": "* / *"
}

# disable https warnings
urllib3.disable_warnings()


def get_oboe_root():
    """Force to https for aws service"""
    if is_deploy_to_aws():
        return config.oboe_root.replace('http:', 'https:')
    else:
        return config.oboe_root


def get_aws_session():
    """We have to login to aws via browser then get its cookies."""

    from ectools.oboe.pages.login_page import LoginPage
    from ectools.utility import get_browser, close_browser
    from requests.cookies import create_cookie

    try:
        browser = get_browser(browser_id='schedule_class', headless=True)  # start a new browser from ectools
        browser.maximize_window()
        page = LoginPage(browser)
        page.get()
        page.login_aws(OBOE_USERNAME, OBOE_PASSWORD)
        page.change_partner()
        session = requests.session()

        for cookie in browser.get_cookies():
            c = create_cookie(cookie['name'], cookie['value'])
            session.cookies.set_cookie(c)

        return session

    finally:
        close_browser(browser_id='schedule_class')


def get_session():
    """Gets a valid oboe service session."""

    if getattr(Cache, 'oboe_service_session', None):
        return Cache.oboe_service_session

    if is_deploy_to_aws():
        session = get_aws_session()

    else:

        dict_data = {
            'username': OBOE_USERNAME,
            'password': OBOE_PASSWORD,
            'submit': 'Log+In'
        }

        session = requests.session()
        response = session.post(get_oboe_root() + "login", dict_data, headers=headers, verify=False)
        assert response.status_code == StatusCode.Success, response.text

    Cache.oboe_service_session = session
    return session


def post_request(relative_url, dict_data=None, json_data=None, is_response_json=True):
    """
    Use the method to post a oboe service request, it will auto login to oboe with valid session.
    """
    if dict_data:
        response = get_session().post(get_oboe_root() + relative_url,
                                      dict_data, headers=headers, verify=False)
    else:
        response = get_session().post(get_oboe_root() + relative_url, data=None, json=json_data,
                                      headers=headers, verify=False)

    assert response.status_code == StatusCode.Success, response.text
    return response.json() if is_response_json else response.text


def get_request(relative_url, is_response_json=True):
    response = get_session().get(get_oboe_root() + relative_url, headers=headers, verify=False)

    assert response.status_code == StatusCode.Success, response.text
    return response.json() if is_response_json else response.text


def is_response_success(response):
    return response[JsonResponse.IsSuccess] == ResponseStatus.Success
