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

            var envString = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.UrlReplacement;
            var id = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.MemberId;
            var name = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount.UserName;
            if (value != null)
            {
                var url = value as string;
                url = url.Replace("$env", envString);
                url = url.Replace("$id", id);
                url = url.Replace("$name", name);
                url = url.Replace("$token", TokenHelper.GetToken(envString));
                return url;
            }

            return value;
        }

        public object ConvertBack(object value, Type targetType, object parameter,
            System.Globalization.CultureInfo culture)
        {
            throw new NotSupportedException();
        }

        #endregion IValueConverter Members
    }
}