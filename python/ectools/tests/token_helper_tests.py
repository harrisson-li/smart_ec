from ectools.config import set_environment
from ectools.logger import get_logger
from ectools.token_helper import get_token, get_site_version


def test_get_token():
    token = get_token()
    get_logger().info("Current token: " + token)
    assert token is not None
    assert len(token) == 32


def test_get_site_version():
    set_environment('uat')
    site_version = get_site_version()
    get_logger().info("Current site version: " + site_version)

    assert site_version == 'development'

    set_environment('qa')
    site_version = get_site_version()
    get_logger().info("Current site version: " + site_version)

    assert site_version == 'qa'

    set_environment('staging')
    site_version = get_site_version()
    get_logger().info("Current site version: " + site_version)

    assert site_version[0].isdigit()

    set_environment('live')
    site_version = get_site_version()
    get_logger().info("Current site version: " + site_version)

    assert site_version[0].isdigit()
