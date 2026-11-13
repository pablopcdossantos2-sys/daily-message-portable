using System.Diagnostics;
using DailyMessage.Core;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI;
using Windows.ApplicationModel;
using Windows.Storage;
using Windows.Storage.Pickers;
using WinRT.Interop;

namespace DailyMessage;

public sealed partial class MainWindow : Window
{
    private MessageConfig _config = new();
    private readonly List<Action> _collectors = [];
    private bool _updatingStartup;
    private bool _updatingUi;

    public MainWindow()
    {
        InitializeComponent();
        Title = "Daily Message";
        RootPanel.Loaded += RootPanel_Loaded;
    }

    private static string LocalFolder
    {
        get
        {
            try { return ApplicationData.Current.LocalFolder.Path; }
            catch
            {
                var path = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "DailyMessage");
                Directory.CreateDirectory(path);
                return path;
            }
        }
    }

    private static string ConfigFile => Path.Combine(LocalFolder, "config.json");
    private static string MediaFolder
    {
        get
        {
            var path = Path.Combine(LocalFolder, "Media");
            Directory.CreateDirectory(path);
            return path;
        }
    }

    private async void RootPanel_Loaded(object sender, RoutedEventArgs e)
    {
        RootPanel.Loaded -= RootPanel_Loaded;
        _config = await ConfigStore.LoadAsync(ConfigFile);
        TitleBox.Text = _config.Title;
        SecondsBox.Value = _config.Seconds;
        _updatingUi = true;
        ThemeBox.SelectedIndex = _config.Theme switch { "light" => 1, "dark" => 2, _ => 0 };
        AccentBox.SelectedIndex = _config.Accent switch { "teal" => 1, "rose" => 2, "amber" => 3, _ => 0 };
        LanguageBox.SelectedIndex = _config.Language switch { "pt-BR" => 1, "en" => 2, _ => 0 };
        _updatingUi = false;
        ApplyTheme();
        ApplyAccent();
        ApplyLanguage();
        RenderBlocks();
        await RefreshStartupAsync();
    }

    private void RenderBlocks()
    {
        BlocksPanel.Children.Clear();
        _collectors.Clear();
        for (var index = 0; index < _config.Blocks.Count; index++)
        {
            var block = _config.Blocks[index];
            var blockIndex = index;
            var card = new Border
            {
                Padding = new Thickness(14),
                CornerRadius = new CornerRadius(10),
                Background = (Brush)Application.Current.Resources["LayerFillColorDefaultBrush"],
                BorderBrush = (Brush)Application.Current.Resources["CardStrokeColorDefaultBrush"],
                BorderThickness = new Thickness(1)
            };
            var content = new StackPanel { Spacing = 8 };
            var header = new Grid { ColumnDefinitions = { new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) }, new ColumnDefinition { Width = GridLength.Auto }, new ColumnDefinition { Width = GridLength.Auto }, new ColumnDefinition { Width = GridLength.Auto } } };
            var label = new TextBlock
            {
                Text = UiText.Get(_config.Language, block.Type switch { "text" => "block.text", "image" => "block.image", _ => "block.checklist" }),
                FontWeight = Microsoft.UI.Text.FontWeights.SemiBold,
                VerticalAlignment = VerticalAlignment.Center
            };
            header.Children.Add(label);

            var moveUp = new Button { Content = "↑", MinWidth = 36, Padding = new Thickness(8, 4, 8, 4), IsEnabled = index > 0 };
            Grid.SetColumn(moveUp, 1);
            moveUp.Click += (_, _) => MoveBlock(blockIndex, -1);
            header.Children.Add(moveUp);

            var moveDown = new Button { Content = "↓", MinWidth = 36, Padding = new Thickness(8, 4, 8, 4), IsEnabled = index < _config.Blocks.Count - 1 };
            Grid.SetColumn(moveDown, 2);
            moveDown.Click += (_, _) => MoveBlock(blockIndex, 1);
            header.Children.Add(moveDown);

            var remove = new Button { Content = UiText.Get(_config.Language, "block.remove"), MinWidth = 76 };
            Grid.SetColumn(remove, 3);
            remove.Click += (_, _) => RemoveBlock(blockIndex);
            header.Children.Add(remove);
            content.Children.Add(header);

            switch (block.Type)
            {
                case "text":
                    BuildTextEditor(content, block);
                    break;
                case "image":
                    BuildImageEditor(content, block);
                    break;
                case "checklist":
                    BuildChecklistEditor(content, block);
                    break;
            }

            card.Child = content;
            BlocksPanel.Children.Add(card);
        }
    }

    private void BuildTextEditor(Panel parent, MessageBlock block)
    {
        var style = new ComboBox { Header = UiText.Get(_config.Language, "style"), Width = 220, SelectedIndex = block.Style switch { "heading" => 1, "note" => 2, _ => 0 } };
        style.Items.Add(new ComboBoxItem { Content = UiText.Get(_config.Language, "style.body") });
        style.Items.Add(new ComboBoxItem { Content = UiText.Get(_config.Language, "style.heading") });
        style.Items.Add(new ComboBoxItem { Content = UiText.Get(_config.Language, "style.note") });
        var text = new TextBox
        {
            Header = UiText.Get(_config.Language, "text.header"),
            Text = block.Text,
            AcceptsReturn = true,
            TextWrapping = TextWrapping.Wrap,
            MinHeight = 110,
            MaxLength = 20000
        };
        parent.Children.Add(style);
        parent.Children.Add(text);
        _collectors.Add(() =>
        {
            block.Style = style.SelectedIndex switch { 1 => "heading", 2 => "note", _ => "body" };
            block.Text = text.Text;
        });
    }

    private void BuildImageEditor(Panel parent, MessageBlock block)
    {
        var location = new TextBlock
        {
            Text = string.IsNullOrWhiteSpace(block.File) ? UiText.Get(_config.Language, "image.none") : block.File,
            TextWrapping = TextWrapping.Wrap,
            Foreground = (Brush)Application.Current.Resources["TextFillColorSecondaryBrush"]
        };
        var choose = new Button { Content = string.IsNullOrWhiteSpace(block.File) ? UiText.Get(_config.Language, "image.choose") : UiText.Get(_config.Language, "image.change") };
        choose.Click += async (_, _) =>
        {
            var path = await PickImageAsync();
            if (path is null) return;
            block.File = path;
            location.Text = Path.GetFileName(path);
            choose.Content = UiText.Get(_config.Language, "image.change");
        };
        var caption = new TextBox { Header = UiText.Get(_config.Language, "image.caption"), Text = block.Caption, MaxLength = 200 };
        parent.Children.Add(location);
        parent.Children.Add(choose);
        parent.Children.Add(caption);
        _collectors.Add(() => block.Caption = caption.Text);
    }

    private void BuildChecklistEditor(Panel parent, MessageBlock block)
    {
        var title = new TextBox { Header = UiText.Get(_config.Language, "check.title"), Text = block.ChecklistTitle, MaxLength = 100 };
        var items = new TextBox
        {
            Header = UiText.Get(_config.Language, "check.items"),
            Text = string.Join(Environment.NewLine, block.Items),
            AcceptsReturn = true,
            TextWrapping = TextWrapping.Wrap,
            MinHeight = 110
        };
        var required = new CheckBox
        {
            Content = UiText.Get(_config.Language, "check.required"),
            IsChecked = block.Required
        };
        parent.Children.Add(title);
        parent.Children.Add(items);
        parent.Children.Add(required);
        _collectors.Add(() =>
        {
            block.ChecklistTitle = title.Text;
            block.Items = items.Text.Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries)
                .Select(x => x.Trim()).Where(x => x.Length > 0).Take(30).ToList();
            block.Required = required.IsChecked == true;
        });
    }

    private async Task<string?> PickImageAsync()
    {
        try
        {
            var picker = new FileOpenPicker();
            foreach (var extension in new[] { ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp" })
                picker.FileTypeFilter.Add(extension);
            InitializeWithWindow.Initialize(picker, WindowNative.GetWindowHandle(this));
            var file = await picker.PickSingleFileAsync();
            if (file is null) return null;

            var extensionName = Path.GetExtension(file.Name).ToLowerInvariant();
            var destinationName = $"{Guid.NewGuid():N}{extensionName}";
            var destination = Path.Combine(MediaFolder, destinationName);
            File.Copy(file.Path, destination, overwrite: true);
            return destinationName;
        }
        catch (Exception ex)
        {
            FeedbackText.Text = UiText.Get(_config.Language, "image.error") + ex.Message;
            return null;
        }
    }

    private void SyncDraft()
    {
        foreach (var collect in _collectors) collect();
        _config.Title = TitleBox.Text;
        var seconds = double.IsFinite(SecondsBox.Value) ? SecondsBox.Value : 10;
        _config.Seconds = (int)Math.Clamp(seconds, 3, 600);
        _config.Theme = ThemeBox.SelectedIndex switch { 1 => "light", 2 => "dark", _ => "system" };
        _config.Accent = AccentBox.SelectedIndex switch { 1 => "teal", 2 => "rose", 3 => "amber", _ => "indigo" };
        _config.Language = LanguageBox.SelectedIndex switch { 1 => "pt-BR", 2 => "en", _ => "auto" };
        _config = _config.Normalize();
        ApplyTheme();
        ApplyAccent();
    }

    private void ApplyLanguage()
    {
        var language = _config.Language;
        Title = "Daily Message";
        SubtitleText.Text = UiText.Get(language, "app.subtitle");
        ContentHeading.Text = UiText.Get(language, "content");
        TitleBox.Header = UiText.Get(language, "title");
        TitleBox.PlaceholderText = UiText.Get(language, "title.placeholder");
        AddTextButton.Content = UiText.Get(language, "add.text");
        AddImageButton.Content = UiText.Get(language, "add.image");
        AddChecklistButton.Content = UiText.Get(language, "add.checklist");
        ContentHint.Text = UiText.Get(language, "content.hint");
        TimeHeading.Text = UiText.Get(language, "time");
        TimeDescription.Text = UiText.Get(language, "time.description");
        SecondsBox.Header = UiText.Get(language, "seconds");
        AppearanceHeading.Text = UiText.Get(language, "appearance");
        ThemeBox.Header = UiText.Get(language, "theme");
        ((ComboBoxItem)ThemeBox.Items[0]).Content = UiText.Get(language, "theme.system");
        ((ComboBoxItem)ThemeBox.Items[1]).Content = UiText.Get(language, "theme.light");
        ((ComboBoxItem)ThemeBox.Items[2]).Content = UiText.Get(language, "theme.dark");
        AccentBox.Header = UiText.Get(language, "accent");
        ((ComboBoxItem)AccentBox.Items[0]).Content = UiText.Get(language, "accent.indigo");
        ((ComboBoxItem)AccentBox.Items[1]).Content = UiText.Get(language, "accent.teal");
        ((ComboBoxItem)AccentBox.Items[2]).Content = UiText.Get(language, "accent.rose");
        ((ComboBoxItem)AccentBox.Items[3]).Content = UiText.Get(language, "accent.amber");
        LanguageBox.Header = UiText.Get(language, "language");
        ((ComboBoxItem)LanguageBox.Items[0]).Content = UiText.Get(language, "language.auto");
        ((ComboBoxItem)LanguageBox.Items[1]).Content = UiText.Get(language, "language.pt");
        ((ComboBoxItem)LanguageBox.Items[2]).Content = "English";
        StartupHeading.Text = UiText.Get(language, "startup");
        StartupToggle.Header = UiText.Get(language, "startup.toggle");
        OpenStartupSettingsButton.Content = UiText.Get(language, "startup.openSettings");
        PreviewButton.Content = UiText.Get(language, "preview");
        SaveButton.Content = UiText.Get(language, "save");
    }

    private void Language_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (_updatingUi || LanguageBox is null || BlocksPanel is null) return;
        _config.Language = LanguageBox.SelectedIndex switch { 1 => "pt-BR", 2 => "en", _ => "auto" };
        ApplyLanguage();
        RenderBlocks();
        _ = RefreshStartupAsync();
    }

    private void Appearance_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (_updatingUi || ThemeBox is null || AccentBox is null) return;
        _config.Theme = ThemeBox.SelectedIndex switch { 1 => "light", 2 => "dark", _ => "system" };
        _config.Accent = AccentBox.SelectedIndex switch { 1 => "teal", 2 => "rose", 3 => "amber", _ => "indigo" };
        ApplyTheme();
        ApplyAccent();
    }

    private void ApplyTheme()
    {
        RootGrid.RequestedTheme = _config.Theme switch
        {
            "light" => ElementTheme.Light,
            "dark" => ElementTheme.Dark,
            _ => ElementTheme.Default
        };
    }

    private static Windows.UI.Color GetAccentColor(string accent) => accent switch
    {
        "teal" => Windows.UI.Color.FromArgb(255, 13, 148, 136),
        "rose" => Windows.UI.Color.FromArgb(255, 225, 29, 72),
        "amber" => Windows.UI.Color.FromArgb(255, 217, 119, 6),
        _ => Windows.UI.Color.FromArgb(255, 99, 102, 241)
    };

    private void ApplyAccent()
    {
        SaveButton.Background = new SolidColorBrush(GetAccentColor(_config.Accent));
    }

    private void AddBlock(MessageBlock block)
    {
        SyncDraft();
        if (_config.Blocks.Count >= 30)
        {
            FeedbackText.Text = UiText.Get(_config.Language, "blocks.limit");
            return;
        }
        if (block.Type == "image" && _config.Blocks.Count(x => x.Type == "image") >= 10)
        {
            FeedbackText.Text = UiText.Get(_config.Language, "images.limit");
            return;
        }
        _config.Blocks.Add(block);
        RenderBlocks();
    }

    private void AddText_Click(object sender, RoutedEventArgs e) => AddBlock(MessageBlock.TextBlock());
    private void AddChecklist_Click(object sender, RoutedEventArgs e) => AddBlock(MessageBlock.ChecklistBlock());

    private async void AddImage_Click(object sender, RoutedEventArgs e)
    {
        SyncDraft();
        if (_config.Blocks.Count >= 30)
        {
            FeedbackText.Text = "O limite de 30 blocos foi atingido.";
            return;
        }
        if (_config.Blocks.Count(x => x.Type == "image") >= 10)
        {
            FeedbackText.Text = "O limite de 10 imagens foi atingido.";
            return;
        }

        var fileName = await PickImageAsync();
        if (string.IsNullOrWhiteSpace(fileName)) return;
        _config.Blocks.Add(new MessageBlock { Type = "image", File = fileName });
        RenderBlocks();
    }

    private void MoveBlock(int index, int direction)
    {
        SyncDraft();
        var target = index + direction;
        if (target < 0 || target >= _config.Blocks.Count) return;
        (_config.Blocks[index], _config.Blocks[target]) = (_config.Blocks[target], _config.Blocks[index]);
        RenderBlocks();
    }

    private void RemoveBlock(int index)
    {
        SyncDraft();
        if (index < 0 || index >= _config.Blocks.Count) return;
        _config.Blocks.RemoveAt(index);
        RenderBlocks();
    }

    private async void Save_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            SyncDraft();
            await ConfigStore.SaveAsync(ConfigFile, _config);
            FeedbackText.Text = UiText.Get(_config.Language, "saved");
        }
        catch (Exception ex)
        {
            FeedbackText.Text = UiText.Get(_config.Language, "save.error") + ex.Message;
        }
    }

    private void Preview_Click(object sender, RoutedEventArgs e)
    {
        SyncDraft();
        var preview = new MessageWindow(_config, preview: true);
        preview.Activate();
    }

    private async void StartupToggle_Toggled(object sender, RoutedEventArgs e)
    {
        if (_updatingStartup) return;
        try
        {
            var result = StartupToggle.IsOn
                ? await StartupService.EnableAsync()
                : await StartupService.DisableAsync();
            await RefreshStartupAsync(result);
        }
        catch (Exception ex)
        {
            StartupNote.Text = $"Não foi possível alterar a inicialização: {ex.Message}";
            await RefreshStartupAsync();
        }
    }

    private async Task RefreshStartupAsync(StartupTaskState? current = null)
    {
        _updatingStartup = true;
        try
        {
            current ??= await StartupService.GetStateAsync();
            switch (current)
            {
                case StartupTaskState.Enabled:
                    StartupToggle.IsOn = true;
                    StartupToggle.IsEnabled = true;
                    StartupNote.Text = "A mensagem será exibida quando você entrar no Windows.";
                    OpenStartupSettingsButton.Visibility = Visibility.Collapsed;
                    break;
                case StartupTaskState.EnabledByPolicy:
                    StartupToggle.IsOn = true;
                    StartupToggle.IsEnabled = false;
                    StartupNote.Text = "A inicialização é gerenciada pela política da organização.";
                    OpenStartupSettingsButton.Visibility = Visibility.Collapsed;
                    break;
                case StartupTaskState.DisabledByUser:
                    StartupToggle.IsOn = false;
                    StartupToggle.IsEnabled = false;
                    StartupNote.Text = "A inicialização foi desativada nas configurações do Windows. Você pode reativá-la por lá.";
                    OpenStartupSettingsButton.Visibility = Visibility.Visible;
                    break;
                case StartupTaskState.DisabledByPolicy:
                    StartupToggle.IsOn = false;
                    StartupToggle.IsEnabled = false;
                    StartupNote.Text = "A inicialização foi bloqueada pela política da organização.";
                    OpenStartupSettingsButton.Visibility = Visibility.Collapsed;
                    break;
                case StartupTaskState.Disabled:
                    StartupToggle.IsOn = false;
                    StartupToggle.IsEnabled = true;
                    StartupNote.Text = "A inicialização automática está desativada.";
                    OpenStartupSettingsButton.Visibility = Visibility.Collapsed;
                    break;
                default:
                    StartupToggle.IsOn = false;
                    StartupToggle.IsEnabled = false;
                    StartupNote.Text = "A inicialização automática estará disponível quando o aplicativo for instalado como MSIX.";
                    OpenStartupSettingsButton.Visibility = Visibility.Collapsed;
                    break;
            }
        }
        catch
        {
            StartupToggle.IsOn = false;
            StartupToggle.IsEnabled = false;
            StartupNote.Text = "A inicialização automática só está disponível na versão instalada pela Microsoft Store.";
        }
        finally
        {
            _updatingStartup = false;
        }
    }

    private async void OpenStartupSettings_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            await Windows.System.Launcher.LaunchUriAsync(new Uri("ms-settings:startupapps"));
        }
        catch { }
    }
}
