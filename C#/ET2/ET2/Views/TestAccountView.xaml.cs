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

namespace ET2.Views
{
    /// <summary>
    /// Interaction logic for TestAccountTool.xaml
    /// </summary>
    public partial class TestAccountView : UserControl
    {
        public TestAccountView()
        {
            InitializeComponent();
        }

        private async void NewAccount(object sender, RoutedEventArgs e)
        {
            var envUrlString = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.UrlReplacement;
            var isV2 = this.chkIsV2.IsChecked.Value;
            ((Button)sender).IsEnabled = false;
            ShellViewModel.Instance.StatusInfoVM.HasBackgroundTask = true;

            await Task.Run(() =>
            {
                ShellViewModel.Instance.TestAccountVM.GenerateAccount(envUrlString, isV2);
            });
            //ShellView.Instance.copyInfoFromStatus.Visibility = Visibility.Visible;
            ((Button)sender).IsEnabled = true;
            ShellViewModel.Instance.StatusInfoVM.HasBackgroundTask = false;
        }

        private void chkIsV2_Click(object sender, RoutedEventArgs e)
        {
            var chk = sender as CheckBox;
            if (chk.IsChecked.Value)
            {
                ShellViewModel.WriteStatus("Platform 2.0 test account.");
            }
            else
            {
                ShellViewModel.WriteStatus("Platform 1.0 test account.");
            }

            ShellViewModel.Instance.TestAccountVM.Save();
        }

        private async void ActivateAccount(object sender, RoutedEventArgs e)
        {
            var envUrlString = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.UrlReplacement;
            var isV2 = this.chkIsV2.IsChecked.Value;
            ((Button)sender).IsEnabled = false;
            ShellViewModel.Instance.StatusInfoVM.HasBackgroundTask = true;

            await Task.Run(() =>
            {
                ShellViewModel.Instance.TestAccountVM.ActivateAccount(envUrlString, isV2);
                ShellViewModel.Instance.TestAccountVM.Save();
                ShellViewModel.Instance.ProductVM.Save();
            });
            ((Button)sender).IsEnabled = true;
            ShellViewModel.Instance.StatusInfoVM.HasBackgroundTask = false;
        }

        private async void NewAndActivate(object sender, RoutedEventArgs e)
        {
            ((Button)sender).IsEnabled = false;

            var envUrlString = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.UrlReplacement;
            var isV2 = this.chkIsV2.IsChecked.Value;

            await Task.Run(() =>
            {
                ShellViewModel.Instance.TestAccountVM.GenerateAccount(envUrlString, isV2);
            });

            //ShellView.Instance.copyInfoFromStatus.Visibility = Visibility.Visible;

            await Task.Run(() =>
            {
                ShellViewModel.Instance.TestAccountVM.ActivateAccount(envUrlString, isV2);
                ShellViewModel.Instance.TestAccountVM.Save();
                ShellViewModel.Instance.ProductVM.Save();
            });

            ((Button)sender).IsEnabled = true;
        }

        private async void ConvertTo20(object sender, RoutedEventArgs e)
        {
            await Task.Run(() =>
            {
                var envUrlString = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.UrlReplacement;
                ShellViewModel.Instance.TestAccountVM.ConvertTo20(envUrlString);
            });
        }

        private void ClickLinkButton(object sender, RoutedEventArgs e)
        {
            var btn = sender as Button;
            var link = btn.ToolTip.ToString();
            System.Diagnostics.Process.Start(link);
        }
    }
}