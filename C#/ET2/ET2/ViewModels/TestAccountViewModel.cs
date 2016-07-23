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
        #region Freqently used URL on test account view, need to move out.

        public string OBOE { get { return "http://$envoboe.ef.com/Oboe2/Login"; } }
        public string ETwon { get { return "http://$env.englishtown.com/partner/englishcenters"; } }
        public string Salesforce { get { return "https://test.salesforce.com/"; } }
        public string StudentTool { get { return "http://$env.englishtown.com/services/ecplatform/Tools/StudentSettings?id=$id"; } }
        public string SubmitScore10 { get { return "http://$env.englishtown.com/services/school/_tools/progress/SubmitScoreHelper.aspx?newengine=true&token="; } }
        public string SubmitScore20 { get { return "http://$env.englishtown.com/services/api/school/_tools/SubmitScoreHelper.aspx"; } }
        public string ClearCache { get { return "http://$env.englishtown.com/services/ecplatform/Tools/CacheClear"; } }
        public string EFErrorLog { get { return "http://errors-cn.englishtown.com/default.aspx?env=Dev"; } }
        public string QADashbord { get { return "http://jenkins.englishtown.com:8080/"; } }
        public string RedCodeRef { get { return "https://confluence.englishtown.com/display/SMart/S15+Redemptions"; } }

        public void NotifyUrlUpdate()
        {
            this.NotifyOfPropertyChange(() => this.OBOE);
            this.NotifyOfPropertyChange(() => this.ETwon);
            this.NotifyOfPropertyChange(() => this.Salesforce);
            this.NotifyOfPropertyChange(() => this.StudentTool);
            this.NotifyOfPropertyChange(() => this.SubmitScore10);
            this.NotifyOfPropertyChange(() => this.SubmitScore20);
            this.NotifyOfPropertyChange(() => this.ClearCache);
            this.NotifyOfPropertyChange(() => this.EFErrorLog);
            this.NotifyOfPropertyChange(() => this.QADashbord);
        }

        #endregion Freqently used URL on test account view, need to move out.

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
            var isV2 = this.CurrentTestAccount.IsV2;
            GenerateAccount(envUrlString, isV2);
        }

        public void GenerateAccount(string envUrlString, bool isV2)
        {
            var accountUrl = URL_NEW_ACCOUNT.FormatWith(envUrlString);
            if (isV2)
            {
                accountUrl += "?v=2";
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
            var isV2 = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.IsV2;
            ActivateAccount(envUrlString, isV2);
        }

        public void ActivateAccount(string envUrlString, bool isV2)
        {
            int id = Convert.ToInt32(CurrentTestAccount.MemberId);
            var url = URL_ACTIVATE_ACCOUNT.FormatWith(envUrlString);

            if (isV2)
            {
                url = URL_ACTIVATE_ACCOUNT_V2.FormatWith(envUrlString);
            }

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