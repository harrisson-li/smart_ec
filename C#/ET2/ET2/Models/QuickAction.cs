using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using EF.Common;
using JetBrains.Annotations;

namespace ET2.Models
{
    public enum ActionTypes
    {
        Cmd,
        Url,
        Python,
        Sql
    }

    public class QuickAction : INotifyPropertyChanged
    {
        private ActionTypes _actionType;

        public ActionTypes ActionType
        {
            get
            {
                return _actionType;
            }
            set
            {
                if (value == _actionType) return;
                _actionType = value;
                OnPropertyChanged();
            }
        }

        private string _name;

        public string Name
        {
            get { return _name; }
            set
            {
                if (value == _name) return;
                _name = value;
                OnPropertyChanged();
            }
        }

        private string _para;

        public string Parameter
        {
            get { return _para; }
            set
            {
                if (value == _para) return;
                _para = value;
                OnPropertyChanged();
            }
        }

        private string _txt;

        public string Text
        {
            get
            {
                if (_txt == null)
                {
                    return _para;
                }
                else
                {
                    return _txt;
                }
            }
            set
            {
                if (value == _txt) return;
                _txt = value;
                OnPropertyChanged();
            }
        }

        public void Perform()
        {
            Log.DebugFormat("Perform Quick Action: {0}", this.ToJsonString());
            switch (this.ActionType)
            {
                case ActionTypes.Cmd:
                    CommandHelper.ExecuteBatch(this.Text);
                    break;

                case ActionTypes.Url:
                    Process.Start(this.Text);
                    break;

                case ActionTypes.Python:
                    // TODO
                    break;

                case ActionTypes.Sql:
                    // TODO
                    break;

                default:
                    break;
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        [NotifyPropertyChangedInvocator]
        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            var handler = PropertyChanged;
            if (handler != null) handler(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}