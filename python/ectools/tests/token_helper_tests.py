from ectools.config import get_logger
from ectools.token_helper import get_token


def test_get_token():
    token = get_token()
    get_logger().info("Current token: %s", token)
    assert token is not None
    assert len(token) == 32
