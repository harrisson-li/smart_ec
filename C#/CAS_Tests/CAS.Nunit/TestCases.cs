using System;
using System.Collections.Generic;
using System.Linq;
using CAS.Core;
using NUnit.Framework;

namespace CAS.Nunit
{
    [TestFixture]
    public class TestCases : TestBase
    {
        private string schoolName = GetConfig<string>("School");

        private DateTime baseDay = DateTime.Today.AddDays(GetConfig<int>("BaseDay"));

        private int timeslotSeq = GetConfig<int>("TimeslotSeq");

        private List<string> enabledSchools = GetConfig<List<string>>("EnabledCenters");

        public School_lkp School { get; set; }

        public int SchoolId { get { return this.School.School_id; } }

        public List<Classroom_lkp> Classrooms { get; set; }

        public List<int> Teachers { get; set; }

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
            c.Insertby = "toby.qin.automation";
            c.Updateby = "automation";
            c.IsRandomTopic = 0;
            c.ReferenceAttendance = 0;
            return c;
        }

        public TestCases()
        {
            DbHelper.PartnerId = GetConfig<int>("PartnerSchoolId");
            this.School = DbHelper.GetSchoolByName(schoolName);
            this.Classrooms = DbHelper.GetClassroomsBySchoolId(this.School.School_id);
            this.Teachers = DbHelper.GetTeachersBySchoolId(this.School.School_id)
                .Select(e => (int)e.Teacher_id).ToList();
        }

        [Test]
        public void VerifyEnabledCenters()
        {
            var schools = DbHelper.OBOE.OboeConfigValues
                .Where(e => e.Variable_id == 110)
                .OrderBy(e => e.School_id);
            Assert.AreEqual(schools.Count(), this.enabledSchools.Count);
            for (int i = 0; i < schools.Count(); i++)
            {
                var id = schools.ToList()[i].School_id;
                var found = DbHelper.OBOE.School_lkps
                   .Where(e => e.School_id == id).Single();
                Console.WriteLine(found.SchoolName);
                Assert.AreEqual(enabledSchools[i], found.SchoolName);
            }
        }

        [Test, Ignore]
        public void EnableCAS_CCL()
        {
            // you have to recycle server
            var school = DbHelper.OBOE.OboeConfigValues
                .Where(e => e.School_id == 9 && e.Variable_id == 110).Single();
            school.School_id = 1; // change to SH_PSQ
            DbHelper.OBOE.SubmitChanges();
        }

        [Test, Ignore]
        public void DisableCAS_CCL()
        {
            // you have to recycle server
            var school = DbHelper.OBOE.OboeConfigValues
                .Where(e => e.School_id == 1 && e.Variable_id == 110).Single();
            school.School_id = 9; // change to SH_ZSP
            DbHelper.OBOE.SubmitChanges();
        }

        [Test, Category("Tool")]
        public void MarkForecastAsBug()
        {
            var id = GetConfig<int>("MarkForecastAsBug");
            var c = DbHelper.OBOE.ScheduledClassForecasts
                .Where(e => e.ScheduledClass_id == id).Single();
            c.Insertby = "mark.bug";
            DbHelper.OBOE.SubmitChanges();
        }

        [Test, Category("Tool")]
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

        [Test, Category("Tool")]
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

        [Test, Category("Tool")]
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

        [Test, Category("Tool")]
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

        [Test, Category("WS")]
        public void Forecast_WS()
        {
            var index = 0;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("WS")]
        public void Forecast_WS_FixClass()
        {
            var index = 0;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("WS")]
        public void Forecast_WS_EmptyTeacherID()
        {
            var index = 1;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
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

        [Test, Category("WS")]
        public void Forecast_WS_Yesterday()
        {
            var index = 2;
            var day = baseDay.AddDays(-1); // yesterday
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("WS")]
        public void Forecast_WS_RandomTopic()
        {
            var index = 2;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("WS")]
        public void Forecast_WS_NoScheduledTopic()
        {
            var index = 4;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("WS")]
        public void Forecast_WS_OldScheduledTopic()
        {
            var index = 5;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-20), classType, dayRange: 14);
            var teacher = this.Teachers[index];

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

        [Test, Category("WS")]
        public void Forecast_WS_FutureScheduledTopic()
        {
            var index = 3;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(7), classType, dayRange: 30);
            var teacher = this.Teachers[index];

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

        [Test, Category("Preview")]
        public void Forecast_Preview()
        {
            var index = 0;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetPreviewTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            c.IsPreview = 1;

            DbHelper.InsertForecastClass(c);
        }

        [Test, Category("Preview")]
        public void Forecast_Preview_EmptyTeacher()
        {
            var index = 1;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetPreviewTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            //var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            //c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            c.IsPreview = 1;

            DbHelper.InsertForecastClass(c);
        }

        [Test, Category("Preview")]
        public void Forecast_Preview_RandomTopic()
        {
            var index = 2;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetPreviewTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            c.IsPreview = 1;
            c.IsRandomTopic = 1;
            c.IsFixedClass = 0;

            DbHelper.InsertForecastClass(c);
        }

