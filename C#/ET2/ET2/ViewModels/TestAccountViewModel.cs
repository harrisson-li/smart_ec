using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
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
        private const string URL_CONVERT_20 = "http://{0}.englishtown.com/services/ecplatform/Tools/StudentSettings/SaveStatusFlag?id={1}&t=1468393171082";
        private const string URL_SUBMIT_SCORE = "http://{0}.englishtown.com/services/school/_tools/progress/SubmitScoreHelper.aspx";

        private List<TestAccount> _historyAccountList;

        public List<TestAccount> HistoryAccountList
        {
            get
            {
                return _historyAccountList;
            }
        }

        public void AddHistoryAccount(TestAccount testAccount = null)
        {
            if (testAccount == null)
            {
                testAccount = CurrentTestAccount;
            }

            _historyAccountList = Settings.LoadTestAccountHistory();
            _historyAccountList.Add(testAccount);

            // remove duplicate accounts by user name
            _historyAccountList = _historyAccountList
                .GroupBy(e => e.UserName)
                .Select(e => e.First()).ToList();

            this.NotifyOfPropertyChange(() => this.HistoryAccountList);

            // Save latest 20 test accounts at most
            var accountToSave = _historyAccountList.Skip(Math.Max(0, _historyAccountList.Count - 20));
            Settings.SaveTestAccountHistory(accountToSave.ToList());
        }

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
            this._historyAccountList = Settings.LoadTestAccountHistory();
        }

        /// <summary>
        /// No matter user type in name or id, we all need to get the specific test account.
        /// Implement this function by sending post data to submit score helper tool.
        /// </summary>
        /// <param name="nameOrId">Name or memmber id of the test account.</param>
        /// <returns>The test account.</returns>
        public TestAccount GetTestAccountByNameOrId(string nameOrId)
        {
            var envUrlString = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.UrlReplacement;
            var url = URL_SUBMIT_SCORE.FormatWith(envUrlString);
            var data = new Dictionary<string, object>();

            data.Add("cmd", "loadStudentInfo");
            data.Add("member_id", nameOrId);
            data.Add("token", TokenHelper.GetToken(envUrlString));

            var result = HttpHelper.Post(url, data);
            ShellViewModel.WriteStatus(result);

            try
            {
                var studentInfo = result.Split(new char[] { '|' });
                var account = new TestAccount();
                account.UserName = studentInfo[1];
                account.MemberId = studentInfo[3];
                account.AccountType = CurrentTestAccount.AccountType;
                return account;
            }
            catch (IndexOutOfRangeException)
            {
                var tips = "Environment = {0}, level initialized?".FormatWith(
                    ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.Name);
                ShellViewModel.WriteStatus("Cannot get student info: {0} ({1})".FormatWith(nameOrId, tips));
                return null;
            }
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

            // append ctr and partner when create new account
            accountUrl += "?ctr={0}&partner={1}".FormatWith(GetCountryByPartner(partner), partner);

            switch (accountType)
            {
                case AccountTypes.E10:
                    accountUrl = accountUrl.Replace("e14hz", partner);
                    break;

                case AccountTypes.S15:
                    break;

                case AccountTypes.S15_V2:
                    accountUrl += "&v=2";
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

                // save current test account to history list
                AddHistoryAccount();
            }
            else
            {
                ShellViewModel.WriteStatus(result);
            }

            Save();
        }

        public string GetCountryByPartner(string partner)
        {
            var ctr = string.Empty;

            switch (partner.ToLower())
            {
                case "cool":
                case "mini":
                    ctr = "cn";
                    break;

                case "ecsp":
                    ctr = "es";
                    break;

                case "cehk":
                    ctr = "hk";
                    break;

                case "rupe":
                    ctr = "ru";
                    break;

                case "indo":
                    ctr = "id";
                    break;

                default:
                    throw new ArgumentException("Unknown partner: {0}".FormatWith(partner));
            }
            return ctr;
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
                case AccountTypes.S15_V2:
                    url = url.Replace("ForE14HZ", "V2");
                    break;

                default:
                    throw new NotSupportedException();
            }

            var isE10 = (accountType == AccountTypes.E10);
            var result = HttpHelper.Post(url, ShellViewModel.Instance.ProductVM.GetPostData(id, isE10));
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