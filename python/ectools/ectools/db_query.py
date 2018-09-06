"""
Use this module to query DB for all environments.
"""
from ectools.config import config


def _get_executor():
    if config.env == 'UAT' or (config.env == 'Live' and config.domain == 'CN'):
        import ectools.database_helper as e
        return e
    else:
        import ectools.internal.dbquery_helper as e
        return e


def fetch_one(sql, as_dict=True):
    return _get_executor().fetch_one(sql, as_dict=as_dict)


def fetch_all(sql, as_dict=True):
    return _get_executor().fetch_all(sql, as_dict=as_dict)


def execute_query(sql):
    return _get_executor().execute_query(sql)
