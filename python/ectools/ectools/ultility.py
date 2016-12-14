import csv
import random
from internal.objects import Configuration
from os.path import dirname, join


def get_data_dir():
    root = dirname(__file__)
    return join(root, Configuration.data_dir)


def get_csv(csv_name):
    return join(get_data_dir(), csv_name + '.csv')


def read_csv_as_dict(csv_name):
    with open(get_csv(csv_name)) as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def get_random_item(in_seq):
    return random.choice(in_seq)


def has_tag(tags, tag):
    tag_list = tags.lower().split()
    return tag.lower() in tag_list


def is_item_has_tag(item, tag):
    return has_tag(item['tags'], tag)


def get_item_has_tag(items, tag):
    found = [x for x in items if is_item_has_tag(x, tag)]
    if len(found) == 0:
        raise ValueError('Cannot find any item has tag: {}'.format(tag))
    return found


def get_score(min=70, max=100):
    return random.choice(range(min, max + 1))
