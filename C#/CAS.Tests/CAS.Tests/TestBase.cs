using CAS.Core;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Text;

namespace CAS.Tests
{
    public class TestBase
    {
        private static Random ran = new Random();

        public string schoolName = GetConfig<string>("School");

        public DateTime baseDay = DateTime.Today.AddDays(GetConfig<int>("BaseDay"));

        public int timeslotSeq = GetConfig<int>("TimeslotSeq");

        public List<string> enabledSchools = GetConfig<List<string>>("EnabledCenters");

        public School_lkp School { get; set; }

        public int SchoolId { get { return this.School.School_id; } }

        public List<Classroom_lkp> Classrooms { get; set; }

        public List<int> TeacherIDs { get; set; }

        public TestBase()
        {
            DbHelper.PartnerSchoolId = GetConfig<int>("PartnerSchoolId");
            this.School = DbHelper.GetSchoolByName(schoolName);
            this.Classrooms = DbHelper.GetClassroomsBySchoolId(this.School.School_id);
            this.TeacherIDs = DbHelper.GetTeachersBySchoolId(this.School.School_id)
                .Select(e => (int)e.Teacher_id).ToList();
        }

        public ScheduledClassForecast GetDefaultForecast(Timeslot timeslot)
        {
            var c = new ScheduledClassForecast();
            c.StartDate = timeslot.StartDate;
            c.EndDate = timeslot.EndDate;
            c.StartTime = Convert.ToInt32(timeslot.StartTime);
            c.EndTime = Convert.ToInt32(timeslot.EndTime);
            c.School_id = this.SchoolId;
            c.IsVirtualSchool = false;
            c.IsDynamicTopic = false;
            c.Insertby = "qa.automation";
            c.Updateby = "automation";
            c.IsRandomTopic = 0;
            c.ReferenceAttendance = 0;
            return c;
        }

        public int GetRandomInt(int max = 100)
        {
            return ran.Next(max);
        }

        public static T GetConfig<T>(string key)
        {
            var str = ConfigurationManager.AppSettings[key];

            if (typeof(T) == typeof(int) || typeof(T) == typeof(string))
            {
                return (T)Convert.ChangeType(str, typeof(T));
            }
            else if (typeof(T) == typeof(List<string>))
            {
                var l = str.Split(new char[] { ',' }).ToList();
                return (T)(object)l;
            }
            else
            {
                throw new ArgumentException("Unsupported type: " + typeof(T));
            }
        }
    }
}