using System;
using ET2.Support;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class ServiceHelperTests
    {
        [TestMethod]
        public void TestIsPlatform2Student()
        {
            var envList = new string[] { "uat", "qa", "staging", "cn1web1" };
            var v2Students = new int[] { 23887469, 10813188, 14838400, 35176322 };
            for (int i = 0; i < envList.Length; i++)
            {
                var env = envList[i];
                var id = v2Students[i];
                Assert.IsTrue(ServiceHelper.IsPlatform2Student(id, env));
            }
        }
    }
}