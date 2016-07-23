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
    public partial class ShellView : MetroWindow
    {
        public static ShellView Instance { get; private set; }
        public BaseMetroDialog CurrentDialog { get; set; }

        public ShellView()
        {
            InitializeComponent();
            Instance = this;
        }

        #region Test Environments

        private async void SwitchEnv(object sender, RoutedEventArgs e)
        {
            // find the dialog resource
            CurrentDialog = (BaseMetroDialog)this.Resources["myDialog"];

            // set dialog title
            var dialog = CurrentDialog as CustomDialog;
            dialog.Title = "Switching Test Environment";

            // add controls to the panel
            var panel = dialog.FindChildren<StackPanel>().First();
            panel.Children.Clear();
            var dict = new Dictionary<string, RadioButton>();
            foreach (var env in ShellViewModel.Instance.TestEnvVM.EnvironmentList)
            {
                var button = new RadioButton();
                button.Name = env.Name;
                button.Content = env.Name;
                button.Tag = env;
                button.Width = 72;
                button.ToolTip = env.UrlReplacement;
                button.Click += ChooseEnv;
                panel.Children.Add(button);
                dict.Add(env.Name, button);
            }

            var currentEnv = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.Name;
            var radio = dict[currentEnv];
            radio.IsChecked = true;
            await this.ShowMetroDialogAsync(CurrentDialog);
        }

        private async void ChooseEnv(object sender, RoutedEventArgs e)
        {
            var selectedEnv = sender as RadioButton;
            ShellViewModel.Instance.TestEnvVM.UpdateEnvironment(selectedEnv.Name);
            await this.HideMetroDialogAsync(CurrentDialog);

            ShellViewModel.WriteStatus(
                "Current Test Environment: {0}".FormatWith(selectedEnv.Content));
        }

        #endregion Test Environments

        #region Help Message

        private void DisplayHelp(object sender, RoutedEventArgs e)
        {
            var title = "EFEC Testing Tools (ET2)";
            var msg = "Please contact <toby.qin@ef.com> if you have questions or bugs on this tool.";
            this.ShowMessageAsync(title, msg, MessageDialogStyle.Affirmative);
        }

        #endregion Help Message

        #region Settings

        private async void DisplaySettings(object sender, RoutedEventArgs e)
        {
            // find the dialog resource
            CurrentDialog = (BaseMetroDialog)this.Resources["myDialog"];

            // set dialog title
            var dialog = CurrentDialog as CustomDialog;
            dialog.Title = "Open Settings Folder";
            dialog.Height = 150;

            // add controls to the panel
            var panel = dialog.FindChildren<StackPanel>().First();
            panel.Children.Clear();
            var settingView = new SettingsView();
            panel.Children.Add(settingView);
            await this.ShowMetroDialogAsync(CurrentDialog);
        }

        #endregion Settings

        public async Task RunInBackgroud(Action act)
        {
            ShellViewModel.Instance.StatusInfoVM.HasBackgroundTask = true;
            await Task.Run(act).ConfigureAwait(false);
            ShellViewModel.Instance.StatusInfoVM.HasBackgroundTask = false;
        }
    }
}