using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CAS.Core
{
    public class Timeslot
    {
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
        public string StartTime { get; set; }
        public string EndTime { get; set; }
    }

    public enum ClassCategorys
    {
        F2F = 1,
        Workshop = 2,
        Apply = 3,
        LifeClub = 4,
        CASeminar = 38,
        BeginnerFoundation = 43,
        CAEvent = 44,
        BaginnerBasics = 49,
        BusinessEnglishWorkshop = 300
    }

    public class ClassType
    {
        public static string F2F_High = "F2F High";
        public static string F2F_Low = "F2F Low";

        public static string BeginnerA = "Beginner A";
        public static string BeginnerB = "Beginner B";
        public static string BeginnerBasics = "Beginner Basics";
        public static string BeginnerFoundationA = "Beginner Foundation A";

        public static string ElementaryA = "Elementary A";
        public static string ElementaryB = "Elementary B";
        public static string IntermediateA = "Intermediate A";
        public static string IntermediateB = "Intermediate B";
        public static string UpperIntermediateA = "Upper-Intermediate A";

        public static string CASeminarElem = "CA Seminar Elem";
        public static string ArtsHigh = "Arts High";
        public static string ArtsLow = "Arts Low";

        public static string InternalSales = "SS_OPT/CT";
        public static string InternalSalesSpecial = "SS_ILAB";
        public static string InternalTraining = "IND";
        public static string InternalAdmin = "TP";
        public static string InternalNonCore = "B2B";
    }

    public class DbHelper
    {
        private static DbHelper instance;
        private OboeDataContext oboe;
        public static int PartnerSchoolId = -1;

        private DbHelper()
        {
            this.oboe = new OboeDataContext();
        }

        public static DbHelper Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = GetInstance();
                }
                return instance;
            }
        }

        public static DbHelper GetInstance()
        {
            var helper = new DbHelper();
            return helper;
        }

        public static OboeDataContext OBOE
        {
            get
            {
                return Instance.oboe;
            }
        }

        public static School_lkp GetSchoolByName(string name)
        {
            return DbHelper.OBOE.School_lkps.Where(e => e.SchoolName == name).Single();
        }

        public static List<Classroom_lkp> GetClassroomsBySchoolId(int schoolId)
        {
            return DbHelper.OBOE.Classroom_lkps
                .Where(e => e.School_id == schoolId && !e.IsDeleted)
                .ToList();
        }

        public static Classroom_lkp GetClassroomByName(int schoolId, string name)
        {
            var all = GetClassroomsBySchoolId(schoolId);
            return all.Where(e => e.ClassroomName == name).Single();
        }

        public static int GetTeacherByName(int schoolId, string name)
        {
            var all = GetTeachersBySchoolId(schoolId);
            return (int)all.Where(e => e.Teacher_Name == name).Single().Teacher_id;
        }

        public static List<Teacher> GetTeachersBySchoolId(int schoolId)
        {
            var roleCodes = new List<string>() { "TCR", "LCTCR", "CATCR" };
            var roles = OBOE.Role_lkps
                .Where(e => roleCodes.Contains(e.RoleCode)
                && !e.IsDeleted)
                .Select(e => e.Role_id)
                .ToList();

            var userRoleSchools = OBOE.UserRoleSchool_lnks
                .Where(e => e.School_id == schoolId
                && roles.Contains(e.Role_id)
                && !(bool)e.IsDeleted);

            var userIds = userRoleSchools.Select(e => e.User_id).ToList();
            var teachers = OBOE.Teachers.Where(e => userIds.Contains(e.Teacher_id)).ToList();
            return teachers;
        }

        /// <summary>
        /// Preview timeslot is half of normal timeslot.
        /// </summary>
        /// <param name="day">When</param>
        /// <param name="seq">Timeslot sequence.</param>
        /// <returns></returns>
        public static Timeslot GetPreviewTimeslot(DateTime day, int seq = 1)
        {
            var timeslotSeq = Math.Ceiling(seq / 2.0);
            var timeslot = GetTimeslot(day, (int)timeslotSeq);

            if (seq % 2 == 0)
            {
                timeslot.StartDate += new TimeSpan(0, 25, 0);
            }
            else
            {
                timeslot.EndDate -= new TimeSpan(0, 25, 0);
            }

            timeslot.StartTime = Convert.ToInt32(string.Format("{0}{1:D2}", timeslot.StartDate.Hour + 8, timeslot.StartDate.Minute)).ToString();
            timeslot.EndTime = Convert.ToInt32(string.Format("{0}{1:D2}", timeslot.EndDate.Hour + 8, timeslot.EndDate.Minute)).ToString();

            return timeslot;
        }

        /// <summary>
        /// Get normal timeslot for today.
        /// </summary>
        /// <param name="seq">Timeslot index / sequence.</param>
        /// <returns></returns>
        public static Timeslot GetTimeslot(int seq = 1)
        {
            return GetTimeslot(DateTime.Today, seq);
        }

        /// <summary>
        /// Get normal timeslot for a day.
        /// </summary>
        /// <param name="day">When.</param>
        /// <param name="seq">Timesloft index / sequence.</param>
        /// <returns></returns>
        public static Timeslot GetTimeslot(DateTime day, int seq = 1)
        {
            var startDate = day.Date + new TimeSpan(seq, 40, 00);
            var endDate = day.Date + new TimeSpan(seq + 1, 30, 00);
            var startTime = Convert.ToInt32(string.Format("{0}{1:D2}", startDate.Hour + 8, startDate.Minute)).ToString();
            var endTime = Convert.ToInt32(string.Format("{0}{1:D2}", endDate.Hour + 8, endDate.Minute)).ToString();

            return new Timeslot()
            {
                StartDate = startDate,
                EndDate = endDate,
                StartTime = startTime,
                EndTime = endTime
            };
        }

        /// <summary>
        /// Calculate last Mondy for a day.
        /// </summary>
        /// <param name="day">The base day.</param>
        /// <returns></returns>
        public static DateTime GetLastMonday(DateTime day)
        {
            return day.AddDays(-(int)day.Date.DayOfWeek + (int)DayOfWeek.Monday);
        }

        /// <summary>
        /// Calculate last Sunday for a day.
        /// </summary>
        /// <param name="day">The base day.</param>
        /// <returns></returns>
        public static DateTime GetLastSunday(DateTime day)
        {
            return GetLastMonday(day).AddDays(-1);
        }

        /// <summary>
        /// Get shceduled class topics for a week.
        /// </summary>
        public static ScheduledClassTopic GetScheduledClassTopic(DateTime startDay, int classTypeId, int dayRange = 7)
        {
            var startDate = GetLastSunday(startDay);
            var endDate = startDate.AddDays(dayRange + 1);

            var found = OBOE.ScheduledClassTopics
                .Where(e => e.StartDate >= startDate
                && e.EndDate <= endDate
                && e.School_id == DbHelper.PartnerSchoolId
                && e.ClassType_id == classTypeId)
                .OrderBy(e => e.StartDate);

            return found.First();
        }

        /// <summary>
        /// Get class type detail by category id and class type name.
        /// </summary>
        public static ClassType_lkp GetClassTypeDetail(int classCategoryId, string classTypeName)
        {
            return OBOE.ClassType_lkps
                .Where(e => e.Name == classTypeName
                && e.ClassCategory_id == classCategoryId
                && !e.IsHidden
                && !e.IsDeleted).Single();
        }

        /// <summary>
        /// Get class type detail by class type name.
        /// </summary>
        public static ClassType_lkp GetClassTypeDetail(string classTypeName)
        {
            return OBOE.ClassType_lkps
                .Where(e => e.Name == classTypeName
                && !e.IsHidden
                && !e.IsDeleted).Single();
        }

        public static void InsertForecastClass(ScheduledClassForecast entity)
        {
            OBOE.ScheduledClassForecasts.InsertOnSubmit(entity);
            OBOE.SubmitChanges(System.Data.Linq.ConflictMode.FailOnFirstConflict);
            PrintClassDetail(entity);
        }

        public static void PrintClassDetail(ScheduledClassForecast entity)
        {
            var school = OBOE.School_lkps.Where(e => e.School_id == entity.School_id).Single();
            var room = OBOE.Classroom_lkps.Where(e => e.Classroom_id == entity.ClassRoom_id).FirstOrDefault();
            var teacher = OBOE.Teachers.Where(e => e.Teacher_id == entity.Teacher_id).FirstOrDefault();
            var clsType = OBOE.ClassType_lkps.Where(e => e.ClassType_id == entity.ClassType_id).Single();
            var clsCategory = OBOE.ClassCategory_lkps.Where(e => e.ClassCategory_id == entity.ClassCategory_id).Single();

            if (room == null)
            {
                room = new Classroom_lkp();
                room.ClassroomName = "NULL";
                room.Classroom_id = 0;
            }

            if (teacher == null)
            {
                teacher = new Teacher();
                teacher.Teacher_id = 0;
                teacher.Teacher_Name = "NULL";
            }

            Console.WriteLine("{0} [{1}({2}) - {3}({4})]: {5}({6}) / {7}({8}) / {9}({10}) / {11}({12}) / {13}({14})",
                entity.ScheduledClass_id,
                entity.StartDate,
                entity.StartTime,
                entity.EndDate,
                entity.EndTime,
                school.SchoolName,
                school.School_id,
                room.ClassroomName,
                room.Classroom_id,
                teacher.Teacher_Name,
                teacher.Teacher_id,
                clsCategory.Name,
                clsCategory.ClassCategory_id,
                clsType.Name,
                clsType.ClassType_id);
        }

        public static void PrintClassDetail(ScheduledClass entity)
        {
            var school = OBOE.School_lkps.Where(e => e.School_id == entity.School_id).Single();
            var room = OBOE.Classroom_lkps.Where(e => e.Classroom_id == entity.ClassRoom_id).Single();
            var teacher = OBOE.Teachers.Where(e => e.Teacher_id == entity.Teacher_id).FirstOrDefault();
            var clsType = OBOE.ClassType_lkps.Where(e => e.ClassType_id == entity.ClassType_id).Single();
            var clsCategory = OBOE.ClassCategory_lkps.Where(e => e.ClassCategory_id == entity.ClassCategory_id).Single();

            if (teacher == null)
            {
                teacher = new Teacher();
                teacher.Teacher_id = 0;
                teacher.Teacher_Name = "NULL";
            }

            Console.WriteLine("{0} [{1}({2}) - {3}({4})]: {5}({6}) / {7}({8}) / {9}({10}) / {11}({12}) / {13}({14})",
                entity.ScheduledClass_id,
                entity.StartDate,
                entity.StartTime,
                entity.EndDate,
                entity.EndTime,
                school.SchoolName,
                school.School_id,
                room.ClassroomName,
                room.Classroom_id,
                teacher.Teacher_Name,
                teacher.Teacher_id,
                clsCategory.Name,
                clsCategory.ClassCategory_id,
                clsType.Name,
                clsType.ClassType_id);
        }
    }
}