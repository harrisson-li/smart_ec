using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using EF.Common;
using EF.Common.Http;
using ET2.Models;

namespace ET2.Support
{
    public class TokenHelper
    {
        private static Dictionary<string, TokenHelper> CachedTokenHelper { get; set; }

        /// <summary>
        /// To get the token from secret page.
        /// </summary>
        /// <param name="env">The target environment.</param>
        /// <returns></returns>
        public static string GetToken(string envString)
        {
            if (CachedTokenHelper == null)
            {
                CachedTokenHelper = new Dictionary<string, TokenHelper>();
            }

            if (!CachedTokenHelper.ContainsKey(envString))
            {
                var tokenHelper = new TokenHelper(envString);
                CachedTokenHelper.Add(envString, tokenHelper);
            }
            return CachedTokenHelper[envString].CurrentToken.Value;
        }

        #region Implement to get token

        private string secretPage = "http://{0}.englishtown.com/services/oboe2/Areas/ServiceTest/MemberSiteSetting.aspx";

        public TokenHelper(string targetEnv)
        {
            secretPage = secretPage.FormatWith(targetEnv);
        }

        private Token _token;

        public Token CurrentToken
        {
            get
            {
                // Get new token when hour changed.
                if (_token == null || _token.RefreshHour != DateTime.Now.Hour)
                {
                    var result = HttpHelper.Get(secretPage);
                    _token = new Token
                    {
                        Value = ExtractTokenValue(result),
                        RefreshHour = DateTime.Now.Hour
                    };
                    Log.InfoFormat("Secrect token: {0}", _token.Value);
                }
                return _token;
            }
        }

        private string ExtractTokenValue(string webResponse)
        {
            // Token: <span id="token">25a3a8597d6a1fc67f68a63e159c918f</span>
            var pattern = @"Token: <span id=""token"">(?<token>.+)</span>";

            var match = Regex.Match(webResponse, pattern);
            if (match.Success)
            {
                return match.Groups[1].Value;
            }

            Log.Warn("Failed to get token from secret page");
            return "<Unknown>";
        }

        public class Token
        {
            public string Value { get; set; }

            public int RefreshHour { get; set; }
        }

        #endregion Implement to get token
    }
}