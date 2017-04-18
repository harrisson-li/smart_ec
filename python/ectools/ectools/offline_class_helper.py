"""
This module will help achieve the minimum class taken to move on to next level. For now, it supports class taken for:
  - f2f
  - workshop
  - apply
  - life_club
  - online_gl

Example to use this module::

  from ectools.offline_class_helper import achieve_minimum_class_taken

  student_id = 123456
  achieve_minimum_class_taken(student_id, f2f=3, workshop=3, apply_or_lc=1)

  # for cehk student they have to do 12 GL
  achieve_minimum_class_taken(student_id, online_gl=12)

.. warning::

  This module will update or insert data in database, so call this
  module in **Staging** or **Live** environment will raise errors.

-----
"""
import re
from datetime import datetime, timedelta

import arrow

from ectools.database_helper import *
from ectools.service_helper import is_v2_student
from ectools.utility import get_score, random_date


class HelperConfig(Base):
    LevelMustComplete = True  # the level must be completed before class taken
    LevelEnrollDateShift = {'days': -30}
    ClassTakenSince = {'days': -29}
    ClassTakenUntil = {'days': -1}
    DefaultMinimumClassTaken = {'f2f': 3, 'workshop': 3, 'apply_or_lc': 1}


def achieve_minimum_class_taken(student_id, **kwargs):
    """
    Achieve minimum class taken to move on to next level.

    :param student_id: the student id.
    :keyword: specify the class type to be taken, example `f2f=3`.

             - f2f
             - workshop
             - apply_event
             - life_club
             - online_gl
             - apply_or_lc

    """
    get_logger().info("Minimum classes taken before moving on to next level")

    if not kwargs:
        kwargs = HelperConfig.DefaultMinimumClassTaken

    if is_v2_student(student_id):
        achieve_minimum_class_taken_v2(student_id, **kwargs)
    else:
        achieve_minimum_class_taken_v1(student_id, **kwargs)


def achieve_minimum_class_taken_v1(student_id, **kwargs):
    """
    Update level and unit progress to past time and bind past class to the student.
    For Smart 15 students.
    """

    def get_level_progress_id():
        sql = """SELECT StudentLevelProgress_id
        FROM SchoolAccount.dbo.StudentLevelProgress
        WHERE StudentCourse_id IN (SELECT
        StudentCourse_id
        FROM SchoolAccount.dbo.StudentCourse
        WHERE Student_id = %s
        AND IsCurrent = 1
        AND IsCurrentForCourseType = 1
        AND IsEnrollable = 1
        AND IsPrimary = 1)"""

        return fetch_one(sql, student_id).StudentLevelProgress_id

    def get_unit_progress_id():
        sql = """SELECT MIN(StudentUnitProgress_id)
        FROM SchoolAccount.dbo.StudentUnitProgress
        WHERE StudentCourse_id IN (SELECT
        StudentCourse_id
        FROM SchoolAccount.dbo.StudentCourse
        WHERE Student_id = %s
        AND IsCurrent = 1
        AND IsCurrentForCourseType = 1
        AND IsEnrollable = 1
        AND IsPrimary = 1)"""

        return fetch_one(sql, student_id)[0]

    def update_progress_start_time(level_progress_id, unit_progress_id):
        get_logger().info("Update level and unit progress start time")

        sql = """DECLARE @starttime as datetime
        SET @starttime = GETDATE() + {}
        -- Update level progress start time to previous time
        UPDATE SchoolAccount.dbo.StudentLevelProgress
        SET StartDateTime = @starttime
        WHERE StudentLevelProgress_id = {}

        -- Update unit progress start time to previous time
        UPDATE SchoolAccount.dbo.StudentUnitProgress
        SET StartDateTime = @starttime
        WHERE StudentUnitProgress_id = {}"""

        execute_query(sql.format(HelperConfig.LevelEnrollDateShift['days'], level_progress_id, unit_progress_id))

    update_progress_start_time(get_level_progress_id(), get_unit_progress_id())
    _main(student_id, **kwargs)


