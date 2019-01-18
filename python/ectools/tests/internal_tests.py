from ectools.config import set_environment, set_partner, config
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
    assert get_database('qa', 'cn')['name'] == 'QA'


def test_get_partner():
    result = get_all_partners()
    assert len(result) > 0
    assert get_partner('cool')['domain'] == 'CN'


def test_get_product():
    result = get_all_partners()
    assert len(result) > 0
    assert get_product_by_id(63)['name'] == 'Smart 18 - School'
    assert get_products_by_partner() is not None
    assert get_products_has_tag('Major') is not None
    assert get_any_product() is not None
    assert get_any_home_product() is not None
    assert get_any_school_product() is not None

    set_partner('mini')
    assert get_any_e10_product() is not None
    assert get_any_eclite_product() is not None


def test_get_phoenix_data():
    set_environment('uat')
    set_partner('rupe')

    result = get_any_phoenix_school(is_virtual=True)
    print(result)
    assert 'Virtual' in result['tags']

    result = get_any_phoenix_product()
    print(result)
    assert 'Phoenix' in result['tags']


def test_get_school():
    set_partner('cool')
    assert len(get_all_schools()) > 0
    assert len(get_test_centers()) > 0
    assert len(get_all_v2_schools()) > 0
    assert len(get_eclite_schools()) > 0
    assert len(get_onlineoc_schools()) > 0
    assert len(get_all_normal_v2_schools()) > 0

    assert get_school_by_name('HK_YLC')['division_code'] == 'HKYLC'
    assert get_school_by_name('QA_T1C') is not None
    assert get_schools_has_tag('TestCenter') is not None

    assert get_schools_by_partner() is not None
    assert get_any_v1_school() is not None
    assert get_any_v2_school() is not None
    assert get_any_onlineoc_school() is not None

    assert 'PC2.0' in get_any_v2_school()['tags']

    set_partner('mini')
    assert get_any_eclite_school() is not None
    assert 'ECLite' in get_any_eclite_school()['tags']

    set_environment('live')
    school = get_any_v1_school()
    assert 'TestCenter' in school['tags']

    school = get_any_v2_school()
    assert 'TestCenter' in school['tags']

    school = get_school_by_name('WX_HDP')
    assert school['partner'] == 'Mini'

    school = get_school_by_name('CN_TSC')
    assert school['partner'] == 'Socn'

    school = get_school_by_name('HZ_CXC', ignore_socn=False)
    assert school['partner'] == 'Socn'


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
    assert context['partnercode']['value'] == 'Cool'
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


def test_get_phoenix_pack():
    set_environment('uat')
    set_partner('rupe')
    pack = get_phoenix_pack(config.env, config.partner, 'Center Pack Basic')
    assert 'Starter' in pack['tags']

    set_partner('ecsp')
    pack = get_phoenix_pack(config.env, config.partner, 'Online Pack Basic')
    assert pack['salesforce_id'] == '01t0l000001DmR2AAK'

    pack = get_phoenix_pack(config.env, config.partner, 'Intensive Center Fee')
    assert pack['salesforce_id'] == '01t0l000001DYGdAAO'

    set_partner('rupe')
    pack = get_phoenix_pack(config.env, config.partner, 'Intensive Online Fee')
    assert pack['salesforce_id'] == '01t0l000001DYGeAAO'


def test_get_phoenix_prod():
    set_environment('uat')
    set_partner('socn')
    prod = get_any_phoenix_product()
    assert 'Trial' not in prod['tags']

    for i in range(10):
        prod = get_any_phoenix_product(include_trial=True)
        if 'Trial' in prod['tags']:
            return

    assert False, 'should get trial product once!'
