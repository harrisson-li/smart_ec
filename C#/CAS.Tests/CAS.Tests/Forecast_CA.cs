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
    public class Forecast_CA : TestBase
    {
        [TestMethod, TestCategory("CA")]
        public void Forecast_CASeminar()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 0;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.CASeminarElem;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            var teacher = this.TeacherIDs[index];

            var c = GetDefaultForecast(timeslot);

            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;

            DbHelper.InsertForecastClass(c);
        }

        /// <summary>
        /// Should be highlighted.
        /// </summary>
        [TestMethod, TestCategory("CA")]
        public void Forecast_CASeminar_EmptyTeacher()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 1;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.CASeminarElem;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            //var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);

            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            //c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;

            DbHelper.InsertForecastClass(c);
        }
    }
}