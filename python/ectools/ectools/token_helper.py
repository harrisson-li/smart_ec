"""
This module will help you get the token string from below url::

  http://{env}.englishtown.com/services/oboe2/Areas/ServiceTest/MemberSiteSetting.aspx

The **token** is used for submit score helper only as I known.
The **site_version** is used for clear cache as parameter

------
"""
import re

from ectools.config import config
from ectools.utility import no_ssl_requests

token_page_url = '{}/services/oboe2/Areas/ServiceTest/MemberSiteSetting.aspx'


def get_token_page():
    page_url = token_page_url.format(config.etown_root)
    return no_ssl_requests().get(page_url)


def get_matched_result(result, pattern, match_index, split_by=None):
    for line in result.split(split_by):
        m = re.match(pattern, line)
        if m:
            return m.group(match_index)
    else:
        raise EnvironmentError("Cannot get the matched pattern!")


def get_token():
    if config.env.lower() in ('uat', 'uatcn', 'qa', 'qacn', 'qahk'):
        return ''
    else:
        result = get_token_page()
        pattern = '.*token">(.*)</span>.*'

        try:
            return get_matched_result(result.text, pattern, 1)
        except Exception:
            raise EnvironmentError("Cannot get token!")


def get_site_version():
    if config.env.lower() in ('uat', 'uatcn'):
        return 'development'
    elif config.env.lower() in ('qa', 'qacn', 'qahk'):
        return 'qa'
    else:
        result = get_token_page()
        pattern = '.*siteversion" value="(.*)" />'

        try:
            return get_matched_result(result.text, pattern, 1, '\n')
        except Exception:
            raise EnvironmentError("Cannot get site version!")
