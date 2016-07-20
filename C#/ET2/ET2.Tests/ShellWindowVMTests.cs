using System;
using System.Collections.Generic;
using EF.Common;
using ET2.Models;
using ET2.Support;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class ShellWindowVMTests
    {
        public TestContext TestContext { get; set; }

        [TestMethod]
        public void TestLoadProductList()
        {
            var list = Settings.LoadProductList();
            TestContext.WriteLine(list.ToJsonString().EscapeBraces());
        }

        [TestMethod]
        public void TestLoadUserfulLkins()
        {
            var list = Settings.LoadUsefulLinks();
            TestContext.WriteLine(list.ToJsonString().EscapeBraces());
        }

        [TestMethod]
        public void TestLoadDivisionCode()
        {
            var list = Settings.LoadDivisionCode();
            TestContext.WriteLine(list.ToJsonString().EscapeBraces());
        }
    }
}