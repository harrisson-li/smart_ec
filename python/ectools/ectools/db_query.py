"""
Use this module to query DB for all environments.
"""
from ectools.config import config
from ectools.logger import get_logger


def _get_executor():
    if config.env == 'UAT' or config.domain == 'CN':
        import ectools.database_helper as e
        return e
    else:
        import ectools.internal.dbquery_helper as e
        return e


def fetch_one(sql, as_dict=True):
    get_logger().debug('SQL: {}'.format(sql))
    return _get_executor().fetch_one(sql, as_dict=as_dict)


def fetch_all(sql, as_dict=True):
    get_logger().debug('SQL: {}'.format(sql))
    return _get_executor().fetch_all(sql, as_dict=as_dict)


def execute_query(sql):
    get_logger().debug('SQL: {}'.format(sql))
    return _get_executor().execute_query(sql)
