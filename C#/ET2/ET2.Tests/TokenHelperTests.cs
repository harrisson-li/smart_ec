using System;
using ET2.Support;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class TokenHelperTests
    {
        [TestMethod]
        public void TestGetToken()
        {
            var envList = new string[] { "uat", "qa", "staging", "webus1" };
            foreach (var env in envList)
            {
                var etown = string.Format("https://{0}.englishtown.com", env);
                var token = TokenHelper.GetToken(etown);
                Log.InfoFormat("{0}: {1}", env, token);
                Assert.AreNotEqual("<Unknown>", token);
            }
        }
    }
}