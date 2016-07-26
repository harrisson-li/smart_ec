using System;
using System.IO;
using log4net;
using log4net.Config;
using log4net.Core;

public class Log
{
    private static ILog logger = null;

    /// <summary>
    /// Config log4net from app.config.
    /// </summary>
    public static void Init()
    {
        logger = LogManager.GetLogger(typeof(Log));
        XmlConfigurator.Configure();
    }

    /// <summary>
    /// Config log4net from specified xml file.
    /// </summary>
    /// <param name="log4netConfigFile"></param>
    public static void Init(string log4netConfigFile)
    {
        logger = LogManager.GetLogger(typeof(Log));
        FileInfo f = new FileInfo(log4netConfigFile);
        XmlConfigurator.ConfigureAndWatch(f);
    }

    private static ILog Instance
    {
        get
        {
            if (logger == null)
            {
                logger = LogManager.GetLogger(typeof(Log));
                string logFilePath = AppDomain.CurrentDomain.BaseDirectory + "\\Config\\log4net.xml";
                FileInfo f = new FileInfo(logFilePath);
                XmlConfigurator.ConfigureAndWatch(f);
            }
            return logger;
        }
    }

    public static bool IsDebugEnabled
    {
        get
        {
            return Instance.IsDebugEnabled;
        }
    }

    public static bool IsErrorEnabled
    {
        get
        {
            return Instance.IsErrorEnabled;
        }
    }

    public static bool IsFatalEnabled
    {
        get
        {
            return Instance.IsFatalEnabled;
        }
    }

    public static bool IsInfoEnabled
    {
        get
        {
            return Instance.IsInfoEnabled;
        }
    }

    public static bool IsWarnEnabled
    {
        get
        {
            return Instance.IsWarnEnabled;
        }
    }

    public static ILogger Logger
    {
        get
        {
            return Instance.Logger;
        }
    }

    public static void Debug(object message)
    {
        Instance.Debug(message);
    }

    public static void Debug(object message, Exception exception)
    {
        Instance.Debug(message, exception);
    }

    public static void DebugFormat(string format, params object[] args)
    {
        Instance.DebugFormat(format, args);
    }

    public static void DebugFormat(string format, object arg0)
    {
        Instance.DebugFormat(format, arg0);
    }

    public static void DebugFormat(string format, object arg0, object arg1)
    {
        Instance.DebugFormat(format, arg0, arg1);
    }

    public static void DebugFormat(IFormatProvider provider, string format,
                            params object[] args)
    {
        Instance.DebugFormat(provider, format, args);
    }

    public static void DebugFormat(string format, object arg0, object arg1,
                            object arg2)
    {
        Instance.DebugFormat(format, arg0, arg1, arg2);
    }

    public static void Error(object message)
    {
        Instance.Error(message);
    }

    public static void Error(object message, Exception exception)
    {
        Instance.Error(message, exception);
    }

    public static void ErrorFormat(string format, params object[] args)
    {
        Instance.ErrorFormat(format, args);
    }

    public static void ErrorFormat(string format, object arg0)
    {
        Instance.ErrorFormat(format, arg0);
    }

    public static void ErrorFormat(string format, object arg0, object arg1)
    {
        Instance.ErrorFormat(format, arg0, arg1);
    }

    public static void ErrorFormat(IFormatProvider provider, string format,
                            params object[] args)
    {
        Instance.ErrorFormat(provider, format, args);
    }

    public static void ErrorFormat(string format, object arg0, object arg1,
                            object arg2)
    {
        Instance.ErrorFormat(format, arg0, arg1, arg2);
    }

    public static void Fatal(object message)
    {
        Instance.Fatal(message);
    }

    public static void Fatal(object message, Exception exception)
    {
        Instance.Fatal(message, exception);
    }

    public static void FatalFormat(string format, params object[] args)
    {
        Instance.FatalFormat(format, args);
    }

    public static void FatalFormat(string format, object arg0)
    {
        Instance.FatalFormat(format, arg0);
    }

    public static void FatalFormat(string format, object arg0, object arg1)
    {
        Instance.FatalFormat(format, arg0, arg1);
    }

    public static void FatalFormat(IFormatProvider provider, string format,
                            params object[] args)
    {
        Instance.FatalFormat(provider, format, args);
    }

    public static void FatalFormat(string format, object arg0, object arg1,
                            object arg2)
    {
        Instance.FatalFormat(format, arg0, arg1, arg2);
    }

    public static void Info(object message)
    {
        Instance.Info(message);
    }

    public static void Info(object message, Exception exception)
    {
        Instance.Info(message, exception);
    }

    public static void InfoFormat(string format, params object[] args)
    {
        Instance.InfoFormat(format, args);
    }

    public static void InfoFormat(string format, object arg0)
    {
        Instance.InfoFormat(format, arg0);
    }

    public static void InfoFormat(string format, object arg0, object arg1)
    {
        Instance.InfoFormat(format, arg0, arg1);
    }

    public static void InfoFormat(IFormatProvider provider, string format,
                           params object[] args)
    {
        Instance.InfoFormat(provider, format, args);
    }

    public static void InfoFormat(string format, object arg0, object arg1,
                           object arg2)
    {
        Instance.InfoFormat(format, arg0, arg1, arg2);
    }

    public static void Warn(object message)
    {
        Instance.Warn(message);
    }

    public static void Warn(object message, Exception exception)
    {
        Instance.Warn(message, exception);
    }

    public static void WarnFormat(string format, params object[] args)
    {
        Instance.WarnFormat(format, args);
    }

    public static void WarnFormat(string format, object arg0)
    {
        Instance.WarnFormat(format, arg0);
    }

    public static void WarnFormat(string format, object arg0, object arg1)
    {
        Instance.WarnFormat(format, arg0, arg1);
    }

    public static void WarnFormat(IFormatProvider provider, string format,
                           params object[] args)
    {
        Instance.WarnFormat(provider, format, args);
    }

    public static void WarnFormat(string format, object arg0, object arg1,
                           object arg2)
    {
        Instance.WarnFormat(format, arg0, arg1, arg2);
    }
}