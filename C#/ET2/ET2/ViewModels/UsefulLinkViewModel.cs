using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Caliburn.Micro;
using ET2.Models;
using ET2.Support;

namespace ET2.ViewModels
{
    public class UsefulLinkViewModel : PropertyChangedBase
    {
        public List<UsefulLink> AllLinks { get; set; }

        public List<UsefulLink> HomeLinks
        {
            get
            {
                return AllLinks.Where(e => e.IsHomeLink).ToList();
            }
        }

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
            this.NotifyOfPropertyChange(() => this.HomeLinks);
            this.NotifyOfPropertyChange(() => this.GridLinks);
        }
    }
}