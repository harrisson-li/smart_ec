import re
import requests
from config import config

token_page_url = '{}/services/oboe2/Areas/ServiceTest/MemberSiteSetting.aspx'


def get_token():
    page_url = token_page_url.format(config.etown_root)
    result = requests.get(page_url)
    pattern = '.*token">(.*)</span>.*'
    for line in result.text.split():
        m = re.match(pattern, line)
        if m:
            return m.group(1)

    else:
        raise Exception("Cannot get token!")
