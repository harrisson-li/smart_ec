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
    etown_root = ''  # https default
    etown_root_http = ''
    oboe_root = '',
    browser_id = 'internal_browser'
    browser_type = 'Chrome'
    browser_headless = False
    default_timeout = 60
    default_poll_time = 0.5
    default_retry_times = 3
    db_path = 'to_be_set'
    remote_api = 'http://cns-qaauto5/api/'
    smart_repo = r'\\cns-qaauto5\Shared\git\smart'
    version_file = r"\\cns-etnexus\pypi\ectools\version.txt"
    version_url = 'http://jenkins.englishtown.com:8081/pypi/ectools/version.txt'
    corp_net_checking_url = 'http://opal.ef.com.cn/wiki'
