using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Data;
using ET2.Support;
using ET2.ViewModels;

namespace ET2.Converters
{
    [ValueConversion(typeof(bool), typeof(Visibility))]
    public class LongTextConverter : IValueConverter
    {
        public object Convert(object value, Type targetType,
                              object parameter, CultureInfo culture)
        {
            if (string.IsNullOrEmpty((string)value) || value.ToString().Length < 85)
            {
                return value;
            }
            else
            {
                var cut = value.ToString().Substring(0, 70);
                return string.Format("{0} ... !!!truncated!!! click to view", cut);
            }
        }

        public object ConvertBack(object value, Type targetType,
            object parameter, CultureInfo culture)
        {
            throw new NotSupportedException();
        }
    }
}