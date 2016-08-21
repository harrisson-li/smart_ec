using System;
using System.Collections.Generic;
using EF.Common;
using ET2.Models;
using ET2.Support;
using ET2.ViewModels;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class ViewModelTests : TestBase
    {
        public ShellViewModel Shell { get; set; }

        public ViewModelTests()
        {
            ShellViewModel.InitForTest();
            Shell = ShellViewModel.Instance;
        }

        [TestMethod]
        public void TestGetAccountInfoByName()
        {
            var name = "ctest2515";
            Shell.TestEnvVM.UpdateEnvironment("qa");
            var account = Shell.TestAccountVM.GetTestAccountByNameOrId(name);
            Assert.AreEqual(name, account.UserName);
            Assert.AreEqual("1", account.Password);
        }

        [TestMethod]
        public void TestGetAccountInfoById()
        {
            var id = "10777008";
            Shell.TestEnvVM.UpdateEnvironment("qa");
            var account = Shell.TestAccountVM.GetTestAccountByNameOrId(id);
            Assert.AreEqual(id, account.MemberId);
            Assert.AreEqual("1", account.Password);
        }

        [TestMethod]
        public void TestGetAccountInfoByInvalid()
        {
            var id = "invalid";
            Shell.TestEnvVM.UpdateEnvironment("qa");
            var account = Shell.TestAccountVM.GetTestAccountByNameOrId(id);
            Assert.AreEqual(null, account);
        }
    }
}