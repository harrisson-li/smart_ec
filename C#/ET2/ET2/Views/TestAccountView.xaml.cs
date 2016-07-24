﻿using System;
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
    }
}