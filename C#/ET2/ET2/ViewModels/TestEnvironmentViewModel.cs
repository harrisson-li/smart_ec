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
    public class TestEnvironmentViewModel : PropertyChangedBase
    {
        private TestEnvironment env;

        public TestEnvironment CurrentEnvironment
        {
            get { return env; }
            set
            {
                if (value == env)
                {
                    return;
                }
                this.env = value;
                this.NotifyOfPropertyChange(() => this.CurrentEnvironment);
                this.NotifyOfPropertyChange(() => this.EnvironmentSwitchText);
            }
        }

        public string EnvironmentSwitchText
        {
            get
            {
                return

                  string.Format("{0} (Switch?)", this.CurrentEnvironment.Name);
            }
        }

        public void UpdateEnvironment(string newEnvironment)
        {
            this.CurrentEnvironment = new TestEnvironment
            {
                Name = newEnvironment,
                UrlReplacement = newEnvironment.ToLower()
            };

            this.Save();
            ShellViewModel.Instance.TestAccountVM.NotifyUrlUpdate();
            ShellViewModel.Instance.UsefulLinkVM.NotifyUrlUpdate();
        }

        public TestEnvironmentViewModel()
        {
            this.CurrentEnvironment = Settings.LoadCurrentTestEnvironment();
        }

        public void Save()
        {
            Settings.SaveCurrentTestEnvironment(CurrentEnvironment);
        }
    }
}