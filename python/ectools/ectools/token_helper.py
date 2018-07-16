"""
This module will help you get the token string from below url::

  http://{env}.englishtown.com/services/oboe2/Areas/ServiceTest/MemberSiteSetting.aspx

The **token** is used for submit score helper only as I known.

------
"""
import re

from ectools.config import config
from ectools.utility import no_ssl_requests

token_page_url = '{}/services/oboe2/Areas/ServiceTest/MemberSiteSetting.aspx'


def get_token():
    page_url = token_page_url.format(config.etown_root)
    result = no_ssl_requests().get(page_url)
    pattern = '.*token">(.*)</span>.*'
    for line in result.text.split():
        m = re.match(pattern, line)
        if m:
            return m.group(1)

    else:
        raise EnvironmentError("Cannot get token!")
