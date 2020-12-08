"""
This module is the main entry to setup **ectools**.
you should specify at least *environment* and *partner* before using any module. Example::

  from ectools.config import setup, set_environment, set_partner

  # setup env and partner at the same time
  setup(env='UAT', partner='Mini') # case-insensitive for setting values'

  # just set environment
  set_environment('qa')  # change to QA now

  # just set partner
  set_partner('INDO') # change to Indo partner

If you did not do the setup work, the tool will use default environment and partner.

Valid environments:
 - UAT *(default)*
 - QA
 - Staging
 - Live

Valid partners:
 - Cool *(default)*
 - Mini
 - Cehk
 - Indo
 - Rupe
 - Ecsp

Somethings you might want to control more behaviors for each module, there is a global `config` at here::

  from ectools.config import config

  print(config.domain)  # current domain account environment and partner
  print(config.country_code)  # current country code

  config.browser_type = 'Firefox'  # change internal browser type
  config.default_timeout = 10  # change default timeout

There are more things you can do with *config*, but I suggest you do not change it except you know what will happen.

To get or set logging behavior, you could take the advantage of `get_logger()` methods::

  from ectools.config import get_logger, set_logger

  logger = get_logger()  # get internal logger
  logger.info('hello')

  # control logging level
  import logging
  logger.setLevel(logging.WARN)

  # add handlers
  handler = prepare_my_handler()  # prepare your handler, e.g. log to a file
  logger.addHandler(handler)

-----

"""
from os.path import dirname, join, abspath

from .internal.constants import HTTP_STATUS_OK
from .internal.data_helper import get_partner, get_environment, get_database
from .internal.objects import *
from .utility import no_ssl_requests

config = Configuration()


def setup(env='UAT', partner='Cool'):
    """
    Set environment and partner for this tool.

    :param env: should be one of 'UAT', 'QA', 'Staging', 'Live'
    :param partner: Should be one of 'Cool', 'Mini', 'Indo', 'Cehk', 'Ecsp', 'Rupe', 'Socn'
    """
    set_partner(partner)
    set_environment(env)


def set_environment(env):
    """
    Set environment for this tool.

    :param env: should be one of 'UAT', 'QA', 'Staging', 'Live'
    """
    if 'qa' in env.lower() and config.partner.lower() in ('cehk', 'indo', 'rupe'):
        config.domain = 'hk'
    env = get_environment(env, config.domain)
    config.env = env['name']
    _setup()


def set_partner(partner):
    """
    Set partner for this tool.

    :param partner: Should be one of 'Cool', 'Mini', 'Indo', 'Cehk', 'Ecsp', 'Rupe', 'Socn'
    """
    partner = get_partner(partner)
    config.partner = partner['name']
    config.domain = partner['domain']
    config.country_code = partner['country_code']
    _setup()


def _reset_cache():
    keys_to_reset = ['connection_info']
    for key in keys_to_reset:
        if hasattr(Cache, key):
            delattr(Cache, key)


def _setup():
    _reset_cache()

    config.base_dir = dirname(abspath(__file__))
    config.data_dir = join(config.base_dir, config.data_dir)
    config.database = get_database(config.env, config.domain)
    if 'QA' in config.env and config.partner.lower() in ('cehk', 'indo'):
        config.domain = 'hk'
    env = get_environment(config.env, config.domain)
    config.etown_root = env['etown_url']
    config.etown_root_http = config.etown_root.replace('https', 'http')
    config.oboe_root = env['oboe_url']
    config.axis_root = env['axis_url']


def is_api_available():
    """Check the API is available or not."""
    return no_ssl_requests().get(config.remote_api).status_code == HTTP_STATUS_OK


def is_deploy_to_aws():
    """For now all environment are using AWS authentication."""
    return True


setup()
