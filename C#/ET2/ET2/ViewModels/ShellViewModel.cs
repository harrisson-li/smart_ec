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
        public static ShellViewModel Instance { get; private set; }

        public void Close()
        {
            this.TryClose();
        }

        protected override void OnInitialize()
        {
            base.OnInitialize();
            this.DisplayName = "EFEC Testing Tools - {0}"
                .FormatWith(Support.VersionHelper.GetCurrentVersion());
            this.TestEnvVM = new TestEnvironmentViewModel();
            this.UsefulLinkVM = new UsefulLinkViewModel();
            this.TestAccountVM = new TestAccountViewModel();
            this.StatusInfoVM = new StatusInfoViewModel();
            this.ProductVM = new ProductViewModel();

            Instance = this;
            Support.VersionHelper.ShowReleaseNote();
        }

        public void WriteStatus(string message)
        {
            Log.InfoFormat("Status: {0}", message);
            this.StatusInfoVM.Text = message;
        }
    }
}