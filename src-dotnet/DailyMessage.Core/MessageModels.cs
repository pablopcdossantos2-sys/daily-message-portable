using System.Text.Json.Serialization;
namespace DailyMessage.Core;

public sealed class MessageBlock
{
    public string Type { get; set; } = "text";
    public string Style { get; set; } = "body";
    public string Text { get; set; } = "";
    public string File { get; set; } = "";
    public string Caption { get; set; } = "";
    [JsonPropertyName("title")]
    public string ChecklistTitle { get; set; } = "";
    public List<string> Items { get; set; } = [];
    public bool Required { get; set; } = true;

    public static MessageBlock TextBlock() => new() { Type = "text", Style = "body" };
    public static MessageBlock ImageBlock() => new() { Type = "image" };
    public static MessageBlock ChecklistBlock() => new() { Type = "checklist", Required = true };
}

public sealed class MessageConfig
{
    public string Title { get; set; } = "Bem-vindo(a)!";
    public List<MessageBlock> Blocks { get; set; } = [new MessageBlock
    {
        Type = "text",
        Style = "body",
        Text = "Que o seu dia seja produtivo. Respire fundo, organize suas prioridades e comece com calma."
    }];
    public int Seconds { get; set; } = 10;
    public string Theme { get; set; } = "system";
    public string Accent { get; set; } = "indigo";
    public string Language { get; set; } = "auto";

    public MessageConfig Normalize()
    {
        var normalized = new MessageConfig
        {
            Title = (Title ?? "").Trim(),
            Seconds = Math.Clamp(Seconds, 3, 600),
            Theme = new[] { "system", "light", "dark" }.Contains(Theme) ? Theme : "system",
            Accent = new[] { "indigo", "teal", "rose", "amber" }.Contains(Accent) ? Accent : "indigo",
            Language = new[] { "auto", "pt-BR", "en" }.Contains(Language) ? Language : "auto",
            Blocks = []
        };

        if (normalized.Title.Length > 80)
            normalized.Title = normalized.Title[..80];

        var textBudget = 30_000;
        var images = 0;
        foreach (var source in Blocks ?? [])
        {
            if (normalized.Blocks.Count >= 30 || source is null)
                break;

            switch (source.Type)
            {
                case "text":
                {
                    var value = (source.Text ?? "").Trim();
                    value = value[..Math.Min(value.Length, Math.Min(20_000, textBudget))];
                    if (value.Length == 0) break;
                    textBudget -= value.Length;
                    normalized.Blocks.Add(new MessageBlock
                    {
                        Type = "text",
                        Style = new[] { "body", "heading", "note" }.Contains(source.Style) ? source.Style : "body",
                        Text = value
                    });
                    break;
                }
                case "image":
                {
                    var name = Path.GetFileName(source.File ?? "");
                    var ext = Path.GetExtension(name).ToLowerInvariant();
                    if (images >= 10 || string.IsNullOrWhiteSpace(name) ||
                        !new[] { ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp" }.Contains(ext))
                        break;
                    images++;
                    normalized.Blocks.Add(new MessageBlock
                    {
                        Type = "image",
                        File = name,
                        Caption = (source.Caption ?? "")[..Math.Min((source.Caption ?? "").Length, 200)]
                    });
                    break;
                }
                case "checklist":
                {
                    var items = (source.Items ?? [])
                        .Where(x => !string.IsNullOrWhiteSpace(x))
                        .Select(x => x.Trim()[..Math.Min(x.Trim().Length, 200)])
                        .Take(30)
                        .ToList();
                    if (items.Count == 0) break;
                    normalized.Blocks.Add(new MessageBlock
                    {
                        Type = "checklist",
                        ChecklistTitle = (source.ChecklistTitle ?? "")[..Math.Min((source.ChecklistTitle ?? "").Length, 100)],
                        Items = items,
                        Required = source.Required
                    });
                    break;
                }
            }
        }

        if (normalized.Blocks.Count == 0)
            normalized.Blocks = [MessageBlock.TextBlock()];

        return normalized;
    }
}

public readonly record struct ChecklistProgress(bool Required, int Total, int Completed)
{
    public bool IsComplete => Completed >= Total;
}

public static class MessageRules
{
    public static int RemainingSeconds(TimeSpan elapsed, int requiredSeconds)
        => Math.Max(0, (int)Math.Ceiling(requiredSeconds - elapsed.TotalSeconds));

    public static bool CanClose(TimeSpan elapsed, int requiredSeconds, IEnumerable<ChecklistProgress> checklists)
    {
        if (elapsed.TotalSeconds < requiredSeconds)
            return false;

        return checklists.Where(x => x.Required).All(x => x.IsComplete);
    }
}
