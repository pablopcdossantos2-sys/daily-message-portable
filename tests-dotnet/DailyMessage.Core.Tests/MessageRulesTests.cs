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
        Assert.Equal(["text", "checklist", "text"], config.Blocks.Select(x => x.Type));
        Assert.Equal("First", config.Blocks[0].Text);
        Assert.Equal("Last", config.Blocks[2].Text);
        Assert.Equal("heading", config.Blocks[2].Style);
    }
}
