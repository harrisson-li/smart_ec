namespace ET2.Services
{
    public interface IServiceLocator
    {
        T GetInstance<T>() where T : class;
    }
}