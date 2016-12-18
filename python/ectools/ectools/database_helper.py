"""
This module provides methods to run sql query and fetch data in database easily, what you need to do is just::

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
  row = fetch_one('select * from oboe.dbo.student where id=? and name=?', (student_id, student_name))
  for i in row:
      print(i)

This module are a simple wrapper on *python dbapi*, you can refer to online resource to learn more.
If you want to do more flexible work on database, you can try::

  set_connection_string('my database connection string')
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

  You cannot use this module to update database in **Staging** or **Live** environment.

-----
"""
from ectools.config import config, get_logger
from .internal.objects import *

try:
    import pyodbc
except ImportError:
    import pypyodbc as pyodbc


def set_connection_string(value=None):
    """
    Set connection string if you want to query to another database.
    By default you do not have to call this method, this module will query in DB according to `ectools.config`.

    :param value: connection string in format:  "DRIVER={SQL Server};SERVER=xxx;UID=xxx;PWD=xxx"
    """
    if not value:
        value = "SERVER={};UID={};PWD={}"
        value = value.format(config.database['server'],
                             config.database['user'],
                             config.database['password'])
        Cache.connection_string = "DRIVER={SQL Server};" + value
    else:
        Cache.connection_string = value


def get_connection_string():
    if not hasattr(Cache, 'connection_string'):
        set_connection_string()

    return Cache.connection_string


def _connect():
    if not hasattr(Cache, 'connection'):
        Cache.connection = pyodbc.connect(get_connection_string())
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


def get_cursor():
    """Get the database cursor."""
    if hasattr(Cache, 'cursor') and isinstance(Cache.cursor, pyodbc.Cursor):
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
