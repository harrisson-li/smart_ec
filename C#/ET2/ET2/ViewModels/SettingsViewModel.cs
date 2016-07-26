using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Caliburn.Micro;
using ET2.Support;

namespace ET2.ViewModels
{
    public class SettingsViewModel : PropertyChangedBase
    {
        public string GlobalSettingsFolder
        {
            get
            {
                return Settings.GlobalSettingFolder;
            }
        }

        public string PrivateSettingsFolder
        {
            get
            {
                return Settings.PersonalSettingFolder;
            }
        }

        public string GlobalHostsFolder
        {
            get
            {
                return Path.Combine(Settings.GlobalSettingFolder, "Hosts");
            }
        }

        public string PrivateHostsFolder
        {
            get
            {
                return Path.Combine(Settings.PersonalSettingFolder, "Hosts");
            }
        }

        public void OpenFolder(string targetFolder)
        {
            Process.Start("explorer.exe", targetFolder);
        }
    }
}