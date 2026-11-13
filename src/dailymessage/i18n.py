from __future__ import annotations

import ctypes
import sys

LANG_NAMES = {"pt-BR": "Português (Brasil)", "en": "English"}

STRINGS: dict[str, dict[str, str]] = {
    "pt-BR": {
        "app.name": "Daily Message",
        "settings.subtitle": "Exiba uma mensagem sempre que o Windows iniciar.",
        "card.content": "Conteúdo da mensagem",
        "content.hint": "Monte a mensagem com blocos de texto, imagens e checklists. A janela se adapta ao tamanho do conteúdo (limite de {max} caracteres de texto no total).",
        "field.title": "Título",
        "field.title.placeholder": "Ex.: Bom dia!",
        "block.text": "Texto",
        "block.image": "Imagem",
        "block.checklist": "Checklist",
        "add.text": "+ Texto",
        "add.image": "+ Imagem",
        "add.checklist": "+ Checklist",
        "label.style": "Estilo",
        "style.body": "Texto normal",
        "style.heading": "Título",
        "style.note": "Nota",
        "image.choose": "Escolher imagem…",
        "image.change": "Trocar imagem…",
        "image.none": "Nenhuma imagem selecionada",
        "image.caption.placeholder": "Legenda (opcional)",
        "image.filter": "Imagens",
        "image.error": "Não foi possível usar a imagem: {detail}",
        "image.missing": "(imagem indisponível)",
        "check.title.placeholder": "Título da checklist (opcional)",
        "check.items_hint": "Um item por linha.",
        "check.required": "Obrigatória para fechar a janela",
        "card.time": "Tempo de exibição obrigatório",
        "time.desc": "A janela só poderá ser fechada quando o contador chegar a zero e todos os itens obrigatórios estiverem marcados.",
        "time.seconds": "segundos",
        "time.range": "Entre {min} e {max} segundos.",
        "card.look": "Aparência",
        "look.theme": "Tema",
        "theme.system": "Sistema",
        "theme.light": "Claro",
        "theme.dark": "Escuro",
        "look.accent": "Cor de destaque",
        "look.language": "Idioma",
        "lang.auto": "Automático",
        "card.autostart": "Inicialização",
        "autostart.switch": "Iniciar junto com o Windows",
        "autostart.desc": "Mostra a mensagem automaticamente quando você entrar no Windows.",
        "autostart.blocked_user": "Desativado nas configurações do Windows. Reative em Configurações > Aplicativos > Inicialização.",
        "autostart.blocked_policy": "A inicialização automática foi bloqueada pela política da sua organização.",
        "autostart.managed_policy": "A inicialização automática é gerenciada pela política da sua organização.",
        "autostart.unsupported": "A inicialização automática só está disponível no Windows.",
        "autostart.store_only": "Instale o Daily Message pela Microsoft Store para habilitar a inicialização automática.",
        "autostart.error": "Não foi possível alterar a inicialização automática.",
        "autostart.open_settings": "Abrir configurações do Windows",
        "btn.preview": "Visualizar",
        "btn.save": "Salvar",
        "saved": "✓ Configurações salvas.",
        "err.seconds": "Informe um número entre {min} e {max}.",
        "err.no_content": "Adicione pelo menos um conteúdo à mensagem.",
        "err.too_many_blocks": "Limite de {max} blocos atingido.",
        "err.too_many_images": "Limite de {max} imagens atingido.",
        "err.too_long": "O texto excede o limite ({max} caracteres no total).",
        "err.save": "Não foi possível salvar: {detail}",
        "msg.wait": "Você poderá continuar em",
        "msg.need_items": "O tempo acabou. Marque todos os itens obrigatórios para continuar.",
        "msg.items_progress": "Itens obrigatórios marcados: {done}/{total}",
        "msg.ready": "Tudo pronto! Você já pode continuar.",
        "msg.ok": "Ok",
        "msg.preview_tag": "Prévia",
        "msg.preview_note": "Prévia · tempo limitado a {s} s (no uso real: o tempo configurado)",
        "footer.about": "Versão {v} · Código aberto (MIT) · Este app não coleta nenhum dado.",
    },
    "en": {
        "app.name": "Daily Message",
        "settings.subtitle": "Show a message every time Windows starts.",
        "card.content": "Message content",
        "content.hint": "Build the message with text, image and checklist blocks. The window adapts to the content size ({max} text characters in total).",
        "field.title": "Title",
        "field.title.placeholder": "E.g.: Good morning!",
        "block.text": "Text",
        "block.image": "Image",
        "block.checklist": "Checklist",
        "add.text": "+ Text",
        "add.image": "+ Image",
        "add.checklist": "+ Checklist",
        "label.style": "Style",
        "style.body": "Normal text",
        "style.heading": "Heading",
        "style.note": "Note",
        "image.choose": "Choose image…",
        "image.change": "Change image…",
        "image.none": "No image selected",
        "image.caption.placeholder": "Caption (optional)",
        "image.filter": "Images",
        "image.error": "Could not use the image: {detail}",
        "image.missing": "(image unavailable)",
        "check.title.placeholder": "Checklist title (optional)",
        "check.items_hint": "One item per line.",
        "check.required": "Required to close the window",
        "card.time": "Required display time",
        "time.desc": "The window can only be closed once the countdown reaches zero and all required items are checked.",
        "time.seconds": "seconds",
        "time.range": "Between {min} and {max} seconds.",
        "card.look": "Appearance",
        "look.theme": "Theme",
        "theme.system": "System",
        "theme.light": "Light",
        "theme.dark": "Dark",
        "look.accent": "Accent color",
        "look.language": "Language",
        "lang.auto": "Automatic",
        "card.autostart": "Startup",
        "autostart.switch": "Start with Windows",
        "autostart.desc": "Shows the message automatically when you sign in to Windows.",
        "autostart.blocked_user": "Disabled in Windows settings. Re-enable it in Settings > Apps > Startup.",
        "autostart.blocked_policy": "Startup was blocked by your organization's policy.",
        "autostart.managed_policy": "Startup is managed by your organization's policy.",
        "autostart.unsupported": "Startup is only available on Windows.",
        "autostart.store_only": "Install Daily Message from the Microsoft Store to enable startup.",
        "autostart.error": "Could not change the startup setting.",
        "autostart.open_settings": "Open Windows settings",
        "btn.preview": "Preview",
        "btn.save": "Save",
        "saved": "✓ Settings saved.",
        "err.seconds": "Enter a number between {min} and {max}.",
        "err.no_content": "Add at least one content block to the message.",
        "err.too_many_blocks": "Limit of {max} blocks reached.",
        "err.too_many_images": "Limit of {max} images reached.",
        "err.too_long": "Text exceeds the limit ({max} characters in total).",
        "err.save": "Could not save: {detail}",
        "msg.wait": "You can continue in",
        "msg.need_items": "Time is up. Check all required items to continue.",
        "msg.items_progress": "Required items checked: {done}/{total}",
        "msg.ready": "All set! You can continue now.",
        "msg.ok": "Ok",
        "msg.preview_tag": "Preview",
        "msg.preview_note": "Preview · time limited to {s} s (real use: the configured time)",
        "footer.about": "Version {v} · Open source (MIT) · This app collects no data.",
    },
}


def detect_system_language() -> str:
    if sys.platform == "win32":
        try:
            buf = ctypes.create_unicode_buffer(85)
            if ctypes.windll.kernel32.GetUserDefaultLocaleName(buf, 85):
                return "pt-BR" if buf.value.lower().startswith("pt") else "en"
        except Exception:
            pass
    return "en"


class Translator:
    def __init__(self, language: str = "auto") -> None:
        lang = detect_system_language() if language == "auto" else language
        self.lang = lang if lang in STRINGS else "en"

    def t(self, key: str, **kwargs) -> str:
        text = STRINGS[self.lang].get(key) or STRINGS["en"].get(key) or key
        return text.format(**kwargs) if kwargs else text
