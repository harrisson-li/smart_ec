import json

import requests

from ectools.config import config
from ectools.internal.objects import Cache

LOGIN_SERVICE_URL = "{}/login/handler.ashx"
TROOP_SERVICE_URL = "{}/services/school/queryproxy?"
DEFAULT_PASSWORD = 1
DEFAULT_HEADER_CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"

# other options
# TROOP_SERVICE_URL = "{}/services/shared/queryproxy?"
# TROOP_SERVICE_URL = "{}/services/api/proxy/queryproxy?"

def _get_default_header():
    return {"Content-Type": DEFAULT_HEADER_CONTENT_TYPE}


def login(username, password=DEFAULT_PASSWORD):
    url = LOGIN_SERVICE_URL.format(config.etown_root)

    parameters = {
        'username': username,
        'password': password,
        'noredirect': '1',
        'plogin': '1'
    }

    headers = _get_default_header()
    response = requests.post(url, data=parameters, headers=headers)

    if response.status_code == 200 and response.text == 'success':
        setattr(Cache, username + '_cookies', response.cookies)
        return response.cookies
    else:
        raise ValueError('Failed to login troop service by {}/{}'.format(username, password))


def query_current_context(username):
    query_string = 'q=context!current'
    context = query(username, query_string, url_with_context=False)['values']
    return context


def _build_context(username):
    if not getattr(Cache, username + '_troop_service_context', None):
        Cache.troop_service_context = query_current_context(username)

    CONTEXT_QUERY_STRING_PATTERN = "c=countrycode=%s|culturecode=%s|partnercode=%s|siteversion=%s"
    context = Cache.troop_service_context
    country_code = context['studentcountrycode']['value']
    culture_code = context['culturecode']['value']
    partner_code = context['partnercode']['value']
    site_version = context['siteversion']['value']

    return CONTEXT_QUERY_STRING_PATTERN % (country_code, culture_code, partner_code, site_version)


def query(username, query_string, url=None, url_with_context=True):
    if not url:
        url = TROOP_SERVICE_URL.format(config.etown_root)

    if url_with_context:
        url += _build_context(username)

    cookies = getattr(Cache, username + '_cookies', None)
    headers = _get_default_header()
    response = requests.post(url, headers=headers, data=query_string, cookies=cookies)

    if response.status_code == 200:
        result = json.loads(response.text)
        if result:
            return result[0]
