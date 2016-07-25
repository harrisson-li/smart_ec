using System;
using EF.Common;
using ET2.Models;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class QuickActionTests : TestBase
    {
        [TestMethod]
        public void TestSaveAndRestoreQuickAction()
        {
            var action = new QuickAction();
            action.ActionType = ActionTypes.Cmd;
            action.Name = "TestAction";
            action.Parameter = "echo hello";

            var json = action.ToJsonString();
            Log.Info("Converted to: \n" + json);

            var actionBack = json.ToJsonObject<QuickAction>();
            Assert.AreEqual(action.Name, actionBack.Name);
            Assert.AreEqual(action.ActionType, actionBack.ActionType);
            Assert.AreEqual(action.Parameter, actionBack.Parameter);
        }
    }
}