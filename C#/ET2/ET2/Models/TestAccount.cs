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
    public enum AccountTypes
    {
        E10,
        S15,
        S15_V2,
        E19
    }

    public class TestAccount : INotifyPropertyChanged
    {
        private string _userName;
        private string _memberId;
        private string _password;

        private AccountTypes _accountTypes = AccountTypes.S15_V2;

        public AccountTypes AccountType
        {
            get { return _accountTypes; }
            set
            {
                if (value == _accountTypes) return;
                _accountTypes = value;
                OnPropertyChanged();
                OnPropertyChanged("IsS18");
                OnPropertyChanged("IsE19");
                OnPropertyChanged("IsV2");
                OnPropertyChanged("IsE10");
            }
        }

        public string UserName
        {
            get { return _userName; }
            set
            {
                if (value == _userName) return;
                _userName = value;
                OnPropertyChanged();
            }
        }

        [DisplayName("Member ID")]
        public string MemberId
        {
            get { return _memberId; }
            set
            {
                if (value == _memberId) return;
                _memberId = value;
                OnPropertyChanged();
            }
        }

        public string Password
        {
            get { return _password; }
            set
            {
                if (value == _password) return;
                _password = value;
                OnPropertyChanged();
            }
        }

        public bool IsE10
        {
            get { return this.AccountType == AccountTypes.E10; }
        }

        public bool IsS18
        {
            get { return this.AccountType == AccountTypes.S15_V2; }
        }

        public bool IsE19
        {
            get { return this.AccountType == AccountTypes.E19; }
        }

        public bool IsV2
        {
            get { return (this.IsS18 || this.IsE19); }
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