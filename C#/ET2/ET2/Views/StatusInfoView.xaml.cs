using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using EF.Common;
using ET2.ViewModels;
using MahApps.Metro.Controls;
using MahApps.Metro.Controls.Dialogs;

namespace ET2.Views
{
    /// <summary>
    /// Interaction logic for StatusInfo.xaml
    /// </summary>
    public partial class StatusInfoView : UserControl
    {
        public StatusInfoView()
        {
            InitializeComponent();
        }

        private void ClickToCopy(object sender, RoutedEventArgs e)
        {
            if (sender is Hyperlink)
            {
                var txt = ((Hyperlink)sender).FindChildren<TextBlock>().FirstOrDefault();
                txt.Text.CopyToClipboard();
                ShellViewModel.WriteStatus("{0} copied.".FormatWith(txt.Text));
            }
        }
    }
}