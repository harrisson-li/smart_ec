using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;
using EF.Common;
using ET2.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using EF.Common.Http;

namespace ET2.Support
{
    public static class Settings
    {
        #region Constants

        private static string REST_HOST = ConfigHelper.GetAppSettingsValue("ApiHost") + "rest/";

        internal class Data
        {
            public const string TestAccountHistory = "Save.TestAccountList";
            public const string CurrentTestAccount = "Save.CurrentTestAccount";
            public const string CurrentTestEnvironment = "Save.CurrentTestEnvironment";
            public const string CurrentProduct = "Save.CurrentProduct";
            public const string LastVersion = "Save.LastVersion";
            public const string HitRecords = "Save.Hits";
            public const string GlobalFolderForDebug = @"%UserProfile%\ET2_Global";
            public const string ReleaseNote = "ReleaseNote.md";
            public const string HostFolder = "Hosts";
            public const string QuickActionFolder = "QuickActions";
        }

        internal class ApiEndpoint
        {
            public const string Partners = "partners";
            public const string Environments = "environments";
            public const string Schools = "schools";
            public const string UsefulLinks = "useful_links";
            public const string Products = "products";
            public const string WhiteList = "white_lists";
        }

        #endregion Constants

        #region Common settings

        public static JArray ReadApiData(string apiName)
        {
            var url = "{0}{1}/".FormatWith(REST_HOST, apiName);
            var response = HttpHelper.Get(url);
            return response.ToJArray();
        }

        public static string AppFolder
        {
            get

            {
                return Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            }
        }

        public static string AppDataFolder
        {
            get
            {
                return Path.Combine(AppFolder, "Data");
            }
        }

        public static string PersonalSettingFolder
        {
            get
            {
                var set = ConfigHelper.GetAppSettingsValue("PersonalSettings");
                var real = Environment.ExpandEnvironmentVariables(set);
                if (!Directory.Exists(real))
                {
                    Directory.CreateDirectory(real);
                }
                return real;
            }
        }

        public static string AsPersonalFile(string fileName)
        {
            return Path.Combine(PersonalSettingFolder, fileName);
        }

        public static string GlobalSettingFolder
        {
            get
            {
                // For debug or development purpose, we can create a local global folder.
                var debugDir = Environment.ExpandEnvironmentVariables(Data.GlobalFolderForDebug);
                if (Directory.Exists(debugDir))
                {
                    return debugDir;
                }
                else
                {
                    var set = ConfigHelper.GetAppSettingsValue("GlobalSettings");
                    var real = Environment.ExpandEnvironmentVariables(set);
                    if (!Directory.Exists(real))
                    {
                        Directory.CreateDirectory(real);
                    }
                    return real;
                }
            }
        }

        public static string AsGlobalFile(string fileName)
        {
            // if exist in personal folder, will return
            var fullName = Path.Combine(PersonalSettingFolder, fileName);
            if (File.Exists(fullName))
            {
                return fullName;
            }
            // if not, will combile the global file path
            else
            {
                return Path.Combine(GlobalSettingFolder, fileName);
            }
        }

        public static void SavePersonalSetting<T>(T settingsObj, string settingsName)
        {
            settingsName = AsPersonalFile(settingsName);
            settingsObj.SaveObject<T>(settingsName);
        }

        public static T LoadPersonalSetting<T>(string settingsName)
        {
            try
            {
                settingsName = AsPersonalFile(settingsName);
                return settingsName.LoadObject<T>();
            }
            catch (System.IO.FileNotFoundException)
            {
                return default(T);
            }
        }

        public static void SaveGlobalSetting<T>(T settingsObj, string settingsName)
        {
            settingsName = AsGlobalFile(settingsName);
            settingsObj.SaveObject<T>(settingsName);
        }

        public static T LoadGlobalSetting<T>(string settingsName)
        {
            try
            {
                settingsName = AsGlobalFile(settingsName);
                return settingsName.LoadObject<T>();
            }
            catch (System.IO.FileNotFoundException)
            {
                return default(T);
            }
        }

        #endregion Common settings

        #region Test account

