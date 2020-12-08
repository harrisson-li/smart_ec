from ectools.config import set_environment
from ectools.oboe.admin_tools_helper import get_token, get_site_version


def test_get_token():
    set_environment('qacn')
    token = get_token()

    assert token is not None

def test_get_site_version():
    set_environment('staging')
    site_version = get_site_version()

    assert site_version is not None
