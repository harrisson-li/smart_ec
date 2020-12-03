from ectools.config import config
from ectools.logger import get_logger
from ectools.oboe.request_helper import post_request, AdminToolsServices


def get_token():
    if config.env.lower() in ('uat', 'uatcn', 'qa', 'qacn', 'qahk'):
        return ''
    else:
        data = {'siteversion': config.env}

        try:
            response = post_request(AdminToolsServices.GetToken, data)
        except Exception:
            raise EnvironmentError("Cannot get token from oboe admin tool!")

        get_logger().info("Token of {}: {}".format(config.env, response['Token']))
        return response['Token']
