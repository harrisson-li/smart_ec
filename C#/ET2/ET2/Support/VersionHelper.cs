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
    }
}