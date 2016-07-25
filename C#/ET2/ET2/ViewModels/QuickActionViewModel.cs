using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Caliburn.Micro;
using ET2.Models;
using ET2.Support;

namespace ET2.ViewModels
{
    public class QuickActionViewModel : PropertyChangedBase
    {
        public List<QuickAction> QuickActions { get; set; }

        public QuickActionViewModel()
        {
            QuickActions = Settings.LoadQuickActions();
        }
    }
}