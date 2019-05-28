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
import json
import pymssql

from .ecdb_helper import _to_insert_values, _to_query_clause
from .internal.objects import Cache

_connection_info = ('CNS-ETDEVDB', 'TestUser', 'testuserdev', 'TestAutomation')
_connection_info_bak = ('den1.mssql6.gear.host', 'ecdb', 'Fi8808P?4s~A', 'ecdb')


def _connect():
    if not hasattr(Cache, 'ecdb_conn_v2'):
        try:
            Cache.ecdb_conn_v2 = pymssql.connect(*_connection_info, login_timeout=10)
            Cache.ecdb_cur_v2 = Cache.ecdb_conn_v2.cursor()
        except Exception as e:
            # TODO: decouple logger functions from config to remove circular imports to be able to use logger anywhere.
            print("Error connecting CNS-ETDEVDB, fallback to den1.mssql6.gear.host, Error info: {}".format(e.args))
            Cache.ecdb_conn_v2 = pymssql.connect(*_connection_info_bak, login_timeout=10)
            Cache.ecdb_cur_v2 = Cache.ecdb_conn_v2.cursor()
    return Cache.ecdb_conn_v2


def _execute(sql, params=None):
    if params:
        _get_cursor().execute(sql, params)
    else:
        _get_cursor().execute(sql)


def _cleanup():
    if hasattr(Cache, 'ecdb_cur_v2'):
        Cache.ecdb_cur_v2.close()
        del Cache.ecdb_cur_v2

    if hasattr(Cache, 'ecdb_conn_v2'):
        Cache.ecdb_conn_v2.close()
        del Cache.ecdb_conn_v2


def _get_conn():
    """Get the database connection."""
    if hasattr(Cache, 'ecdb_conn_v2') and isinstance(Cache.ecdb_conn_v2, pymssql.Connection):
        return Cache.ecdb_conn_v2


def _get_cursor():
    """Get the database cursor."""
    if hasattr(Cache, 'ecdb_cur_v2') and isinstance(Cache.ecdb_cur_v2, pymssql.Cursor):
        return Cache.ecdb_cur_v2


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

    # only read table with ec_ prefix
    if not table_name.startswith('ec_'):
        table_name = 'ec_' + table_name

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
    columns = ['[{}]'.format(x) for x in list(row_dict.keys())]
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


def is_db_available():
    try:
        read_table('ec_products', row_limit=1)
        return True
    except:
        return False


def get_config_value(name, is_json=False, one_row_only=True, value_only=True):
    """
    get config value for ectools from TestAutomation.dbo.ec_config_value.
    :param name: the config name.
    :param is_json: parse to dict type if config value is json.
    :param one_row_only: just return the first row if multiple rows found.
    :param value_only: just return value, else return full row.
    :return:
    """
    found = search_rows('ec_config_value', {'name': name, 'enabled': 1})
    if found:
        if one_row_only:
            if value_only:
                return json.loads(found[0]['value']) if is_json else found[0]['value']
            else:
                return found[0]
        else:
            if value_only:
                values = [row['value'] for row in found]
                return [json.loads(v) for v in values] if is_json else values
            else:
                return found

    return None
