from ectools.utility import *

from .objects import Cache

try:
    from ectools.ecdb_helper_v2 import read_table
except ImportError:
    from ectools.ecdb_helper import read_table


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
        Cache.databases = read_data('databases')
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


def get_product_by_id(product, **kwargs):
    product_id = product['id'] if isinstance(product, dict) else product

    if 'is_s18' in kwargs:
        is_s18 = kwargs['is_s18']
    else:
        is_s18 = True

    if 'is_e19' in kwargs:
        is_e19 = kwargs['is_e19']
    else:
        is_e19 = False

    if 'is_smart_plus' in kwargs:
        is_smart_plus = kwargs['is_smart_plus']
    else:
        is_smart_plus = False

    found = [x for x in get_all_products()
             if int(x['id']) == int(product_id)]

    # if more results found, filter by s18, else ignore it
    if len(found) > 1:
        found = [x for x in found if (is_item_has_tag(x, 'S18') == is_s18 and is_item_has_tag(x, 'E19') == is_e19
                                      and is_item_has_tag(x, 'Smart_Plus') == is_smart_plus)]

    assert len(found), "No such product: {}!".format(product_id)
    return found[0]


def get_default_product(partner=None, **kwargs):
    from ectools.config import config
    if not partner:
        partner = config.partner

    if 'is_s18' in kwargs:
        is_s18 = kwargs['is_s18']
    else:
        is_s18 = True

    if 'is_e19' in kwargs:
        is_e19 = kwargs['is_e19']
    else:
        is_e19 = False

    if 'is_smart_plus' in kwargs:
        is_smart_plus = kwargs['is_smart_plus']
    else:
        is_smart_plus = False

    return [x for x in get_all_products()
            if is_item_has_tag(x, 'default')
            and x['partner'].lower() == partner.lower()
            and is_item_has_tag(x, 'S18') == is_s18
            and is_item_has_tag(x, 'E19') == is_e19
            and is_item_has_tag(x, 'Smart_Plus') == is_smart_plus][0]


def is_s18_product(product):
    assert isinstance(product, dict)
    return is_item_has_tag(product, 'S18')


def is_e19_product(product):
    assert isinstance(product, dict)
    return is_item_has_tag(product, 'E19')


def is_smart_plus_product(product):
    assert isinstance(product, dict)
    return is_item_has_tag(product, 'Smart_Plus')


def get_products_has_tag(tag):
    return get_item_has_tag(get_all_products(), tag)


def get_products_by_partner(by_partner=None, **kwargs):
    from ectools.config import config

    if by_partner is None:
        by_partner = config.partner

    if 'is_e10' in kwargs:
        is_e10 = kwargs['is_e10']
    else:
        is_e10 = False

    # TODO: make the "default value" manage in a dedicated place
    if 'is_s18' in kwargs:
        is_s18 = kwargs['is_s18']
    else:
        is_s18 = True

    if 'is_e19' in kwargs:
        is_e19 = kwargs['is_e19']
    else:
        is_e19 = False

    if 'is_smart_plus' in kwargs:
        is_smart_plus = kwargs['is_smart_plus']
    else:
        is_smart_plus = False

    return [x for x in get_all_products() if
            x['partner'].lower() == by_partner.lower()
            and is_item_has_tag(x, 'E10') == is_e10
            and is_item_has_tag(x, 'S18') == is_s18
            and is_item_has_tag(x, 'E19') == is_e19
            and is_item_has_tag(x, 'Smart_Plus') == is_smart_plus]


def get_product_by_product_name(product_name, by_partner=None):
    from ectools.config import config

    if by_partner is None:
        by_partner = config.partner

    return [x for x in get_all_products() if
            x['partner'].lower() == by_partner.lower()
            and x['name'] == product_name][0]


def get_any_product(by_partner=None, **kwargs):
    if 'is_major' in kwargs:
        is_major = kwargs['is_major']
    else:
        is_major = True
    found = [x for x in get_products_by_partner(by_partner, **kwargs)]

    if is_major:
        found = get_item_has_tag(found, 'major')

    return get_random_item(found)


def get_any_e10_product(by_partner=None):
    return get_any_product(by_partner, is_e10=True, is_s18=False, is_e19=False, is_major=False)


def get_any_e19_product(by_partner=None):
    return get_any_product(by_partner, is_e10=False, is_s18=False, is_e19=True, is_major=True)


