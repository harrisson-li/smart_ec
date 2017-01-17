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
        private string _partner = Settings.LoadCurrentProduct().Partner;
        private bool _isV2 = Settings.LoadCurrentTestAccount().IsV2;
        private bool _isE10 = Settings.LoadCurrentTestAccount().IsE10;

        /// <summary>
        /// When account type changed, will call this method.
        /// </summary>
        public void NotifyAccountTypeChanged()
        {
            // get current account status
            _isV2 = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.IsV2;
            _isE10 = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.IsE10;

            // update city list
            this.NotifyOfPropertyChange(() => this.ProductCityList);
            var existSchool = this.DivisionList
                .Where(e => e.PartnerCode == CurrentPartner)
                .Where(e => e.City == CurrentCity)
                .Where(e => e.IsV2 == _isV2)
                .Count() > 0;

            // update current city only if there is matched schools
            if (!existSchool)
            {
                var school = this.DivisionList
                    .Where(e => e.PartnerCode == CurrentPartner)
                    .Where(e => e.IsV2 == _isV2).First();
                this.CurrentCity = school.City;
            }

            // update school list and school name
            this.NotifyOfPropertyChange(() => this.ProductSchoolList);
            this.CurrentSchool = this.ProductSchoolList.First();

            // update product for e10 student
            this.NotifyOfPropertyChange(() => this.ProductNameList);
            this.ProductName = this.ProductNameList.First();
        }

        #region Partner filters

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

                this.NotifyOfPropertyChange();
                this.NotifyOfPropertyChange(() => this.ProductNameList);
                this.NotifyOfPropertyChange(() => this.ProductCityList);
                this.CurrentCity = this.ProductCityList.First();
                this.ProductName = this.ProductNameList.First();
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
                var prod = ProductList.Where(e => e.Name == _name).Single();

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
        }

        public List<string> ProductNameList
        {
            get
            {
                return ProductList
                    .Where(e => e.Partner == CurrentPartner)
                    .Where(e => e.IsE10 == _isE10)
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
                var school = DivisionList
                    .Where(e => e.City == value)
                    .Where(e => e.IsV2 == _isV2).First();

                CurrentProduct.DivisionCode = school.DivisionCode;
                this.NotifyOfPropertyChange();
                this.NotifyOfPropertyChange(() => this.ProductSchoolList);
                CurrentSchool = school.SchoolName;
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
                    .Where(e => e.PartnerCode == CurrentPartner)
                    .Where(e => e.City == CurrentCity)
                    .Where(e => e.IsV2 == _isV2)
                    .Select(e => e.SchoolName).Distinct().ToList();
            }
        }

        #endregion City, School and Division Code filters

        public ProductViewModel()
        {
            _prod = Settings.LoadCurrentProduct();
        }

        /// <summary>
        /// Gets the post data to activate a student, it is not the same for E10 and S15.
        /// </summary>
        /// <param name="memberId">The member id.</param>
        /// <param name="isE10">if set to <c>true</c> [is e10 student].</param>
        /// <returns></returns>
        public Dictionary<string, object> GetPostData(int memberId, bool isE10)
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

            if (isE10)
            {
                postData.Add("levelQty", CurrentProduct.LevelQty);
            }
            else
            {
                if (CurrentProduct.IncludesEnroll)
                {
                    postData.Add("includesenroll", "on");
                }
            }

            return postData;
        }

        /// <summary>
        /// Saves current product info to disk.
        /// </summary>
        public void Save()
        {
            Settings.SaveCurrentProduct(CurrentProduct);
        }
    }
}