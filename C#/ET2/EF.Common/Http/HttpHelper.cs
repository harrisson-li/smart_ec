using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Web;

namespace EF.Common.Http
{
    public static class HttpHelper
    {
        /// <summary>
        /// To send a GET request.
        /// </summary>
        /// <param name="url">target</param>
        /// <returns></returns>
        public static string Get(string url)
        {
            var header = GetDefaultHeader(url);
            return new HttpRequest().Send(ref header);
        }

        /// <summary>
        /// To send a POST request.
        /// </summary>
        /// <param name="url">target url.</param>
        /// <param name="data">post data.</param>
        /// <returns></returns>
        public static string Post(string url, string data)
        {
            var header = GetDefaultHeader(url);
            header.Method = "POST";
            header.PostData = data;
            return new HttpRequest().Send(ref header);
        }

        public static string PostJson(string url, object jsonObject)
        {
            var header = GetDefaultHeader(url);
            header.Method = "POST";
            header.ContentType = "application/json";
            header.PostData = jsonObject.ToJsonString();
            return new HttpRequest().Send(ref header);
        }

        /// <summary>
        /// To send a POST request with dict post data.
        /// </summary>
        /// <param name="url">target url.</param>
        /// <param name="data">post data.</param>
        /// <returns></returns>
        public static string Post(string url, Dictionary<string, object> data)
        {
            return Post(url, ConvertDictToPostData(data));
        }

        private static string ConvertDictToPostData(Dictionary<string, object> data)
        {
            NameValueCollection qString = HttpUtility.ParseQueryString(String.Empty);
            foreach (var d in data)
            {
                qString.Add(d.Key, d.Value.ToString());
            }
            string postdata = qString.ToString();
            return postdata;
        }

        private static HttpHeader GetDefaultHeader(string url)
        {
            var uri = new Uri(url);
            var header = new HttpHeader();
            header.Host = url;
            header.Origin = uri.Host;
            header.Referer = uri.Host;
            header.Method = "GET";

            return header;
        }
    }
}