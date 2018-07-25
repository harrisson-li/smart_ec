using System;
using System.Collections.Generic;
using System.Deployment.Application;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace ET2.Support
{
    public static class VersionHelper
    {
        private static ET2Version _currentVersion;

        /// <summary>
        /// Fix note line break to Windows style.
        /// </summary>
        private static void FixReleaseNote()
        {
            var note = File.ReadAllText(Settings.Data.ReleaseNote);
            if (!note.Contains("\r\n"))
            {
                note = note.Replace("\n", "\r\n");
                File.WriteAllText(Settings.Data.ReleaseNote, note);
            }
        }

        /// <summary>
        /// To get current version.
        /// </summary>
        /// <returns></returns>
        public static ET2Version GetCurrentVersion()
        {
            FixReleaseNote();

            if (_currentVersion == null)
            {
                var build = string.Empty;
                if (ApplicationDeployment.IsNetworkDeployed)
                {
                    build = ApplicationDeployment
                        .CurrentDeployment.CurrentVersion.ToString();
                }
                else
                {
                    build = Assembly.GetExecutingAssembly()
                        .GetName().Version.ToString();
                }

                var note = File.ReadAllText(Settings.Data.ReleaseNote);
                _currentVersion = new ET2Version { Build = build, ReleaseNote = note };
            }
            return _currentVersion;
        }

        private static ET2Version _lastVersion;

        /// <summary>
        /// To get last version.
        /// </summary>
        /// <returns></returns>
        public static ET2Version GetLastVersion()
        {
            // try to get last version from registry
            // if not found will return empty string
            // save current version to app folder at the same time

            if (_lastVersion == null)
            {
                var versionFile = Settings.AsPersonalFile(Settings.Data.LastVersion);
                _lastVersion = new ET2Version();

                if (File.Exists(versionFile))
                {
                    _lastVersion = Settings.LoadPersonalSetting<ET2Version>(Settings.Data.LastVersion);
                }

                var currentVersion = GetCurrentVersion();
                Settings.SavePersonalSetting<ET2Version>(currentVersion, Settings.Data.LastVersion);
            }

            return _lastVersion;
        }

        /// <summary>
        /// To check if this is a new version.
        /// </summary>
        public static bool IsNewVersion()
        {
            return GetCurrentVersion().Build != GetLastVersion().Build;
        }

        /// <summary>
        /// To check if release note changed.
        /// </summary>
        /// <returns></returns>
        public static bool IsReleaseNoteChanged()
        {
            return GetCurrentVersion().ReleaseNote != GetLastVersion().ReleaseNote;
        }

        /// <summary>
        /// Only show release note when version and note changed.
        /// </summary>
        public static void ShowReleaseNote()
        {
            Log.InfoFormat("Check version, last version - {0}, current version - {1}",
                GetLastVersion().Build, GetCurrentVersion().Build);
            if (IsNewVersion() && IsReleaseNoteChanged())
            {
                System.Diagnostics.Process.Start("notepad.exe", Settings.Data.ReleaseNote);
            }
        }

        public class ET2Version
        {
            public string Build { get; set; }

            public string ReleaseNote { get; set; }
        }
    }
}