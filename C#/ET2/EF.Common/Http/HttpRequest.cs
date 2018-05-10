using System;
using System.Drawing;
using System.IO;
using System.Net;
using System.Text;

namespace EF.Common.Http
{
    public class HttpRequest
    {
        public CookieContainer Cookies { get; set; }

        public HttpRequest()
        {
            this.Cookies = new CookieContainer();
        }

        public string Send(ref HttpHeader header)
        {
            header.Dump();
            HttpWebResponse response = null;
            string responseString = string.Empty;

            HttpWebRequest request = (HttpWebRequest)HttpWebRequest.Create(header.Host);
            request.ProtocolVersion = new Version("1.1");
            request.Referer = header.Referer;
            request.Accept = "*/*";
            request.CookieContainer = this.Cookies;
            request.Timeout = 1000 * 60 * 5; // 5 mins
            request.Headers.Add("Accept-Language", "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4");
            request.Headers.Add("Origin", header.Origin);
            request.KeepAlive = true;
            request.UserAgent = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36";
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
            ServicePointManager.ServerCertificateValidationCallback += (sender, certificate, chain, sslPolicyErrors) => true;

            if (header.Method.ToLower() == "post")
            {
                request.Method = "POST";
                if (string.IsNullOrEmpty(header.ContentType))
                {
                    request.ContentType = "application/x-www-form-urlencoded; charset=UTF-8";
                }
                else
                {
                    request.ContentType = header.ContentType;
                }
                if (header.PostData != null && header.PostData.Length > 0)
                {
                    byte[] byteData = Encoding.Default.GetBytes(header.PostData);
                    request.ContentLength = byteData.Length;
                    Stream WriteStream = request.GetRequestStream();
                    WriteStream.Write(byteData, 0, byteData.Length);
                    WriteStream.Close();
                }
            }

            try
            {
                response = (HttpWebResponse)request.GetResponse();
                response.Dump();
            }
            catch (WebException ex)
            {
                Log.Error(ex);
                if (ex.Response != null)
                {
                    response = (HttpWebResponse)ex.Response;
                }
                else
                {
                    return ex.Message;
                }
            }

            foreach (Cookie cookie in request.CookieContainer.GetCookies(request.RequestUri))
            {
                this.Cookies.Add(cookie);
            }

            Stream dataStream = response.GetResponseStream();
            if (header.IsImage)
            {
                Bitmap img = new Bitmap(dataStream);
                header.Image = img;
            }
            else
            {
                StreamReader reader = new StreamReader(dataStream);
                responseString = reader.ReadToEnd();
                header.AbsoluteUri = response.ResponseUri.AbsoluteUri;
                reader.Close();
                dataStream.Close();
                response.Close();
                header.Html = responseString;
            }

            responseString.Dump();
            return responseString;
        }
    }
}