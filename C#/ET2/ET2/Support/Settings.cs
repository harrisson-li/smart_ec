using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;
using CsvHelper;
using EF.Common;
using ET2.Models;

namespace ET2.Support
{
    public static class Settings
    {
        private static string CurrentTestAccount = "Save.CurrentTestAccount";
        private static string CurrentTestEnvironment = "Save.CurrentTestEnvironment";
        private static string CurrentProduct = "Save.CurrentProduct";
        private static string UserLinks = "UsefulLinks.csv";
        private static string ProductList = "ProductList.csv";
        private static string DivisionCode = "DivisionCode.csv";
        private static string globalFolderForDebug = @"%UserProfile%\ET2_Global";

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
                var debugDir = Environment.ExpandEnvironmentVariables(globalFolderForDebug);
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

        public static void SavePersoanlSetting<T>(T settingsObj, string settingsName)
        {
            settingsName = AsPersonalFile(settingsName);
            settingsObj.SaveObject<T>(settingsName);
        }

        public static T LoadPersoanlSetting<T>(string settingsName)
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

        public static void SaveCurrentTestAccount(TestAccount obj)
        {
            SavePersoanlSetting<TestAccount>(obj, CurrentTestAccount);
        }

        public static TestAccount LoadCurrentTestAccount()
        {
            var obj = LoadPersoanlSetting<TestAccount>(CurrentTestAccount);
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

        public static void SaveCurrentTestEnvironment(TestEnvironment obj)
        {
            SavePersoanlSetting<TestEnvironment>(obj, CurrentTestEnvironment);
        }

        public static TestEnvironment LoadCurrentTestEnvironment()
        {
            var obj = LoadPersoanlSetting<TestEnvironment>(CurrentTestEnvironment);
            if (obj == null)
            {
                obj = new TestEnvironment
                {
                    Name = "UAT",
                    UrlReplacement = "uat"
                };
            }

            return obj;
        }

        public static void SaveCurrentProduct(Product obj)
        {
            SavePersoanlSetting<Product>(obj, CurrentProduct);
        }

        public static Product LoadCurrentProduct()
        {
            var obj = LoadPersoanlSetting<Product>(CurrentProduct);
            if (obj == null || obj.Name.IsNullOrEmpty())
            {
                obj = LoadProductList().First();
            }

            if (obj.DivisionCode.IsNullOrEmpty())
            {
                obj.DivisionCode = LoadDivisionCode().Where(e =>
                e.PartnerCode == obj.Partner).First().DivisionCode;
            }

            return obj;
        }

        public static Division LoadCurrentDivision()
        {
            return LoadDivisionCode()
                .Where(e => e.DivisionCode == LoadCurrentProduct().DivisionCode)
                .First();
        }

        public static List<Product> LoadProductList()
        {
            var dataFile = Path.Combine(AppDataFolder, ProductList);
            var globalFile = AsGlobalFile(ProductList);
            if (!File.Exists(globalFile))
            {
                File.Copy(dataFile, globalFile);
            }

            var table = LoadDataFromCsv(globalFile);
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
                      StartLevel = "0A"
                  }).ToList();
            return list;
        }

        public static List<UsefulLink> LoadUsefulLinks()
        {
            var dataFile = Path.Combine(AppDataFolder, UserLinks);
            var globalFile = AsGlobalFile(UserLinks);
            if (!File.Exists(globalFile))
            {
                File.Copy(dataFile, globalFile);
            }

            var table = LoadDataFromCsv(globalFile);
            var list = table.Rows.Cast<DataRow>()
                  .Select(e => new UsefulLink
                  {
                      Url = e["URL"].ToString(),
                      Description = e["Description"].ToString(),
                      Name = e["Name"].ToString(),
                      Hits = e["Hits"].ConvertValue<int>(),
                      IsHomeLink = e["IsHomeLink"].ConvertValue<bool>(),
                      IsHide = e["Hide"].ConvertValue<bool>()
                  }).ToList();
            return list;
        }

        public static List<Division> LoadDivisionCode()
        {
            var dataFile = Path.Combine(AppDataFolder, DivisionCode);
            var globalFile = AsGlobalFile(DivisionCode);
            if (!File.Exists(globalFile))
            {
                File.Copy(dataFile, globalFile);
            }

            var table = LoadDataFromCsv(globalFile);
            var list = table.Rows.Cast<DataRow>()
                  .Select(e => new Division
                  {
                      PartnerCode = e["PartnerCode"].ToString().ToLower(),
                      City = e["City"].ToString(),
                      SchoolName = e["SchoolName"].ToString(),
                      DivisionCode = e["DivisionCode"].ToString()
                  }).ToList();
            return list;
        }

        public static DataTable LoadDataFromCsv(string csvFile)
        {
            using (TextReader reader = File.OpenText(csvFile))
            {
                var csv = new CsvReader(reader);
                csv.ReadHeader();
                var headers = csv.FieldHeaders.ToList();
                var table = BuildTableWithHeaders(headers);
                while (csv.Read())
                {
                    table.Rows.Add(csv.CurrentRecord);
                }

                return table;
            }
        }

        private static DataTable BuildTableWithHeaders(List<string> listOfHeaders)
        {
            var table = new DataTable();
            foreach (string header in listOfHeaders)
            {
                table.Columns.Add(header, typeof(string));
            }
            return table;
        }
    }
}