namespace DailyMessage;

internal static class AppPaths
{
    public static string LocalFolder
    {
        get
        {
            try
            {
                return Windows.Storage.ApplicationData.Current.LocalFolder.Path;
            }
            catch
            {
                var fallback = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "DailyMessage");
                Directory.CreateDirectory(fallback);
                return fallback;
            }
        }
    }

    public static string ConfigFile => Path.Combine(LocalFolder, "config.json");
    public static string MediaFolder
    {
        get
        {
            var folder = Path.Combine(LocalFolder, "Media");
            Directory.CreateDirectory(folder);
            return folder;
        }
    }
}
