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
            var envList = new string[] { "uat", "qa", "staging", "cn1web1", "webus1" };
            foreach (var env in envList)
            {
                Log.InfoFormat("{0}: {1}", env, TokenHelper.GetToken(env));
            }
        }
    }
}