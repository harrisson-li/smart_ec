from ectools.config import set_environment
from ectools.internal import troop_service_helper as troop
from ectools.internal.data_helper import *


def test_read_data():
    names = ['products', 'partners', 'schools', 'environments']
    for name in names:
        rows = read_data(name)
        assert len(rows) > 0


def test_get_environment():
    result = get_all_environments()
    assert len(result) > 0
    assert get_environment('uat', 'cn')['name'] == 'UAT'


def test_get_database():
    result = get_all_database()
    assert len(result) > 0
    assert get_database('qa', 'cn')['server'] == 'USB-ETQADB'


def test_get_partner():
    result = get_all_partners()
    assert len(result) > 0
    assert get_partner('cool')['domain'] == 'CN'


def test_get_product():
    result = get_all_partners()
    assert len(result) > 0
    assert get_product_by_id(63)['name'] == 'Smart 15 - School'
    assert get_products_by_partner() is not None
    assert get_products_has_tag('Major') is not None
    assert get_any_product() is not None
    assert get_any_home_product() is not None
    assert get_any_school_product() is not None
    assert get_any_e10_product() is not None


def test_get_school():
    result = get_all_schools()
    assert len(result) > 0
    assert get_school_by_name('HK_YLC')['division_code'] == 'HKYLC'
    assert get_schools_by_partner() is not None
    assert get_any_school() is not None
    assert get_schools_has_tag('TestCenter') is not None
    assert get_any_v2_school() is not None


def test_get_random_level():
    level = get_random_level(min_level=2, max_level=16)
    assert level != get_all_levels()[0]
    level = get_random_level(min_level=1, max_level=2)
    assert level in get_all_levels()[:2]


def test_troop_send_login_request():
    set_environment('qa')
    username, password = 'stest82330', 1
    troop.login(username, password)


def test_troop_get_current_context():
    set_environment('qa')
    username, password = 'stest82330', 1
    troop.login(username, password)
    context = troop.query_current_context(username)
    assert context is not None
    print(context)
    assert context['culturecode']['value'] == 'zh-CN'
    assert context['siteversion']['value'] == 'qa'
    assert context['partnercode']['value'] == 'None'
    assert context['countrycode']['value'] == 'cn'


def test_troop_get_member_site_settings():
    set_environment('qa')
    username, password = 'stest82330', 1

    key = 'e12.enrolled'
    site_area = 'school'
    query_string = 'q=member_site_setting!"{};{}"'.format(site_area, key)

    troop.login(username, password)
    result = troop.query(username, query_string)
    print(result)
    assert result['value'] == 'True'


def test_troop_get_current_user_info():
    set_environment('qa')
    username, password = 'stest82330', 1

    query_string = 'q=user!current'
    troop.login(username, password)
    result = troop.query(username, query_string)
    print(result)
    assert result['lastName'] == 'test'
    assert result['member_id'] == 11262083

    result = troop.query(username, query_string, url_with_context=False)
    print(result)
    assert result['lastName'] == 'test'
    assert result['firstName'] == 's14hz'
    assert result['userName'] == 'stest82330'
    assert result['email'] == 'te636257602331089480@qp1.org'
    assert result['lastName'] == 'test'
    assert result['partnerCode'] == 'Cool'
    assert result['divisionCode'] == 'SSCNBJ5'
