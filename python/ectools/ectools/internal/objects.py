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
    domain = 'cn'
    base_dir = '.'
    data_dir = 'data'


class Student(Base):
    member_id = None
    username = None
    password = None
    is_activated = False
    product = None
    school = None
    is_e10 = None
    is_v2 = None


class Product(Base):
    def __init__(self):
        self.detail = {}

    id = None
    name = None
    partner = None
    product_type = None
    is_s15 = True
    is_e10 = False


class School(Base):
    partner = None
    city = None
    name = None
    division_code = None
