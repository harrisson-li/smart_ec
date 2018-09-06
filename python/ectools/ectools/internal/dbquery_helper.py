"""
Helper to query DB from https://xxx.englishtown.com/dbquery/dbquery.aspx,
this page is provided by release team, ping them for more info.
"""

from ectools.config import config, Cache
from ectools.internal.pages.dbquery_page import DbQueryPage
from ectools.utility import get_browser, close_browser, ensure_safe_query

BROWSER_ID = 'dbquery'


def _page():
    browser = getattr(Cache, BROWSER_ID)
    return DbQueryPage(browser, config.env)


def _login_required(func):
    def wrapper(*args, **kwargs):
        try:
            _login()
            return func(*args, **kwargs)
        finally:
            _logout()

    return wrapper


def _login():
    get_browser(browser_id=BROWSER_ID)
    _page().login()


def _logout():
    close_browser(browser_id=BROWSER_ID)


@_login_required
def fetch_one(sql, as_dict=True):
    """Get first record from query."""
    return fetch_all(sql, as_dict)[0]


@_login_required
def fetch_all(sql, as_dict=True):
    """Get all records from query."""
    ensure_safe_query(sql)
    _page().execute_query(sql)
    return _page().get_result(as_dict)


@_login_required
def execute_query(sql):
    """Execute query and return message, most for update,delete or sp."""
    ensure_safe_query(sql)
    _page().update_query_page()
    _page().execute_query(sql)
    return _page().get_message()
