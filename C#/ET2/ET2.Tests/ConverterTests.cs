using System;

using EF.Common;
using ET2.Converters;
using ET2.ViewModels;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace ET2.Tests
{
    [TestClass]
    public class ConverterTests
    {
        public ShellViewModel Shell { get; set; }

        public ConverterTests()
        {
            ShellViewModel.InitForTest();
            Shell = ShellViewModel.Instance;
        }

        [TestMethod]
        public void TestInveseConverter()
        {
            var cvt = new InverseBooleanConverter();
            var source = true;
            var target = cvt.Convert(source, typeof(bool), null, null);
            Assert.AreEqual(false, target);
        }
    }
}