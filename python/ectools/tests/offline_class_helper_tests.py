from ectools.config import set_environment, set_partner
from ectools.offline_class_helper import achieve_minimum_class_taken, HelperConfig
from ectools.service_helper import add_offline_coupon


def test_use_config():
    from ectools.offline_class_helper import HelperConfig

    # for v2 student, the level must completed before class taken by default
    assert HelperConfig.LevelMustComplete == True

    # set it to false if you do not want to check
    HelperConfig.LevelMustComplete = False

    # default setting if not args passed in minimum class taken function
    assert HelperConfig.DefaultMinimumClassTaken == {'f2f_pl': 3, 'workshop_gl': 3, 'apply_or_lc': 1}

    # default shift value for level progress start date / enroll date
    assert HelperConfig.LevelEnrollDateShift == {'days': -30}

    # update it to whatever you want
    HelperConfig.LevelEnrollDateShift = {'days': -60}

    # default date range to pick a class to taken
    assert HelperConfig.ClassTakenSince == {'days': -29}
    assert HelperConfig.ClassTakenUntil == {'days': -1}

    # default PL class type code
    assert HelperConfig.DefaultPLCode == 'CP20'

    # you can change it to PL40
    HelperConfig.DefaultPLCode = 'PL'


def test_class_taken_online():
    set_environment('uat')
    student_id = 23909095
    HelperConfig.LevelMustComplete = False
    achieve_minimum_class_taken(student_id, online_pl=1)


def test_class_taken_offline():
    set_environment('uat')
    set_partner('cool')
    student_id = 24013734
    add_offline_coupon(student_id, 'WS', 1)
    HelperConfig.LevelMustComplete = False
    achieve_minimum_class_taken(student_id, workshop_gl=1)
