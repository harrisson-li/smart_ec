using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Data;
using ET2.Support;
using ET2.ViewModels;

namespace ET2.Converters
{
    [ValueConversion(typeof(bool), typeof(bool))]
    public class UrlConverter : IValueConverter
    {
        #region IValueConverter Members

        public object Convert(object value, Type targetType, object parameter,
            System.Globalization.CultureInfo culture)
        {
            if (value.GetType() != typeof(String))
            {
                throw new InvalidOperationException("The target must be a string");
            }

            var originUrl = value as string;
            return ShellViewModel.Instance.UsefulLinkVM.ConvertLink(originUrl);
        }

        public object ConvertBack(object value, Type targetType, object parameter,
            System.Globalization.CultureInfo culture)
        {
            throw new NotSupportedException();
        }

        #endregion IValueConverter Members
    }
}