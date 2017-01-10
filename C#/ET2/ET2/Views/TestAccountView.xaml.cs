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
using ET2.Models;
using ET2.Support;
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
            InitLinkButtons();
            InitQuickActions();
        }

        private void InitLinkButtons()
        {
            this.homeLinks.Children.Clear();
            foreach (var link in Settings.LoadHomeLinks())
            {
                var btn = new Button();
                btn.Content = link.Name;
                btn.Click += OpenLink;
                btn.MouseEnter += UpdateToolTip;
                btn.Width = 120;
                btn.Margin = new Thickness(0, 8, 20, 0);
                btn.Tag = link;
                this.homeLinks.Children.Add(btn);
            }
        }

        private void InitQuickActions()
        {
            foreach (var quickAction in Settings.LoadQuickActions())
            {
                var btn = new Button();
                btn.Content = quickAction.Name;
                btn.Tag = quickAction;
                btn.Width = 130;
                btn.Background = new SolidColorBrush(Colors.LightGray);
                btn.Margin = new Thickness(5, 0, 5, 5);
                btn.HorizontalContentAlignment = HorizontalAlignment.Left;
                btn.MouseEnter += RefreshQuickAction;
                btn.Click += PerformQuickAction;
                this.quickActionsPanel.Children.Add(btn);
            }
        }

        private void PerformQuickAction(object sender, RoutedEventArgs e)
        {
            var act = (sender as Button).Tag as QuickAction;
            act.Perform();
        }

        private void RefreshQuickAction(object sender, MouseEventArgs e)
        {
            var btn = sender as Button;
            var act = btn.Tag as QuickAction;
            act.Text = ShellViewModel.Instance.UsefulLinkVM.ConvertLink(act.Parameter);
            act.Text = Environment.ExpandEnvironmentVariables(act.Text);
            btn.ToolTip = act.Text;
        }

        private async void NewAccount(object sender, RoutedEventArgs e)
        {
            await ShellView.Instance.RunInBackgroud(() =>
           {
               ShellViewModel.Instance.TestAccountVM.GenerateAccount();
           });
        }

        private async void ActivateAccount(object sender, RoutedEventArgs e)
        {
            await ShellView.Instance.RunInBackgroud(() =>
            {
                ShellViewModel.Instance.TestAccountVM.ActivateAccount();
                ShellViewModel.Instance.ProductVM.Save();
            });
        }

        private async void NewAndActivate(object sender, RoutedEventArgs e)
        {
            await ShellView.Instance.RunInBackgroud(() =>
            {
                ShellViewModel.Instance.TestAccountVM.GenerateAccount();
                ShellViewModel.Instance.TestAccountVM.ActivateAccount();
                ShellViewModel.Instance.ProductVM.Save();
            });
        }

        private async void ConvertTo20(object sender, RoutedEventArgs e)
        {
            await ShellView.Instance.RunInBackgroud(() =>
            {
                ShellViewModel.Instance.TestAccountVM.ConvertTo20();
            });
        }

        private void OpenLink(object sender, RoutedEventArgs e)
        {
            var btn = sender as Button;

            if (btn.ToolTip == null)
            {
                UpdateToolTip(sender, e);
            }
            var link = btn.ToolTip.ToString();
            System.Diagnostics.Process.Start(link);
        }

        private void UpdateToolTip(object sender, RoutedEventArgs e)
        {
            var btn = sender as Button;
            var link = btn.Tag as UsefulLink;
            btn.ToolTip = ShellViewModel.Instance.UsefulLinkVM.ConvertLink(link.Url);
        }

        private async void GetStudentInfo(object sender, RoutedEventArgs e)
        {
            var name = (sender as TextBox).Text;
            var currentAccount = ShellViewModel.Instance.TestAccountVM.CurrentTestAccount;
            if (name != currentAccount.MemberId)
            {
                await ShellView.Instance.RunInBackgroud(() =>
                {
                    var newAccount = ShellViewModel.Instance.TestAccountVM.GetTestAccountByNameOrId(name);
                    if (newAccount == null)
                    {
                        // Revert if failed to get student info
                        newAccount = currentAccount;
                    }
                    else
                    {
                        // remember the test account as well
                        ShellViewModel.Instance.TestAccountVM.AddHistoryAccount(newAccount);
                    }

                    ShellViewModel.Instance.TestAccountVM.CurrentTestAccount = newAccount;
                });
            }
        }
    }
}