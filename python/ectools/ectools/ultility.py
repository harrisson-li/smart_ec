import csv
import random
from datetime import datetime, timedelta
from os.path import dirname, join

from internal.objects import Configuration


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


def get_score(min_score=70, max_score=100):
    """Return a random score in range between min_score and max_score."""
    return random.choice(range(min_score, max_score + 1))


def random_date(start, end, fmt=None):
    """
    If no format specified will treat start and end as datetime object.

    Example:
        random_date('2010-1-1', '2012-1-1', '%Y-%m-%d')

        s = datetime.now() + timedelta(days=-29)
        e = datetime.now() + timedelta(days=-1)
        random_date(s, e)
    """

    if format:
        start = datetime.strptime(start, fmt)
        end = datetime.strptime(end, fmt)

    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    return start + timedelta(seconds=random.randrange(int_delta))