def achieve_minimum_class_taken_v2(student_id, **kwargs):
    """
    Update enroll date to past time and bind past classes to the student.
    For platform 2.0 students.
    """

    def update_level_enrollment_date():
        get_logger().info("Update level enroll date")

        sql = """SELECT	*
        FROM school_{0}.dbo.StudentCourseItem sci
        WHERE sci.Student_id = {1}
        AND ItemType_id = 2
        AND CompleteDate IS NOT NULL
        AND sci.ExtraData LIKE '%levelCode"%'
        ORDER BY sci.SeqNo DESC"""

        if not HelperConfig.LevelMustComplete:
            sql = sql.replace('AND CompleteDate IS NOT NULL', '')

        db_suffix = str(student_id)[-1]
        row = fetch_one(sql.format(db_suffix, student_id))
        extra_data = row.ExtraData
        course_item_id = row.StudentCourseItem_id
        pattern = r'.*enrollDate":"([\d\-T\:]*)"'
        match = re.match(pattern, extra_data)

        if match:
            original_date = arrow.get(match.group(1))
            enroll_date = original_date.shift(**HelperConfig.LevelEnrollDateShift).format('YYYY-MM-DDTHH:mm:ss')
            extra_data = re.sub(r'("enrollDate":"[\d\-T\:]*")', '"enrollDate":"{}"'.format(enroll_date), extra_data)

        sql = """UPDATE school_{0}.dbo.StudentCourseItem
        SET ExtraData = '{1}'
        WHERE StudentCourseItem_id = '{2}'
        AND student_id = {3}"""

        execute_query(sql.format(db_suffix, extra_data, course_item_id, student_id))

    update_level_enrollment_date()
    _main(student_id, **kwargs)


def _get_class_type_mapping():
    """ClassTypeName: [CouponClassCategoryGroup_id,ClassType_id]"""
    return {'f2f': [1, 1], 'workshop': [2, 2], 'apply': [3, 3], 'life_club': [6, 4]}


def _get_past_class_id(class_category_id):
    sql = """SELECT TOP 1 * FROM [Oboe].[dbo].[ScheduledClass]
    WHERE ClassCategory_id = {0}
    AND StartDate > GETDATE() + {1}
    AND StartDate < GETDATE() + {2}
    AND EndDate < GETDATE() + {2}
    AND IsPublished = 1
    AND IsDeleted = 0
    """

    return fetch_one(sql.format(class_category_id,
                                HelperConfig.ClassTakenSince['days'],
                                HelperConfig.ClassTakenUntil['days'])
                     ).ScheduledClass_id


def _get_coupon_count(student_id, coupon_type_id):
    sql = """SELECT COUNT(*)
    FROM oboe.dbo.Coupon
    WHERE booking_id IS NULL
    AND student_id = {}
    AND couponClassCategoryGroup_id = {}"""

    return fetch_one(sql.format(student_id, coupon_type_id))[0]


def _insert_booking_id(student_id, schedule_id, coupon_category_id):
    sql = """INSERT INTO oboe.dbo.Booking
    VALUES ({}, {}, '2', 1, 1, 0, GETDATE() - 3, GETDATE() - 3, '1')
    """
    execute_query(sql.format(schedule_id, student_id))

    sql = """SELECT booking_id
    FROM oboe.dbo.Booking
    WHERE student_id = {}
    AND ScheduledClass_id = {}
    ORDER BY UpdateDate DESC"""

    book_id = fetch_one(sql.format(student_id, schedule_id))[0]

    sql = """DECLARE @coupon_id AS INT
    SELECT @coupon_id = MIN(coupon_id)
    FROM oboe.dbo.Coupon
    WHERE booking_id IS NULL
    AND student_id = %s
    AND couponClassCategoryGroup_id = %s
    AND IsActivated = 1
    AND IsDeleted = 0
    UPDATE oboe.dbo.Coupon
    SET booking_id = %s
    WHERE coupon_id = @coupon_id"""

    execute_query(sql, (student_id, coupon_category_id, book_id))


