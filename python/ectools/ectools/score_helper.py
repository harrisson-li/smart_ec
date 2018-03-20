"""
This module help you submit score to do unit move on or level move on testing.
It will check whether the student is v2 or not, then use correct score helper version::

  from ectools.score_helper import *

  student_id = 123456

  # (recommended) call by with statement, it will help you manage browser
  with submit_score_helper(student_id)
      submit_current_unit(score=87,skip_activity=1)  # unit move on test
      pass_six_units_and_level_test(score=95)

  # (not recommended) load student then do whatever you want
  load_student(student_id)
  submit_current_unit(score=87,skip_activity=1)

  pass_six_units(score=95)
  pass_level_test()

  # you have to close browser by yourself
  close_browser()

You do not have to start browser, if there is no browser, the tool will start one.
However, you have to close the browser, because the tool does know when it is okay to close for you.
You don't have to give the score every time, the tool will randomly generate a score > 70.

-----
"""
from contextlib import contextmanager

import ectools.utility
from ectools.service_helper import is_v2_student
from ectools.utility import get_score
from .internal.business import score_helper_v1
from .internal.business import score_helper_v2
from .internal.level_test_helper import pass_level_test_v2
from .internal.objects import *


def _is_submit_for_v2():
    return getattr(Cache, 'submit_for_v2', False)


def _get_score_helper():
    if _is_submit_for_v2():
        return score_helper_v2
    else:
        return score_helper_v1


@contextmanager
def submit_score_helper(student_id):
    try:
        load_student(student_id=student_id)
        yield
    finally:
        close_browser()


def load_student(student_id, reload_page=True):
    Cache.submit_for_v2 = is_v2_student(student_id)
    Cache.current_student_id = student_id
    _get_score_helper().load_student(student_id, reload_page)


def submit_current_unit(score=get_score(), skip_activity=0):
    _get_score_helper().submit_current_unit(score, skip_activity)


def submit_for_unit(unit_id, score=get_score(), skip_activity=0):
    _get_score_helper().submit_for_unit(unit_id, score, skip_activity)


def pass_to_unit(unit_id, score=get_score(), skip_activity=0):
    _get_score_helper().pass_to_unit(unit_id, score, skip_activity)


def pass_six_units(score=get_score()):
    _get_score_helper().pass_six_units(score)


def enroll_to_unit(unit_id):
    _get_score_helper().enroll_to_unit(unit_id)


def pass_level_test(score=get_score()):
    student_id = getattr(Cache, 'current_student_id')
    pass_level_test_v2(student_id, score)


def pass_six_units_and_level_test(score=get_score()):
    _get_score_helper().pass_six_units(score)
    pass_level_test(score)


def close_browser():
    """To close browser for score helper."""
    ectools.utility.close_browser()
