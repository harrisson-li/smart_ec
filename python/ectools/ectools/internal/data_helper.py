from ectools.ecdb_helper import read_table
from ectools.utility import *

from .objects import Cache


def has_tag(tags, tag):
    tag_list = tags.lower().split()
    return tag.lower() in tag_list


def is_item_has_tag(item, tag):
    tags = item.get('tags', '')
    return has_tag(tags, tag)


def get_item_has_tag(items, tag):
    found = [x for x in items if is_item_has_tag(x, tag)]
    if len(found) == 0:
        raise ValueError('Cannot find any item has tag: {}'.format(tag))
    return found


def read_data(table_name):
    rows = read_table(table_name)
    # filter out all items tag by 'ignore'
    return [r for r in rows if not is_item_has_tag(r, 'ignore')]


def _filter(item, name, domain):
    return item['name'].lower() == name.lower() and (
        (item['domain'].lower() == domain.lower()) or (item['domain'] == 'all'))


def get_all_environments():
    if not hasattr(Cache, 'environments'):
        Cache.environments = read_data('environments')
    return Cache.environments


def get_environment(env_name, domain):
    found = [x for x in get_all_environments() if _filter(x, env_name, domain)]
    assert len(found), "No such environment: {}!".format(env_name)
    return found[0]


def get_all_database():
    if not hasattr(Cache, 'databases'):
        Cache.databases = read_data('database')
    return Cache.databases


def get_database(env_name, domain):
    found = [x for x in get_all_database() if _filter(x, env_name, domain)]
    assert len(found), "No such database: {}/{}!".format(env_name, domain)
    return found[0]


def get_all_partners():
    if not hasattr(Cache, 'partners'):
        Cache.partners = read_data('partners')
    return Cache.partners


def get_partner(by_name):
    found = [x for x in get_all_partners() if x['name'].lower() == by_name.lower()]
    assert len(found), "No such partner: {}!".format(by_name)
    return found[0]


def get_all_products():
    if not hasattr(Cache, 'products'):
        Cache.products = read_data('products')
    return Cache.products


def get_product_by_id(product):
    product_id = product['id'] if isinstance(product, dict) else product
    found = [x for x in get_all_products() if int(x['id']) == int(product_id)]
    assert len(found), "No such product: {}!".format(product_id)
    return found[0]


def get_products_has_tag(tag):
    return get_item_has_tag(get_all_products(), tag)


def get_products_by_partner(partner=None, is_e10=False):
    from ectools.config import config
    if partner is None:
        partner = config.partner
    found = [x for x in get_all_products() if
             x['partner'].lower() == partner.lower()
             and is_item_has_tag(x, 'E10') == is_e10]
    return found


def get_any_product(by_partner=None, is_e10=False, is_major=True):
    found = get_products_by_partner(by_partner, is_e10)

    if is_major:
        found = get_item_has_tag(found, 'major')

    return get_random_item(found)


def get_any_e10_product(by_partner=None):
    return get_any_product(by_partner, is_e10=True, is_major=False)


def get_any_home_product(by_partner=None, is_major=True):
    found = [x for x in get_products_by_partner(by_partner) if x['product_type'] == 'Home']

    if is_major:
        return get_item_has_tag(found, 'major')[0]
    else:
        return get_random_item(found)


def get_any_school_product(by_partner=None, is_major=True):
    found = [x for x in get_products_by_partner(by_partner)
             if x['product_type'] == 'School' and not is_item_has_tag(x, 'ECLite')]

    if is_major:
        return get_item_has_tag(found, 'major')[0]
    else:
        return get_random_item(found)


def get_eclite_products(partner=None):
    from ectools.config import config
    if partner is None:
        partner = config.partner

    found = [x for x in get_products_by_partner(partner)
             if x['product_type'] == 'School' and is_item_has_tag(x, 'ECLite')]

    return found


def get_any_eclite_product(by_partner=None):
    found = get_eclite_products(by_partner)
    return get_random_item(found)


def get_all_schools(cached=True):
    if cached:
        if not hasattr(Cache, 'schools'):
            Cache.schools = read_data('schools')
        return Cache.schools
    else:
        return read_table('schools')


def get_school_by_name(name, cached=False):
    """name should be str or a dict with name key."""
    name = name if isinstance(name, str) else name['name']
    found = [x for x in get_all_schools(cached=cached) if x['name'] == name]
    assert len(found), "No such school: {}!".format(name)
    return found[0]


def get_schools_has_tag(tag):
    return get_item_has_tag(get_all_schools(cached=False), tag)


def get_test_centers():
    return get_schools_has_tag('TestCenter')


def get_all_v2_schools():
    return get_schools_has_tag('PC2.0')


def get_eclite_schools():
    return get_schools_has_tag('ECLite')


def get_onlineoc_schools():
    return get_schools_has_tag('OnlineOC')


def get_schools_by_partner(partner=None):
    from ectools.config import config
    if partner is None:
        partner = config.partner
    found = [x for x in get_all_schools()
             if x['partner'].lower() == partner.lower()]
    return found


def is_v2_school(school):
    school = get_school_by_name(school, cached=True)
    return is_item_has_tag(school, 'PC2.0')


def is_lite_school(school):
    school = get_school_by_name(school, cached=True)
    return is_item_has_tag(school, 'ECLite')


def is_lite_product(product):
    prod = get_product_by_id(product)
    return is_item_has_tag(prod, 'ECLite')


def is_onlineoc_school(school):
    school = get_school_by_name(school, cached=True)
    return is_item_has_tag(school, 'OnlineOC')


def _pick_one_school(schools):
    from ectools.config import config
    # only return test center for live
    if config.env == 'Live':
        schools = [x for x in schools if is_item_has_tag(x, 'TestCenter')]

    return get_random_item(schools)


def get_any_school(partner=None):
    """return v1 school."""

    found = [x for x in get_schools_by_partner(partner)
             if not is_v2_school(x)]

    return _pick_one_school(found)


def get_all_normal_v2_schools(partner=None):
    """return v2 school and not include eclite school"""

    found = [x for x in get_schools_by_partner(partner)
             if is_v2_school(x)
             and not is_lite_school(x)]

    return found


def get_any_v2_school(partner=None):
    # not include eclite school
    found = get_all_normal_v2_schools(partner)
    return _pick_one_school(found)


def get_any_eclite_school(partner=None):
    found = [x for x in get_schools_by_partner(partner)
             if is_lite_school(x)]

    return _pick_one_school(found)


def get_any_onlineoc_school(partner=None):
    """return onlineOC school, but not include eclite school"""

    found = [x for x in get_schools_by_partner(partner)
             if is_onlineoc_school(x)
             and not is_lite_school(x)]

    return _pick_one_school(found)


def get_all_levels():
    level_list = ['0A', '0B']
    # noinspection PyTypeChecker
    level_list.extend(range(1, 15))
    return level_list


def get_random_level(min_level=1, max_level=16):
    level_list = get_all_levels()[min_level - 1:max_level - 1]
    return get_random_item(level_list)
