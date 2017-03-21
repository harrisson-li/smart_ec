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
    public class Forecast_Apply : TestBase
    {
        [TestMethod, TestCategory("Apply")]
        public void Forecast_Apply_()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 1;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.ArtsHigh;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.TeacherIDs[index];

            var c = GetDefaultForecast(timeslot);

            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            //c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;

            DbHelper.InsertForecastClass(c);
        }

        /// <summary>
        /// Should be hightlighted.
        /// </summary>
        [TestMethod, TestCategory("Apply")]
        public void Forecast_Apply_EmptyTeacherId()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 2;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.ArtsLow;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            //var teacher = this.TeacherIDs[index];

            var c = GetDefaultForecast(timeslot);

            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            //c.ClassTopic_id = classTopic.ClassTopic_id;
            //c.Teacher_id = teacher;
            //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;

            DbHelper.InsertForecastClass(c);
        }
    }
}