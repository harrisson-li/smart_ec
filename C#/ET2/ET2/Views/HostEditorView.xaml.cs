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

        private string GetHostLocation()
        {
            var windir = Environment.GetFolderPath(Environment.SpecialFolder.Windows);
            return System.IO.Path.Combine(windir, @"System32\drivers\etc");
        }

        private string GetHostFileLocation()
        {
            return System.IO.Path.Combine(GetHostLocation(), "hosts");
        }

        private void btnExplore_Click(object sender, RoutedEventArgs e)
        {
            var batch = "cmd /c Explorer.exe {0}".FormatWith(GetHostLocation());
            CommandHelper.ExecuteBatch(batch);
        }

        private void btnEdit_Click(object sender, RoutedEventArgs e)
        {
            // todo: should back up the file at first.
            var batch = "cmd /c notepad.exe {0}".FormatWith(GetHostFileLocation());
            CommandHelper.ExecuteBatch(batch);
        }
    }
}