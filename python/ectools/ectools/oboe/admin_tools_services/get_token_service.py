from ectools.config import config
from ectools.logger import get_logger
from ectools.oboe.request_helper import post_request, AdminToolsServices


def get_token():
    data = {'siteversion': config.env}

    response = post_request(AdminToolsServices.GetToken, data)

    get_logger().info("Token of {}: {}".format(config.env, response['Token']))
    return response['Token']
