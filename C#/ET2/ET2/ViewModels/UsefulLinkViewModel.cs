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
        public List<UsefulLink> Links { get; set; }

        public UsefulLinkViewModel()
        {
            this.Links = Settings.LoadUsefulLinks();
        }
    }
}