        [Test, Category("Preview")]
        public void Forecast_Preview_NoScheduleTopic()
        {
            var index = 3;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetPreviewTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            //c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            c.IsPreview = 1;

            DbHelper.InsertForecastClass(c);
        }

        [Test, Category("Preview")]
        public void Forecast_Preview_Yesterday()
        {
            var index = 4;
            var day = baseDay.AddDays(-1); // tomorrow
            var timeslot = DbHelper.GetPreviewTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            c.IsPreview = 1;

            DbHelper.InsertForecastClass(c);
        }

        [Test, Category("F2F")]
        public void Forecast_F2F()
        {
            var index = 0;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_Low;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("F2F")]
        public void Forecast_F2F_FixedClass()
        {
            var index = 0;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_Low;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("F2F")]
        public void Forecast_F2F_EmptyTopic()
        {
            var index = 1;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_High;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("F2F")]
        public void Forecast_F2F_EmptyTeacherID()
        {
            var index = 2;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_Low;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
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

        [Test, Category("F2F")]
        public void Forecast_F2F_BadTeacherId_Existed()
        {
            var index = 3;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_Low;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
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

        [Test, Category("F2F")]
        public void Forecast_F2F_BadTeacherId_NotExisted()
        {
            var index = 4;
            var day = baseDay.AddDays(1); // tomorrow
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[index];
            var classType = ClassType.F2F_Low;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
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

        [Test, Category("Apply")]
        public void Forecast_Apply()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 1;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.ArtsHigh;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("Apply")]
        public void Forecast_Apply_EmptyTeacherId()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 2;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.ArtsLow;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            //var teacher = this.Teachers[index];

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

        [Test, Category("BF")]
        public void Forecast_BeginnerFoundation()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 0;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerFoundationA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("BF")]
        public void Forecast_BeginnerFoundation_BadClassroom_NotExist()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 1;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classType = ClassType.BeginnerFoundationA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);

            c.ClassRoom_id = -100;
            c.ClassroomPhysicalCapacity = 2;
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;

            DbHelper.InsertForecastClass(c);
        }

        [Test, Category("BF")]
        public void Forecast_BeginnerFoundation_BadClassroom_Exist()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 2;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classType = ClassType.BeginnerFoundationA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);

            c.ClassRoom_id = 60;
            c.ClassroomPhysicalCapacity = 2;
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;

            DbHelper.InsertForecastClass(c);
        }

        [Test, Category("BB")]
        public void Forecast_BeginnerBasic()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 3;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerBasics;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("BB")]
        public void Forecast_BeginnerBasic_RandomTopic()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 4;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerBasics;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("BB")]
        public void Forecast_BeginnerBasic_EmptyTeacherId()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 5;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.BeginnerBasics;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
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

        [Test, Category("CA")]
        public void Forecast_CASeminar()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 0;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.CASeminarElem;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

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

        [Test, Category("CA")]
        public void Forecast_CASeminar_EmptyTeacher()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 1;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.CASeminarElem;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
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

        [Test, Category("Internal")]
        public void Forecast_Internal_ILab()
        {
            var day = baseDay.AddDays(1); // tomorrow
            var index = 0;
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq);
            var classroom = this.Classrooms[index];
            var classType = ClassType.InternalSalesSpecial;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[index];

            var c = GetDefaultForecast(timeslot);
            c.ClassRoom_id = classroom.Classroom_id;
            c.ClassroomPhysicalCapacity = Convert.ToInt16(classroom.DefaultPhysicalCapacity);
            c.ClassCategory_id = classTypeDetail.ClassCategory_id;
            c.ClassType_id = classTypeDetail.ClassType_id;
            //c.ClassTopic_id = classTopic.ClassTopic_id;
            c.Teacher_id = teacher;
            //c.ScheduledClassTopic_id = classTopic.ScheduledClassTopic_id;
            DbHelper.InsertForecastClass(c);

            index++;  // empty teacher id for this type should be higlighted

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

            index++;  // empty classroom for this type should be showed in teacher page

            //classroom = this.Classrooms[index];
            //var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            teacher = this.Teachers[index];

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

        [Test, Category("Internal")]
        public void Forecast_Internal()
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
                var teacher = this.Teachers[i];

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

        [Test, Category("Internal")]
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
                var teacher = this.Teachers[i];

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

        [Test, Category("Internal")]
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
                var teacher = this.Teachers[i];

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

        [Test]
        public void Forecast_NextWeek()
        {
            var day = baseDay.AddDays(7); // next week
            var timeslot = DbHelper.GetTimeslot(day: day, seq: timeslotSeq); // first timeslot
            var classroom = this.Classrooms[0];
            var classType = ClassType.BeginnerA;
            var classTypeDetail = DbHelper.GetClassTypeDetail(classType);
            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            var teacher = this.Teachers[0];

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
            classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
            teacher = this.Teachers[1];

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

        [Test]
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
                            var classTopic = DbHelper.GetScheduledClassTopic(day.AddDays(-1), classType);
                            var teacher = this.Teachers[k];

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
                            var teacher = this.Teachers[k];

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