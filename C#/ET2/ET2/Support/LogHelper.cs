using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;
using EF.Common;

namespace ET2.Support
{
    public static class LogHelper
    {
        public static string CurrentLogFile
        {
            get
            {
                var tempFolder = Environment.GetEnvironmentVariable("TEMP");
                var currentProcess = Process.GetCurrentProcess();
                var logFileName = "ET2-{0}.log".FormatWith(currentProcess.Id);
                return Path.Combine(tempFolder, logFileName);
            }
        }

        public static void OpenCurrentLogFile()
        {
            Process.Start("notepad.exe", CurrentLogFile);
        }

        public static string GetCurrentLogFileContent()
        {
            return File.ReadAllText(CurrentLogFile);
        }
    }
}