using Windows.ApplicationModel;

namespace DailyMessage;

internal static class StartupService
{
    public const string TaskId = "DailyMessageTask";

    public static async Task<StartupTaskState?> GetStateAsync()
    {
        try
        {
            var task = await StartupTask.GetAsync(TaskId);
            return task.State;
        }
        catch
        {
            return null;
        }
    }

    public static async Task<StartupTaskState> EnableAsync()
    {
        var task = await StartupTask.GetAsync(TaskId);
        return await task.RequestEnableAsync();
    }

    public static async Task<StartupTaskState> DisableAsync()
    {
        var task = await StartupTask.GetAsync(TaskId);
        task.Disable();
        return task.State;
    }
}
