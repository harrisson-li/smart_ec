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
    public class Forecast_Others : TestBase
    {
        [TestMethod]
        public void Forecast_NextWeek()
        {
            var day = baseDay.AddDays(7); // next week
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[0];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            var teacher = this.TeacherIDs[0];

            var c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;

            DbHelper.InsertForecastClass(c);

            classroom = this.Classrooms[1];
            classType = ClassType.F2F_Low;
            classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
            teacher = this.TeacherIDs[1];

            c = GetDefaultForecast(timeslot);
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

        [TestMethod]
        public void PerformanceLoadClass()
        {
            var nextMonday = DbHelper.GetLastMonday(DateTime.Now).AddDays(7);

            for (int i = 0; i < 7; i++) // week days
            {
                this.baseDay = nextMonday.AddDays(i);
                for (int j = 1; j < 13; j++)  // timeslot
                {
                    this.timeslotSeq = j;
                    for (int k = 0; k < 14; k++) // classroom and teacher
                    {
                        var day = baseDay; // tomorrow
                        var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
                        var classroom = this.Classrooms[k];

                        if (GetRandomInt() > 50)
                        {
                            var classType = ClassType.BeginnerA;
                            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
                            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classTypeDetail.ClassType_id);
                            var teacher = this.TeacherIDs[k];

                            var c = GetDefaultForecast(timeslot);
                            c.ClassRoom_id = classroom.Classroom_id;
                            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
                            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
                            c.ClassType_id = classTypeDetail.ClassType_id;
                            c.ClassTopic_id = classTopic.ClassTopic_id;
                            c.Teacher_id = teacher;
                            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;

                            if (GetRandomInt() > 50)
                            {
                                c.IsRandomTopic = 1;
                            }

                            DbHelper.InsertForecastClass(c);
                        }
                        else
                        {
                            var classType = ClassType.F2F_Low;
                            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
                            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
                            var teacher = this.TeacherIDs[k];

                            var c = GetDefaultForecast(timeslot);
                            c.ClassRoom_id = classroom.Classroom_id;
                            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
                            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
                            c.ClassType_id = classTypeDetail.ClassType_id;
                            //c.ClassTopic_id = classTopic.ClassTopic_id;
                            c.Teacher_id = teacher;
                            //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
                            c.IsDynamicTopic = true;

                            DbHelper.InsertForecastClass(c);
                        }
                    }
                }
            }
        }
    }
}