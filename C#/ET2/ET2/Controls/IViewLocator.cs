using System;
using System.Windows;

namespace ET2.Controls
{
    public interface IViewLocator
    {
        UIElement GetOrCreateViewType(Type viewType);
    }
}