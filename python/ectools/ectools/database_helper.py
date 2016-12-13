import pyodbc

from config import config
from internal.objects import *


def _connect():
    if not hasattr(Cache, 'connection'):
        connection_string = "SERVER={};UID={};PWD={}"
        connection_string = connection_string.format(config.database['Server'],
                                                     config.database['User'],
                                                     config.database['Password'])
        Cache.connection = pyodbc.connect("DRIVER={SQL Server};" + connection_string)
        Cache.cursor = Cache.connection.cursor()
    return Cache.connection


def _execute(sql, params=None):
    if params:
        get_cursor().execute(sql, params)
    else:
        get_cursor().execute(sql)


def _cleanup():
    if hasattr(Cache, 'cursor'):
        Cache.cursor.close()
        del Cache.cursor

    if hasattr(Cache, 'connection'):
        Cache.connection.close()
        del Cache.connection


def get_cursor():
    """To get database cursor."""
    if hasattr(Cache, 'cursor') and isinstance(Cache.cursor, pyodbc.Cursor):
        return Cache.cursor


def connect_db(func=None):
    """To connect to database, can be used as decorator."""
    if func is None:
        return _connect()
    else:
        def wrapper(*args, **kwargs):
            try:
                _connect()
                return func(*args, **kwargs)
            finally:
                _cleanup()

        return wrapper


@connect_db
def fetch_one(sql, params=None, as_dict=False):
    """Fetch first row from a sql query."""
    _execute(sql, params)
    row = get_cursor().fetchone()

    if row:
        if as_dict:
            columns = [column[0] for column in get_cursor().description]
            return dict(zip(columns, row))
        else:
            return row


@connect_db
def fetch_all(sql, params=None, as_dict=False):
    """Fetch all rows from a sql query."""
    _execute(sql, params)
    rows = get_cursor().fetchall()

    if as_dict:
        columns = [column[0] for column in get_cursor().description]
        result = []

        for row in rows:
            result.append(dict(zip(columns, row)))

        return result
    else:
        return rows


@connect_db
def execute_query(sql, params=None):
    """Execute a sql query and return affected row counts."""
    _execute(sql, params)
    get_cursor().commit()
    return get_cursor().rowcount
