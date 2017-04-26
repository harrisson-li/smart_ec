using System;
using System.Text.RegularExpressions;
using EF.Common;
using EF.Common.Http;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class EFCommonTests : TestBase
    {
        [TestMethod]
        public void TestHttpGetPost()
        {
            // Create new 2.0 account in UAT
            var env = "uat";
            var accountUrl = "http://{0}.englishtown.com/services/oboe2/salesforce/test/CreateMemberFore14hz?v=2".FormatWith(env);
            var result = HttpHelper.Get(accountUrl);
            TestContext.WriteLine(result);

            var pattern = @".+studentId\: (?<id>\d+), username\: (?<name>.+),";
            var match = Regex.Match(result, pattern);
            if (match.Success)
            {
                var id = match.Groups["id"].Value;
                var name = match.Groups["name"].Value;

                TestContext.WriteLine("ID: {0}\nName: {1}", id, name);

                var actUrl = "http://{0}.englishtown.com/services/oboe2/salesforce/test/ActivateV2".FormatWith(env);
                var postData = @"memberId={0}&startLevel=0B&mainRedemptionCode=I15PEMAIN+&mainRedemptionQty=3&freeRedemptionCode=I15PEF1D+&freeRedemptionQty=3&divisionCode=INDO2&productId=87&securityverified=on&includesenroll=on".FormatWith(id);

                result = HttpHelper.Post(actUrl, postData);
                TestContext.WriteLine(result);
            }
            else
            {
                Assert.Fail("Can not get new test account");
            }
        }

        [TestMethod]
        public void TestHttpPostJsonObject()
        {
            var url = "http://cns-qaauto5/api/get_account";
            var jsonObj = new { env = "UAT", member_id = 23907713 };
            var response = HttpHelper.PostJson(url, jsonObj);
            Console.WriteLine(response);
            var obj = response.ToJObject();
            Assert.AreEqual(obj["result"][0]["member_id"], 23907713);
            Assert.AreEqual(obj["result"][0]["invalid"], null);
        }

        [TestMethod]
        public void TestHttpPostJsonArray()
        {
            var url = "http://cns-qaauto5/rest/schools";
            var response = HttpHelper.Get(url);
            Console.WriteLine(response);

            var arr = response.ToJArray();
            Assert.IsTrue(arr.Count > 0);

            foreach (var item in arr)
            {
                Console.WriteLine("{0}: {1}", item["city"], item["name"]);
            }
        }
    }
}