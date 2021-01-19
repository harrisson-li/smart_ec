from lxml import etree

from ectools.config import config
from ectools.logger import get_logger
from ectools.oboe.request_helper import get_session, get_request, AdminToolsServices, get_oboe_root, headers
from ectools.oboe.utils import StatusCode


def get_token():
    if config.env.lower() in ('uat', 'uatcn', 'qa', 'qacn', 'qahk'):
        return ''
    else:
        try:
            tech_support_html = get_tech_support_html()
            token = tech_support_html.xpath(u"//span[@id='token']/text()")[0]
        except Exception:
            raise EnvironmentError("Cannot get token from oboe admin tool!")

        get_logger().info("Token of {}: {}".format(config.env, token))
        return token


def get_site_version():
    try:
        tech_support_html = get_tech_support_html()
        site_version = tech_support_html.xpath(u"//input[@id='siteversion']/@value")[0]

        return site_version
    except Exception:
        raise EnvironmentError("Cannot get site version!")


def get_tech_support_html():
    response = get_request(AdminToolsServices.TechSupport, is_response_json=False)

    tech_support_html = etree.HTML(response)

    return tech_support_html
