using System;
using System.IO;
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
            action.AsAdmin = true;

            var json = action.ToJsonString();
            Log.Info("Converted to: \n" + json);

            var actionBack = json.ToJsonObject<QuickAction>();
            Assert.AreEqual(action.Name, actionBack.Name);
            Assert.AreEqual(action.ActionType, actionBack.ActionType);
            Assert.AreEqual(action.Parameter, actionBack.Parameter);
        }

        [TestMethod]
        public void TestRunCmd()
        {
            var action = new QuickAction();
            action.ActionType = ActionTypes.Cmd;
            action.Name = "TestAction";
            action.Parameter = "ping www.englishtown.com.cn > a.txt";
            action.AsAdmin = false;
            action.WaitForExit = true;

            action.Perform();
        }

        [TestMethod]
        public void TestRunPython()
        {
            var content = @"from datetime import datetime
with open('test.txt', 'w') as f:
    for i in range(10):
        print datetime.now()
        f.write(str(datetime.now()))
";
            var pyFile = "my_test.py";
            File.WriteAllText(pyFile, content, System.Text.Encoding.UTF8);

            if (File.Exists("test.txt"))
            {
                File.Delete("test.txt");
            }

            var action = new QuickAction();
            action.ActionType = ActionTypes.Python;
            action.Name = "TestAction";
            action.Parameter = pyFile;
            action.AsAdmin = false;
            action.WaitForExit = true;

            action.Perform();

            Assert.IsTrue(File.Exists("test.txt"));
        }

        [TestMethod]
        public void TestRunPythonWithArgument()
        {
            var content = @"import sys
to_file = 'test.txt'
with open(to_file, 'w') as f:
    info = 'number of arguments: {},'.format(len(sys.argv))
    info += 'they are {}'.format(str(sys.argv))
    f.write(info)
    print info
";
            var pyFile = "my_test.py";
            File.WriteAllText(pyFile, content, System.Text.Encoding.UTF8);

            if (File.Exists("test.txt"))
            {
                File.Delete("test.txt");
            }

            var action = new QuickAction();
            action.ActionType = ActionTypes.Python;
            action.Name = "TestAction";
            action.Parameter = "\"{0}\" a b c d".FormatWith(pyFile);
            action.AsAdmin = false;
            action.WaitForExit = true;

            action.Perform();

            Assert.IsTrue(File.Exists("test.txt"));
            Log.Info(File.ReadAllText("test.txt"));
        }
    }
}