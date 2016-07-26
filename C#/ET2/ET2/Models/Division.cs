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
    public class Division : INotifyPropertyChanged
    {
        private string _partnerCode;

        public string PartnerCode
        {
            get { return _partnerCode; }
            set
            {
                if (value == _partnerCode) return;
                _partnerCode = value;
                OnPropertyChanged();
            }
        }

        private string _city;

        public string City
        {
            get { return _city; }
            set
            {
                if (value == _city) return;
                _city = value;
                OnPropertyChanged();
            }
        }

        private string _schoolName;

        public string SchoolName
        {
            get { return _schoolName; }
            set
            {
                if (value == _schoolName) return;
                _schoolName = value;
                OnPropertyChanged();
            }
        }

        private string _divCode;

        public string DivisionCode
        {
            get { return _divCode; }
            set
            {
                if (value == _divCode) return;
                _divCode = value;
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