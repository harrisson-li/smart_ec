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

        public void UrlUpdate()
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

        public TestAccountViewModel()
        {
            this.CurrentTestAccount = Settings.LoadCurrentTestAccount();
        }

        public void GenerateAccount(string envUrlString, bool isV2)
        {
            var accountUrl = "http://{0}.englishtown.com/services/oboe2/salesforce/test/CreateMemberFore14hz".FormatWith(envUrlString);
            if (isV2)
            {
                accountUrl += "?v=2";
            }
            var result = HttpHelper.Get(accountUrl);
            ShellViewModel.Instance.StatusInfoVM.Text = result;

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
                ShellViewModel.Instance.StatusInfoVM.Text = result;
            }

            Save();
        }

        public void ActivateAccount(string envUrlString, bool isV2)
        {
            int id = Convert.ToInt32(CurrentTestAccount.MemberId);
            var url = "http://{0}.englishtown.com/services/oboe2/salesforce/test/ActivateForE14HZ".FormatWith(envUrlString);

            if (isV2)
            {
                url = "http://{0}.englishtown.com/services/oboe2/salesforce/test/ActivateV2".FormatWith(envUrlString);
            }

            var result = HttpHelper.Post(url, ShellViewModel.Instance.ProductVM.GetPostData(id, isV2));
            ShellViewModel.Instance.StatusInfoVM.Text = result;
        }

        public void ConvertTo20(string envUrlString)
        {
            int id = Convert.ToInt32(CurrentTestAccount.MemberId);
            var url = "http://{0}.englishtown.com/services/ecplatform/Tools/StudentSettings/SaveStatusFlag?id={1}&t=1468393171082"
                .FormatWith(envUrlString, id);

            var data = "studentId={0}&flag=12&value=true&IsDBOnly=false".FormatWith(id);
            var result = HttpHelper.Post(url, data);
            ShellViewModel.Instance.StatusInfoVM.Text = "IsEcRolloutSchoolPlatform2 = true";
        }

        public void Save()
        {
            Settings.SaveCurrentTestAccount(CurrentTestAccount);
        }
    }
}