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


def fit_and_center(win, width: int, height: int, *, min_size=(560, 460), max_ratio: float = 0.9, fill_height_for_large: bool = False) -> None:
    """Ajusta ao conteúdo; mensagens longas podem ocupar toda a altura útil."""
    scale = _window_scale(win)
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    max_w = screen_w / scale * max_ratio
    available_h = max(300, screen_h - 80)  # preserva a área da barra de tarefas
    max_h = available_h / scale if fill_height_for_large else available_h / scale * max_ratio
    w = int(min(max(width, min_size[0]), max_w))
    h = int(min(max(height, min_size[1]), max_h))
    win.minsize(min(min_size[0], w), min(min_size[1], h))
    win.geometry(f"{w}x{h}")
    # A posição horizontal sempre é centralizada; janelas altas começam no topo útil.
    x = int((screen_w - w * scale) / 2)
    y = 0 if fill_height_for_large and height >= max_h else int((screen_h - h * scale) / 2) - 20
    win.wm_geometry(f"+{max(x, 0)}+{max(y, 0)}")


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