        public static void SaveCurrentTestAccount(TestAccount obj)
        {
            SavePersonalSetting<TestAccount>(obj, Data.CurrentTestAccount);
        }

        public static TestAccount LoadCurrentTestAccount()
        {
            var obj = LoadPersonalSetting<TestAccount>(Data.CurrentTestAccount);
            if (obj == null)
            {
                obj = new TestAccount()
                {
                    MemberId = "Input/New",
                    UserName = "***",
                    Password = "***"
                };
            }

            return obj;
        }

        public static void SaveTestAccountHistory(List<TestAccount> obj)
        {
            SavePersonalSetting<List<TestAccount>>(obj, Data.TestAccountHistory);
        }

        public static List<TestAccount> LoadTestAccountHistory()
        {
            var obj = LoadPersonalSetting<List<TestAccount>>(Data.TestAccountHistory);
            if (obj == null)
            {
                return new List<TestAccount>();
            }

            return obj;
        }

        #endregion Test account

        #region Test environment

        private static List<TestEnvironment> _environments = null;

        public static List<TestEnvironment> LoadEnvironments()
        {
            if (_environments == null)
            {
                var data = ReadApiData(ApiEndpoint.Environments);

                _environments = data.Select(e => new TestEnvironment
                {
                    Name = (string)e["description"],
                    UrlReplacement = (string)e["replace_to"],
                    Mark = (string)e["mark"]
                }).ToList();

                // remove live environment for users not in white list
                if (!IsWhiteListUser())
                {
                    _environments = _environments.Where(e => !e.Name.ToLower().Contains("live")).ToList();
                }
            }
            return _environments;
        }

        public static void SaveCurrentTestEnvironment(TestEnvironment obj)
        {
            SavePersonalSetting<TestEnvironment>(obj, Data.CurrentTestEnvironment);
        }

        public static TestEnvironment LoadCurrentTestEnvironment()
        {
            var obj = LoadPersonalSetting<TestEnvironment>(Data.CurrentTestEnvironment);

            if (obj == null)
            {
                obj = LoadEnvironments().First();
            }
            else
            {
                // load default value for users who use et2 in live environment previously
                // but he is not white list now
                if (!IsWhiteListUser() && obj.Name.ToLower().Contains("live"))
                {
                    obj = LoadEnvironments().First();
                }
            }

            return obj;
        }

        #endregion Test environment

        #region Products

        public static void SaveCurrentProduct(Product obj)
        {
            SavePersonalSetting<Product>(obj, Data.CurrentProduct);
        }

        public static Product LoadCurrentProduct()
        {
            var obj = LoadPersonalSetting<Product>(Data.CurrentProduct);
            if (obj == null || obj.Name.IsNullOrEmpty())
            {
                obj = LoadProductList()
                    .Where(e => e.Tags.Contains("default")).First();
            }

            if (obj.DivisionCode.IsNullOrEmpty())
            {
                obj.DivisionCode = LoadDivision()
                    .Where(e => e.PartnerCode == obj.Partner)
                    .First().DivisionCode;
            }

            return obj;
        }

        private static List<Product> _productList = null;

        public static List<Product> LoadProductList()
        {
            if (_productList == null)
            {
                var data = ReadApiData(ApiEndpoint.Products);
                _productList = data.Select(e => new Product
                {
                    FreeRedCode = e["free_code"].ToString(),
                    FreeRedQty = 3,
                    Id = Convert.ToInt32(e["id"]),
                    IncludesEnroll = true,
                    LevelQty = 16,
                    MainRedCode = e["main_code"].ToString(),
                    MainRedQty = 3,
                    Name = "{0}>{1}".FormatWith(e["id"], e["name"]),
                    Partner = e["partner"].ToString().ToLower(),
                    SecurityVerified = true,
                    StartLevel = "0A",
                    IsE10 = e["tags"].ToString().Contains("E10"),
                    Tags = e["tags"].ToString()
                }).ToList();
            }
            return _productList;
        }

        #endregion Products

        #region Division code

