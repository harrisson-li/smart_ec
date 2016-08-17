using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Caliburn.Micro;
using EF.Common;
using EF.Common.Http;
using ET2.Models;
using ET2.Support;

namespace ET2.ViewModels
{
    public class TestAccountViewModel : PropertyChangedBase
    {
        #region Test account functions

        private const string URL_NEW_ACCOUNT = "http://{0}.englishtown.com/services/oboe2/salesforce/test/CreateMemberFore14hz";
        private const string URL_ACTIVATE_ACCOUNT = "http://{0}.englishtown.com/services/oboe2/salesforce/test/ActivateForE14HZ";
        private const string URL_ACTIVATE_ACCOUNT_V2 = "http://{0}.englishtown.com/services/oboe2/salesforce/test/ActivateV2";
        private const string URL_CONVERT_20 = "http://{0}.englishtown.com/services/ecplatform/Tools/StudentSettings/SaveStatusFlag?id={1}&t=1468393171082";

        private TestAccount _testAccount;

        public TestAccount CurrentTestAccount
        {
            get
            {
                return _testAccount;
            }
            set
            {
                _testAccount = value;
                this.NotifyOfPropertyChange(() => this.CurrentTestAccount);
            }
        }

        public TestAccountViewModel()
        {
            this.CurrentTestAccount = Settings.LoadCurrentTestAccount();
        }

        public void GenerateAccount()
        {
            var envUrlString = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.UrlReplacement;
            var accountType = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.AccountType;
            var partner = ShellViewModel.Instance.ProductVM.CurrentPartner;
            GenerateAccount(envUrlString, accountType, partner);
        }

        public void GenerateAccount(string envUrlString, AccountTypes accountType, string partner)
        {
            var accountUrl = URL_NEW_ACCOUNT.FormatWith(envUrlString);
            switch (accountType)
            {
                case AccountTypes.E10:
                    accountUrl = accountUrl.Replace("e14hz", partner);
                    break;

                case AccountTypes.S15:
                    break;

                case AccountTypes.S15_V2:
                    accountUrl += "?v=2";
                    break;

                default:
                    throw new NotSupportedException();
            }

            var result = HttpHelper.Get(accountUrl);
            ShellViewModel.WriteStatus(result);

            var pattern = @".+studentId\: (?<id>\d+), username\: (?<name>.+), password\: (?<pw>.+)<br.+";
            var match = Regex.Match(result, pattern);
            if (match.Success)
            {
                this.CurrentTestAccount.MemberId = match.Groups["id"].Value;
                this.CurrentTestAccount.UserName = match.Groups["name"].Value;
                this.CurrentTestAccount.Password = match.Groups["pw"].Value;
            }
            else
            {
                ShellViewModel.WriteStatus(result);
            }

            Save();
        }

        public void ActivateAccount()
        {
            var envUrlString = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.UrlReplacement;
            var accountType = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.AccountType;
            var partner = ShellViewModel.Instance.ProductVM.CurrentPartner;
            ActivateAccount(envUrlString, accountType, partner);
        }

        public void ActivateAccount(string envUrlString, AccountTypes accountType, string partner)
        {
            int id = Convert.ToInt32(CurrentTestAccount.MemberId);
            var url = URL_ACTIVATE_ACCOUNT.FormatWith(envUrlString);

            switch (accountType)
            {
                case AccountTypes.E10:
                    url = url.Replace("ForE14HZ", "E10");
                    break;

                case AccountTypes.S15:
                    break;

                case AccountTypes.S15_V2:
                    url = URL_ACTIVATE_ACCOUNT_V2.FormatWith(envUrlString);
                    break;

                default:
                    throw new NotSupportedException();
            }

            var isV2 = (accountType == AccountTypes.S15_V2);
            var result = HttpHelper.Post(url, ShellViewModel.Instance.ProductVM.GetPostData(id, isV2));
            ShellViewModel.WriteStatus(result);
            Save();
        }

        public void ConvertTo20()
        {
            var id = Convert.ToInt32(CurrentTestAccount.MemberId);
            var envUrlString = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.UrlReplacement;
            ConvertTo20(id, envUrlString);
        }

        public void ConvertTo20(int id, string envUrlString)
        {
            var url = URL_CONVERT_20.FormatWith(envUrlString, id);

            var data = "studentId={0}&flag=12&value=true&IsDBOnly=false".FormatWith(id);
            var result = HttpHelper.Post(url, data);
            ShellViewModel.WriteStatus("IsEcRolloutSchoolPlatform2 = true");
        }

        public void Save()
        {
            Settings.SaveCurrentTestAccount(CurrentTestAccount);
        }

        #endregion Test account functions
    }
}