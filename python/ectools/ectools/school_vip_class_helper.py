"""
This module help you book school vip class (F2F VIP/1:1 Teacher Review).

  from ectools.school_vip_class_helper import *

  student_id = 123456
  school_name = 'xx_xxx'
  class_category = 'F2F Vip'
  search_date = '2020-09-18'

  # (recommended) call by with statement, it will help you manage browser
  with school_vip_class_helper(student_id, school_name, class_category, search_date):
      book_school_vip_class(student_name, class_id)

  # (not recommended) load student then do whatever you want
  school_vip_class_helper(student_id, school_name, class_category, search_date)

  book_school_vip_class(student_name, class_id)

  # you have to close browser by yourself
  close_browser()

You do not have to start browser, if there is no browser, the tool will start one.
However, you have to close the browser, because the tool does know when it is okay to close for you.
-----
"""
from contextlib import contextmanager

from ectools.internal.business import school_vip_booking_helper
from ectools.internal.objects import Cache
from ectools.utility import close_browser


@contextmanager
def school_vip_class_helper(student_id, school_name, class_category, class_date):
    try:
        search_school_vip_class(student_id, school_name, class_category, class_date)
        yield
    finally:
        close_browser()


def search_school_vip_class(student_id, school_name, class_category, class_date):
    Cache.current_student_id = student_id
    school_vip_booking_helper.search_school_vip_class(student_id, school_name, class_category, class_date)


def book_school_vip_class(student_name, scheduled_class_id):
    school_vip_booking_helper.book_school_vip_class(student_name, scheduled_class_id)


def book_school_vip_class_failed(student_name, scheduled_class_id):
    school_vip_booking_helper.book_school_vip_class_failed(student_name, scheduled_class_id)
