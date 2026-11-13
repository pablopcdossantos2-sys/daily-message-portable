"""Janela de configurações com editor de blocos (texto, imagem, checklist)."""
from __future__ import annotations

import copy
import dataclasses
import logging
import os
import webbrowser
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from . import REPO_URL, __version__, autostart, media, theme, uiutil
from . import config as cfgmod
from .config import (MAX_BLOCKS, MAX_CAPTION_LEN, MAX_IMAGES, MAX_LIST_TITLE_LEN, MAX_SECONDS,
                     MAX_TITLE_LEN, MAX_TOTAL_TEXT, MIN_SECONDS, Config)
from .i18n import LANG_NAMES, Translator
from .message_window import open_preview

log = logging.getLogger(__name__)
PRESETS = ["5", "10", "15", "30", "60"]


class SettingsApp(ctk.CTk):
    def __init__(self, cfg: Config) -> None:
        theme.apply_mode(cfg.theme)
        super().__init__(fg_color=theme.BG)
        self.cfg = cfg
        self.blocks: list[dict] = copy.deepcopy(cfg.blocks)
        self._getters: list = []
        self.tr = Translator(cfg.language)
        self.title(self.tr.t("app.name"))
        uiutil.fit_and_center(self, 780, 860, min_size=(660, 520))
        uiutil.apply_icon(self)
        self._build()

    # ---------------------------------------------------------- helpers
    def _card(self, parent, title: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color=theme.SURFACE, corner_radius=16,
                            border_width=1, border_color=theme.BORDER)
        card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(card, text=title, font=theme.font(15, "bold"), text_color=theme.TEXT,
                     anchor="w").pack(fill="x", padx=20, pady=(16, 4))
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=(0, 18))
        return body

    def _muted(self, parent, text: str, size: int = 13, **kw) -> ctk.CTkLabel:
        return ctk.CTkLabel(parent, text=text, font=theme.font(size), text_color=theme.MUTED,
                            anchor="w", justify="left", **kw)

    @staticmethod
    def _field(bg=theme.SURFACE_ALT) -> dict:
        return dict(fg_color=bg, border_color=theme.BORDER, text_color=theme.TEXT)

    def _defer(self, fn) -> None:
        # adia a reconstrução para não destruir um botão dentro do próprio clique
        self.after(150, fn)

    def _feedback(self, text: str, error: bool = False) -> None:
        self.feedback.configure(text=text, text_color=theme.DANGER if error else theme.SUCCESS)
        self.after(4500, lambda: self._clear_feedback(text))

    def _clear_feedback(self, text: str) -> None:
        try:
            if self.feedback.cget("text") == text:
                self.feedback.configure(text="")
        except Exception:
            pass

    # ---------------------------------------------------------- construção
    def _build(self) -> None:
        for child in self.winfo_children():
            child.destroy()
        tr, cfg = self.tr, self.cfg
        accent = theme.accent(cfg.accent)
        accent_hover = theme.hover_of(accent)

        footer = ctk.CTkFrame(self, fg_color=theme.SURFACE, corner_radius=0)
        footer.pack(side="bottom", fill="x")
        inner = ctk.CTkFrame(footer, fg_color="transparent")
        inner.pack(fill="x", padx=22, pady=14)
        self.feedback = ctk.CTkLabel(inner, text="", font=theme.font(13), anchor="w")
        self.feedback.pack(side="left")
        ctk.CTkButton(inner, text=tr.t("btn.save"), width=130, height=42, corner_radius=12,
                      font=theme.font(14, "bold"), fg_color=accent, hover_color=accent_hover,
                      text_color=theme.ON_ACCENT, command=self._save).pack(side="right")
        ctk.CTkButton(inner, text=tr.t("btn.preview"), width=130, height=42, corner_radius=12,
                      font=theme.font(14), fg_color="transparent", border_width=1,
                      border_color=theme.BORDER, text_color=theme.TEXT,
                      hover_color=theme.SURFACE_ALT, command=self._preview).pack(side="right", padx=(0, 10))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=14, pady=(14, 0))
        ctk.CTkLabel(scroll, text=tr.t("app.name"), font=theme.font(26, "bold"),
                     text_color=theme.TEXT, anchor="w").pack(fill="x", padx=4)
        self._muted(scroll, tr.t("settings.subtitle"), 14).pack(fill="x", padx=4, pady=(0, 16))

        # --- conteúdo ---
        body = self._card(scroll, tr.t("card.content"))
        self._muted(body, tr.t("content.hint", max=MAX_TOTAL_TEXT), wraplength=640).pack(anchor="w", pady=(0, 10))
        self._muted(body, tr.t("field.title")).pack(anchor="w")
        self.title_entry = ctk.CTkEntry(body, height=40, corner_radius=10, font=theme.font(14),
                                        placeholder_text=tr.t("field.title.placeholder"), **self._field())
        self.title_entry.pack(fill="x", pady=(4, 6))
        self.title_entry.insert(0, cfg.title)
        self.blocks_frame = ctk.CTkFrame(body, fg_color="transparent")
        self.blocks_frame.pack(fill="x", pady=(8, 0))
        add_row = ctk.CTkFrame(body, fg_color="transparent")
        add_row.pack(anchor="w", pady=(4, 0))
        for kind in ("text", "image", "checklist"):
            ctk.CTkButton(add_row, text=tr.t(f"add.{kind}"), height=36, corner_radius=10,
                          font=theme.font(13, "bold"), fg_color=accent, hover_color=accent_hover,
                          text_color=theme.ON_ACCENT,
                          command=lambda k=kind: self._add(k)).pack(side="left", padx=(0, 8))
        self._render_blocks()

        # --- tempo ---
        body = self._card(scroll, tr.t("card.time"))
        self._muted(body, tr.t("time.desc"), wraplength=640).pack(anchor="w", pady=(0, 10))
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(anchor="w")
        btn = dict(width=40, height=40, corner_radius=10, fg_color=theme.SURFACE_ALT,
                   hover_color=theme.BORDER, text_color=theme.TEXT, font=theme.font(18, "bold"))
        ctk.CTkButton(row, text="−", command=lambda: self._bump(-1), **btn).pack(side="left")
        self.sec_var = ctk.StringVar(value=str(cfg.seconds))
        ctk.CTkEntry(row, width=90, height=40, justify="center", corner_radius=10,
                     font=theme.font(18, "bold"), textvariable=self.sec_var,
                     **self._field()).pack(side="left", padx=8)
        ctk.CTkButton(row, text="+", command=lambda: self._bump(1), **btn).pack(side="left")
        self._muted(row, tr.t("time.seconds"), 14).pack(side="left", padx=12)
        self.presets = ctk.CTkSegmentedButton(
            body, values=PRESETS, height=34, corner_radius=10,
            selected_color=accent, selected_hover_color=accent_hover,
            unselected_color=theme.SURFACE_ALT, unselected_hover_color=theme.BORDER,
            fg_color=theme.SURFACE_ALT, text_color=theme.TEXT,
            command=lambda v: self.sec_var.set(v))
        self.presets.pack(anchor="w", pady=(12, 4))
        self._muted(body, tr.t("time.range", min=MIN_SECONDS, max=MAX_SECONDS), 12).pack(anchor="w")
        self.sec_var.trace_add("write", self._filter_seconds)
        self._filter_seconds()

        # --- aparência ---
        body = self._card(scroll, tr.t("card.look"))
        self._muted(body, tr.t("look.theme")).pack(anchor="w")
        modes = [("system", tr.t("theme.system")), ("light", tr.t("theme.light")),
                 ("dark", tr.t("theme.dark"))]
        seg = ctk.CTkSegmentedButton(
            body, values=[n for _, n in modes], height=34, corner_radius=10,
            selected_color=accent, selected_hover_color=accent_hover,
            unselected_color=theme.SURFACE_ALT, unselected_hover_color=theme.BORDER,
            fg_color=theme.SURFACE_ALT, text_color=theme.TEXT,
            command=lambda label: self._on_theme({n: k for k, n in modes}[label]))
        seg.pack(anchor="w", pady=(4, 12))
        seg.set(dict(modes)[cfg.theme])

        self._muted(body, tr.t("look.accent")).pack(anchor="w")
        chips = ctk.CTkFrame(body, fg_color="transparent")
        chips.pack(anchor="w", pady=(6, 12))
        for name, color in theme.ACCENTS.items():
            ctk.CTkButton(chips, text="", width=34, height=34, corner_radius=17, fg_color=color,
                          hover_color=theme.hover_of(color),
                          border_width=3 if name == cfg.accent else 0, border_color=theme.TEXT,
                          command=lambda n=name: self._on_accent(n)).pack(side="left", padx=(0, 10))

        self._muted(body, tr.t("look.language")).pack(anchor="w")
        names = {"auto": tr.t("lang.auto"), **LANG_NAMES}
        self.lang_var = ctk.StringVar(value=names[cfg.language])
        ctk.CTkOptionMenu(
            body, values=list(names.values()), variable=self.lang_var, height=36, corner_radius=10,
            font=theme.font(14), dropdown_font=theme.font(14), fg_color=theme.SURFACE_ALT,
            button_color=theme.BORDER, button_hover_color=theme.MUTED, text_color=theme.TEXT,
            command=lambda label: self._on_language({v: k for k, v in names.items()}[label]),
        ).pack(anchor="w", pady=(4, 0))

        # --- inicialização ---
        body = self._card(scroll, tr.t("card.autostart"))
        self.auto_switch = ctk.CTkSwitch(body, text=tr.t("autostart.switch"), font=theme.font(14),
                                         text_color=theme.TEXT, progress_color=accent,
                                         command=self._on_autostart)
        self.auto_switch.pack(anchor="w")
        self._muted(body, tr.t("autostart.desc")).pack(anchor="w", pady=(4, 0))
        self.auto_note = ctk.CTkLabel(body, text="", font=theme.font(13), text_color=theme.DANGER,
                                      anchor="w", justify="left", wraplength=600)
        self.auto_note.pack(anchor="w", pady=(8, 0))
        self.auto_open = ctk.CTkButton(
            body, text=tr.t("autostart.open_settings"), height=34, corner_radius=10,
            fg_color=theme.SURFACE_ALT, hover_color=theme.BORDER, text_color=theme.TEXT,
            command=lambda: os.startfile("ms-settings:startupapps"))
        self._apply_autostart(autostart.get_status())

        about = self._muted(scroll, tr.t("footer.about", v=__version__), 12)
        about.pack(anchor="w", padx=4, pady=(4, 16))
        about.configure(cursor="hand2")
        about.bind("<Button-1>", lambda _e: webbrowser.open(REPO_URL))

    # ---------------------------------------------------------- editor de blocos
    def _render_blocks(self) -> None:
        for child in self.blocks_frame.winfo_children():
            child.destroy()
        self._getters = []
        for idx, block in enumerate(self.blocks):
            self._block_card(idx, block)

    def _sync_blocks(self) -> None:
        for block, get in zip(self.blocks, self._getters):
            get(block)

    def _block_card(self, idx: int, b: dict) -> None:
        tr = self.tr
        card = ctk.CTkFrame(self.blocks_frame, fg_color=theme.SURFACE_ALT, corner_radius=12,
                            border_width=1, border_color=theme.BORDER)
        card.pack(fill="x", pady=(0, 10))
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(head, text=tr.t(f"block.{b['type']}"), font=theme.font(13, "bold"),
                     text_color=theme.accent(self.cfg.accent)).pack(side="left")
        small = dict(width=30, height=28, corner_radius=8, fg_color="transparent",
                     hover_color=theme.BORDER, text_color=theme.TEXT, font=theme.font(14))
        ctk.CTkButton(head, text="✕", command=lambda: self._remove(idx), **small).pack(side="right")
        ctk.CTkButton(head, text="↓", command=lambda: self._move(idx, 1),
                      state="normal" if idx < len(self.blocks) - 1 else "disabled", **small).pack(side="right")
        ctk.CTkButton(head, text="↑", command=lambda: self._move(idx, -1),
                      state="normal" if idx > 0 else "disabled", **small).pack(side="right")
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=12, pady=(0, 12))
        builder = {"text": self._edit_text, "image": self._edit_image,
                   "checklist": self._edit_checklist}[b["type"]]
        self._getters.append(builder(body, b))

    def _edit_text(self, body, b: dict):
        tr = self.tr
        keys = ("body", "heading", "note")
        names = {k: tr.t(f"style.{k}") for k in keys}
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=(0, 6))
        self._muted(row, tr.t("label.style"), 12).pack(side="left", padx=(0, 8))
        var = ctk.StringVar(value=names.get(b.get("style", "body"), names["body"]))
        ctk.CTkOptionMenu(row, values=[names[k] for k in keys], variable=var, height=30, width=170,
                          corner_radius=8, font=theme.font(13), dropdown_font=theme.font(13),
                          fg_color=theme.SURFACE, button_color=theme.BORDER,
                          button_hover_color=theme.MUTED, text_color=theme.TEXT).pack(side="left")
        box = ctk.CTkTextbox(body, height=120, corner_radius=10, font=theme.font(14),
                             border_width=1, wrap="word", **self._field(theme.SURFACE))
        box.pack(fill="x")
        box.insert("1.0", b.get("text", ""))
        inv = {v: k for k, v in names.items()}

        def get(d: dict) -> None:
            d["text"] = box.get("1.0", "end-1c")
            d["style"] = inv.get(var.get(), "body")

        return get

    def _edit_image(self, body, b: dict):
        tr = self.tr
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        thumb = ctk.CTkLabel(row, text="—", width=120, height=90, corner_radius=8,
                             fg_color=theme.BORDER, text_color=theme.MUTED)
        thumb.pack(side="left")
        side = ctk.CTkFrame(row, fg_color="transparent")
        side.pack(side="left", padx=12, anchor="n")
        name_lbl = self._muted(side, "", 12)
        name_lbl.pack(anchor="w", pady=(2, 6))
        choose = ctk.CTkButton(side, text="", height=32, corner_radius=8, font=theme.font(13),
                               fg_color=theme.SURFACE, hover_color=theme.BORDER,
                               text_color=theme.TEXT, border_width=1, border_color=theme.BORDER)
        choose.pack(anchor="w")

        def show() -> None:
            path = media.resolve(b.get("file", ""))
            if path:
                try:
                    pil = Image.open(path)
                    pil.load()
                    pil.thumbnail((120, 90))
                    img = ctk.CTkImage(light_image=pil, dark_image=pil, size=pil.size)
                    thumb.configure(image=img, text="")
                    thumb._img_ref = img  # evita coleta de lixo
                    name_lbl.configure(text=path.name)
                    choose.configure(text=tr.t("image.change"))
                    return
                except Exception:
                    log.exception("Falha ao gerar miniatura")
            thumb.configure(image=None, text="—")
            name_lbl.configure(text=tr.t("image.none"))
            choose.configure(text=tr.t("image.choose"))

        def pick() -> None:
            name = self._pick_image()
            if name:
                b["file"] = name
                show()

        choose.configure(command=pick)
        show()
        cap = ctk.CTkEntry(body, height=34, corner_radius=8, font=theme.font(13),
                           placeholder_text=tr.t("image.caption.placeholder"), **self._field(theme.SURFACE))
        cap.pack(fill="x", pady=(8, 0))
        cap.insert(0, b.get("caption", ""))

        def get(d: dict) -> None:
            d["caption"] = cap.get().strip()[:MAX_CAPTION_LEN]

        return get

    def _edit_checklist(self, body, b: dict):
        tr = self.tr
        accent = theme.accent(self.cfg.accent)
        title = ctk.CTkEntry(body, height=34, corner_radius=8, font=theme.font(13),
                             placeholder_text=tr.t("check.title.placeholder"), **self._field(theme.SURFACE))
        title.pack(fill="x", pady=(0, 6))
        title.insert(0, b.get("title", ""))
        box = ctk.CTkTextbox(body, height=110, corner_radius=10, font=theme.font(14),
                             border_width=1, wrap="word", **self._field(theme.SURFACE))
        box.pack(fill="x")
        box.insert("1.0", "\n".join(b.get("items", [])))
        self._muted(body, tr.t("check.items_hint"), 12).pack(anchor="w", pady=(2, 6))
        req = ctk.BooleanVar(value=bool(b.get("required", True)))
        ctk.CTkCheckBox(body, text=tr.t("check.required"), variable=req, font=theme.font(13),
                        text_color=theme.TEXT, fg_color=accent, hover_color=theme.hover_of(accent),
                        checkmark_color=theme.ON_ACCENT, checkbox_width=20, checkbox_height=20,
                        corner_radius=6).pack(anchor="w")

        def get(d: dict) -> None:
            d["title"] = title.get().strip()[:MAX_LIST_TITLE_LEN]
            d["items"] = [ln.strip() for ln in box.get("1.0", "end-1c").splitlines() if ln.strip()]
            d["required"] = bool(req.get())

        return get

    def _pick_image(self) -> str | None:
        tr = self.tr
        path = filedialog.askopenfilename(
            parent=self, title=tr.t("image.choose"),
            filetypes=[(tr.t("image.filter"), "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("*", "*.*")])
        if not path:
            return None
        try:
            return media.import_image(path)
        except Exception as exc:
            log.exception("Falha ao importar imagem")
            self._feedback(tr.t("image.error", detail=str(exc)), error=True)
            return None

    def _add(self, kind: str) -> None:
        tr = self.tr
        self._sync_blocks()
        if len(self.blocks) >= MAX_BLOCKS:
            return self._feedback(tr.t("err.too_many_blocks", max=MAX_BLOCKS), error=True)
        block = cfgmod.new_block(kind)
        if kind == "image":
            if sum(1 for x in self.blocks if x.get("type") == "image") >= MAX_IMAGES:
                return self._feedback(tr.t("err.too_many_images", max=MAX_IMAGES), error=True)
            name = self._pick_image()
            if not name:
                return
            block["file"] = name
        self.blocks.append(block)
        self._defer(self._render_blocks)

    def _remove(self, idx: int) -> None:
        self._sync_blocks()
        if 0 <= idx < len(self.blocks):
            del self.blocks[idx]
        self._defer(self._render_blocks)

    def _move(self, idx: int, delta: int) -> None:
        self._sync_blocks()
        j = idx + delta
        if 0 <= idx < len(self.blocks) and 0 <= j < len(self.blocks):
            self.blocks[idx], self.blocks[j] = self.blocks[j], self.blocks[idx]
        self._defer(self._render_blocks)

    # ---------------------------------------------------------- eventos
    def _filter_seconds(self, *_args) -> None:
        raw = self.sec_var.get()
        clean = "".join(ch for ch in raw if ch in "0123456789")[:3]
        if clean != raw:
            self.sec_var.set(clean)
            return
        self.presets.set(clean)

    def _bump(self, delta: int) -> None:
        current = cfgmod.parse_seconds(self.sec_var.get())
        base = current if current is not None else self.cfg.seconds
        self.sec_var.set(str(max(MIN_SECONDS, min(MAX_SECONDS, base + delta))))

    def _on_theme(self, mode: str) -> None:
        self.cfg.theme = mode
        theme.apply_mode(mode)

    def _on_accent(self, name: str) -> None:
        self._collect_draft()
        self.cfg.accent = name
        self._defer(self._build)

    def _on_language(self, code: str) -> None:
        self._collect_draft()
        self.cfg.language = code
        self.tr = Translator(code)
        self.title(self.tr.t("app.name"))
        self._defer(self._build)

    def _apply_autostart(self, st: autostart.Status, error: bool = False) -> None:
        (self.auto_switch.select if st.enabled else self.auto_switch.deselect)()
        self.auto_switch.configure(state="normal" if st.can_change else "disabled")
        note = "autostart.error" if error else st.note_key
        self.auto_note.configure(text=self.tr.t(note) if note else "")
        if st.note_key == "autostart.blocked_user" and not error:
            self.auto_open.pack(anchor="w", pady=(8, 0))
        else:
            self.auto_open.pack_forget()

    def _on_autostart(self) -> None:
        want = bool(self.auto_switch.get())
        try:
            self._apply_autostart(autostart.set_enabled(want))
        except Exception:
            log.exception("Falha ao alterar a inicialização automática")
            self._apply_autostart(autostart.get_status(), error=True)

    def _collect_draft(self) -> None:
        self.cfg.title = self.title_entry.get().strip()[:MAX_TITLE_LEN]
        self._sync_blocks()
        secs = cfgmod.parse_seconds(self.sec_var.get())
        if secs is not None:
            self.cfg.seconds = secs

    def _validated_blocks(self) -> list[dict] | None:
        tr = self.tr
        self._collect_draft()
        if cfgmod.text_too_long(self.blocks):
            self._feedback(tr.t("err.too_long", max=MAX_TOTAL_TEXT), error=True)
            return None
        blocks = cfgmod.sanitize_blocks(self.blocks)
        if not blocks:
            self._feedback(tr.t("err.no_content"), error=True)
            return None
        return blocks

    def _preview(self) -> None:
        blocks = self._validated_blocks()
        if blocks is None:
            return
        open_preview(self, dataclasses.replace(self.cfg, blocks=blocks).sanitized(), self.tr)

    def _save(self) -> None:
        tr = self.tr
        if cfgmod.parse_seconds(self.sec_var.get()) is None:
            return self._feedback(tr.t("err.seconds", min=MIN_SECONDS, max=MAX_SECONDS), error=True)
        blocks = self._validated_blocks()
        if blocks is None:
            return
        cfg = dataclasses.replace(self.cfg, blocks=blocks).sanitized()
        try:
            cfgmod.save(cfg)
            media.cleanup(cfgmod.used_media(cfg.blocks))
        except OSError as exc:
            return self._feedback(tr.t("err.save", detail=str(exc)), error=True)
        self.cfg = cfg
        self.blocks = copy.deepcopy(cfg.blocks)
        self._render_blocks()
        self._feedback(tr.t("saved"))


def run_settings(cfg: Config) -> None:
    SettingsApp(cfg).mainloop()
