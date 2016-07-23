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
        private string _txt;

        public string Text
        {
            get { return this._txt; }
            set
            {
                if (value == this._txt)
                {
                    return;
                }
                this._txt = value;
                this.NotifyOfPropertyChange();
            }
        }

        private bool isBackground;

        public bool HasBackgroundTask
        {
            get { return this.isBackground; }
            set
            {
                if (value == this.isBackground)
                {
                    return;
                }
                this.isBackground = value;
                this.NotifyOfPropertyChange();
            }
        }

        public StatusInfoViewModel()
        {
            this.Text = "Ready";
        }
    }
}