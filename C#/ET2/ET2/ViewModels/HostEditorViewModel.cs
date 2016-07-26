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
    public class HostEditorViewModel : PropertyChangedBase
    {
        public List<HostFile> HostFileList { get; set; }

        public HostFile CurrentHost
        {
            get
            {
                var systemHost = Settings.GetSystemHostFile();
                foreach (var host in HostFileList)
                {
                    host.IsActivated = (host.Content == systemHost.Content);
                }
                return this.HostFileList.Where(e => e.IsActivated).First();
            }
        }

        public void NotifyHostChanged()
        {
            ShellViewModel.WriteStatus("Current Host: {0}".FormatWith(CurrentHost.Name));
            this.NotifyOfPropertyChange(() => this.CurrentHost);
            this.NotifyOfPropertyChange(() => this.HostFileList);
        }

        public HostEditorViewModel()
        {
            this.HostFileList = Settings.LoadHostFiles();
        }
    }
}