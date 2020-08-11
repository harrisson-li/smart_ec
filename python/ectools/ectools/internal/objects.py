"""Where to place all object models"""
from os.path import join


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
    axis_root = ''
    browser_id = 'internal_browser'
    browser_type = 'Chrome'
    browser_headless = True
    default_timeout = 60
    default_poll_time = 0.5
    default_retry_times = 3
    db_path = 'to_be_set'
    remote_api = 'http://cnshhq-w0633/api/'
    smart_repo = r'\\cnshhq-w0633\Shared\git\smart'
    version_file = join('/opt', 'ectools_packages', 'pypi', 'ectools', 'version.txt')
    version_url = 'http://10.179.237.165:8081/pypi/ectools/version.txt'
