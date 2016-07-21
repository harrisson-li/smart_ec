using System;
using System.Collections.Generic;
using System.Deployment.Application;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;

namespace ET2.Support
{
    public static class VersionHelper
    {
        /// <summary>
        /// To get current version.
        /// </summary>
        /// <returns></returns>
        public static string GetCurrentVersion()
        {
            if (ApplicationDeployment.IsNetworkDeployed)
            {
                return ApplicationDeployment
                    .CurrentDeployment.CurrentVersion.ToString();
            }
            else
            {
                return Assembly.GetEntryAssembly()
                    .GetName().Version.ToString();
            }
        }

        /// <summary>
        /// To get last version.
        /// </summary>
        /// <returns></returns>
        public static string GetLastVersion()
        {
            // try to get last version from registry
            // if not found will return empty string
            // save current version to registry at the same time
            throw new NotImplementedException();
        }

        /// <summary>
        /// To check if this is a new version.
        /// </summary>
        public static bool IsNewVersion()
        {
            return GetCurrentVersion() != GetLastVersion();
        }
    }
}