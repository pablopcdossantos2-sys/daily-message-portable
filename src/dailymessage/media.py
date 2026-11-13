"""Armazenamento local das imagens usadas nas mensagens."""
from __future__ import annotations

import uuid
from pathlib import Path

from PIL import Image, ImageOps

from . import config

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
MAX_SIDE = 2560
MAX_SOURCE_BYTES = 25 * 1024 * 1024


def media_dir() -> Path:
    return config.config_dir() / "media"


def import_image(src) -> str:
    """Valida, normaliza e copia a imagem para a pasta de mídia. Retorna o nome salvo."""
    src = Path(src)
    if src.suffix.lower() not in ALLOWED_EXT:
        raise ValueError("formato de imagem não suportado")
    if src.stat().st_size > MAX_SOURCE_BYTES:
        raise ValueError("arquivo maior que 25 MB")
    try:
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)
            im.load()
            im.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
            alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
            name = f"{uuid.uuid4().hex}{'.png' if alpha else '.jpg'}"
            directory = media_dir()
            directory.mkdir(parents=True, exist_ok=True)
            if alpha:
                im.convert("RGBA").save(directory / name, "PNG")
            else:
                im.convert("RGB").save(directory / name, "JPEG", quality=90)
    except (OSError, Image.DecompressionBombError) as exc:
        raise ValueError(str(exc)) from exc
    return name


def resolve(name: str) -> Path | None:
    """Caminho do arquivo salvo, ou None se o nome for inválido/inexistente."""
    if not isinstance(name, str) or not config.IMAGE_NAME_RE.match(name):
        return None
    path = media_dir() / name
    return path if path.is_file() else None


def cleanup(keep: set[str]) -> None:
    """Remove imagens que não são mais usadas por nenhum bloco."""
    directory = media_dir()
    if not directory.is_dir():
        return
    for f in directory.iterdir():
        if f.is_file() and f.name not in keep:
            try:
                f.unlink()
            except OSError:
                pass
