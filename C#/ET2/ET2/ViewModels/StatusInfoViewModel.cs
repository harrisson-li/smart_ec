using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Caliburn.Micro;

namespace ET2.ViewModels
{
    public class StatusInfoViewModel : PropertyChangedBase
    {
        private string txt;

        public string Text
        {
            get { return this.txt; }
            set
            {
                if (value == this.txt)
                {
                    return;
                }
                this.txt = value;
                this.NotifyOfPropertyChange(() => this.Text);
            }
        }

        public StatusInfoViewModel()
        {
            this.Text = "Ready";
        }
    }
}