using System;
using ET2.Support;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class VersionHelperTests : TestBase
    {
        [TestMethod]
        public void TestGetCurrentVersion()
        {
            var ver = VersionHelper.GetCurrentVersion();
            Log.Info(ver.Build);
            Assert.IsNotNull(ver.Build);
            Assert.IsNotNull(ver.ReleaseNote);
        }

        [TestMethod]
        public void TestGetLastVersion()
        {
            var ver = VersionHelper.GetLastVersion();
            Log.Info(ver.Build);
            Assert.IsNotNull(ver.Build);
        }
    }
}