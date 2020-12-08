from ectools.oboe.admin_tools_services import get_token_service


def get_token():
    return get_token_service.get_token()


def get_site_version():
    return get_token_service.get_site_version()
