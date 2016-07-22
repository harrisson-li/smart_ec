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

        public List<TestEnvironment> EnvironmentList { get; set; }

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
            this.CurrentEnvironment = this.EnvironmentList
                .Where(e => e.Name.ToLower() == newEnvironment.ToLower()).Single();

            this.Save();
            ShellViewModel.Instance.TestAccountVM.NotifyUrlUpdate();
            ShellViewModel.Instance.UsefulLinkVM.NotifyUrlUpdate();
        }

        public TestEnvironmentViewModel()
        {
            this.EnvironmentList = Settings.LoadEnvironments();
            this.CurrentEnvironment = Settings.LoadCurrentTestEnvironment();
        }

        public void Save()
        {
            Settings.SaveCurrentTestEnvironment(CurrentEnvironment);
        }
    }
}