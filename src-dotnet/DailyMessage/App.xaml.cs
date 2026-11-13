using Microsoft.UI.Xaml;
using Microsoft.Windows.AppLifecycle;

namespace DailyMessage;

public partial class App : Application
{
    private Window? _window;

    public App()
    {
        InitializeComponent();
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        var activation = AppInstance.GetCurrent().GetActivatedEventArgs();
        var startupLaunch = activation?.Kind == ExtendedActivationKind.StartupTask;

        _window = startupLaunch
            ? new MessageWindow(preview: false)
            : new MainWindow();

        _window.Activate();
    }
}
