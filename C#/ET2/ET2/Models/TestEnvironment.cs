using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using Caliburn.Micro;
using JetBrains.Annotations;

namespace ET2.Models
{
    public class TestEnvironment : INotifyPropertyChanged
    {
        private string _name;

        /// <summary>
        /// The name of test environment.
        /// </summary>
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

        private string _url;

        /// <summary>
        /// Replacement string on current environment.
        /// </summary>
        public string UrlReplacement
        {
            get { return _url; }
            set
            {
                if (value == _url) return;
                _url = value;
                OnPropertyChanged();
            }
        }

        private string _mark;

        /// <summary>
        /// Special mark for this environment.
        /// </summary>
        public string Mark
        {
            get { return _mark; }
            set
            {
                if (value == _mark) return;
                _mark = value;
                OnPropertyChanged();
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