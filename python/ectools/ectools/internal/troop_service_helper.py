import json

from requests import Session

from ectools.config import config
from ectools.internal.objects import Cache
from ectools.utility import no_ssl_requests

LOGIN_SERVICE_URL = "{}/login/secure.ashx"
TROOP_SERVICE_URL = "{}/services/api/proxy/queryproxy?"
TROOP_COMMAND_URL = "{0}/services/api/ecplatform/command/{1}?"

DEFAULT_HEADER_CONTENT_TYPE = "application/x-www-form-urlencoded; charset=UTF-8"
DEFAULT_PASSWORD = 1


# other options
# TROOP_SERVICE_URL = "{}/services/shared/queryproxy?"
# TROOP_SERVICE_URL = "{}/services/school/queryproxy?"

def _get_default_header():
    return {"Content-Type": DEFAULT_HEADER_CONTENT_TYPE}


def get_request_session(username):
    """get one session  for same username."""
    if not username:
        username = 'temp_user'

    session = getattr(Cache, username + '_session', no_ssl_requests())
    setattr(Cache, username + '_session', session)

    assert isinstance(session, Session)
    return session


def login(username, password=DEFAULT_PASSWORD):
    """Login a username to the session."""
    if getattr(Cache, username + '_login_success', False):
        return

    parameters = {
        'username': username,
        'password': password
    }

    url = LOGIN_SERVICE_URL.format(config.etown_root)
    session = get_request_session(username)
    response = session.post(url, data=parameters, headers=_get_default_header())

    if '"success":true' in response.text:
        setattr(Cache, username + '_login_success', True)
    else:
        raise ValueError('Failed to login troop service by {}/{}'.format(username, password))


def query_current_context(username):
    query_string = 'q=context!current'
    return query(username, query_string, url_with_context=False)['values']


def _build_context(username, use_default_context=True):
    context_id = username + '_troop_service_context'

    # try to get from cache, if not found then query from troop
    if not getattr(Cache, context_id, None):
        setattr(Cache, context_id, query_current_context(username))

    context_values = getattr(Cache, context_id)

    context = {}
    for k in context_values:
        context[k] = context_values[k]['value']

    if use_default_context:
        context['culturecode'] = 'en'
        context['languagecode'] = 'en'

    return 'c=' + '|'.join(['{}={}'.format(k, context[k]) for k in context if context[k] is not None])


def query(username, query_string, url_with_context=True, return_first_item=True, url_query_string=None,
          use_default_context=True):
    url = TROOP_SERVICE_URL.format(config.etown_root)

    if url_with_context:
        url += _build_context(username, use_default_context)

    if url_query_string:
        url += url_query_string

    headers = _get_default_header()
    response = get_request_session(username).post(url, headers=headers, data=query_string)

    if response.status_code == 200:
        result = json.loads(response.text)
        if result:
            return result[0] if return_first_item else result


def troop_command_service(username, url_troop_command, data, url_with_context=True, return_first_item=True,
                          use_default_context=True):
    if url_troop_command is None:
        url = TROOP_COMMAND_URL.format(config.etown_root)
    else:
        url = TROOP_COMMAND_URL.format(config.etown_root, url_troop_command)

    if url_with_context:
        url += _build_context(username, use_default_context)

    headers = {"Content-Type": "application/json"}
    response = get_request_session(username).post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = json.loads(response.text)
        if result:
            return result[0] if return_first_item else result