        public static Division LoadCurrentDivision()
        {
            var isV2 = LoadCurrentTestAccount().IsV2;
            var partner = LoadCurrentProduct().Partner.ToLower();

            return LoadDivision()
                .Where(e => e.IsV2 == isV2)
                .Where(e => e.PartnerCode.ToLower() == partner)
                .First();
        }

        private static List<Division> _divisionList = null;

        public static List<Division> LoadDivision()
        {
            if (_divisionList == null)
            {
                var data = ReadApiData(ApiEndpoint.Schools);
                _divisionList = data.Select(e => new Division
                {
                    PartnerCode = e["partner"].ToString().ToLower(),
                    City = e["city"].ToString(),
                    SchoolName = e["name"].ToString(),
                    DivisionCode = e["division_code"].ToString(),
                    Tags = e["tags"].ToString()
                }).ToList();
            }
            return _divisionList;
        }

        #endregion Division code

        #region Useful links

        private static JArray _links = null;

        private static JArray LoadLinks()
        {
            if (_links == null)
            {
                _links = ReadApiData(ApiEndpoint.UsefulLinks);
            }
            return _links;
        }

        public static List<FixLink> LoadFixLinks()
        {
            var data = LoadLinks().Where(e => e["tags"].ToString().Contains("fix_link"));
            var list = data.Select(e => new FixLink
            {
                Origin = e["name"].ToString(),
                Fixed = e["url"].ToString()
            }).ToList();

            return list;
        }

        private static T GetJsonProperty<T>(string json, string propertyName, T defaultValue)
        {
            var obj = json.ToJObject();
            var value = obj[propertyName];

            if (value == null)
            {
                return defaultValue;
            }
            else
            {
                return value.Value<T>();
            }
        }

        public static List<UsefulLink> LoadUsefulLinks()
        {
            var data = LoadLinks().Where(e => e["tags"].ToString().Contains("et2"));
            var list = data.Select(e => new UsefulLink
            {
                Url = e["url"].ToString(),
                Name = e["name"].ToString(),
                Hits = 0,
                IsHomeLink = e["tags"].ToString().Contains("home"),
                IsHide = false,
                Rank = GetJsonProperty<int>(e["detail"].ToString(), "rank", 0)
            }).ToList();

            return list;
        }

        public static List<UsefulLink> LoadHomeLinks()
        {
            return LoadUsefulLinks()
                .Where(e => e.IsHomeLink)
                .OrderBy(e => e.Rank).Reverse().ToList();
        }

        public static Dictionary<string, int> LoadHitRecords()
        {
            var obj = LoadPersonalSetting<Dictionary<string, int>>(Data.HitRecords);
            if (obj == null)
            {
                obj = new Dictionary<string, int>();
            }

            return obj;
        }

        public static void SaveHitRecords(Dictionary<string, int> obj)
        {
            SavePersonalSetting<Dictionary<string, int>>(obj, Data.HitRecords);
        }

        #endregion Useful links

        #region Host files

        public static string GetSystemHostLocation()
        {
            var windir = Environment.GetFolderPath(Environment.SpecialFolder.Windows);
            return System.IO.Path.Combine(windir, @"System32\drivers\etc");
        }

        public static HostFile GetSystemHostFile()
        {
            return new HostFile
            {
                FullName = System.IO.Path.Combine(GetSystemHostLocation(), "hosts"),
                IsPrivate = true,
                IsActivated = true
            };
        }

        public static void BackupSystemHost()
        {
            var bak = "MyHost.{0}"
                .FormatWith(DateTime.Now.ToString("yyyyMMdd_HHmmss"));
            bak = Path.Combine(AsPersonalFile(Data.HostFolder), bak);

            // backup to personal host folder
            var cmd = "copy \"{0}\" \"{1}\" /y".FormatWith(GetSystemHostFile().FullName, bak);
            CommandHelper.ExecuteBatch(cmd, asAdmin: false, waitForExit: true);
        }

