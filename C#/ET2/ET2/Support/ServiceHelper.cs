using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using ET2.MemberSettingsSvc;

namespace ET2.Support
{
    public class ServiceHelper
    {
        private static string configName = "BasicHttpBinding_IMemberSettingsService";
        private static string svcAddress = "http://{0}.englishtown.com/services/shared/1.0/membersettings.svc";

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
    }
}