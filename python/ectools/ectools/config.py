"""Where to place global settings"""

import logging
import sys
from os.path import dirname, join, abspath

from .internal.data_helper import get_partner, get_environment, get_database
from .internal.objects import *

config = Configuration()


def setup(env='UAT', partner='Cool'):
    set_partner(partner)
    set_environment(env)


def set_environment(env):
    env = get_environment(env, config.domain)
    config.env = env['name']
    _setup()


def set_partner(partner):
    partner = get_partner(partner)
    config.partner = partner['name']
    config.domain = partner['domain']
    config.country_code = partner['country_code']
    _setup()


def set_logger():
    logger = logging.getLogger(config.name)
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s %(levelname)-7s: %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)
    return logger


def get_logger():
    return logging.getLogger(config.name)


def _setup():
    set_logger()
    config.base_dir = dirname(abspath(__file__))
    config.data_dir = join(config.base_dir, config.data_dir)
    config.database = get_database(config.env, config.domain)
    env = get_environment(config.env, config.domain)
    config.etown_root = env['etown']
    config.oboe_root = env['oboe']


setup()
