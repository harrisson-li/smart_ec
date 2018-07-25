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

        private bool IsClientInfoUpdated = false;
        private string ApiHost = ConfigHelper.GetAppSettingsValue("ApiHost") + "api/";
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
            try
            {
                var requestData = new { env = GetCurrentEnvironment(), username_or_id = nameOrId };
                var api = ApiHost + "get_account";
                var response = HttpHelper.PostJson(api, requestData);
                var account = response.ToJObject();
                Log.InfoFormat("Get account by name or id: {0}", response);

                if (account["member_id"] != null)
                {
                    var student = new TestAccount();
                    student.UserName = (string)account["username"];
                    student.MemberId = (string)account["member_id"];
                    student.AccountType = CurrentTestAccount.AccountType;
                    return student;
                }
            }
            catch (Exception ex)
            {
                ShellViewModel.WriteStatus("Failed! {0}".FormatWith(ex.Message));
            }

            ShellViewModel.WriteStatus("Incorrect environment or bad student, please check.");
            return null;
        }

        private string GetCurrentEnvironment()
        {
            var env = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.Name;
            if (env.StartsWith("Live"))
            {
                env = "Live";
            }

            return env;
        }

        public void GenerateAccount()
        {
            var partner = ShellViewModel.Instance.ProductVM.CurrentPartner;
            var accountType = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.AccountType;

            GenerateAccount(accountType, partner);
        }

        public void GenerateAccount(AccountTypes accountType, string partner)
        {
            var api = ApiHost + "new_account";
            var isE10 = (accountType == AccountTypes.E10);
            var requestData = new { env = GetCurrentEnvironment(), partner = partner, is_e10 = isE10 };

            try
            {
                var response = HttpHelper.PostJson(api, requestData);
                var account = response.ToJObject();

                if (account["member_id"] != null)
                {
                    Log.InfoFormat("New Account: {0}", response);

                    this.CurrentTestAccount.MemberId = (string)account["member_id"];
                    this.CurrentTestAccount.UserName = (string)account["username"];
                    this.CurrentTestAccount.Password = (string)account["password"];

                    // save current test account to history list
                    AddHistoryAccount();
                    Save();
                }
                else
                {
                    ShellViewModel.WriteStatus("Failed: {0}".FormatWith(response));
                }
            }
            catch (Exception ex)
            {
                ShellViewModel.WriteStatus("Failed: {0}".FormatWith(ex.Message));
            }
        }

        public void ActivateAccount()
        {
            var accountType = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.AccountType;
            ActivateAccount(accountType);
        }

        public void ActivateAccount(AccountTypes accountType)
        {
            var api = ApiHost + "activate_account";
            var id = Convert.ToInt32(CurrentTestAccount.MemberId);
            var username = CurrentTestAccount.UserName;
            var data = ShellViewModel.Instance.ProductVM;

            var requestData = new
            {
                env = GetCurrentEnvironment(),
                partner = data.CurrentPartner,
                is_e10 = (accountType == AccountTypes.E10),
                is_v2 = (accountType == AccountTypes.S15_V2),
                is_s18 = data.CurrentProduct.Tags.Contains("S18"),
                auto_onlineoc = data.CurrentProduct.AutoOnlineOc,
                center_pack = data.CurrentProduct.CenterPack,
                online_pack = data.CurrentProduct.OnlinePack,
                product_id = data.CurrentProduct.Id,
                school_name = data.CurrentSchool,
                student = new { member_id = id, username = username },
                startLevel = data.CurrentProduct.StartLevel,
                mainRedemptionQty = data.CurrentProduct.MainRedQty,
                freeRedemptionQty = data.CurrentProduct.FreeRedQty,
                securityverified = data.CurrentProduct.SecurityVerified ? "on" : "off",
                includesenroll = data.CurrentProduct.IncludesEnroll ? "on" : "off",
                source = "ET2 Windows"
            };

            try
            {
                var response = HttpHelper.PostJson(api, requestData);
                var account = response.ToJObject();

                if (account["member_id"] != null)
                {
                    Log.InfoFormat("Activate Account: {0}", response);
                    Save();
                }
                else
                {
                    ShellViewModel.WriteStatus("Failed: {0}".FormatWith(response));
                }
            }
            catch (Exception ex)
            {
                ShellViewModel.WriteStatus("Failed: {0}".FormatWith(ex.Message));
            }
        }

        public void Save()
        {
            Settings.SaveCurrentTestAccount(CurrentTestAccount);

            try
            {
                int id = Convert.ToInt32(CurrentTestAccount.MemberId);
                var requestData = new
                {
                    env = GetCurrentEnvironment(),
                    member_id = id,
                    created_by = Environment.UserName,
                    remove_tags = "ectools"
                };

                var api = ApiHost + "save_account";
                HttpHelper.PostJson(api, requestData);

                // save client info for ET2 web
                UpdateClientInfo();
            }
            catch (Exception ex)
            {
                ShellViewModel.WriteStatus("Failed: {0}".FormatWith(ex.Message));
            }
        }

        private void UpdateClientInfo()
        {
            if (!IsClientInfoUpdated)
            {
                var clientData = new
                {
                    hostname = Environment.MachineName,
                    username = Environment.UserName,
                    source = "ET2",
                    tags = Environment.OSVersion.VersionString
                };

                var api = ApiHost + "update_client";
                HttpHelper.PostJson(api, clientData);

                IsClientInfoUpdated = true;
            }
        }

        #endregion Test account functions
    }
}