using System.Text.Json;

namespace DailyMessage.Core;

public static class ConfigStore
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true,
        WriteIndented = true
    };

    public static async Task<MessageConfig> LoadAsync(string filePath, CancellationToken cancellationToken = default)
    {
        try
        {
            if (!File.Exists(filePath))
                return new MessageConfig();

            await using var stream = File.OpenRead(filePath);
            var config = await JsonSerializer.DeserializeAsync<MessageConfig>(stream, JsonOptions, cancellationToken).ConfigureAwait(false);
            return (config ?? new MessageConfig()).Normalize();
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or JsonException)
        {
            return new MessageConfig();
        }
    }

    public static async Task SaveAsync(string filePath, MessageConfig config, CancellationToken cancellationToken = default)
    {
        var directory = Path.GetDirectoryName(filePath);
        if (string.IsNullOrWhiteSpace(directory))
            throw new ArgumentException("The configuration path must include a directory.", nameof(filePath));

        Directory.CreateDirectory(directory);
        var temporary = filePath + ".tmp";
        await using (var stream = File.Create(temporary))
        {
            await JsonSerializer.SerializeAsync(stream, config.Normalize(), JsonOptions, cancellationToken).ConfigureAwait(false);
            await stream.FlushAsync(cancellationToken).ConfigureAwait(false);
        }

        File.Move(temporary, filePath, overwrite: true);
    }
}
