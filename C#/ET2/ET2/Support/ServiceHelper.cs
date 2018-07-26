using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using EF.Common;
using EF.Common.Http;
using ET2.MemberSettingsSvc;

namespace ET2.Support
{
    public class ServiceHelper
    {
        private static string configName = "BasicHttpBinding_IMemberSettingsService";
        private static string svcAddress = "http://{0}.englishtown.com/services/shared/1.0/membersettings.svc";
        private static string API_ROOT = ConfigHelper.GetAppSettingsValue("ApiHost") + "api/";

        public static bool IsPlatform2Student(int studentId, string env)
        {
            var address = string.Format(svcAddress, env);
            using (var client = new MemberSettingsServiceClient(configName, address))
            {
                var result = client.LoadMemberSiteSettings(new LoadMemberSiteSettingsParams()
                {
                    Member_id = studentId,
                    SiteArea = "school"
                });

                if (result.SiteSettings.Keys.Contains("student.platform.version"))
                {
                    return result.SiteSettings["student.platform.version"] == "2.0";
                }
            }

            return false;
        }

        public static string GetOneTips()
        {
            var url = "{0}{1}".FormatWith(API_ROOT, "give_me_joke");
            try
            {
                var response = HttpHelper.Get(url);
                return (string)response.ToJObject()["content"];
            }
            catch
            {
                // if cannot get tip via api, return default text.
                return "Working...";
            }
        }
    }
}