def get_any_home_product(by_partner=None, is_major=True, **kwargs):
    found = [x for x in get_products_by_partner(by_partner, **kwargs)
             if x['product_type'] == 'Home']

    if is_major:
        return get_item_has_tag(found, 'major')[0]
    else:
        return get_random_item(found)


def get_any_school_product(by_partner=None, is_major=True, **kwargs):
    found = [x for x in get_products_by_partner(by_partner, **kwargs)
             if x['product_type'] == 'School'
             and not is_item_has_tag(x, 'ECLite')]

    if is_major:
        return get_item_has_tag(found, 'major')[0]
    else:
        return get_random_item(found)


def get_any_phoenix_product(by_partner=None, **kwargs):
    if 'is_trial' in kwargs:
        is_trial = kwargs['is_trial']
    else:
        is_trial = False

    found = [x for x in get_products_by_partner(by_partner, **kwargs)
             if is_item_has_tag(x, 'Phoenix')]

    found = [x for x in found if is_item_has_tag(x, 'Trial') == is_trial]
    return get_random_item(found)


def get_smart_plus_pro_product(by_partner=None, **kwargs):
    found = [x for x in get_products_by_partner(by_partner, **kwargs)
             if is_item_has_tag(x, 'Pro')]

    return get_random_item(found)


def get_smart_plus_flex_pl_product(by_partner=None, **kwargs):
    found = [x for x in get_products_by_partner(by_partner, **kwargs)
             if is_item_has_tag(x, 'Flex_PL')]

    return get_random_item(found)


def get_smart_plus_flex_gl_product(by_partner=None, **kwargs):
    found = [x for x in get_products_by_partner(by_partner, **kwargs)
             if is_item_has_tag(x, 'Flex_GL')]

    return get_random_item(found)


def get_smart_plus_flex_vip_product(by_partner=None, **kwargs):
    found = [x for x in get_products_by_partner(by_partner, **kwargs)
             if is_item_has_tag(x, 'Flex_VIP')]

    return get_random_item(found)


def get_eclite_products(partner=None, **kwargs):
    from ectools.config import config
    if partner is None:
        partner = config.partner

    found = [x for x in get_products_by_partner(partner, **kwargs)
             if x['product_type'] == 'School' and is_item_has_tag(x, 'ECLite')]

    return found


def get_any_eclite_product(by_partner=None, **kwargs):
    found = get_eclite_products(by_partner, **kwargs)
    return get_random_item(found)


def get_all_schools(cached=True):
    if cached:
        if not hasattr(Cache, 'schools'):
            Cache.schools = read_data('schools')
        return Cache.schools
    else:
        return read_data('schools')


def get_school_by_name(name, cached=False, ignore_socn=True):
    """name should be str or a dict with name key."""
    name = name if isinstance(name, str) else name['name']
    found = [x for x in get_all_schools(cached=cached) if x['name'] == name]
    assert len(found), "No such school: {}!".format(name)

    # just return if only one match
    if len(found) == 1:
        return found[0]
    else:
        # filter socn school as it might be duplicate with cool / mini school
        if ignore_socn:
            found = [x for x in found if x['partner'] != 'Socn']
        else:  # when check socn student basic info, still need socn partner
            found = [x for x in found if x['partner'] == 'Socn']

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
    """will not return eclite schools."""
    from ectools.config import config

    assert config.partner in ['Cool', 'Mini', 'Socn'], 'Invalid partner for OnlineOC: {}!'.format(config.partner)
    schools = get_schools_has_tag('PC2.0')
    return [s for s in schools if not is_item_has_tag(s, 'ECLite')]


def get_schools_by_partner(partner=None):
    from ectools.config import config
    if partner is None:
        partner = config.partner
    found = [x for x in get_all_schools()
             if x['partner'].lower() == partner.lower()]
    return found


def get_default_school(partner=None):
    return [x for x in get_schools_by_partner(partner)
            if is_item_has_tag(x, 'default')][0]


def is_v2_school(school):
    if not isinstance(school, dict):
        school = get_school_by_name(school, cached=True)

    return is_item_has_tag(school, 'PC2.0')


def is_lite_school(school):
    if not isinstance(school, dict):
        school = get_school_by_name(school, cached=True)

    return is_item_has_tag(school, 'ECLite')


