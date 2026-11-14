"""Ícone de presença do StartupMessage na bandeja do Windows."""
from __future__ import annotations

import logging

import pystray
from PIL import Image

from . import paths

log = logging.getLogger(__name__)


def start():
    """Inicia o ícone em thread própria e retorna a instância para encerramento."""
    image_path = paths.resource_path("assets", "icon.png")
    try:
        image = Image.open(image_path).convert("RGBA")
        icon = pystray.Icon(
            "StartupMessage",
            image,
            "StartupMessage — mensagem de inicialização",
        )
        icon.run_detached()
        return icon
    except Exception:
        log.exception("Não foi possível iniciar o ícone da bandeja")
        return None


def stop(icon) -> None:
    if icon is not None:
        try:
            icon.stop()
        except Exception:
            log.debug("Não foi possível encerrar o ícone da bandeja", exc_info=True)
