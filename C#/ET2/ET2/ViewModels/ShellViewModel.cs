using System.ComponentModel.Composition;
using Caliburn.Micro;
using EF.Common;

namespace ET2.ViewModels
{
    [Export(typeof(IShell))]
    public class ShellViewModel : Screen, IShell
    {
        public TestEnvironmentViewModel TestEnvVM { get; set; }
        public UsefulLinkViewModel UsefulLinkVM { get; set; }
        public TestAccountViewModel TestAccountVM { get; set; }
        public ProductViewModel ProductVM { get; set; }
        public StatusInfoViewModel StatusInfoVM { get; set; }
        public HostEditorViewModel HostVM { get; set; }
        public SettingsViewModel SettingsVM { get; set; }
        public QuickActionViewModel QuickActionVM { get; set; }
        public static ShellViewModel Instance { get; private set; }

        public void Close()
        {
            this.TryClose();
        }

        protected override void OnInitialize()
        {
            base.OnInitialize();
            this.DisplayName = "EFEC Testing Tools - {0}"
                .FormatWith(Support.VersionHelper.GetCurrentVersion().Build);
            this.TestEnvVM = new TestEnvironmentViewModel();
            this.UsefulLinkVM = new UsefulLinkViewModel();
            this.TestAccountVM = new TestAccountViewModel();
            this.StatusInfoVM = new StatusInfoViewModel();
            this.ProductVM = new ProductViewModel();
            this.HostVM = new HostEditorViewModel();
            this.SettingsVM = new SettingsViewModel();
            this.QuickActionVM = new QuickActionViewModel();

            Instance = this;
            Support.VersionHelper.ShowReleaseNote();
        }

        public static void WriteStatus(string message)
        {
            Log.InfoFormat("Status: {0}", message);
            Instance.StatusInfoVM.Text = message.Replace("\n", "");
        }

        public static void InitForTest()
        {
            var shell = new ShellViewModel();
            shell.OnInitialize();
        }
    }
}