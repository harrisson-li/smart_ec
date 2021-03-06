"""
Use this module to connect ectools db, which will contains tool configurations and test data.

ecdb.db will be hosted on remote server, if due to network issue you cannot reach it, we will
build a local db in your user profile directory.


"""

import collections
import glob
import sqlite3
from os.path import join, dirname, exists, expanduser, abspath

from ectools.utility import read_text, convert_to_str
from .internal.objects import Configuration, Cache

_db_name = 'ec.sqlite'
_remote_db_dir = "//cns-qaauto5/Shared/Automation/"
_local_db_dir = expanduser('~')


def _get_data_dir():
    """Get the real path for ectools/data directory."""
    root = dirname(__file__)
    return join(root, Configuration.data_dir)


def _using_remote_db():
    return exists(_remote_db_dir)


def _get_db_path():
    """First try to use remote shared db, if not able to connect then use local db."""
    if _using_remote_db():
        Configuration.db_path = join(_remote_db_dir, _db_name)
    else:
        Configuration.db_path = join(_local_db_dir, _db_name)

    return Configuration.db_path


def _get_db_schema():
    return [abspath(s) for s in glob.glob(_get_data_dir() + '/*.sql')]


def _build_db():
    """
    1. Build the db if it does not exist on remote server.
    2. Always build local db to ensure it is up to date.
    """
    if getattr(Cache, 'db_has_built', False):
        return

    if not exists(_get_db_path()) or Configuration.db_path == join(_local_db_dir, _db_name):
        conn = sqlite3.connect(Configuration.db_path)
        for schema in _get_db_schema():
            sql = read_text(schema)
            conn.executescript(sql)
        conn.commit()
        conn.close()
        Cache.db_has_built = True


def _connect():
    # _build_db()
    Cache.db_has_built = True
    _get_db_path()
    if not hasattr(Cache, 'ecdb_conn'):
        Cache.ecdb_conn = sqlite3.connect(Configuration.db_path)
        Cache.ecdb_cur = Cache.ecdb_conn.cursor()
    return Cache.ecdb_conn


def _execute(sql, params=None):
    if params:
        get_cursor().execute(sql, params)
    else:
        get_cursor().execute(sql)


def _cleanup():
    if hasattr(Cache, 'ecdb_cur'):
        Cache.ecdb_cur.close()
        del Cache.ecdb_cur

    if hasattr(Cache, 'ecdb_conn'):
        Cache.ecdb_conn.close()
        del Cache.ecdb_conn


def get_conn():
    """Get the database connection."""
    if hasattr(Cache, 'ecdb_conn') and isinstance(Cache.ecdb_conn, sqlite3.Connection):
        return Cache.ecdb_conn


def get_cursor():
    """Get the database cursor."""
    if hasattr(Cache, 'ecdb_cur') and isinstance(Cache.ecdb_cur, sqlite3.Cursor):
        return Cache.ecdb_cur


def connect_database(func=None):
    """Connect to database, can be used as decorator."""
    if func is None:
        return _connect()
    else:
        def wrapper(*args, **kwargs):
            try:
                _connect()
                return func(*args, **kwargs)
            except Exception as e:
                msg = "Please check DB @ {}!".format(Configuration.db_path)
                e.args = e.args + (msg,)
                raise e
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
    row = get_cursor().fetchone()

    if row:
        columns = [column[0] for column in get_cursor().description]
        if as_dict:
            return dict(zip(columns, row))
        else:
            t = collections.namedtuple('row', columns, rename=True)
            return t(*row)


@connect_database
def fetch_all(sql, params=None, as_dict=False):
    """Fetch all rows from a sql query."""
    _execute(sql, params)
    rows = get_cursor().fetchall()
    columns = [column[0] for column in get_cursor().description]
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
    get_conn().commit()
    return get_cursor().rowcount


def read_table(table_name, row_limit=500, order_by_column=None, order_desc=False, as_dict=True):
    """Read all rows from a table."""
    if order_by_column:
        order_statement = 'ORDER BY {}'.format(order_by_column)
        if order_desc:
            order_statement += ' DESC'
    else:
        order_statement = ''

    sql = "SELECT * FROM {} {} LIMIT {}".format(table_name, order_statement, row_limit)
    return fetch_all(sql, as_dict=as_dict)


def create_table(table_name, *columns):
    sql = "CREATE TABLE {} ({})".format(table_name, ','.join(columns))
    return execute_query(sql)


def drop_table(table_name):
    sql = "DROP TABLE IF EXISTS {}".format(table_name)
    return execute_query(sql)


def _escape_value(v):
    if isinstance(v, int):
        return str(v)

    elif v is None:
        return "''"

    else:
        value = convert_to_str(v).replace("'", "''")
        return "'{}'".format(value)


def _to_insert_values(values):
    escaped = [_escape_value(v) for v in values]
    return ','.join(escaped)


def add_row(table_name, *values):
    sql = "INSERT INTO {} VALUES ({})".format(table_name, _to_insert_values(values))
    return execute_query(sql)


def add_row_as_dict(table_name, row_dict):
    columns = list(row_dict.keys())
    values = list(row_dict.values())
    sql = "INSERT INTO {} ({}) VALUES ({})".format(table_name, ','.join(columns), _to_insert_values(values))
    return execute_query(sql)


def _to_query_clause(d, sep='AND'):
    clause = []

    for k, v in d.items():
        text = " [{}]={} ".format(k, _escape_value(v))
        clause.append(text)

    return sep.join(clause)


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
