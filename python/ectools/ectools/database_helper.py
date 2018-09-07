"""
.. attention::

  You must have **pymssql**<http://pymssql.org/en/stable/> installed on the machine.

This module provides functions to run sql query and fetch data in database easily, here is the example::

  from ectools.database_helper import execute_query, fetch_one, fetch_all

  # get one row from a query
  row = fetch_one('select * from oboe.dbo.student')  # fetch data in current environment
  print(row.Name)  # read data via column name
  print(row[1])  # read data via column index

  row = fetch_one('select * from oboe.dbo.student', as_dict=True)
  print(row['Name'])  # read data as dict

  # get all rows from a query
  rows = fetch_all('select top 10 * from oboe.dbo.student')
  print(len(rows))  # return all rows in the query

  # execute a query, for example update or insert data, or run store procedure
  row_count = execute_query('insert into oboe.dbo.student values(....)')
  assert row_count > 0  # will return affected row counts


The `fetch_one()`, `fetch_all()` and `execute_query()` should be the major methods in this module.
You might want to add query parameters somethings, do it like this::

  student_id, student_name = 13, 'toby'
  row = fetch_one('select * from oboe.dbo.student where id=%s and name=%s', (student_id, student_name))
  for i in row:
      print(i)

This module are a simple wrapper on *python dbapi*, you can refer to online resource to learn more.
If you want to do more flexible work on database, you can try::

  set_connection_info(server, user, password)
  conn = connect_database()  # now you connect to above db
  cursor = get_cursor()  # now you get the database cursor

  # do anything you want by conn and cursor

  close_database()  # close your database

However, I would recommend you use `connect_database` as d decorator to make sure db always be closed::

  @connect_database
  def my_work():
      cursor = get_cursor()
      # do my work with cursor

.. warning::

  Update database in **Staging** or **Live** environment is not supported.

-----
"""
import collections
import pymssql

from ectools.config import config, get_logger
from .internal.objects import *


def set_connection_info(server=None, user=None, password=None, database=None):
    """
    Set connection if you want to query to another database.
    By default you do not have to call this method, this module will query in DB according to `ectools.config`.

    :param server: default to server in current environment.
    :param user: default.
    :param password: default.
    :param database: (Optional) default empty.
    """

    if not server:
        server = config.database['server']

    if not user:
        user = config.database['user']

    if not password:
        password = config.database['password']

    if database is None:
        Cache.connection_info = (server, user, password)
    else:
        Cache.connection_info = (server, user, password, database)


def get_connection_info():
    if not hasattr(Cache, 'connection_info'):
        set_connection_info()

    return Cache.connection_info


def _connect():
    if not hasattr(Cache, 'connection'):
        Cache.connection = pymssql.connect(*get_connection_info(), login_timeout=10)
        Cache.cursor = Cache.connection.cursor()
    return Cache.connection


def _execute(sql, params=None):
    if config.env == 'Live':
        get_logger().warn('Execute query in live: \n{}'.format(sql))

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


def get_conn():
    """Get the database connection."""
    if hasattr(Cache, 'connection') and isinstance(Cache.connection, pymssql.Connection):
        return Cache.connection


def get_cursor():
    """Get the database cursor."""
    if hasattr(Cache, 'cursor') and isinstance(Cache.cursor, pymssql.Cursor):
        return Cache.cursor


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


def able_to_connect_db():
    """Check if able to connect to db or not."""
    try:
        fetch_one('SELECT TOP 1 Student_id FROM Oboe.dbo.Student')
        return True
    except pymssql.OperationalError:
        get_logger().warning('Failed to connect to DB.')
        return False


@connect_database
def fetch_one(sql, params=None, as_dict=False):
    """Fetch first row from a sql query."""
    _execute(sql, params)
    result = fetch_all(sql, params, as_dict)
    return result[0] if len(result) else None


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
