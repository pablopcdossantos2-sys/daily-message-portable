using System.Diagnostics;
using DailyMessage.Core;
using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using WinRT.Interop;

namespace DailyMessage;

public sealed partial class MessageWindow : Window
{
    private readonly bool _preview;
    private readonly MessageConfig _config;
    private readonly Stopwatch _clock = Stopwatch.StartNew();
    private readonly int _seconds;
    private readonly List<(bool Required, List<CheckBox> Items)> _checklists = [];
    private readonly DispatcherQueueTimer _timer;
    private nint _hwnd;
    private bool _locked = true;

    public MessageWindow(MessageConfig? config = null, bool preview = false)
    {
        InitializeComponent();
        _preview = preview;
        _config = config?.Normalize() ?? ConfigStore.LoadAsync(GetConfigPath()).GetAwaiter().GetResult();
        _seconds = preview ? Math.Min(_config.Seconds, 5) : _config.Seconds;
        MessageRootGrid.RequestedTheme = _config.Theme switch
        {
            "light" => ElementTheme.Light,
            "dark" => ElementTheme.Dark,
            _ => ElementTheme.Default
        };
        var accent = _config.Accent switch
        {
            "teal" => Windows.UI.Color.FromArgb(255, 13, 148, 136),
            "rose" => Windows.UI.Color.FromArgb(255, 225, 29, 72),
            "amber" => Windows.UI.Color.FromArgb(255, 217, 119, 6),
            _ => Windows.UI.Color.FromArgb(255, 99, 102, 241)
        };
        CloseButton.Background = new Microsoft.UI.Xaml.Media.SolidColorBrush(accent);
        CountdownBar.Foreground = new Microsoft.UI.Xaml.Media.SolidColorBrush(accent);
        Title = preview ? "Daily Message — Prévia" : "Daily Message";
        CountdownBar.Maximum = _seconds;
        CountdownBar.Value = _seconds;
        MessageTitle.Text = _config.Title;

        BuildMessage();
        Activated += (_, _) =>
        {
            if (_hwnd == 0)
            {
                _hwnd = WindowNative.GetWindowHandle(this);
                Win32WindowLock.SetTopMost(_hwnd);
                ApplyLock(true);
            }
        };

        _timer = DispatcherQueue.GetForCurrentThread().CreateTimer();
        _timer.Interval = TimeSpan.FromMilliseconds(200);
        _timer.Tick += (_, _) => RefreshState();
        _timer.Start();
        RefreshState();
    }

    private static string GetConfigPath()
    {
        try { return Path.Combine(Windows.Storage.ApplicationData.Current.LocalFolder.Path, "config.json"); }
        catch
        {
            var folder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "DailyMessage");
            Directory.CreateDirectory(folder);
            return Path.Combine(folder, "config.json");
        }
    }

    private void BuildMessage()
    {
        string mediaFolder;
        try { mediaFolder = Path.Combine(Windows.Storage.ApplicationData.Current.LocalFolder.Path, "Media"); }
        catch { mediaFolder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "DailyMessage", "Media"); }

        foreach (var block in _config.Blocks)
        {
            switch (block.Type)
            {
                case "text":
                {
                    var text = new TextBlock
                    {
                        Text = block.Text,
                        TextWrapping = TextWrapping.Wrap,
                        FontSize = block.Style switch { "heading" => 22, "note" => 13, _ => 16 },
                        FontWeight = block.Style == "heading" ? Microsoft.UI.Text.FontWeights.SemiBold : Microsoft.UI.Text.FontWeights.Normal,
                        Foreground = block.Style == "note"
                            ? (Microsoft.UI.Xaml.Media.Brush)Application.Current.Resources["TextFillColorSecondaryBrush"]
                            : (Microsoft.UI.Xaml.Media.Brush)Application.Current.Resources["TextFillColorPrimaryBrush"]
                    };
                    MessageBlocks.Children.Add(text);
                    break;
                }
                case "image":
                {
                    var path = Path.Combine(mediaFolder, Path.GetFileName(block.File));
                    if (!File.Exists(path)) break;
                    var image = new Image { Stretch = Microsoft.UI.Xaml.Media.Stretch.Uniform, MaxWidth = 720, MaxHeight = 420 };
                    image.ImageOpened += (_, _) =>
                    {
                        if (image.Source is BitmapImage bitmap && bitmap.PixelWidth > 0 && bitmap.PixelHeight > 0)
                        {
                            var scale = Math.Min(1.0, Math.Min(720.0 / bitmap.PixelWidth, 420.0 / bitmap.PixelHeight));
                            image.Width = bitmap.PixelWidth * scale;
                            image.Height = bitmap.PixelHeight * scale;
                        }
                    };
                    image.Source = new BitmapImage(new Uri(path));
                    MessageBlocks.Children.Add(image);
                    if (!string.IsNullOrWhiteSpace(block.Caption))
                    {
                        MessageBlocks.Children.Add(new TextBlock
                        {
                            Text = block.Caption,
                            FontSize = 12,
                            Foreground = (Microsoft.UI.Xaml.Media.Brush)Application.Current.Resources["TextFillColorSecondaryBrush"],
                            TextWrapping = TextWrapping.Wrap
                        });
                    }
                    break;
                }
                case "checklist":
                {
                    var panel = new StackPanel { Spacing = 6 };
                    if (!string.IsNullOrWhiteSpace(block.ChecklistTitle))
                        panel.Children.Add(new TextBlock { Text = block.ChecklistTitle, FontWeight = Microsoft.UI.Text.FontWeights.SemiBold });
                    var boxes = new List<CheckBox>();
                    foreach (var item in block.Items)
                    {
                        var check = new CheckBox { Content = item, IsChecked = false };
                        check.Checked += (_, _) => RefreshState();
                        check.Unchecked += (_, _) => RefreshState();
                        boxes.Add(check);
                        panel.Children.Add(check);
                    }
                    _checklists.Add((block.Required, boxes));
                    MessageBlocks.Children.Add(panel);
                    break;
                }
            }
        }
    }

    private IEnumerable<ChecklistProgress> Progress()
    {
        return _checklists.Select(x =>
            new ChecklistProgress(x.Required, x.Items.Count, x.Items.Count(c => c.IsChecked == true)));
    }

    private void RefreshState()
    {
        var elapsed = _clock.Elapsed;
        var remaining = MessageRules.RemainingSeconds(elapsed, _seconds);
        CountdownText.Text = _preview
            ? $"Prévia — tempo restante: {remaining} s"
            : $"Tempo restante: {remaining} s";
        CountdownBar.Value = Math.Max(0, remaining);
        var required = Progress().Where(x => x.Required).ToArray();
        var allItems = required.All(x => x.IsComplete);
        var canClose = MessageRules.CanClose(elapsed, _seconds, required);
        StatusText.Text = elapsed.TotalSeconds < _seconds
            ? "A mensagem permanecerá aberta durante o tempo definido."
            : allItems
                ? "Tudo pronto. Você já pode continuar."
                : "O tempo terminou. Marque todos os itens obrigatórios para continuar.";
        CloseButton.IsEnabled = canClose;
        ApplyLock(!canClose);
    }

    private void ApplyLock(bool locked)
    {
        if (_locked == locked && _hwnd == 0) return;
        _locked = locked;
        if (_hwnd != 0)
            Win32WindowLock.SetLocked(_hwnd, locked);
    }

    private void CloseButton_Click(object sender, RoutedEventArgs e)
    {
        if (!_locked)
        {
            _timer.Stop();
            Close();
        }
    }
}
