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
    public class Forecast_Internal : TestBase
    {
        /// <summary>
        ///  empty teacher id for this class type should be higlighted.
        /// </summary>
        [TestMethod, TestCategory("Internal")]
        public void Forecast_Internal_ILab()
        {
            // teacher is not empty, should not be highlighted.

            var day = baseDay.AddDays(1); // tomorrow
            var index = 0;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.InternalSalesSpecial;
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

            // teacher is empty, should be highlighted
            index++;

            classroom = this.Classrooms[index];
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            //teacher = this.Teachers[index];

            c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            //c.ClassTopic_id = classTopic.ClassTopic_id;
            //c.Teacher_id = teacher;
            //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            DbHelper.InsertForecastClass(c);

            // empty classroom for this type should be showed in teacher page
            index++;

            //classroom = this.Classrooms[index];
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            teacher = this.TeacherIDs[index];

            c = GetDefaultForecast(timeslot);
            //c.ClassRoom_id = classroom.Classroom_id;
            //c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            //c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            DbHelper.InsertForecastClass(c);
        }

        /// <summary>
        /// Forecast all types of internal class, except ILab.
        /// </summary>
        [TestMethod, TestCategory("Internal")]
        public void Forecast_Internal_()
        {
            var types = new List<string>()
            {
                ClassType.InternalSales,
                ClassType.InternalAdmin,
                ClassType.InternalNonCore,
                ClassType.InternalTraining
            };

            for (int i = 0; i < 4; i++)
            {
                var day = baseDay.AddDays(1); // tomorrow
                var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
                var classroom = this.Classrooms[i];
                var classType = types[i];
                var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
                //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
                var teacher = this.TeacherIDs[i];

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
        }

        /// <summary>
        /// Forecast all types of internal class with empty teacher id, should not highlighted.
        /// </summary>
        [TestMethod, TestCategory("Internal")]
        public void Forecast_Internal_EmptyTeacherId()
        {
            var types = new List<string>()
            {
                ClassType.InternalSales,
                ClassType.InternalAdmin,
                ClassType.InternalNonCore,
                ClassType.InternalTraining
            };

            for (int i = 4; i < 8; i++)
            {
                var day = baseDay.AddDays(1); // tomorrow
                var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
                var classroom = this.Classrooms[i];
                var classType = types[i - 4];
                var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
                //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
                var teacher = this.TeacherIDs[i];

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

        /// <summary>
        /// Forecast all types of internal class without classroom, should show on schedule by teacher page.
        /// About to publish, no highlighted.
        /// </summary>
        [TestMethod, TestCategory("Internal")]
        public void Forecast_Internal_EmptyClassroom()
        {
            var types = new List<string>()
            {
                ClassType.InternalSales,
                ClassType.InternalAdmin,
                ClassType.InternalNonCore,
                ClassType.InternalTraining
            };

            for (int i = 0; i < 4; i++)
            {
                var day = baseDay.AddDays(1); // tomorrow
                var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
                //var classroom = this.Classrooms[i];
                var classType = types[i];
                var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
                //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
                var teacher = this.TeacherIDs[i];

                var c = GetDefaultForecast(timeslot);
                //c.ClassRoom_id = classroom.Classroom_id;
                //c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
                c.ClassCategory_id = classTypeDetail.ClassCategory_id;
                c.ClassType_id = classTypeDetail.ClassType_id;
                //c.ClassTopic_id = classTopic.ClassTopic_id;
                c.Teacher_id = teacher;
                //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
                DbHelper.InsertForecastClass(c);
            }
        }
    }
}