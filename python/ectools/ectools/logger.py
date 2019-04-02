import logging

from .internal.objects import Cache, Configuration

cache_logger_attribute_name = 'sys_logger'
config = Configuration


def get_logger(force_sys_logging=False):
    """
    If ptest installed will return ptest reporter, else sys logging.
    :param force_sys_logging: always return sys logging if set to True.
    :return: a logger object.
    """
    if force_sys_logging:
        return get_sys_logger()
    else:
        return get_ptest_logger() or get_sys_logger()


def get_sys_logger():
    if not hasattr(Cache, cache_logger_attribute_name):
        return logging.getLogger(config.name)
    else:
        return getattr(Cache, cache_logger_attribute_name)


def get_ptest_logger():
    try:
        from ptest.plogger import preporter
        return preporter
    except ImportError:
        return None
