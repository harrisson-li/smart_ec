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
    public class Forecast_BB : TestBase
    {
        [TestMethod, TestCategory("BB")]
        public void Forecast_BeginnerBasic()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 3;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerBasics;
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
        /// Should be hightlighted.
        /// </summary>
        [TestMethod, TestCategory("BB")]
        public void Forecast_BeginnerBasic_RandomTopic()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 4;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerBasics;
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
            c.IsRandomTopic = 1;

            DbHelper.InsertForecastClass(c);
        }

        /// <summary>
        /// Should be highlighted.
        /// </summary>
        [TestMethod, TestCategory("BB")]
        public void Forecast_BeginnerBasic_EmptyTeacherId()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 5;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerBasics;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            //var teacher = this.TeacherIDs[index];

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