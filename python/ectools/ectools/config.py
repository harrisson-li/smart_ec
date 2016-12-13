"""Where to place global settings"""

from internal.objects import *
from assertpy import assert_that
import logging
import sys
from os.path import dirname, join, abspath

config = Configuration()


def setup(env='UAT', partner='Cool'):
    set_environment(env)
    set_partner(partner)
    set_logger()


def set_environment(env):
    Cache.is_setup = True
    config.env = env
    config.base_dir = dirname(abspath(__file__))
    config.data_dir = join(config.base_dir, config.data_dir)


def set_partner(partner):
    config.partner = partner


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


setup()
