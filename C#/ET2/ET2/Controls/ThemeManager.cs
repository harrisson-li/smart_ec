using System;
using System.ComponentModel.Composition;
using System.Windows;

namespace ET2.Controls
{
    [Export(typeof(IThemeManager))]
    public class ThemeManager : IThemeManager
    {
        private readonly ResourceDictionary themeResources;

        public ThemeManager()
        {
            this.themeResources = new ResourceDictionary
            {
                Source = new Uri("pack://application:,,,/ET2;component/Resources/Theme_Blue.xaml")
            };
        }

        public ResourceDictionary GetThemeResources()
        {
            return this.themeResources;
        }
    }
}