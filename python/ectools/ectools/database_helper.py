from config import config
from internal.objects import *

try:
    import pyodbc
except ImportError:
    import pypyodbc as pyodbc


def set_connection_string(value=None):
    if not value:
        value = "SERVER={};UID={};PWD={}"
        value = value.format(config.database['server'],
                             config.database['user'],
                             config.database['password'])
        value = "DRIVER={SQL Server};" + value

    Cache.connection_string = value


def get_connection_string():
    if not hasattr(Cache, 'connection_string'):
        set_connection_string()
    else:
        return Cache.connection_string


def _connect():
    if not hasattr(Cache, 'connection'):
        Cache.connection = pyodbc.connect(get_connection_string())
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


def connect_database(func=None):
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


def close_database():
    _cleanup()


@connect_database
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


@connect_database
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


@connect_database
def execute_query(sql, params=None):
    """Execute a sql query and return affected row counts."""
    _execute(sql, params)
    get_cursor().commit()
    return get_cursor().rowcount
