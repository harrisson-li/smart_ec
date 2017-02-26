from os import remove, path

import ectools.ecdb_helper as db_helper
from ectools.config import get_logger


def test_get_db_path():
    db_helper._remote_db_path = "//some/where"
    db_path = db_helper._get_db_path()
    get_logger().info(db_path)
    assert "some" not in db_path


def test_build_db():
    if path.exists(db_helper._get_db_path()):
        remove(db_helper._get_db_path())

    db_helper._remote_db_path = "//some/where"
    db_helper._build_db()


def test_fetchone():
    sql = "select * from partner"
    row = db_helper.fetch_one(sql)
    get_logger().info(row)
    assert row.name == 'Cool'

    row = db_helper.fetch_one(sql, as_dict=True)
    get_logger().info(row)
    assert row['name'] == 'Cool'


def test_fetchall():
    sql = "select * from environment"
    rows = db_helper.fetch_all(sql)
    assert len(rows) > 3
    assert rows[0].name == 'UAT'

    rows = db_helper.fetch_all(sql, as_dict=True)
    assert len(rows) > 3
    assert rows[0]['name'] == 'UAT'


def test_sql_with_parameters():
    sql = "select * from partner where name = ?"
    row = db_helper.fetch_one(sql, ('Cool',))
    get_logger().info(row)
    assert row.domain == 'CN'


def test_read_rows():
    rows = db_helper.read_rows('product')
    assert len(rows) > 10
    assert rows[0]['id'] == 63

    rows = db_helper.read_rows('school', row_limit=3, order_by_column='city', order_desc=True)
    get_logger().info(rows)
    assert rows[0]['city'] == 'XiAn'


def test_create_and_use_table():
    db_helper.drop_table('test')

    columns = ['id', 'name', 'note']
    db_helper.create_table('test', *columns)

    row = [1, 'test', "t's note"]
    db_helper.add_row('test', *row)

    row = db_helper.read_rows('test', as_dict=False)
    get_logger().info(row)
    assert row[0].id == 1
    assert row[0].note == "t's note"

    row_dict = {'id': 2, 'name': 'bbb', 'note': 'another'}
    db_helper.add_row_as_dict('test', row_dict)
    row = db_helper.read_rows('test')
    get_logger().info(row)
    assert row[1]['note'] == 'another'

    search_dict = {'id': 2, 'name': 'bbb'}
    update_dict = {'name': 'aaa', 'note': 'new note'}
    db_helper.update_rows('test', search_dict, update_dict)
    row = db_helper.read_rows('test')
    assert row[1]['note'] == 'new note'

    search_dict = {'id': 2, 'name': 'aaa'}
    db_helper.delete_rows('test', search_dict)
    row = db_helper.read_rows('test')
    assert len(row) == 1