def is_lite_product(product):
    if not isinstance(product, dict):
        product = get_product_by_id(product)

    return is_item_has_tag(product, 'ECLite')


def is_phoenix_product(product):
    if not isinstance(product, dict):
        product = get_product_by_id(product)

    return is_item_has_tag(product, 'Phoenix')


def is_trial_product(product):
    if not isinstance(product, dict):
        product = get_product_by_id(product)

    return is_item_has_tag(product, 'Trial')


def is_e19_product(product):
    if not isinstance(product, dict):
        product = get_product_by_id(product)

    return is_item_has_tag(product, 'E19')


def is_onlineoc_school(school):
    from ectools.config import config

    if config.partner not in ['Cool', 'Mini', 'Socn']:
        return False

    if not isinstance(school, dict):
        school = get_school_by_name(school, cached=True)

    return not is_item_has_tag(school, 'OC-Off')


def is_virtual_school(school):
    if not isinstance(school, dict):
        school = get_school_by_name(school, cached=True)

    return is_item_has_tag(school, 'Virtual')


def _pick_one_school(schools):
    from ectools.config import config
    # only return test center for live
    if config.env == 'Live':
        schools = [x for x in schools if is_item_has_tag(x, 'TestCenter')]

    return get_random_item(schools)


def get_any_v1_school(partner=None):
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


def get_any_phoenix_school(partner=None, is_virtual=True):
    found = [x for x in get_all_normal_v2_schools(partner)
             if is_virtual_school(x) == is_virtual]

    return _pick_one_school(found)


def get_all_levels():
    level_list = ['0A', '0B']
    # noinspection PyTypeChecker
    level_list.extend(range(1, 15))
    return level_list


def get_random_level(min_level=1, max_level=16):
    level_list = get_all_levels()[min_level - 1:max_level - 1]
    return get_random_item(level_list)


def get_all_phoenix_pack():
    if not hasattr(Cache, 'phoenix_pack'):
        Cache.phoenix_pack = read_data('phoenix_pack')
    return Cache.phoenix_pack


def get_phoenix_pack(env_name, partner, pack_name, is_v1_pack=True):
    found = [x for x in get_all_phoenix_pack() if x['name'] == pack_name]
    # env example: All, UAT, UAT+QA
    found = [x for x in found if x['env'] == 'All' or env_name in x['env']]
    # partner example: All, Cool, Cool+Mini
    found = [x for x in found if x['partner'] == 'All' or partner in x['partner']]
    # tag contains v1 or v2
    pack_tag = 'v1' if is_v1_pack else 'v2'
    found = [x for x in found if pack_tag in x['tags']]

    assert len(found), "No such package: {}/{}/{}/{}!".format(env_name, partner, pack_name, pack_tag)
    return found[0]


def get_all_move_on_info():
    if not hasattr(Cache, 'move_on_info'):
        Cache.move_on_info = read_data('move_on_info')
    return Cache.move_on_info


def get_move_on_info(product_id, tag=None):
    found = [x for x in get_all_move_on_info() if x['product_id'] == product_id]

    if tag:
        found = [x for x in found if tag in x['tags']]

    assert len(found), "No such move on info: {}/{}!".format(product_id, tag)
    return found[0]


def get_all_mobile_build_info():
    if not hasattr(Cache, 'mobile_build_info'):
        Cache.mobile_build_info = read_data('mobile_build_info')
    return Cache.mobile_build_info


def get_latest_android_build_info_for_cn():
    found = [x for x in get_all_mobile_build_info() if x['platform'] == 'Android' and 'Juno' in x['tags']]

    found = sorted(found, key=lambda x: x['release_date'], reverse=True)

    assert len(found), "No Android Juno build info found."
    return found[0]


def get_all_online_teachers():
    if not hasattr(Cache, 'online_teachers'):
        Cache.online_teachers = read_data('online_teachers')
    return Cache.online_teachers


def get_random_online_teacher(env_name):
    found = [x for x in get_all_online_teachers() if env_name.lower() in x['env'].lower()]
    assert len(found), "No online teachers in {}!".format(env_name)
    return get_random_item(found)


def get_online_teacher_by_id(teacher_id):
    found = [x for x in get_all_online_teachers() if teacher_id == x['teacher_id']]
    assert len(found), "No online teacher found with teacher_id = {}!".format(teacher_id)
    return found[0]
