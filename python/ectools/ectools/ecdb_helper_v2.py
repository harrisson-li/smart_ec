"""
This module is a shortcut to query db: CNS-ETDEVDB / TestAutomation

Due to performance and stability reason, we will use this DB as a backup for test data.
For long term, we might retire sqlite. The usage for this module is similar as ecdb_module.

Major functions::

  fetch_one()  # query one row of data
  fetch_all()  # query all rows of data

  # shortcut methods
  read_table()
  add_row()    # by list data type
  add_row_as_dict() # by dict data type
  search_row()
  update_rows()
  delete_rows()

"""

import collections
import pymssql

from .ecdb_helper import _to_insert_values, _to_query_clause
from .internal.objects import Cache

_connection_info = ('CNS-ETDEVDB', 'TestUser', 'testuserdev', 'TestAutomation')


def _connect():
    if not hasattr(Cache, 'ecdb_v2_conn'):
        Cache.ecdb_v2_conn = pymssql.connect(*_connection_info, login_timeout=10)
        Cache.ecdb_v2_cur = Cache.ecdb_v2_conn.cursor()
    return Cache.ecdb_v2_conn


def _execute(sql, params=None):
    if params:
        _get_cursor().execute(sql, params)
    else:
        _get_cursor().execute(sql)


def _cleanup():
    if hasattr(Cache, 'ecdb_v2_cur'):
        Cache.ecdb_v2_cur.close()
        del Cache.ecdb_v2_cur

    if hasattr(Cache, 'ecdb_v2_conn'):
        Cache.ecdb_v2_conn.close()
        del Cache.ecdb_v2_conn


def _get_conn():
    """Get the database connection."""
    if hasattr(Cache, 'ecdb_v2_conn') and isinstance(Cache.ecdb_v2_conn, pymssql.Connection):
        return Cache.ecdb_v2_conn


def _get_cursor():
    """Get the database cursor."""
    if hasattr(Cache, 'ecdb_v2_cur') and isinstance(Cache.ecdb_v2_cur, pymssql.Cursor):
        return Cache.ecdb_v2_cur


def connect_database(func=None):
    """Connect to database, can be used as decorator."""
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
    """Close database and release resource."""
    _cleanup()


@connect_database
def fetch_one(sql, params=None, as_dict=False):
    """Fetch first row from a sql query."""
    _execute(sql, params)
    row = _get_cursor().fetchone()

    if row:
        columns = [column[0] for column in _get_cursor().description]
        if as_dict:
            return dict(zip(columns, row))
        else:
            t = collections.namedtuple('row', columns, rename=True)
            return t(*row)


@connect_database
def fetch_all(sql, params=None, as_dict=False):
    """Fetch all rows from a sql query."""
    _execute(sql, params)
    rows = _get_cursor().fetchall()
    columns = [column[0] for column in _get_cursor().description]
    result = []

    for row in rows:

        if as_dict:
            result.append(dict(zip(columns, row)))
        else:
            t = collections.namedtuple('row', columns, rename=True)
            result.append(t(*row))

    return result


@connect_database
def execute_query(sql, params=None):
    """Execute a sql query and return affected row counts."""
    _execute(sql, params)
    _get_conn().commit()
    return _get_cursor().rowcount


def read_table(table_name, row_limit=500, order_by_column=None, order_desc=False, as_dict=True):
    """Read all rows from a table."""
    if order_by_column:
        order_statement = 'ORDER BY {}'.format(order_by_column)
        if order_desc:
            order_statement += ' DESC'
    else:
        order_statement = ''

    sql = "SELECT TOP {} * FROM {} {}".format(row_limit, table_name, order_statement)
    return fetch_all(sql, as_dict=as_dict)


def add_row(table_name, *values):
    sql = "INSERT INTO {} VALUES ({})".format(table_name, _to_insert_values(values))
    return execute_query(sql)


def add_row_as_dict(table_name, row_dict):
    columns = list(row_dict.keys())
    values = list(row_dict.values())
    sql = "INSERT INTO {} ({}) VALUES ({})".format(table_name, ','.join(columns), _to_insert_values(values))
    return execute_query(sql)


def search_rows(table_name, search_dict):
    sql = "SELECT * FROM {} WHERE {}".format(table_name, _to_query_clause(search_dict))
    return fetch_all(sql, as_dict=True)


def update_rows(table_name, search_dict, update_dict):
    sql = "UPDATE {} set {} WHERE {}".format(table_name,
                                             _to_query_clause(update_dict, ','),
                                             _to_query_clause(search_dict))
    execute_query(sql)


def delete_rows(table_name, search_dict):
    sql = "DELETE FROM {} WHERE {}".format(table_name, _to_query_clause(search_dict))
    return execute_query(sql)
