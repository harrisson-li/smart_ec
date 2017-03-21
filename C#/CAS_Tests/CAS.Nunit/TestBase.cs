using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Text;

namespace CAS.Nunit
{
    public class TestBase
    {
        private static Random ran = new Random();

        public int GetRandomInt(int max = 100)
        {
            return ran.Next(max);
        }

        public static T GetConfig<T>(string key)
        {
            var str = ConfigurationManager.AppSettings[key];
            if (typeof(T) == typeof(int) || typeof(T) == typeof(string))
            {
                return (T)Convert.ChangeType(str, typeof(T));
            }
            else if (typeof(T) == typeof(List<string>))
            {
                var l = str.Split(new char[] { ',' }).ToList();
                return (T)(object)l;
            }
            else
            {
                throw new ArgumentException("Unsupported type: " + typeof(T));
            }
        }
    }
}