using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Caliburn.Micro;
using EF.Common;
using ET2.Models;
using ET2.Support;

namespace ET2.ViewModels
{
    public class UsefulLinkViewModel : PropertyChangedBase
    {
        public List<UsefulLink> AllLinks { get; set; }

        public List<FixLink> FixLinks { get; set; }

        public List<UsefulLink> GridLinks
        {
            get
            {
                return AllLinks.Where(e => !e.IsHide)
                    .OrderBy(e => e.Hits).Reverse().ToList();
            }
        }

        private Dictionary<string, int> HitRecords { get; set; }

        public UsefulLinkViewModel()
        {
            this.AllLinks = Settings.LoadUsefulLinks();
            this.HitRecords = Settings.LoadHitRecords();
            this.FixLinks = Settings.LoadFixLinks();
            this.MergeHits();
        }

        public void MergeHits()
        {
            foreach (var hits in this.HitRecords)
            {
                var link = AllLinks.Where(e => e.Name == hits.Key).FirstOrDefault();
                if (link != null)
                {
                    link.Hits = hits.Value;
                }
            }
        }

        public void UpdateHits(UsefulLink currentLink)
        {
            // update in links

            currentLink.Hits++;
            NotifyUrlUpdate();

            // update in dictionary and save
            if (HitRecords.ContainsKey(currentLink.Name))
            {
                HitRecords[currentLink.Name]++;
            }
            else
            {
                HitRecords.Add(currentLink.Name, 1);
            }

            Settings.SaveHitRecords(this.HitRecords);
        }

        public void NotifyUrlUpdate()
        {
            this.NotifyOfPropertyChange(() => this.GridLinks);

            // Update link template to real link
            foreach (var link in AllLinks)
            {
                link.Text = ConvertLink(link.Url);
            }
        }

        /// <summary>
        /// To convert original URL to real URL.
        /// </summary>
        /// <param name="originUrl">An URL with token.</param>
        /// <returns></returns>
        public string ConvertLink(string originUrl)
        {
            var envString = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.UrlReplacement;
            var id = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.MemberId;
            var name = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.UserName;
            var mark = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.Mark;
            var partner = ShellViewModel.Instance.ProductVM.CurrentPartner;
            var school = ShellViewModel.Instance.ProductVM.CurrentSchool;
            var level = ShellViewModel.Instance.ProductVM.CurrentProduct.StartLevel;
            var productId = ShellViewModel.Instance.ProductVM.CurrentProduct.Id;
            var accountType = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.AccountType.ToString();

            if (!originUrl.IsNullOrEmpty())
            {
                Log.DebugFormat("Covert URL From: {0}", originUrl);

                originUrl = originUrl.Replace("$env", envString);
                originUrl = originUrl.Replace("$id", id);
                originUrl = originUrl.Replace("$name", name);
                originUrl = originUrl.Replace("$mark", mark);
                originUrl = originUrl.Replace("$partner", partner);
                originUrl = originUrl.Replace("$school", school);
                originUrl = originUrl.Replace("$level", level);
                originUrl = originUrl.Replace("$productId", productId.ToString());
                originUrl = originUrl.Replace("$accountType", accountType.ToString());
                originUrl = originUrl.Replace("$token", TokenHelper.GetToken(envString));
                originUrl = TryToFixLink(originUrl);

                Log.DebugFormat("Covert URL To: {0}", originUrl);
            }

            return originUrl;
        }

        /// <summary>
        /// Try to fix link address if found in FixLinks.csv
        /// </summary>
        /// <param name="linkAddress">Original link address.</param>
        /// <returns></returns>
        public string TryToFixLink(string linkAddress)
        {
            var fixedLink = this.FixLinks
                .Where(e => e.Origin == linkAddress).FirstOrDefault();

            if (fixedLink != null)
            {
                return fixedLink.Fixed;
            }
            else
            {
                return linkAddress;
            }
        }
    }
}