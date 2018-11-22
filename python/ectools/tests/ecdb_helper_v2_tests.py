import ectools.ecdb_helper_v2 as db_helper
from ectools.config import get_logger


def test_fetchone():
    sql = "SELECT * FROM teachers"
    row = db_helper.fetch_one(sql)
    get_logger().info(row)
    assert row is not None


def test_fetchall():
    sql = "SELECT * FROM teachers"
    rows = db_helper.fetch_all(sql)
    assert len(rows) > 3

    rows = db_helper.fetch_all(sql, as_dict=True)
    assert len(rows) > 3


def test_sql_with_parameters():
    sql = "SELECT * FROM teachers WHERE member_id = %s"
    row = db_helper.fetch_one(sql, ('30219936',))
    get_logger().info(row)
    assert row is not None


def test_table_shortcut_functions():
    test_table = 'ec_unit_test'
    db_helper.execute_query('truncate table ' + test_table)

    row = [1, test_table, "t's note"]
    db_helper.add_row(test_table, *row)

    row = db_helper.read_table(test_table, as_dict=False)
    get_logger().info(row)
    assert row[0].id == 1
    assert row[0].note == "t's note"

    row_dict = {'id': 2, 'name': 'bbb', 'note': 'another'}
    db_helper.add_row_as_dict(test_table, row_dict)
    row = db_helper.read_table(test_table)
    get_logger().info(row)
    assert row[1]['note'] == 'another'

    search_dict = {'id': 2, 'name': 'bbb'}
    rows = db_helper.search_rows(test_table, search_dict)
    assert len(rows) == 1
    assert rows[0]['name'] == 'bbb'

    update_dict = {'name': 'aaa', 'note': 'new note'}
    db_helper.update_rows(test_table, search_dict, update_dict)
    row = db_helper.read_table(test_table)
    assert row[1]['note'] == 'new note'

    search_dict = {'id': 2, 'name': 'aaa'}
    db_helper.delete_rows(test_table, search_dict)
    row = db_helper.read_table(test_table)
    assert len(row) == 1


def test_ecdb_v2_available():
    assert db_helper.is_db_available()
