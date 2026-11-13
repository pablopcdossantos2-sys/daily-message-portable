using System.Globalization;

namespace DailyMessage;

internal static class UiText
{
    private static readonly Dictionary<string, (string Pt, string En)> Texts = new()
    {
        ["app.subtitle"] = ("Monte a mensagem que será exibida quando você entrar no Windows.", "Create the message that will appear when you sign in to Windows."),
        ["content"] = ("Conteúdo da mensagem", "Message content"),
        ["title"] = ("Título", "Title"),
        ["title.placeholder"] = ("Ex.: Bom dia!", "E.g. Good morning!"),
        ["add.text"] = ("+ Texto", "+ Text"),
        ["add.image"] = ("+ Imagem", "+ Image"),
        ["add.checklist"] = ("+ Checklist", "+ Checklist"),
        ["content.hint"] = ("Organize blocos de texto, imagens e checklists. Limite total: 30.000 caracteres.", "Arrange text, image and checklist blocks. Total limit: 30,000 characters."),
        ["time"] = ("Tempo obrigatório", "Required display time"),
        ["time.description"] = ("A mensagem só poderá ser fechada quando o contador chegar a zero e todas as checklists obrigatórias estiverem concluídas.", "The message can only be closed when the countdown reaches zero and every required checklist is complete."),
        ["seconds"] = ("Segundos (3 a 600)", "Seconds (3 to 600)"),
        ["appearance"] = ("Aparência", "Appearance"),
        ["theme"] = ("Tema", "Theme"),
        ["theme.system"] = ("Sistema", "System"),
        ["theme.light"] = ("Claro", "Light"),
        ["theme.dark"] = ("Escuro", "Dark"),
        ["accent"] = ("Cor de destaque", "Accent color"),
        ["accent.indigo"] = ("Índigo", "Indigo"),
        ["accent.teal"] = ("Verde-azulado", "Teal"),
        ["accent.rose"] = ("Rosa", "Rose"),
        ["accent.amber"] = ("Âmbar", "Amber"),
        ["language"] = ("Idioma", "Language"),
        ["language.auto"] = ("Automático", "Automatic"),
        ["language.pt"] = ("Português (Brasil)", "Portuguese (Brazil)"),
        ["startup"] = ("Inicialização com o Windows", "Windows startup"),
        ["startup.toggle"] = ("Iniciar junto com o Windows", "Start with Windows"),
        ["startup.enabled"] = ("A mensagem será exibida quando você entrar no Windows.", "The message will appear when you sign in to Windows."),
        ["startup.disabled"] = ("A inicialização automática está desativada.", "Automatic startup is disabled."),
        ["startup.blockedUser"] = ("A inicialização foi desativada nas configurações do Windows. Você pode reativá-la por lá.", "Startup was disabled in Windows settings. You can re-enable it there."),
        ["startup.blockedPolicy"] = ("A inicialização foi bloqueada pela política da organização.", "Startup was blocked by your organization's policy."),
        ["startup.managedPolicy"] = ("A inicialização é gerenciada pela política da organização.", "Startup is managed by your organization's policy."),
        ["startup.openSettings"] = ("Abrir configurações de inicialização do Windows", "Open Windows startup settings"),
        ["preview"] = ("Visualizar", "Preview"),
        ["save"] = ("Salvar", "Save"),
        ["saved"] = ("Configurações salvas neste computador.", "Settings saved on this computer."),
        ["save.error"] = ("Não foi possível salvar: ", "Could not save: "),
        ["blocks.limit"] = ("O limite de 30 blocos foi atingido.", "The 30-block limit has been reached."),
        ["images.limit"] = ("O limite de 10 imagens foi atingido.", "The 10-image limit has been reached."),
        ["image.choose"] = ("Escolher imagem...", "Choose image..."),
        ["image.change"] = ("Trocar imagem...", "Change image..."),
        ["image.none"] = ("Nenhuma imagem selecionada", "No image selected"),
        ["image.caption"] = ("Legenda (opcional)", "Caption (optional)"),
        ["image.error"] = ("Não foi possível importar a imagem: ", "Could not import image: "),
        ["check.title"] = ("Título da checklist (opcional)", "Checklist title (optional)"),
        ["check.items"] = ("Itens — um por linha", "Items — one per line"),
        ["check.required"] = ("Obrigatória para fechar a janela", "Required to close the window"),
        ["block.text"] = ("Texto", "Text"),
        ["block.image"] = ("Imagem", "Image"),
        ["block.checklist"] = ("Checklist", "Checklist"),
        ["block.remove"] = ("Remover", "Remove"),
        ["style"] = ("Estilo", "Style"),
        ["style.body"] = ("Texto normal", "Normal text"),
        ["style.heading"] = ("Título", "Heading"),
        ["style.note"] = ("Nota", "Note"),
        ["text.header"] = ("Texto", "Text"),
        ["message.wait"] = ("A mensagem permanecerá aberta durante o tempo definido.", "The message will remain open for the selected time."),
        ["message.needItems"] = ("O tempo terminou. Marque todos os itens obrigatórios para continuar.", "Time is up. Check all required items to continue."),
        ["message.ready"] = ("Tudo pronto. Você já pode continuar.", "All set. You can continue now."),
        ["message.remaining"] = ("Tempo restante: {0} s", "Time remaining: {0} s"),
        ["message.preview"] = ("Prévia — tempo restante: {0} s", "Preview — time remaining: {0} s"),
        ["message.previewTitle"] = ("Daily Message — Prévia", "Daily Message — Preview")
    };

    public static bool IsEnglish(string language)
        => language == "en" || (language == "auto" &&
            !CultureInfo.CurrentUICulture.TwoLetterISOLanguageName.Equals("pt", StringComparison.OrdinalIgnoreCase));

    public static string Get(string language, string key)
    {
        if (!Texts.TryGetValue(key, out var pair))
            return key;
        return IsEnglish(language) ? pair.En : pair.Pt;
    }

    public static string Get(string language, string key, params object[] args)
        => string.Format(CultureInfo.CurrentCulture, Get(language, key), args);
}
