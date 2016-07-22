using System;
using System.Collections.Generic;
using EF.Common;
using ET2.Models;
using ET2.Support;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class ShellWindowVMTests : TestBase
    {
        [TestMethod]
        public void TestLoadProductList()
        {
            var list = Settings.LoadProductList();
            Log.Info(list.ToJsonString());
        }

        [TestMethod]
        public void TestLoadUserfulLkins()
        {
            var list = Settings.LoadUsefulLinks();
            Log.Info(list.ToJsonString());
        }

        [TestMethod]
        public void TestLoadDivisionCode()
        {
            var list = Settings.LoadDivisionCode();
            Log.Info(list.ToJsonString());
        }
    }
}