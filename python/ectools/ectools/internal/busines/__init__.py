import logging
from functools import wraps

from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.remote.webdriver import WebDriver

from internal.objects import *

instance = Container()


def initialize(browser=None):
    """Function to initialize business, if no browser given, will start a new one for you."""

    LOGGER.setLevel(logging.WARNING)  # set logger level for selenium

    if browser is None:
        instance.browser = webdriver.Chrome()
    else:
        instance.browser = browser

    assert isinstance(instance.browser, WebDriver)


def browser_required(func):
    """Decorator to initiate ectools business"""

    @wraps(func)
    def wrapper(*args):

        try:
            initialize(browser=None)
            return func(*args)

        finally:
            shutdown()

    return wrapper


def shutdown():
    if hasattr(instance, 'browser'):
        instance.browser.quit()


def get_browser():
    """Function to get browser after initialization."""
    if hasattr(instance, 'browser') and isinstance(instance.browser, WebDriver):
        return instance.browser
    else:
        raise EnvironmentError("You must initialize business at first!")
