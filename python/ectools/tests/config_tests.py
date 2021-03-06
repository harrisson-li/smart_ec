from assertpy import assert_that

from ectools.config import setup, set_environment, set_partner, config, is_api_available


def test_setup():
    setup('qa', 'MINI')
    assert_that(config.env).is_equal_to('QA')
    assert_that(config.partner).is_equal_to('Mini')


def test_set_env():
    set_environment('Staging')
    assert_that(config.env).is_equal_to('Staging')
    try:
        set_environment('invalid')
    except AssertionError as e:
        assert_that(e.args[0]).contains('No such environment')


def test_set_partner():
    set_partner('cehk')
    assert_that(config.partner).is_equal_to('Cehk')
    assert_that(config.country_code).is_equal_to('hk')

    set_partner('socn')
    assert_that(config.partner).is_equal_to('Socn')
    assert_that(config.country_code).is_equal_to('cn')

    try:
        set_partner('bad')
    except AssertionError as e:
        assert_that(e.args[0]).contains('No such partner')


def test_api_available():
    assert is_api_available()
