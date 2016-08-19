using System.Collections.Generic;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using JetBrains.Annotations;

namespace ET2.Models
{
    public class Product : INotifyPropertyChanged
    {
        private int _productId;
        private string _name;
        private bool _isE10;

        public bool IsE10
        {
            get { return _isE10; }
            set
            {
                if (value == _isE10) return;
                _isE10 = value;
                OnPropertyChanged();
            }
        }

        public int Id
        {
            get { return _productId; }
            set
            {
                if (value == _productId) return;
                _productId = value;
                OnPropertyChanged();
            }
        }

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

        private string _partner;

        public string Partner
        {
            get { return _partner; }
            set
            {
                if (value == _partner) return;
                _partner = value;
                OnPropertyChanged();
            }
        }

        private string _startLv;

        public string StartLevel
        {
            get { return _startLv; }
            set
            {
                if (value == _startLv) return;
                _startLv = value;
                OnPropertyChanged();
            }
        }

        private int _lvQty;

        public int LevelQty
        {
            get { return _lvQty; }
            set
            {
                if (value == _lvQty) return;
                _lvQty = value;
                OnPropertyChanged();
            }
        }

        private string _mainRedCode;

        public string MainRedCode
        {
            get { return _mainRedCode; }
            set
            {
                if (value == _mainRedCode) return;
                _mainRedCode = value;
                OnPropertyChanged();
            }
        }

        private int _mainRedQty;

        public int MainRedQty
        {
            get { return _mainRedQty; }
            set
            {
                if (value == _mainRedQty) return;
                _mainRedQty = value;
                OnPropertyChanged();
            }
        }

        private string _freeRedCode;

        public string FreeRedCode
        {
            get { return _freeRedCode; }
            set
            {
                if (value == _freeRedCode) return;
                _freeRedCode = value;
                OnPropertyChanged();
            }
        }

        private int _freeRedQty;

        public int FreeRedQty
        {
            get { return _freeRedQty; }
            set
            {
                if (value == _freeRedQty) return;
                _freeRedQty = value;
                OnPropertyChanged();
            }
        }

        private string _dvCode;

        public string DivisionCode
        {
            get { return _dvCode; }
            set
            {
                if (value == _dvCode) return;
                _dvCode = value;
                OnPropertyChanged();
            }
        }

        private bool _isSecurityVerified;

        public bool SecurityVerified
        {
            get { return _isSecurityVerified; }
            set
            {
                if (value == _isSecurityVerified) return;
                _isSecurityVerified = value;
                OnPropertyChanged();
            }
        }

        private bool _isIncludesEnroll;

        public bool IncludesEnroll
        {
            get { return _isIncludesEnroll; }
            set
            {
                if (value == _isIncludesEnroll) return;
                _isIncludesEnroll = value;
                OnPropertyChanged();
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