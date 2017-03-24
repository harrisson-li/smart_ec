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
    public class Forecast_BE_Workshop : TestBase
    {
        [TestMethod, TestCategory("BE_WS")]
        public void Forecast_BE_WS()
        {
            var index = 0;  // index for teacher, classroom in a school
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.ElementaryB;
            var classCategoryId = ClassCategorys.BusinessEnglishWorkshop;
            var classTypeDetail = DbHelper.GetClassTypeDetail((int)classCategoryId, classType);
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

        [TestMethod, TestCategory("BE_WS")]
        public void Forecast_BE_WS_FixClass()
        {
            var index = 0;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.ElementaryB;
            var classCategoryId = ClassCategorys.BusinessEnglishWorkshop;
            var classTypeDetail = DbHelper.GetClassTypeDetail((int)classCategoryId, classType);
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
            c.IsFixedClass = 1;

            DbHelper.InsertForecastClass(c);
        }

        [TestMethod, TestCategory("BE_WS")]
        public void Forecast_BE_WS_EmptyTeacherID()
        {
            var index = 1;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.ElementaryB;
            var classCategoryId = ClassCategorys.BusinessEnglishWorkshop;
            var classTypeDetail = DbHelper.GetClassTypeDetail((int)classCategoryId, classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            //var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            //c.teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;

            DbHelper.InsertForecastClass(c);
        }

        [TestMethod, TestCategory("BE_WS")]
        public void Forecast_BE_WS_Yesterday()
        {
            var index = 2;
            var day = baseDay.AddDays(-1); // yesterday
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.ElementaryB;
            var classCategoryId = ClassCategorys.BusinessEnglishWorkshop;
            var classTypeDetail = DbHelper.GetClassTypeDetail((int)classCategoryId, classType);
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

        [TestMethod, TestCategory("BE_WS")]
        public void Forecast_BE_WS_RandomTopic()
        {
            var index = 2;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.ElementaryB;
            var classCategoryId = ClassCategorys.BusinessEnglishWorkshop;
            var classTypeDetail = DbHelper.GetClassTypeDetail((int)classCategoryId, classType);
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

        [TestMethod, TestCategory("BE_WS")]
        public void Forecast_BE_WS_NoScheduledTopic()
        {
            var index = 4;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.ElementaryB;
            var classCategoryId = ClassCategorys.BusinessEnglishWorkshop;
            var classTypeDetail = DbHelper.GetClassTypeDetail((int)classCategoryId, classType);
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
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

        [TestMethod, TestCategory("BE_WS")]
        public void Forecast_BE_WS_OldScheduledTopic()
        {
            var index = 5;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.ElementaryB;
            var classCategoryId = ClassCategorys.BusinessEnglishWorkshop;
            var classTypeDetail = DbHelper.GetClassTypeDetail((int)classCategoryId, classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-20), classTypeDetail.ClassType_id, dayRange: 14);
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

        [TestMethod, TestCategory("BE_WS")]
        public void Forecast_BE_WS_FutureScheduledTopic()
        {
            var index = 3;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.ElementaryB;
            var classCategoryId = ClassCategorys.BusinessEnglishWorkshop;
            var classTypeDetail = DbHelper.GetClassTypeDetail((int)classCategoryId, classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(7), classTypeDetail.ClassType_id, dayRange: 30);
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
    }
}