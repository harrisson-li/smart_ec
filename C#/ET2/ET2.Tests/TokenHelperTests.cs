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
                var etown = string.Format("http://{0}.englishtown.com", env) ;
                Log.InfoFormat("{0}: {1}", env, TokenHelper.GetToken(etown));
            }
        }
    }
}