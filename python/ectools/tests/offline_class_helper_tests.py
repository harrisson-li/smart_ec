def test_use_config():
    from ectools.offline_class_helper import HelperConfig

    # for v2 student, the level must completed before class taken by default
    assert HelperConfig.LevelMustComplete == True

    # set it to false if you do not want to check
    HelperConfig.LevelMustComplete = False

    # default setting if not args passed in for minimum class taken function
    assert HelperConfig.DefaultMinimumClassTaken == {'f2f': 3, 'workshop': 3, 'apply_or_lc': 1}

    # default value for level progress start date / enroll date
    assert HelperConfig.LevelEnrollDateShift == {'days': -30}

    # update it to whatever you want
    HelperConfig.LevelEnrollDateShift = {'days': -60}

    # default date range to pick a class to taken
    assert HelperConfig.ClassTakenSince == {'days': -29}
    assert HelperConfig.ClassTakenUntil == {'days': -1}
