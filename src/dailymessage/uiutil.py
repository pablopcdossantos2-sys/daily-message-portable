from __future__ import annotations

import logging

from . import paths

log = logging.getLogger(__name__)


def _window_scale(win) -> float:
    try:
        return float(win._get_window_scaling())
    except Exception:
        return 1.0


def center_window(win, width: int, height: int) -> None:
    """Define o tamanho (escalado pelo CustomTkinter) e centraliza em pixels reais."""
    win.geometry(f"{width}x{height}")
    scale = _window_scale(win)
    x = int((win.winfo_screenwidth() - width * scale) / 2)
    y = int((win.winfo_screenheight() - height * scale) / 2) - 20
    win.wm_geometry(f"+{max(x, 0)}+{max(y, 0)}")  # wm_geometry não é re-escalado


def fit_and_center(win, width: int, height: int, *, min_size=(560, 460), max_ratio: float = 0.9) -> None:
    """Ajusta o tamanho ao conteúdo, limitado a ~90 % da tela, e centraliza."""
    scale = _window_scale(win)
    max_w = win.winfo_screenwidth() / scale * max_ratio
    max_h = (win.winfo_screenheight() - 80) / scale * max_ratio  # ~80 px de barra de tarefas
    w = int(min(max(width, min_size[0]), max_w))
    h = int(min(max(height, min_size[1]), max_h))
    win.minsize(min(min_size[0], w), min(min_size[1], h))
    center_window(win, w, h)


def apply_icon(win) -> None:
    ico = paths.resource_path("assets", "icon.ico")
    if not ico.exists():
        return

    def _set():
        try:
            win.iconbitmap(str(ico))
        except Exception:
            log.debug("iconbitmap falhou", exc_info=True)

    _set()
    win.after(300, _set)  # o CustomTkinter tenta trocar o ícone após ~200 ms
