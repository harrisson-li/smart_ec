from internal.data_helper import *
import logging


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
    assert get_products_by_partner() is not None
    assert get_products_has_tag('Major') is not None
    assert get_any_product() is not None
    assert get_any_home_product() is not None
    assert get_any_school_product() is not None
    assert get_any_e10_product() is not None


def test_get_school():
    result = get_all_schools()
    assert len(result) > 0
    assert get_school_by_name('HK_YLC')['DivisionCode'] == 'HKYLC'
    assert get_schools_by_partner() is not None
    assert get_any_school() is not None
    assert get_schools_has_tag('TestCenter') is not None
    assert get_any_v2_school() is not None
