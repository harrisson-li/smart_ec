using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace EF.Common
{
    public static class CommandHelper
    {
        private static string GenerateTempBatch(string batchFileContent)
        {
            var tempDir = Path.GetTempPath();
            var tempScript = Path.GetTempFileName() + ".bat";
            tempScript = Path.Combine(tempDir, tempScript);
            File.WriteAllText(tempScript, batchFileContent);
            return tempScript;
        }

        public static void ExecuteBatch(string batchScriptContent)
        {
            ExecuteBatch(batchScriptContent, asAdmin: false);
        }

        public static void ExecuteBatch(string batchScriptContent, bool asAdmin)
        {
            ExecuteBatch(batchScriptContent, asAdmin, false);
        }

        public static void ExecuteBatch(string batchScriptContent, bool asAdmin, bool waitForExit)
        {
            var pInfo = new ProcessStartInfo();
            var tempScript = GenerateTempBatch(batchScriptContent);
            pInfo.FileName = tempScript;
            pInfo.UseShellExecute = true;
            pInfo.WindowStyle = ProcessWindowStyle.Hidden;
            var p = RunProcess(pInfo, asAdmin);
            if (waitForExit)
            {
                p.WaitForExit();
            }
        }

        public static Process RunProcess(ProcessStartInfo pInfo)
        {
            return RunProcess(pInfo, asAdmin: false);
        }

        public static Process RunProcess(ProcessStartInfo pInfo, bool asAdmin)
        {
            if (asAdmin)
            {
                pInfo.Verb = "runas";
                pInfo.UseShellExecute = true;
            }

            return Process.Start(pInfo);
        }
    }
}