        public static List<HostFile> LoadHostFiles()
        {
            var builtInHosts = Path.Combine(AppDataFolder, Data.HostFolder);
            var globalHostFolder = AsGlobalFile(Data.HostFolder);
            var personalHostFolder = AsPersonalFile(Data.HostFolder);

            // copy all default settings to global folder for first time
            if (!Directory.Exists(globalHostFolder))
            {
                Directory.CreateDirectory(globalHostFolder);

                Directory.GetFiles(builtInHosts).ToList().ForEach(
                e =>
                {
                    File.Copy(e, e.Replace(builtInHosts, globalHostFolder), true);
                });
            }

            // Create persoanl host folder if not existed
            if (!Directory.Exists(personalHostFolder))
            {
                Directory.CreateDirectory(personalHostFolder);
            }

            // Copy system host file to personal folder
            File.Copy(GetSystemHostFile().FullName, Path.Combine(personalHostFolder, "SystemHost.Current"), true);

            // Create origin backup if it does not exist
            var defaultHostBackup = Path.Combine(personalHostFolder, "SystemHost.Origin");
            if (!File.Exists(defaultHostBackup))
            {
                File.Copy(GetSystemHostFile().FullName, defaultHostBackup);
            }

            var list = new List<HostFile>();
            // Load all global host files
            Directory.GetFiles(globalHostFolder, "*", SearchOption.TopDirectoryOnly)
                .ToList().ForEach(e =>
                {
                    list.Add(new HostFile
                    {
                        FullName = e,
                        IsPrivate = false
                    });
                });

            // Load all personal host files
            Directory.GetFiles(personalHostFolder, "*", SearchOption.TopDirectoryOnly)
                .ToList().ForEach(e =>
                {
                    list.Add(new HostFile
                    {
                        FullName = e,
                        IsPrivate = true
                    });
                });

            // Remove duplicate host files
            list = list.GroupBy(e => e.Content).Select(g => g.First()).ToList();

            return list;
        }

        #endregion Host files

        #region Quick actions

        /// <summary>
        /// Synchronizes the public actions to local, all users will share public actions.
        /// </summary>
        public static void SyncPublicActionsToLocal()
        {
            var publicActionFolder = Path.Combine(GlobalSettingFolder, Data.QuickActionFolder);
            var localActionFolder = Path.Combine(PersonalSettingFolder, Data.QuickActionFolder);

            if (Directory.Exists(publicActionFolder))
            {
                var cmd = @"robocopy ""{0}"" ""{1}"" /mir /r:1".FormatWith(publicActionFolder, localActionFolder);
                CommandHelper.ExecuteBatch(cmd, asAdmin: false, waitForExit: true);
            }
        }

        public static List<QuickAction> LoadQuickActions()
        {
            SyncPublicActionsToLocal();

            var actionFolder = Path.Combine(PersonalSettingFolder, Data.QuickActionFolder);
            var actionList = new List<QuickAction>();

            // Create personal quick actions folder
            if (!Directory.Exists(actionFolder))
            {
                Directory.CreateDirectory(actionFolder);
                var builtInActions = Path.Combine(AppDataFolder, Data.QuickActionFolder);

                Directory.GetFiles(builtInActions).ToList().ForEach(e =>
                {
                    File.Copy(e, e.Replace(builtInActions, actionFolder), true);
                });
            }

            // Only load action from action folder.
            if (Directory.Exists(actionFolder))
            {
                // file like *.action is self deined actions.
                foreach (var act in Directory.GetFiles(actionFolder, "*.action", SearchOption.TopDirectoryOnly))
                {
                    var json = File.ReadAllText(act);
                    actionList.Add(json.ToJsonObject<QuickAction>());
                }
            }
            return actionList.OrderBy(e => e.Name).ToList();
        }

        #endregion Quick actions

        #region WhiteList

        private static List<string> _whiteList = null;

        public static List<string> LoadWhiteList()
        {
            if (_whiteList == null)
            {
                var data = ReadApiData(ApiEndpoint.WhiteList);
                _whiteList = data.Select(e => e["username"].ToString().ToLower()).ToList();
            }

            return _whiteList;
        }

        public static bool IsWhiteListUser()
        {
            return LoadWhiteList().Contains(Environment.UserName.ToLower());
        }

        #endregion
    }
}