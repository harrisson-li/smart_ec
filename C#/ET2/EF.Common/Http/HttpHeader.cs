using System.Drawing;
using System.Net;

namespace EF.Common.Http
{
    public struct HttpHeader
    {
        public string Host;
        public string Origin;
        public string Referer;
        public CookieCollection Cookies;
        public string PostData;
        public string Method;
        public string ContentType;
        public string Html;
        public string AbsoluteUri;
        public Bitmap Image;
        public bool IsImage;
    }
}