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
using EF.Common;
using ET2.Models;
using ET2.Support;
using ET2.ViewModels;

namespace ET2.Views
{
    /// <summary>
    /// Interaction logic for HostEditor.xaml
    /// </summary>
    public partial class HostEditorView : UserControl
    {
        public HostEditorView()
        {
            InitializeComponent();
        }

        private void ExploreHostFolder(object sender, RoutedEventArgs e)
        {
            Process.Start("explorer.exe", Settings.GetSystemHostLocation());
        }

        private void ViewCurrentHost(object sender, RoutedEventArgs e)
        {
            var cmd = "cmd /c notepad.exe {0}".FormatWith(Settings.GetSystemHostFile().FullName);
            CommandHelper.ExecuteBatch(cmd, asAdmin: true);
        }

        private void BackupCurrentHost(object sender, RoutedEventArgs e)
        {
            Settings.BackupSystemHost();
            ShellViewModel.WriteStatus("System host had been saved to personal host folder.");
        }

        private void ViewHost(object sender, RoutedEventArgs e)
        {
            var host = (sender as Button).DataContext as HostFile;
            host.View();
        }

        private void ActivateHost(object sender, RoutedEventArgs e)
        {
            var host = (sender as FrameworkElement).DataContext as HostFile;
            host.Activate();
            ShellViewModel.Instance.HostVM.NotifyHostChanged();
        }
    }
}