using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace EF.Common
{
    public class SmartWaiter
    {
        public static int DefaultTimeout = 60; // by seconds

        public static void TryWaitFor(Func<bool> delegateFunc)
        {
            var message = delegateFunc.Method.Name;
            TryWaitFor(delegateFunc, message);
        }

        public static void TryWaitFor(Func<bool> delegateFunc, string message)
        {
            TryWaitFor(delegateFunc, message, DefaultTimeout);
        }

        public static void TryWaitFor(Func<bool> delegateFunc, string message, int timeoutSecond)
        {
            var start = DateTime.Now;
            var exMessage = string.Empty;
            do
            {
                try
                {
                    if (delegateFunc())
                    {
                        return;
                    }
                }
                catch (Exception ex)
                {
                    exMessage = ex.Message;
                }
                System.Threading.Thread.Sleep(1 * 1000);
            } while (DateTime.Now - start <= TimeSpan.FromSeconds(timeoutSecond));

            if (!string.IsNullOrEmpty(exMessage))
            {
                Log.ErrorFormat("Error occurred when try {0}, Exception Message: {1}", message, exMessage);
            }

            Log.Warn(string.Format("Timeout <{0}> seconds to {1}", timeoutSecond, message));
        }

        public static void WaitFor(Func<bool> delegateFunc)
        {
            var message = delegateFunc.Method.Name;
            WaitFor(delegateFunc, message);
        }

        public static void WaitFor(Func<bool> delegateFunc, string message)
        {
            WaitFor(delegateFunc, message, DefaultTimeout);
        }

        public static void WaitFor(Func<bool> delegateFunc, string message, int timeoutSeconds)
        {
            var start = DateTime.Now;
            do
            {
                if (delegateFunc())
                {
                    return;
                }
                System.Threading.Thread.Sleep(1 * 1000);
            } while (DateTime.Now - start <= TimeSpan.FromSeconds(timeoutSeconds));

            throw new TimeoutException(string.Format("Timeout <{0}> seconds to {1}", timeoutSeconds, message));
        }
    }
}