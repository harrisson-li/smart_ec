using CAS.Core;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CAS.Tests
{
    [TestClass]
    public class Forecast_Tool : TestBase
    {
        /// <summary>
        /// You have to update "MarkForecastAsBug" in app.config, then clean action will skip this data
        /// </summary>
        [TestMethod, TestCategory("Tool")]
        public void MarkForecastAsBug()
        {
            var id = GetConfig<int>("MarkForecastAsBug");
            var c = DbHelper.OBOE.ScheduledClassForecasts
                .Where(e => e.ScheduledClass_id == id).Single();
            c.Insertby = "mark.bug";
            DbHelper.OBOE.SubmitChanges();
        }

        /// <summary>
        /// Clean up a specify forcast data, please update "CleanupForecastId" in app.config
        /// </summary>
        [TestMethod, TestCategory("Tool")]
        public void CleanupForecastById()
        {
            var id = GetConfig<int>("CleanupForecastId");
            var list = DbHelper.OBOE.ScheduledClassForecasts
                .Where(e => e.ScheduledClass_id == id);

            foreach (var item in list)
            {
                DbHelper.OBOE.ScheduledClassForecasts.DeleteOnSubmit(item);
            }

            DbHelper.OBOE.SubmitChanges();
        }

        /// <summary>
        /// Clean all forcast data, except those mark as bug
        /// </summary>
        [TestMethod, TestCategory("Tool")]
        public void CleanupForecast()
        {
            var list = DbHelper.OBOE.ScheduledClassForecasts
                .Where(e => e.StartDate >= DateTime.Today &&
                e.Updateby == "automation" &&
                e.Insertby != "mark.bug" &&
                e.School_id == this.SchoolId);

            foreach (var item in list)
            {
                DbHelper.OBOE.ScheduledClassForecasts.DeleteOnSubmit(item);
                DbHelper.PrintClassDetail(item);
            }

            DbHelper.OBOE.SubmitChanges();
        }

        /// <summary>
        /// Conflict check, get all classes for a teacher, update app.config > GetClassByTeacher
        /// </summary>
        [TestMethod, TestCategory("Tool")]
        public void GetClassByTeacher()
        {
            var teacherId = GetConfig<int>("GetClassByTeacher");
            var list = DbHelper.OBOE.ScheduledClasses
                .Where(e => e.Teacher_id == teacherId
                && e.StartDate > DateTime.Now
                && !e.IsDeleted);

            Console.WriteLine("All found by teacher {0}:", teacherId);
            foreach (var item in list)
            {
                DbHelper.PrintClassDetail(item);
            }
        }

        /// <summary>
        /// Conflict check, get all classes for a classroom, update app.config > GetClassByClassroom
        /// </summary>
        [TestMethod, TestCategory("Tool")]
        public void GetClassByClassroom()
        {
            var classroomId = GetConfig<int>("GetClassByClassroom");
            var list = DbHelper.OBOE.ScheduledClasses
                .Where(e => e.ClassRoom_id == classroomId
                && e.StartDate > DateTime.Now
                && !e.IsDeleted);

            Console.WriteLine("All found by classroom {0}:", classroomId);
            foreach (var item in list)
            {
                DbHelper.PrintClassDetail(item);
            }
        }
    }
}