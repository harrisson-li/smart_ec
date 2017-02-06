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

        [TestMethod]
        public void TestTokenReplacement()
        {
            Shell.TestEnvVM.UpdateEnvironment("qa");
            var originText = "$env $id $name $partner $school $level $accountType";
            var actualReplacedTo = Shell.UsefulLinkVM.ConvertLink(originText);
            var currentAccount = Shell.TestAccountVM.CurrentTestAccount;
            var currentProduct = Shell.ProductVM.CurrentProduct;

            Log.Info(actualReplacedTo);
            Assert.IsTrue(actualReplacedTo.Contains(currentAccount.MemberId));
            Assert.IsTrue(actualReplacedTo.Contains(currentAccount.UserName));
            Assert.IsTrue(actualReplacedTo.Contains(currentProduct.StartLevel));
            Assert.IsTrue(actualReplacedTo.Contains(currentProduct.Partner));
            Assert.IsTrue(actualReplacedTo.Contains(Shell.ProductVM.CurrentSchool));
        }
    }
}