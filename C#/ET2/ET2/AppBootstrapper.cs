using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.ComponentModel.Composition.Hosting;
using System.ComponentModel.Composition.Primitives;
using System.Linq;
using System.Windows;
using Caliburn.Micro;
using ET2.Controls;

namespace ET2
{
    public class AppBootstrapper : BootstrapperBase
    {
        private CompositionContainer container;

        public AppBootstrapper()
        {
            Log.Init();
            Log.Info("Application start.");
            AppDomain.CurrentDomain.UnhandledException += GlobalUnhandleException;
            Initialize();
        }

        /// <summary>
        /// Genreate more readable error message.
        /// </summary>
        private string GetReadableException(Exception ex)
        {
            var messageList = new List<string>();
            var counter = 0;
            var e = ex;
            while (e != null)
            {
                messageList.Add(String.Format("{0}: {1}", e.Source, e.Message));
                e = e.InnerException;
                counter++;
            }

            messageList.Reverse();
            for (int i = 0; i < messageList.Count; i++)
            {
                var from = i == 0 ? "Failed from " : "Then from ";
                messageList[i] = string.Format("{0}{1}{2}", new string(' ', i * 4), from, messageList[i]);
            }

            return String.Join("\n", messageList);
        }

        private void GlobalUnhandleException(object sender, UnhandledExceptionEventArgs e)
        {
            var ex = e.ExceptionObject as Exception;
            var message = GetReadableException(ex);

            Log.Error(message);
            Log.Error("Unhandle error: ");
            Log.Error(ex);
            System.Diagnostics.Trace.Fail(message);
        }

        protected override void BuildUp(object instance)
        {
            this.container.SatisfyImportsOnce(instance);
        }

        /// <summary>
        ///     By default, we are configured to use MEF
        /// </summary>
        protected override void Configure()
        {
            var catalog =
                new AggregateCatalog(
                    AssemblySource.Instance.Select(x => new AssemblyCatalog(x)).OfType<ComposablePartCatalog>());

            this.container = new CompositionContainer(catalog);

            var batch = new CompositionBatch();

            batch.AddExportedValue<IWindowManager>(new WindowManager());
            batch.AddExportedValue<IEventAggregator>(new EventAggregator());
            batch.AddExportedValue(this.container);
            batch.AddExportedValue(catalog);

            this.container.Compose(batch);
        }

        protected override IEnumerable<object> GetAllInstances(Type serviceType)
        {
            return this.container.GetExportedValues<object>(AttributedModelServices.GetContractName(serviceType));
        }

        protected override object GetInstance(Type serviceType, string key)
        {
            var contract = string.IsNullOrEmpty(key) ? AttributedModelServices.GetContractName(serviceType) : key;
            var exports = this.container.GetExportedValues<object>(contract);

            if (exports.Any())
            {
                return exports.First();
            }

            throw new Exception(string.Format("Could not locate any instances of contract {0}.", contract));
        }

        protected override void OnStartup(object sender, StartupEventArgs e)
        {
            var startupTasks =
                GetAllInstances(typeof(StartupTask))
                .Cast<ExportedDelegate>()
                .Select(exportedDelegate => (StartupTask)exportedDelegate.CreateDelegate(typeof(StartupTask)));

            startupTasks.Apply(s => s());

            DisplayRootViewFor<IShell>();
        }
    }
}