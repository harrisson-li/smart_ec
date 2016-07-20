using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace EF.Common
{
    /// <summary>
    /// A class to hold all extension methods.
    /// </summary>
    public static class ExtensionMethods
    {
        /// <summary>
        /// Same as string.Format()
        /// Example: "{0}".FormatWith(value) instead of string.Format("{0}", value)
        /// </summary>
        public static string FormatWith(this string formatedString, params object[] args)
        {
            return string.Format(formatedString, args);
        }

        /// <summary>
        /// Convert any object to JSON string.
        /// </summary>
        public static string ToJsonString<T>(this T obj)
        {
            return Newtonsoft.Json.JsonConvert.SerializeObject(obj);
        }

        /// <summary>
        /// Convert JSON string to object.
        /// </summary>
        public static T ToJsonObject<T>(this string jsonString)
        {
            return Newtonsoft.Json.JsonConvert.DeserializeObject<T>(jsonString);
        }

        public static void SaveObject<T>(this T obj, string toFile)
        {
            var json = obj.ToJsonString<T>();
            File.WriteAllText(toFile, json);
        }

        public static T LoadObject<T>(this string fromFile)
        {
            var json = File.ReadAllText(fromFile);
            return json.ToJsonObject<T>();
        }

        /// <summary>
        /// You will need to escape braces in string.Format function
        /// </summary>
        public static string EscapeBraces(this string s)
        {
            return s.Replace("{", "{{")
                    .Replace("}", "}}");
        }

        /// <summary>
        /// Convert DB value to C# value.
        /// 1. DBNull to NULL
        /// 2. Empty string to NULL
        /// 3. Others keep unchanged.
        /// </summary>
        public static object ConvertFromDBVal(this object obj)
        {
            if (obj == null || obj == DBNull.Value)
            {
                return null;
            }
            else if (obj is string)
            {
                return ((string)obj).IsNullOrEmpty() ? null : (string)obj;
            }
            else
            {
                return obj;
            }
        }

        public static bool IsNullOrEmpty(this string str)
        {
            return string.IsNullOrEmpty(str);
        }

        /// <summary>
        /// Remove last characters from string.
        /// </summary>
        /// <param name="str">The input string.</param>
        /// <param name="characters">Characters to remove.</param>
        /// <returns>The new string.</returns>
        public static string RemoveLast(this string str, int characters = 1)
        {
            return str.Remove(str.Length - characters);
        }

        /// <summary>
        /// To escape SQL characters in text, example: ' to ''
        /// </summary>
        /// <param name="columnValue">The input column value</param>
        /// <returns>The updated column value.</returns>
        public static object EscapeSqlCharaters(this object columnValue)
        {
            if (object.Equals(null, columnValue))
            {
                return columnValue;
            }
            else
            {
                return Regex.Replace(columnValue.ToString(), "'", "''");
            }
        }

        /// <summary>
        /// Convert first character to upper case.
        /// </summary>
        public static string FirstCharToUpper(this string input)
        {
            if (String.IsNullOrEmpty(input))
            {
                throw new ArgumentException("input is empty!");
            }
            return input.First().ToString().ToUpper() + input.Substring(1);
        }

        /// <summary>
        /// Get MD5 for the path if the path exist
        /// </summary>
        /// <param name="path">File path</param>
        /// <returns></returns>
        public static string GetMD5(this string filePath)
        {
            if (File.Exists(filePath))
            {
                using (var md5 = MD5.Create())
                {
                    using (var stream = File.OpenRead(filePath))
                    {
                        return Encoding.Default.GetString(md5.ComputeHash(stream));
                    }
                }
            }
            else
            {
                throw new FileNotFoundException(filePath);
            }
        }

        /// <summary>
        /// Copy current string to clipboard.
        /// </summary>
        /// <param name="str"></param>
        public static void CopyToClipboard(this string str)
        {
            if (!str.IsNullOrEmpty())
            {
                Clipboard.SetText(str);
            }
        }

        public static T ConvertValue<T>(this object value)
        {
            if (value == null)
            {
                return default(T);
            }
            else if (value.GetType() == typeof(string)
                && value.ToString().IsNullOrEmpty())
            {
                return default(T);
            }
            else
            {
                return (T)Convert.ChangeType(value, typeof(T));
            }
        }

        public static T DeepCopy<T>(this T obj)
        {
            var json = obj.ToJsonString();
            return json.ToJsonObject<T>();
        }
    }
}