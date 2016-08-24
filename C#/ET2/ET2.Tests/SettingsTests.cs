using System;
using System.IO;
using EF.Common;
using ET2.Support;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class SettingsTests : TestBase
    {
        [TestMethod]
        public void TestCommonSettings()
        {
            Assert.IsNotNull(Settings.AppFolder);
            Assert.IsTrue(Settings.AppDataFolder.Contains(Settings.AppFolder));
            Assert.IsNotNull(Settings.PersonalSettingFolder);
            Assert.IsNotNull(Settings.GlobalSettingFolder);

            var testFileName = "test";
            var personalFile = Settings.AsPersonalFile(testFileName);
            Assert.IsTrue(personalFile.Contains(Settings.PersonalSettingFolder));

            var globalFile = Settings.AsGlobalFile(testFileName);
            Assert.IsTrue(globalFile.Contains(Settings.GlobalSettingFolder));

            var now = DateTime.Now;
            Settings.SavePersonalSetting<DateTime>(now, testFileName);
            var now1 = Settings.LoadPersonalSetting<DateTime>(testFileName);
            Assert.AreEqual(now, now1);
            File.Delete(Settings.AsPersonalFile(testFileName));

            Settings.SaveGlobalSetting<DateTime>(now, testFileName);
            var now2 = Settings.LoadGlobalSetting<DateTime>(testFileName);
            Assert.AreEqual(now, now2);
            File.Delete(Settings.AsGlobalFile(testFileName));
        }

        [TestMethod]
        public void TestLoadProductList()
        {
            var list = Settings.LoadProductList();
            Log.Info(list.ToJsonString());
            Assert.IsTrue(list.Count > 0);
        }

        [TestMethod]
        public void TestLoadUserfulLkins()
        {
            var list = Settings.LoadUsefulLinks();
            Log.Info(list.ToJsonString());
            Assert.IsTrue(list.Count > 0);
        }

        [TestMethod]
        public void TestLoadDivisionCode()
        {
            var list = Settings.LoadDivisionCode();
            Log.Info(list.ToJsonString());
            Assert.IsTrue(list.Count > 0);
        }

        [TestMethod]
        public void TestLoadEnvironments()
        {
            var list = Settings.LoadEnvironments();
            Log.Info(list.ToJsonString());
            Assert.IsTrue(list.Count > 0);
        }

        [TestMethod]
        public void TestLoadFixLinks()
        {
            var list = Settings.LoadFixLinks();
            Log.Info(list.ToJsonString());
            Assert.IsTrue(list.Count > 0);
        }

        [TestMethod]
        public void TestLoadHostFiles()
        {
            var list = Settings.LoadHostFiles();
            Log.Info(list.ToJsonString());
            Assert.IsTrue(list.Count > 0);
        }

        [TestMethod]
        public void TestLoadQuickActions()
        {
            var list = Settings.LoadQuickActions();
            Log.Info(list.ToJsonString());
            Assert.IsNotNull(list);
        }
    }
}