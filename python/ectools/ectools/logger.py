import logging
import sys

from ectools.internal.objects import Configuration as Config


def _set_logger():
    logger = logging.getLogger(Config.name)
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s %(levelname)-7s: %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)


def get_logger(force_sys_logging=False):
    """
    If ptest installed will return ptest reporter, else sys logging.
    :param force_sys_logging: always return sys logging if set to True.
    :return: a logger object.
    """
    if force_sys_logging:
        return logging.getLogger(Config.name)
    else:
        return get_ptest_logger() or logging.getLogger(Config.name)


def get_ptest_logger():
    try:
        from ptest.plogger import preporter
        return preporter
    except ImportError:
        return None


_set_logger()
