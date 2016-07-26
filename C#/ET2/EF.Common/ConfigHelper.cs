using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace EF.Common
{
    public static class ConfigHelper
    {
        public static string GetAppSettingsValue(string key)
        {
            return ConfigurationManager.AppSettings[key];
        }
    }
}