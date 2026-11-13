from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path


APP_DIR_NAME = "DailyMessage"
MIN_SECONDS, MAX_SECONDS, DEFAULT_SECONDS = 3, 600, 10
MAX_TITLE_LEN = 80
MAX_BLOCKS, MAX_IMAGES = 30, 10
MAX_TEXT_LEN, MAX_TOTAL_TEXT = 20_000, 30_000
MAX_ITEMS, MAX_ITEM_LEN = 30, 200
MAX_CAPTION_LEN, MAX_LIST_TITLE_LEN = 200, 100
THEMES = ("system", "light", "dark")
ACCENTS = ("indigo", "teal", "rose", "amber")
LANGUAGES = ("auto", "pt-BR", "en")
TEXT_STYLES = ("body", "heading", "note")
IMAGE_NAME_RE = re.compile(r"^[0-9a-f]{32}\.(png|jpg)$")
DEFAULT_TEXT = (
    "Que o seu dia seja produtivo. Respire fundo, organize suas "
    "prioridades e comece com calma."
)


# ---------------------------------------------------------------- blocos
def new_block(kind: str) -> dict:
    if kind == "text":
        return {"type": "text", "style": "body", "text": ""}
    if kind == "image":
        return {"type": "image", "file": "", "caption": ""}
    if kind == "checklist":
        return {"type": "checklist", "title": "", "items": [], "required": True}
    raise ValueError(f"tipo de bloco desconhecido: {kind}")


def default_blocks() -> list[dict]:
    block = new_block("text")
    block["text"] = DEFAULT_TEXT
    return [block]


def _clip(value, limit: int) -> str:
    return value.strip()[:limit] if isinstance(value, str) else ""


def sanitize_blocks(raw) -> list[dict]:
    """Valida/normaliza a lista de blocos. Descarta blocos vazios ou inválidos."""
    out: list[dict] = []
    budget, images = MAX_TOTAL_TEXT, 0
    for b in raw if isinstance(raw, list) else []:
        if len(out) >= MAX_BLOCKS:
            break
        if not isinstance(b, dict):
            continue
        kind = b.get("type")
        if kind == "text":
            text = _clip(b.get("text"), min(MAX_TEXT_LEN, budget))
            if not text:
                continue
            budget -= len(text)
            style = b.get("style")
            out.append({"type": "text", "style": style if style in TEXT_STYLES else "body",
                        "text": text})
        elif kind == "image":
            name = b.get("file")
            if not (isinstance(name, str) and IMAGE_NAME_RE.match(name)) or images >= MAX_IMAGES:
                continue
            images += 1
            out.append({"type": "image", "file": name,
                        "caption": _clip(b.get("caption"), MAX_CAPTION_LEN)})
        elif kind == "checklist":
            raw_items = b.get("items")
            if not isinstance(raw_items, list):
                continue
            items = [_clip(i, MAX_ITEM_LEN) for i in raw_items if isinstance(i, str)]
            items = [i for i in items if i][:MAX_ITEMS]
            if not items:
                continue
            required = b.get("required", True)
            out.append({"type": "checklist", "title": _clip(b.get("title"), MAX_LIST_TITLE_LEN),
                        "items": items, "required": required if isinstance(required, bool) else True})
    return out


def text_too_long(blocks: list[dict]) -> bool:
    lengths = [len(str(b.get("text", "")).strip()) for b in blocks if b.get("type") == "text"]
    return any(n > MAX_TEXT_LEN for n in lengths) or sum(lengths) > MAX_TOTAL_TEXT


def used_media(blocks: list[dict]) -> set[str]:
    return {b["file"] for b in blocks if b.get("type") == "image" and b.get("file")}


# ---------------------------------------------------------------- config
@dataclass
class Config:
    title: str = "Bem-vindo(a)!"
    blocks: list = field(default_factory=default_blocks)
    seconds: int = DEFAULT_SECONDS
    theme: str = "system"
    accent: str = "indigo"
    language: str = "auto"

    def sanitized(self) -> "Config":
        d = Config()
        title = self.title if isinstance(self.title, str) else d.title
        blocks = sanitize_blocks(self.blocks) if isinstance(self.blocks, list) else default_blocks()
        ok_int = isinstance(self.seconds, int) and not isinstance(self.seconds, bool)
        seconds = self.seconds if ok_int else d.seconds
        return Config(
            title=title.strip()[:MAX_TITLE_LEN],
            blocks=blocks,
            seconds=max(MIN_SECONDS, min(MAX_SECONDS, seconds)),
            theme=self.theme if self.theme in THEMES else d.theme,
            accent=self.accent if self.accent in ACCENTS else d.accent,
            language=self.language if self.language in LANGUAGES else d.language,
        )


def parse_seconds(text: str) -> int | None:
    text = (text or "").strip()
    if not text or any(ch not in "0123456789" for ch in text):
        return None
    value = int(text)
    return value if MIN_SECONDS <= value <= MAX_SECONDS else None


def config_dir() -> Path:
    """Dados privados do pacote MSIX; fallback local apenas durante desenvolvimento."""
    try:
        from . import winapi
        if winapi.is_packaged():
            from winrt.windows.storage import ApplicationData
            return Path(ApplicationData.current.local_folder.path)
    except Exception:
        pass
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
    return Path(root) / APP_DIR_NAME


def config_path() -> Path:
    return config_dir() / "config.json"


def load() -> Config:
    try:
        raw = json.loads(config_path().read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("config inválida")
    except (OSError, ValueError):
        return Config()
    if "blocks" not in raw and isinstance(raw.get("message"), str):  # formato antigo
        raw["blocks"] = [{"type": "text", "style": "body", "text": raw["message"]}]
    known = {f.name for f in fields(Config)}
    try:
        return Config(**{k: v for k, v in raw.items() if k in known}).sanitized()
    except TypeError:
        return Config()


def save(cfg: Config) -> None:
    cfg = cfg.sanitized()
    directory = config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    tmp = directory / "config.json.tmp"
    tmp.write_text(json.dumps(asdict(cfg), ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, directory / "config.json")
