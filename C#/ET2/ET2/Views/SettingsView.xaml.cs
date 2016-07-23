using System;
using System.Collections.Generic;
using System.Diagnostics;
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
using ET2.Models;
using ET2.ViewModels;
using MahApps.Metro.Controls.Dialogs;

namespace ET2.Views
{
    /// <summary>
    /// Interaction logic for UsefulLinkTool.xaml
    /// </summary>
    public partial class SettingsView : UserControl
    {
        public SettingsView()
        {
            InitializeComponent();
            this.txtIntro.Text = "All settings are placed in private or public settings folder. Copy public settings to private folder can overwrite them.";
        }

        private async void OpenSettingsFoler(object sender, RoutedEventArgs e)
        {
            var btn = sender as Button;
            if (btn.Content.ToString() == "Private Settings")
            {
                ShellViewModel.Instance.SettingsVM.OpenFolder(
                    ShellViewModel.Instance.SettingsVM.PrivateSettingsFolder);
            }
            else if (btn.Content.ToString() == "Public Settings")
            {
                ShellViewModel.Instance.SettingsVM.OpenFolder(
                   ShellViewModel.Instance.SettingsVM.GlobalSettingsFolder);
            }

            await ShellView.Instance.HideMetroDialogAsync(
                ShellView.Instance.CurrentDialog);
        }
    }
}