using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CAS.Core;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace CAS.Tests
{
    [TestClass]
    public class Forecast_F2F : TestBase
    {
        [TestMethod, TestCategory("F2F")]
        public void Forecast_F2F_()
        {
            var index = 0;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_Low;
            var classCategoryId = (int)ClassCategorys.F2F;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classCategoryId, classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            var teacher = this.TeacherIDs[index];

            var c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            //c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            c.IsDynamicTopic = true; // cool must be dynamic, mini must change to false.

            DbHelper.InsertForecastClass(c);
        }

        /// <summary>
        /// Fixed class should be in color red.
        /// </summary>
        [TestMethod, TestCategory("F2F")]
        public void Forecast_F2F_FixedClass()
        {
            var index = 0;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_Low;
            var classCategoryId = (int)ClassCategorys.F2F;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classCategoryId, classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            var teacher = this.TeacherIDs[index];

            var c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            //c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            c.IsDynamicTopic = true; // cool must be dynamic, mini must change to false.
            c.IsFixedClass = 1;

            DbHelper.InsertForecastClass(c);
        }

        /// <summary>
        /// Should be highlighted in color green.
        /// </summary>
        [TestMethod, TestCategory("F2F")]
        public void Forecast_F2F_EmptyTopic()
        {
            var index = 1;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_High;
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
            c.IsDynamicTopic = true; // cool must be dynamic, mini must change to false.
            //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;

            DbHelper.InsertForecastClass(c);
        }

        /// <summary>
        /// Should be hightlighted in color green.
        /// </summary>
        [TestMethod, TestCategory("F2F")]
        public void Forecast_F2F_EmptyTeacherID()
        {
            var index = 2;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_Low;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            //var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);

            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            // c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            c.IsDynamicTopic = true; // cool must be dynamic, mini must change to false.

            DbHelper.InsertForecastClass(c);
        }

        /// <summary>
        /// Should not be able to load.
        /// </summary>
        [TestMethod, TestCategory("F2F")]
        public void Forecast_F2F_BadTeacherId_Existed()
        {
            var index = 3;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_Low;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            var teacher = 0;

            var c = GetDefaultForecast(timeslot);

            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            c.IsDynamicTopic = true; // cool must be dynamic, mini must change to false.

            DbHelper.InsertForecastClass(c);
        }

        /// <summary>
        /// Should not be able to load.
        /// </summary>
        [TestMethod, TestCategory("F2F")]
        public void Forecast_F2F_BadTeacherId_NotExisted()
        {
            var index = 4;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_Low;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            var teacher = -111;

            var c = GetDefaultForecast(timeslot);

            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            c.IsDynamicTopic = true;

            DbHelper.InsertForecastClass(c);
        }
    }
}