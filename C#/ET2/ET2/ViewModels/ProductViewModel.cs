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
    public class ProductViewModel : PropertyChangedBase
    {
        #region Partner filters

        private string _partner = Settings.LoadCurrentProduct().Partner;
        private bool _isV2 = Settings.LoadCurrentTestAccount().IsV2;

        public void NotifySchoolUpdate()
        {
            _isV2 = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.IsV2;
            this.NotifyOfPropertyChange(() => this.ProductCityList);
            this.NotifyOfPropertyChange(() => this.ProductSchoolList);
            this.NotifyOfPropertyChange(() => this.CurrentCity);
            this.NotifyOfPropertyChange(() => this.CurrentSchool);
        }

        public string CurrentPartner
        {
            get
            {
                return _partner.ToLower();
            }
            set
            {
                if (_partner == value || _partner.IsNullOrEmpty())
                {
                    return;
                }
                _partner = value;
                var prod = ProductList
                    .Where(e => e.Partner == CurrentPartner)
                    .First().DeepCopy();
                CurrentProduct = prod;
                ProductName = prod.Name;

                this.NotifyOfPropertyChange();
                this.NotifyOfPropertyChange(() => this.ProductNameList);
                this.NotifyOfPropertyChange(() => this.ProductMainRedCodeList);
                this.NotifyOfPropertyChange(() => this.ProductFreeRedCodeList);
                this.NotifyOfPropertyChange(() => this.ProductCityList);
                this.CurrentCity = this.ProductCityList.First();
            }
        }

        public List<string> PartnerList
        {
            get
            {
                return new List<string>() { "cool", "mini", "cehk", "rupe", "indo", "ecsp" };
            }
        }

        #endregion Partner filters

        #region Product filters

        private string _name = Settings.LoadCurrentProduct().Name;

        public string ProductName
        {
            get
            {
                return this._name;
            }
            set
            {
                if (value == this._name || value.IsNullOrEmpty())
                {
                    return;
                }

                if (ProductList.Where(e => e.Name == _name).Count() == 0)
                {
                    return;
                }

                this._name = value;
                var prod = ProductList
                    .Where(e => e.Name == _name)
                    .Single().DeepCopy();
                this.CurrentProduct.Id = prod.Id;
                this.CurrentProduct.Name = prod.Name;
                this.CurrentProduct.Partner = prod.Partner;
                this.CurrentProduct.MainRedCode = prod.MainRedCode;
                this.CurrentProduct.FreeRedCode = prod.FreeRedCode;
                this.NotifyOfPropertyChange();
            }
        }

        private List<Product> _productList;

        public List<Product> ProductList
        {
            get
            {
                if (_productList == null)
                {
                    _productList = Settings.LoadProductList();
                }
                return _productList;
            }
        }

        private Product _prod;

        public Product CurrentProduct
        {
            get
            {
                return _prod;
            }
            set
            {
                _prod = value;
                this.NotifyOfPropertyChange(() => this.CurrentProduct);
            }
        }

        public List<string> ProductNameList
        {
            get
            {
                return ProductList
                    .Where(e => e.Partner == CurrentPartner)
                    .Select(e => e.Name).ToList();
            }
        }

        public List<string> ProductStartLevelList
        {
            get
            {
                return new List<string>() { "0A", "0B" }
                .Concat(Enumerable.Range(1, 14)
                .Select(e => e.ToString())).ToList();
            }
        }

        public List<string> ProductMainRedCodeList
        {
            get
            {
                return ProductList
                    .Where(e => e.Partner == CurrentPartner)
                    .Select(e => e.MainRedCode).ToList();
            }
        }

        public List<string> ProductFreeRedCodeList
        {
            get
            {
                return ProductList
                    .Where(e => e.Partner == CurrentPartner)
                    .Select(e => e.FreeRedCode).ToList();
            }
        }

        #endregion Product filters

        #region City, School and Division Code filters

        private string _city = Settings.LoadCurrentDivision().City;

        public string CurrentCity
        {
            get
            {
                return _city;
            }
            set
            {
                if (_city == value || value.IsNullOrEmpty())
                {
                    return;
                }
                _city = value;

                // when city changed, need to update div code and school list and div list
                var div = DivisionList
                    .Where(e => e.City == value).First();
                CurrentProduct.DivisionCode = div.DivisionCode;

                this.NotifyOfPropertyChange();
                this.NotifyOfPropertyChange(() => this.ProductSchoolList);
                CurrentSchool = div.SchoolName;
            }
        }

        private string _school = Settings.LoadCurrentDivision().SchoolName;

        public string CurrentSchool
        {
            get
            {
                return _school;
            }
            set
            {
                if (_school == value || value.IsNullOrEmpty())
                {
                    return;
                }
                _school = value;

                // when school changed, need to update div code and div list
                var div = DivisionList
                    .Where(e => e.SchoolName == value).First();
                CurrentProduct.DivisionCode = div.DivisionCode;
                ShellViewModel.WriteStatus("Division Code = {0}".FormatWith(div.DivisionCode));

                //this.NotifyOfPropertyChange(() => this.DivisionList);
                this.NotifyOfPropertyChange();
            }
        }

        private List<Division> _divList;

        public List<Division> DivisionList
        {
            get
            {
                if (_divList == null)
                {
                    _divList = Settings.LoadDivision();
                }
                return _divList;
            }
        }

        public List<string> ProductDivisionCodeList
        {
            get
            {
                return DivisionList
                    .Where(e => e.City == CurrentCity)
                    .Select(e => e.DivisionCode).ToList();
            }
        }

        public List<string> ProductCityList
        {
            get
            {
                return DivisionList
                    .Where(e => e.PartnerCode == CurrentPartner)
                    .Where(e => e.IsV2 == _isV2)
                    .Select(e => e.City).Distinct().ToList();
            }
        }

        public List<string> ProductSchoolList
        {
            get
            {
                return DivisionList
                    .Where(e => e.City == CurrentCity)
                    .Where(e => e.IsV2 == _isV2)
                    .Select(e => e.SchoolName).Distinct().ToList();
            }
        }

        #endregion City, School and Division Code filters

        public ProductViewModel()
        {
            this.CurrentProduct = Settings.LoadCurrentProduct();
        }

        public Dictionary<string, object> GetPostData(int memberId, bool isV2)
        {
            var postData = new Dictionary<string, object>();

            postData.Add("memberId", memberId);
            postData.Add("startLevel", CurrentProduct.StartLevel);
            postData.Add("mainRedemptionCode", CurrentProduct.MainRedCode);
            postData.Add("mainRedemptionQty", CurrentProduct.MainRedQty);
            postData.Add("freeRedemptionCode", CurrentProduct.FreeRedCode);
            postData.Add("freeRedemptionQty", CurrentProduct.FreeRedQty);
            postData.Add("divisionCode", CurrentProduct.DivisionCode);
            postData.Add("productId", CurrentProduct.Id);
            if (CurrentProduct.SecurityVerified)
            {
                postData.Add("securityverified", "on");
            }

            if (isV2)
            {
                if (CurrentProduct.IncludesEnroll)
                {
                    postData.Add("includesenroll", "on");
                }
            }
            else
            {
                postData.Add("levelQty", CurrentProduct.LevelQty);
            }

            return postData;
        }

        public void Save()
        {
            Settings.SaveCurrentProduct(CurrentProduct);
        }
    }
}