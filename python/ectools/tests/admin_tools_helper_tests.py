from ectools.config import set_environment
from ectools.oboe.admin_tools_helper import get_token


def test_get_token():
    set_environment('qacn')
    token = get_token()

    assert token is not None
