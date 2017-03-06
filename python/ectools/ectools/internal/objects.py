"""Where to place all object models"""


class Base(object):
    def __repr__(self):
        return "%r" % self.__dict__


class Container(Base):
    """Class to contain runtime attributes"""
    pass


Cache = Container()


class Configuration(Base):
    name = 'ectools'
    env = 'UAT'
    partner = 'Cool'
    domain = 'CN'
    country_code = 'cn'
    base_dir = '.'
    data_dir = 'data'
    database = None
    etown_root = ''
    oboe_root = '',
    browser_id = 'internal_browser'
    browser_type = 'Chrome'
    default_timeout = 60
    default_poll_time = 0.5
    default_retry_times = 3
    db_path = 'to_be_set'
