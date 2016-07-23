using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using EF.Common;
using ET2.Support;
using JetBrains.Annotations;

namespace ET2.Models
{
    public class HostFile : INotifyPropertyChanged
    {
        private string _fullName;

        public string FullName
        {
            get { return _fullName; }
            set
            {
                if (value == _fullName) return;
                _fullName = value;
                OnPropertyChanged();
                OnPropertyChanged("Name");
                OnPropertyChanged("Content");
            }
        }

        private bool _isPrivate;

        public bool IsPrivate
        {
            get { return _isPrivate; }
            set
            {
                if (value == _isPrivate) return;
                _isPrivate = value;
                OnPropertyChanged();
            }
        }

        private bool _isActivated;

        public bool IsActivated
        {
            get { return _isActivated; }
            set
            {
                if (value == _isActivated) return;
                _isActivated = value;
                OnPropertyChanged();
            }
        }

        public string Name
        {
            get
            {
                return new FileInfo(this.FullName).Name;
            }
        }

        public string Type
        {
            get
            {
                return IsPrivate ? "Private" : "Public";
            }
        }

        public string Content
        {
            get
            {
                return File.ReadAllText(this.FullName);
            }
        }

        public void View()
        {
            var cmd = "notepad.exe {0}".FormatWith(this.FullName);
            CommandHelper.ExecuteBatch(cmd);
        }

        public void Activate()
        {
            // To activate current you must run as admin
            var cmd = "copy \"{0}\" \"{1}\" /y".FormatWith(this.FullName, Settings.GetSystemHostFile().FullName);
            CommandHelper.ExecuteBatch(cmd, asAdmin: true, waitForExit: true);

            // Verify if activated success
            if (this.Content == Settings.GetSystemHostFile().Content)
            {
                this.IsActivated = true;
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;

        [NotifyPropertyChangedInvocator]
        protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
        {
            var handler = PropertyChanged;
            if (handler != null)
            {
                handler(this, new PropertyChangedEventArgs(propertyName));
            }
        }
    }
}