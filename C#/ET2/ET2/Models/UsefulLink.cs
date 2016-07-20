using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using JetBrains.Annotations;

namespace ET2.Models
{
    public class UsefulLink : INotifyPropertyChanged
    {
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

        private string _url;

        public string Url
        {
            get { return _url; }
            set
            {
                if (value == _url) return;
                _url = value;
                OnPropertyChanged();
            }
        }

        private string _des;

        public string Description
        {
            get { return _des; }
            set
            {
                if (value == _des) return;
                _des = value;
                OnPropertyChanged();
            }
        }

        private int _hits;

        public int Hits
        {
            get { return _hits; }
            set
            {
                if (value == _hits) return;
                _hits = value;
                OnPropertyChanged();
            }
        }

        private bool _isHome;

        public bool IsHomeLink
        {
            get { return _isHome; }
            set
            {
                if (value == _isHome) return;
                _isHome = value;
                OnPropertyChanged();
            }
        }

        private bool _isHide;

        public bool IsHide
        {
            get { return _isHide; }
            set
            {
                if (value == _isHide) return;
                _isHide = value;
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