def _class_taken(student_id, class_type, count, ignore_if_no_coupon=False):
    if count is None:
        return

    get_logger().info("Class taken for {}: {}".format(class_type, count))
    coupon_category_id = _get_class_type_mapping()[class_type][0]
    class_category_id = _get_class_type_mapping()[class_type][1]

    while count > 0:
        coupon_count = _get_coupon_count(student_id, coupon_category_id)

        if coupon_count == 0:
            message = "No enough coupon for: {}".format(class_type)

            if ignore_if_no_coupon:
                get_logger().warn(message)
                break
            else:
                raise Exception(message)

        schedule_id = _get_past_class_id(class_category_id)
        _insert_booking_id(student_id, schedule_id, coupon_category_id)
        count -= 1


def _class_taken_for_gl(student_id, count):
    if count is None:
        return

    sql = """INSERT INTO SchoolAccount.dbo.StudentClassAttendance
         ( Student_id,
           Class_id,
           ServiceTypeCode,
           SchoolCode,
           EntryDate,
           StatusCode,
           TeacherMember_id,
           Grade,
           Comment,
           StudentCourse_id,
           Course_id,
           CourseUnit_id,
           InsertDate,
           UpdateDate,
           Topic,
           Topic_id
          )
        VALUES
         ( '{0}',
           '700000',
           'GL',
           'Courseware',
           '{1:%Y-%m-%d %I:%M}',
           'Attended',
           '15000000',
           '{2}',
           'automation testing by ectools',
           '1000000',
           '378',
           '1798',
           GETDATE(),
           GETDATE(),
           'Cities and countries',
           '191'
          )"""

    get_logger().info("Class taken for online GL: {}".format(count))
    start = datetime.now() + timedelta(**HelperConfig.ClassTakenSince)
    end = datetime.now() + timedelta(**HelperConfig.ClassTakenUntil)

    for i in range(count):
        execute_query(sql.format(student_id, random_date(start, end), get_score()))


def _class_taken_for_pl(student_id, count):
    if count is None:
        return

    sql = """INSERT INTO SchoolAccount.dbo.StudentClassAttendance
         ( Student_id,
           Class_id,
           ServiceTypeCode,
           SchoolCode,
           EntryDate,
           StatusCode,
           TeacherMember_id,
           Grade,
           Comment,
           StudentCourse_id,
           Course_id,
           CourseUnit_id,
           InsertDate,
           UpdateDate,
           Topic,
           Topic_id
          )
        VALUES
         ( '{0}',
           '700000',
           'PL',
           'Courseware',
           '{1:%Y-%m-%d %I:%M}',
           'Attended',
           '15000000',
           '{2}',
           'automation testing by ectools',
           '1000000',
           '378',
           '1798',
           GETDATE(),
           GETDATE(),
           'Cities and countries',
           '191'
          )"""

    get_logger().info("Class taken for online PL: {}".format(count))
    start = datetime.now() + timedelta(**HelperConfig.ClassTakenSince)
    end = datetime.now() + timedelta(**HelperConfig.ClassTakenUntil)

    for i in range(count):
        execute_query(sql.format(student_id, random_date(start, end), get_score()))


def _main(student_id, **kwargs):
    """Taken specific count for each type of class."""
    assert len(kwargs) > 0

    f2f = kwargs.get('f2f')
    workshop = kwargs.get('workshop')
    apply_event = kwargs.get('apply_event')
    life_club = kwargs.get('life_club')
    online_gl = kwargs.get('online_gl')
    online_pl = kwargs.get('online_pl')
    apply_or_lc = kwargs.get('apply_or_lc')

    _class_taken(student_id, 'f2f', f2f)
    _class_taken(student_id, 'workshop', workshop)
    _class_taken_for_gl(student_id, online_gl)
    _class_taken_for_pl(student_id, online_pl)

    if apply_or_lc:
        _class_taken(student_id, 'apply', apply_or_lc, True)
        _class_taken(student_id, 'life_club', apply_or_lc, True)
    else:
        _class_taken(student_id, 'apply', apply_event)
        _class_taken(student_id, 'life_club', life_club)
