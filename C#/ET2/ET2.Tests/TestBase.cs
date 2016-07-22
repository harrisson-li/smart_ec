using System;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class TestBase
    {
        public TestContext TestContext { get; set; }

        [AssemblyInitialize]
        public static void Configure(TestContext tc)
        {
            Log.Init();
        }

        public TestBase()
        {
        }
    }
}