using Xunit;
using DailyMessage.Core;

namespace DailyMessage.Core.Tests;

public sealed class MessageRulesTests
{
    [Fact]
    public void CannotCloseBeforeTimerEnds()
    {
        Assert.False(MessageRules.CanClose(
            TimeSpan.FromSeconds(4), 5, Array.Empty<ChecklistProgress>()));
    }

    [Fact]
    public void CanCloseAfterTimerWhenNoRequiredChecklistExists()
    {
        Assert.True(MessageRules.CanClose(
            TimeSpan.FromSeconds(5), 5,
            [new ChecklistProgress(false, 2, 0)]));
    }

    [Fact]
    public void RequiredChecklistKeepsWindowLockedUntilAllItemsAreChecked()
    {
        Assert.False(MessageRules.CanClose(
            TimeSpan.FromSeconds(10), 5,
            [new ChecklistProgress(true, 3, 2)]));

        Assert.True(MessageRules.CanClose(
            TimeSpan.FromSeconds(10), 5,
            [new ChecklistProgress(true, 3, 3)]));
    }

    [Fact]
    public void RemainingSecondsRoundsUpAndNeverGoesBelowZero()
    {
        Assert.Equal(3, MessageRules.RemainingSeconds(TimeSpan.FromSeconds(2.1), 5));
        Assert.Equal(0, MessageRules.RemainingSeconds(TimeSpan.FromSeconds(8), 5));
    }

    [Fact]
    public void NormalizationEnforcesLimitsAndPreservesBlockOrder()
    {
        var config = new MessageConfig
        {
            Seconds = 999,
            Blocks =
            [
                new MessageBlock { Type = "text", Text = " First " },
                new MessageBlock { Type = "checklist", ChecklistTitle = "Tasks", Items = [" one ", "two"], Required = true },
                new MessageBlock { Type = "text", Text = "Last", Style = "heading" }
            ]
        }.Normalize();

        Assert.Equal(600, config.Seconds);
        Assert.Equal(new[] { "text", "checklist", "text" }, config.Blocks.Select(x => x.Type).ToArray());
        Assert.Equal("First", config.Blocks[0].Text);
        Assert.Equal("Last", config.Blocks[2].Text);
        Assert.Equal("heading", config.Blocks[2].Style);
    }
    [Fact]
    public async Task ConfigStoreReadsLegacyPythonChecklistSchema()
    {
        var path = Path.Combine(Path.GetTempPath(), $"daily-message-{Guid.NewGuid():N}", "config.json");
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        try
        {
            await File.WriteAllTextAsync(path, """
                {
                  "title": "Olá",
                  "seconds": 12,
                  "theme": "dark",
                  "blocks": [
                    { "type": "checklist", "title": "Rotina", "items": ["Água", "Agenda"], "required": true }
                  ]
                }
                """);

            var config = await ConfigStore.LoadAsync(path);

            Assert.Equal("Olá", config.Title);
            Assert.Equal("Rotina", config.Blocks[0].ChecklistTitle);
            Assert.Equal(new[] { "Água", "Agenda" }, config.Blocks[0].Items);
            Assert.True(config.Blocks[0].Required);
        }
        finally
        {
            Directory.Delete(Path.GetDirectoryName(path)!, recursive: true);
        }
    }

    [Fact]
    public async Task ConfigStoreWritesCamelCaseFieldsAndLegacyChecklistTitle()
    {
        var path = Path.Combine(Path.GetTempPath(), $"daily-message-{Guid.NewGuid():N}", "config.json");
        try
        {
            await ConfigStore.SaveAsync(path, new MessageConfig
            {
                Title = "Olá",
                Blocks = [new MessageBlock { Type = "checklist", ChecklistTitle = "Rotina", Items = ["Água"] }]
            });

            using var document = System.Text.Json.JsonDocument.Parse(await File.ReadAllTextAsync(path));
            var root = document.RootElement;
            Assert.True(root.TryGetProperty("blocks", out var blocks));
            Assert.True(blocks[0].TryGetProperty("title", out var title));
            Assert.Equal("Rotina", title.GetString());
            Assert.False(blocks[0].TryGetProperty("checklistTitle", out _));
        }
        finally
        {
            if (Directory.Exists(Path.GetDirectoryName(path)!))
                Directory.Delete(Path.GetDirectoryName(path)!, recursive: true);
        }
    }

}
