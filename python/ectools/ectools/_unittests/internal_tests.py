from internal.data_helper import *
from config import get_logger

logger = get_logger()


def test_read_data_csv():
    names = ['products', 'partners', 'schools', 'environments']
    for name in names:
        rows = read_csv_as_dict(name)
        assert len(rows) > 0


def test_get_environment():
    result = get_all_environments()
    assert len(result) > 0
    assert get_environment('uat', 'cn')['Name'] == 'UAT'


def test_get_database():
    result = get_all_database()
    assert len(result) > 0
    assert get_database('qa', 'cn')['Server'] == 'USB-ETOWNQADB'


def test_get_partner():
    result = get_all_partners()
    assert len(result) > 0
    assert get_partner('cool')['Domain'] == 'CN'


def test_get_product():
    result = get_all_partners()
    assert len(result) > 0
    assert get_product_by_id(63)['PackageName'] == 'Smart 15 - School'


def test_get_school():
    result = get_all_schools()
    assert len(result) > 0
    assert get_school_by_name('HK_YLC')['DivisionCode'] == 'HKYLC'
