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


# noinspection PyShadowingBuiltins
def get_product_by_id(id):
    found = [x for x in get_all_products() if int(x['id']) == int(id)]
    assert len(found), "No such product: {}!".format(id)
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
    found = [x for x in get_products_by_partner(by_partner) if x['product_type'] == 'School']

    if is_major:
        return get_item_has_tag(found, 'major')[0]
    else:
        return get_random_item(found)


def get_default_activation_data(product):
    from ectools.config import config
    return {'mainRedemptionQty': 3,
            'freeRedemptionQty': 3,
            'startLevel': '0A',
            'levelQty': 16,
            'securityverified': 'on',
            'includesenroll': 'on',
            'productId': product['id'],
            'mainRedemptionCode': product['main_code'],
            'freeRedemptionCode': product['free_code'],
            'ctr': config.country_code,
            'partner': config.partner.lower()
            }


def get_all_schools():
    if not hasattr(Cache, 'schools'):
        Cache.schools = read_data('schools')
    return Cache.schools


def get_school_by_name(name):
    found = [x for x in get_all_schools() if x['name'] == name]
    assert len(found), "No such school: {}!".format(name)
    return found[0]


def get_schools_has_tag(tag):
    return get_item_has_tag(get_all_schools(), tag)


def get_test_centers():
    return get_schools_has_tag('TestCenter')


def get_all_v2_schools():
    return get_schools_has_tag('PC2.0')


def get_schools_by_partner(partner=None):
    from ectools.config import config
    if partner is None:
        partner = config.partner
    found = [x for x in get_all_schools() if x['partner'].lower() == partner.lower()]
    return found


def get_any_school(by_partner=None):
    found = get_schools_by_partner(by_partner)
    found = [x for x in found if not is_v2_school(x['name'])]
    return get_random_item(found)


def is_v2_school(school_name):
    found = [x for x in get_all_v2_schools() if x['name'] == school_name]
    return len(found) != 0


def get_any_v2_school(partner=None):
    from ectools.config import config
    if partner is None:
        partner = config.partner
    found = [x for x in get_all_v2_schools() if x['partner'].lower() == partner.lower()]
    return get_random_item(found)


def get_all_levels():
    level_list = ['0A', '0B']
    # noinspection PyTypeChecker
    level_list.extend(range(1, 15))
    return level_list


def get_random_level(min_level=1, max_level=16):
    level_list = get_all_levels()[min_level - 1:max_level - 1]
    return get_random_item(level_list)
