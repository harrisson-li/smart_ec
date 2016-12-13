import csv
import os
import random

from config import config


def get_csv(csv_name):
    return os.path.join(config.data_dir, csv_name + '.csv')


def read_csv_as_dict(csv_name):
    with open(get_csv(csv_name)) as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def get_random_item(in_seq):
    return random.choice(in_seq)


def has_tag(tags, tag):
    tag_list = tags.lower().split()
    return tag.lower() in tag_list


def get_element_has_tag(elements, tag):
    found = [x for x in elements if has_tag(x['Tags'], tag)]
    if len(found) == 0:
        raise ValueError('Cannot find any element has tag: {}'.format(tag))
    return found


def get_score(min=70, max=100):
    return random.choice(range(min, max + 1))
