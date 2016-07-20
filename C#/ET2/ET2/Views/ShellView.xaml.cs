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

        public ShellView()
        {
            InitializeComponent();
            this.copyInfoFromStatus.Visibility = Visibility.Collapsed;
            Instance = this;
        }

        private BaseMetroDialog CurrentDialog { get; set; }

        private async void SwitchEnv(object sender, RoutedEventArgs e)
        {
            CurrentDialog = (BaseMetroDialog)this.Resources["switchEnv"];
            var currentEnv = ShellViewModel.Instance.TestEnvVM.CurrentEnvironment.Name;
            var dialog = CurrentDialog as CustomDialog;
            var radio = dialog.FindChildren<RadioButton>()
                .Where(r => r.Name == currentEnv.ToLower()).First();
            radio.IsChecked = true;
            await this.ShowMetroDialogAsync(CurrentDialog);
        }

        private async void ChooseEnv(object sender, RoutedEventArgs e)
        {
            var selectedEnv = sender as RadioButton;
            ShellViewModel.Instance.TestEnvVM.UpdateEnvironment(selectedEnv.Content.ToString());
            await this.HideMetroDialogAsync(CurrentDialog);

            ShellViewModel.Instance.StatusInfoVM.Text = "Current Test Environment: {0}".FormatWith(selectedEnv.Content);
        }

        private void DisplayHelp(object sender, RoutedEventArgs e)
        {
            var title = "EFEC Testing Tools";
            var msg = "Please contact <toby.qin@ef.com> if you have questions or bugs on this tool.";
            this.ShowMessageAsync(title, msg, MessageDialogStyle.Affirmative);
        }

        private void ClickToCopy(object sender, RoutedEventArgs e)
        {
            if (sender is Hyperlink)
            {
                var txt = ((Hyperlink)sender).FindChildren<TextBlock>().FirstOrDefault();
                txt.Text.CopyToClipboard();
                ShellViewModel.Instance.StatusInfoVM.Text = "{0} copied.".FormatWith(txt.Text);
            }
        }
    }
}