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

from ectools.db_query import execute_query, fetch_one
from ectools.internal.objects import Base
from ectools.logger import get_logger
from ectools.service_helper import is_v2_student, clear_booking_mem_cache_by_date_range, \
    clear_offline_class_taken_cache, clear_online_class_taken_cache
from ectools.utility import get_score, random_date


class HelperConfig(Base):
    LevelMustComplete = True  # the level must be completed before class taken
    LevelEnrollDateShift = {'days': -30}
    ClassTakenSince = {'days': -29}
    ClassTakenUntil = {'days': -1}
    DefaultMinimumClassTaken = {'f2f': 3, 'workshop': 3, 'apply_or_lc': 1}
    DefaultPLCode = 'CP20'


def reset_config():
    """To reset config for this helper if you want to keep the default behavior."""
    HelperConfig.LevelMustComplete = True
    HelperConfig.LevelEnrollDateShift = {'days': -30}
    HelperConfig.ClassTakenSince = {'days': -29}
    HelperConfig.ClassTakenUntil = {'days': -1}
    HelperConfig.DefaultMinimumClassTaken = {'f2f': 3, 'workshop': 3, 'apply_or_lc': 1}
    HelperConfig.DefaultPLCode = 'CP20'


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
        WHERE Student_id = {}
        AND IsCurrent = 1
        AND IsCurrentForCourseType = 1
        AND IsEnrollable = 1
        AND IsPrimary = 1)""".format(student_id)

        return fetch_one(sql, as_dict=False).StudentLevelProgress_id

    def get_unit_progress_id():
        sql = """SELECT MIN(StudentUnitProgress_id)
        FROM SchoolAccount.dbo.StudentUnitProgress
        WHERE StudentCourse_id IN (SELECT
        StudentCourse_id
        FROM SchoolAccount.dbo.StudentCourse
        WHERE Student_id = {}
        AND IsCurrent = 1
        AND IsCurrentForCourseType = 1
        AND IsEnrollable = 1
        AND IsPrimary = 1)""".format(student_id)

        return fetch_one(sql, as_dict=False)[0]

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
        row = fetch_one(sql.format(db_suffix, student_id), as_dict=False)
        extra_data = row.ExtraData
        course_item_id = row.StudentCourseItem_id
        pattern = r'.*enrollDate":"([\d\-T\:]*)"'
        match = re.match(pattern, extra_data)

        if match:
            original_date = arrow.get(match.group(1))
            enroll_date = original_date.shift(**HelperConfig.LevelEnrollDateShift).format('YYYY-MM-DDTHH:mm:ss')
            extra_data = re.sub(r'("enrollDate":"[\d\-T\:]*")', '"enrollDate":"{}"'.format(enroll_date), extra_data)

        sql = """UPDATE school_{0}.dbo.StudentCourseItem
        SET ExtraData = '{1}', StartDate = '{2}'
        WHERE StudentCourseItem_id = '{3}'
        AND student_id = {4}"""

        execute_query(sql.format(db_suffix, extra_data, enroll_date, course_item_id, student_id))

    update_level_enrollment_date()
    _main(student_id, **kwargs)


def _get_class_type_mapping():
    """ClassTypeName: [CouponClassCategoryGroup_id,ClassType_id]"""
    return {'f2f': [1, 1], 'workshop': [2, 2], 'apply': [3, 4], 'life_club': [6, 4]}


def _get_past_class_item(class_category_id, student_id):
    """Get a class in past time for specified class category."""
    sql = """SELECT TOP 1 * FROM [Oboe].[dbo].[ScheduledClass]
    WHERE ClassCategory_id = {0}
    AND StartDate > GETDATE() + {1}
    AND StartDate < GETDATE() + {2}
    AND EndDate < GETDATE() + {2}
    AND IsPublished = 1
    AND IsDeleted = 0
    AND ScheduledClass_id NOT IN (
	SELECT ScheduledClass_id FROM oboe.dbo.Booking
	WHERE Student_id = {3}
	AND BookingStatus_id NOT IN (0,4))
    """

    return fetch_one(sql.format(class_category_id,
                                HelperConfig.ClassTakenSince['days'],
                                HelperConfig.ClassTakenUntil['days'],
                                student_id), as_dict=False)


def _get_coupon_count(student_id, coupon_type_id):
    """Get coupon count for a student."""
    sql = """SELECT COUNT(*)
    FROM oboe.dbo.Coupon
    WHERE booking_id IS NULL
    AND student_id = {}
    AND couponClassCategoryGroup_id = {}"""

    return fetch_one(sql.format(student_id, coupon_type_id), as_dict=False)[0]


def _is_coupon_free_student(student_id):
    sql = """SELECT COUNT(*) FROM oboe.dbo.ProductFeatureMapping_lnk pfm
    JOIN oboe.dbo.Product_lkp p ON p.Product_id = pfm.Product_id
    JOIN oboe.dbo.Student s ON s.Product_id = p.Product_id
    WHERE  pfm.ProductFeatureCode ='CouponFree'
    AND s.Student_id = {}"""

    is_coupon_free = int(fetch_one(sql.format(student_id), as_dict=False)[0])
    return is_coupon_free > 0


def _insert_booking_id(student_id, schedule_class, coupon_category_id):
    """Insert booking record and set status as checked in."""
    scheduled_id = schedule_class.ScheduledClass_id
    get_logger().debug('Insert booking record for class: {}'.format(scheduled_id))

    sql = """INSERT INTO oboe.dbo.Booking 
           ([ScheduledClass_id]
           ,[Student_id]
           ,[BookingStatus_id]
           ,[LevelIndex]
           ,[UnitIndex]
           ,[IsDeleted]
           ,[InsertDate]
           ,[UpdateDate]
           ,[LevelCode])
    VALUES ({}, {}, 2, 1, 1, 0, CAST('{}' AS DATETIME2), GETDATE(), '1')
    """
    execute_query(sql.format(scheduled_id,
                             student_id,
                             schedule_class.EndDate))

    # if student is coupon free, no need to update coupon table, just return
    if _is_coupon_free_student(student_id):
        return

    sql = """SELECT booking_id
    FROM oboe.dbo.Booking
    WHERE student_id = {}
    AND ScheduledClass_id = {}
    ORDER BY Booking_id DESC"""

    book_id = fetch_one(sql.format(student_id, scheduled_id), as_dict=False)[0]

    sql = """DECLARE @coupon_id AS INT
    SELECT @coupon_id = MIN(coupon_id)
    FROM oboe.dbo.Coupon
    WHERE booking_id IS NULL
    AND student_id = {}
    AND couponClassCategoryGroup_id = {}
    AND IsActivated = 1
    AND IsDeleted = 0
    UPDATE oboe.dbo.Coupon
    SET booking_id = {}
    WHERE coupon_id = @coupon_id"""

    execute_query(sql.format(student_id, coupon_category_id, book_id))


def _class_taken(student_id, class_type, count, ignore_if_no_coupon=False):
    if count is None:
        return

    get_logger().info("Class taken for {}: {}".format(class_type, count))
    coupon_category_id = _get_class_type_mapping()[class_type][0]
    class_category_id = _get_class_type_mapping()[class_type][1]
    is_coupon_free = _is_coupon_free_student(student_id)

    while count > 0:

        # set coupon to valid number for coupon free student
        if is_coupon_free:
            coupon_count = 1
        else:
            coupon_count = _get_coupon_count(student_id, coupon_category_id)

        # verify coupon before booking
        if coupon_count == 0:
            message = "No enough coupon for: {}".format(class_type)

            if ignore_if_no_coupon:
                get_logger().warn(message)
                break
            else:
                raise Exception(message)

        schedule_class = _get_past_class_item(class_category_id, student_id)
        _insert_booking_id(student_id, schedule_class, coupon_category_id)
        count -= 1
        clear_booking_mem_cache_by_date_range(student_id)
        clear_offline_class_taken_cache(student_id)


def _class_taken_for_online_class(student_id, count, type_code):
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
           '{1}',
           'Courseware',
           '{2:%Y-%m-%d %I:%M}',
           'Attended',
           '15000000',
           '{3}',
           'automation testing by ectools',
           '1000000',
           '378',
           '1798',
           GETDATE(),
           GETDATE(),
           'Cities and countries',
           '191'
          )"""

    get_logger().info("Class taken for online {}: {}".format(type_code, count))
    start = datetime.now() + timedelta(**HelperConfig.ClassTakenSince)
    end = datetime.now() + timedelta(**HelperConfig.ClassTakenUntil)

    for i in range(count):
        execute_query(sql.format(student_id, type_code, random_date(start, end), get_score()))

    clear_booking_mem_cache_by_date_range(student_id)
    clear_online_class_taken_cache(student_id)


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
    _class_taken_for_online_class(student_id, online_gl, type_code='GL')
    _class_taken_for_online_class(student_id, online_pl, type_code=HelperConfig.DefaultPLCode)

    if apply_or_lc:
        _class_taken(student_id, 'apply', apply_or_lc, True)
        _class_taken(student_id, 'life_club', apply_or_lc, True)
    else:
        _class_taken(student_id, 'apply', apply_event)
        _class_taken(student_id, 'life_club', life_club)


def _get_arrow_time(time_value):
    """Convert time value to Arrow object."""
    return time_value if isinstance(time_value, arrow.Arrow) else arrow.get(time_value)


def _days_to_now(time_value):
    """Days delta for time value to utc now."""
    time = _get_arrow_time(time_value)
    return (time - arrow.utcnow()).days


def take_class(student_id, start_date=None, end_date=None, **kwargs):
    """
    Take a class in past time, required start_date and end_date
    :param student_id: student id / member id.
    :param start_date: UTC start_time in popular format or Arrow object.
    :param end_date: UTC end_time in popular format or Arrow object.
    :param kwargs:  specify the class type to be taken, example `f2f=3`.

             - f2f
             - workshop
             - apply_event
             - life_club
             - online_gl
             - apply_or_lc
    """

    # set start date and end date
    if start_date:
        HelperConfig.ClassTakenSince = {'days': _days_to_now(start_date)}

    if end_date:
        HelperConfig.ClassTakenUntil = {'days': _days_to_now(end_date)}

    # take class and reset
    _main(student_id, **kwargs)
    reset_config()
