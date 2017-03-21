using System;
using System.Collections.Generic;
using System.Linq;
using CAS.Core;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace CAS.Tests
{
    /// <summary>
    /// Please review and update target DB, school, timeslot from app.config at first.
    /// </summary>
    [TestClass]
    public class Check_CCL : TestBase
    {
        /// <summary>
        /// check CCL enabled for expected shcools
        /// </summary>
        [TestMethod, TestCategory("CCL")]
        public void VerifyEnabledSchools()
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

        [TestMethod, Ignore, TestCategory("CCL")]
        public void EnableCAS_CCL()
        {
            // you have to recycle server
            var school = DbHelper.OBOE.OboeConfigValues
                .Where(e => e.School_id == 9 && e.Variable_id == 110).Single();
            school.School_id = 1; // Remove SH_ZSP, change to SH_PSQ
            DbHelper.OBOE.SubmitChanges();
        }

        [TestMethod, Ignore, TestCategory("CCL")]
        public void DisableCAS_CCL()
        {
            // you have to recycle server
            var school = DbHelper.OBOE.OboeConfigValues
                .Where(e => e.School_id == 1 && e.Variable_id == 110).Single();
            school.School_id = 9; // Remove SH_PSQ, change to SH_ZSP
            DbHelper.OBOE.SubmitChanges();
        }
    }
}