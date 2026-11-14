from __future__ import annotations

import customtkinter as ctk

Color = tuple[str, str]  # (modo claro, modo escuro) — formato nativo do CustomTkinter

FONT_FAMILY = "Segoe UI"

BG: Color = ("#F2F3F8", "#0D0F15")
SURFACE: Color = ("#FFFFFF", "#161920")
SURFACE_ALT: Color = ("#F6F7FB", "#1D212B")
BORDER: Color = ("#E2E5EE", "#262B38")
TEXT: Color = ("#12141C", "#F2F4FA")
MUTED: Color = ("#6A7186", "#8D95AA")
DANGER: Color = ("#D92D4A", "#FF6B81")
SUCCESS: Color = ("#0E9F6E", "#34D399")
ON_ACCENT: Color = ("#FFFFFF", "#0B0D14")

ACCENTS: dict[str, Color] = {
    "indigo": ("#4F46E5", "#818CF8"),
    "teal": ("#0D9488", "#2DD4BF"),
    "rose": ("#E11D48", "#FB7185"),
    "amber": ("#D97706", "#FBBF24"),
}


def accent(name: str) -> Color:
    return ACCENTS.get(name, ACCENTS["indigo"])


def _mix_hex(a: str, b: str, t: float) -> str:
    ca = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(x * (1 - t) + y * t) for x, y in zip(ca, cb))


def mix(a: Color, b: Color, t: float) -> Color:
    """Mistura a→b (t=0 → a, t=1 → b) nos dois modos."""
    return (_mix_hex(a[0], b[0], t), _mix_hex(a[1], b[1], t))


def hover_of(color: Color) -> Color:
    return mix(color, ("#000000", "#FFFFFF"), 0.14)


def font(size: int, weight: str = "normal", family: str = FONT_FAMILY) -> ctk.CTkFont:
    return ctk.CTkFont(family=family or FONT_FAMILY, size=size, weight=weight)


def apply_mode(theme: str) -> None:
    ctk.set_appearance_mode(theme if theme in ("light", "dark") else "system")
