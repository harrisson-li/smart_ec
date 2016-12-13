import csv
import os

from objects import Cache
from ultility import *


def _filter(target, name, domain):
    return target['Name'].lower() == name.lower() and (
        (target['Domain'].lower() == domain.lower()) or (target['Domain'] == 'all'))


def get_all_environments():
    if not hasattr(Cache, 'environments'):
        Cache.environments = read_csv_as_dict('environments')
    return Cache.environments


def get_environment(env_name, domain):
    found = [x for x in get_all_environments() if _filter(x, env_name, domain)]
    assert len(found), "No such environment: {}!".format(env_name)
    return found[0]


def get_all_database():
    if not hasattr(Cache, 'databases'):
        Cache.databases = read_csv_as_dict('database')
    return Cache.databases


def get_database(env_name, domain):
    found = [x for x in get_all_database() if _filter(x, env_name, domain)]
    assert len(found), "No such database: {}/{}!".format(env_name, domain)
    return found[0]


def get_all_partners():
    if not hasattr(Cache, 'partners'):
        Cache.partners = read_csv_as_dict('partners')
    return Cache.partners


def get_partner(by_name):
    found = [x for x in get_all_partners() if x['Name'].lower() == by_name.lower()]
    assert len(found), "No such partner: {}!".format(by_name)
    return found[0]


def get_all_products():
    if not hasattr(Cache, 'products'):
        Cache.products = read_csv_as_dict('products')
    return Cache.products


def get_product_by_id(id):
    found = [x for x in get_all_products() if x['Id'] == str(id)]
    assert len(found), "No such product: {}!".format(id)
    return found[0]


def get_all_schools():
    if not hasattr(Cache, 'schools'):
        Cache.schools = read_csv_as_dict('schools')
    return Cache.schools


def get_school_by_name(name):
    found = [x for x in get_all_schools() if x['Name'] == name]
    assert len(found), "No such school: {}!".format(name)
    return found[0]
