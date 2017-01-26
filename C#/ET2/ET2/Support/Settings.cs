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

namespace ET2.Support
{
    public static class Settings
    {
        #region Constants

        internal class Data
        {
            public const string TestAccountHistory = "Save.TestAccountList";
            public const string CurrentTestAccount = "Save.CurrentTestAccount";
            public const string CurrentTestEnvironment = "Save.CurrentTestEnvironment";
            public const string CurrentProduct = "Save.CurrentProduct";
            public const string LastVersion = "Save.LastVersion";
            public const string HitRecords = "Save.Hits";
            public const string UserLinks = "UsefulLinks.csv";
            public const string ProductList = "ProductList.csv";
            public const string DivisionCode = "DivisionCode.csv";
            public const string FixLinks = "FixLinks.csv";
            public const string Envrionments = "Environments.csv";
            public const string WhiteList = "WhiteList.csv";
            public const string GlobalFolderForDebug = @"%UserProfile%\ET2_Global";
            public const string ReleaseNote = "ReleaseNote.md";
            public const string HostFolder = "Hosts";
            public const string QuickActionFolder = "QuickActions";
        }

        #endregion Constants

        #region Common settings

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

        public static List<TestEnvironment> LoadEnvironments()
        {
            var dataFile = Path.Combine(AppDataFolder, Data.Envrionments);
            var globalFile = AsGlobalFile(Data.Envrionments);
            if (!File.Exists(globalFile))
            {
                File.Copy(dataFile, globalFile);
            }

            var table = CsvHelper.LoadDataFromCsv(globalFile);
            var list = table.Rows.Cast<DataRow>()
                  .Select(e => new TestEnvironment
                  {
                      Name = (string)e["Name"],
                      UrlReplacement = (string)e["Replacement"],
                      Mark = (string)e["Mark"]
                  }).ToList();

            // remove live environment for users not in white list
            if (!IsWhiteListUser())
            {
                list = list.Where(e => !e.Name.ToLower().Contains("live")).ToList();
            }
            return list;
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
                // for users who launch et2 in live environment, but now he is not white list
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
                obj = LoadProductList().First();
            }

            if (obj.DivisionCode.IsNullOrEmpty())
            {
                obj.DivisionCode = LoadDivision().Where(e =>
                e.PartnerCode == obj.Partner).First().DivisionCode;
            }

            return obj;
        }

        public static List<Product> LoadProductList()
        {
            var dataFile = Path.Combine(AppDataFolder, Data.ProductList);
            var globalFile = AsGlobalFile(Data.ProductList);
            if (!File.Exists(globalFile))
            {
                File.Copy(dataFile, globalFile);
            }

            var table = CsvHelper.LoadDataFromCsv(globalFile);
            var list = table.Rows.Cast<DataRow>()
                  .Select(e => new Product
                  {
                      FreeRedCode = e["FreeRedCode"].ToString(),
                      FreeRedQty = 3,
                      Id = Convert.ToInt32(e["Product_id"]),
                      IncludesEnroll = true,
                      LevelQty = 16,
                      MainRedCode = e["MainRedCode"].ToString(),
                      MainRedQty = 3,
                      Name = e["PackageName"].ToString(),
                      Partner = e["PartnerCode"].ToString().ToLower(),
                      SecurityVerified = true,
                      StartLevel = "0A",
                      IsE10 = e["E10"].ConvertValue<bool>()
                  }).ToList();
            return list;
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

        public static List<Division> LoadDivision()
        {
            var dataFile = Path.Combine(AppDataFolder, Data.DivisionCode);
            var globalFile = AsGlobalFile(Data.DivisionCode);
            if (!File.Exists(globalFile))
            {
                File.Copy(dataFile, globalFile);
            }

            var table = CsvHelper.LoadDataFromCsv(globalFile);
            var list = table.Rows.Cast<DataRow>()
                  .Select(e => new Division
                  {
                      PartnerCode = e["PartnerCode"].ToString().ToLower(),
                      City = e["City"].ToString(),
                      SchoolName = e["SchoolName"].ToString(),
                      DivisionCode = e["DivisionCode"].ToString(),
                      Tags = e["Tags"].ToString()
                  }).ToList();
            return list;
        }

        #endregion Division code

        #region Useful links

        public static List<FixLink> LoadFixLinks()
        {
            var dataFile = Path.Combine(AppDataFolder, Data.FixLinks);
            var globalFile = AsGlobalFile(Data.FixLinks);
            if (!File.Exists(globalFile))
            {
                File.Copy(dataFile, globalFile);
            }

            var table = CsvHelper.LoadDataFromCsv(globalFile);
            var list = table.Rows.Cast<DataRow>()
                  .Select(e => new FixLink
                  {
                      Origin = e["Origin"].ToString(),
                      Fixed = e["Fixed"].ToString()
                  }).ToList();
            return list;
        }

        public static List<UsefulLink> LoadUsefulLinks()
        {
            var dataFile = Path.Combine(AppDataFolder, Data.UserLinks);
            var globalFile = AsGlobalFile(Data.UserLinks);
            if (!File.Exists(globalFile))
            {
                File.Copy(dataFile, globalFile);
            }

            var table = CsvHelper.LoadDataFromCsv(globalFile);
            var list = table.Rows.Cast<DataRow>()
                  .Select(e => new UsefulLink
                  {
                      Url = e["URL"].ToString(),
                      Description = e["Description"].ToString(),
                      Name = e["Name"].ToString(),
                      Hits = e["Hits"].ConvertValue<int>(),
                      IsHomeLink = e["IsHomeLink"].ConvertValue<bool>(),
                      IsHide = e["Hide"].ConvertValue<bool>(),
                      Rank = e["Rank"].ConvertValue<int>()
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

        public static List<string> LoadWhiteList()
        {
            var dataFile = Path.Combine(AppDataFolder, Data.WhiteList);
            var globalFile = AsGlobalFile(Data.WhiteList);
            if (!File.Exists(globalFile))
            {
                File.Copy(dataFile, globalFile);
            }

            var table = CsvHelper.LoadDataFromCsv(globalFile);
            var list = table.Rows.Cast<DataRow>()
                  .Select(e => e["UserName"].ToString().ToLower())
                  .ToList();
            return list;
        }

        public static bool IsWhiteListUser()
        {
            return LoadWhiteList().Contains(Environment.UserName.ToLower());
        }

        #endregion
    }
}