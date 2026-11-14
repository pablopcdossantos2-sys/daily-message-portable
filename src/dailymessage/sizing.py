"""Estimativa do tamanho inicial da janela a partir do conteúdo (sem dependências de GUI)."""
from __future__ import annotations

import math

BASE_W, BASE_H = 640, 240  # largura padrão; altura = título + rodapé + margens


def estimate_size(blocks: list[dict], font_size: int = 16) -> tuple[int, int]:
    """Estima dimensões considerando o tamanho tipográfico configurado."""
    font_scale = max(0.625, min(2.5, font_size / 16))
    w, h = BASE_W, BASE_H
    for b in blocks:
        kind = b.get("type")
        if kind == "text":
            heading = b.get("style") == "heading"
            per_line = max(20, int((55 if heading else 75) / font_scale))
            lines = sum(max(1, math.ceil(len(p) / per_line)) for p in b["text"].split("\n"))
            h += int(lines * (32 if heading else 26) * font_scale) + 16
        elif kind == "image":
            w = max(w, 780)
            h += 340
        elif kind == "checklist":
            h += int((70 + 40 * len(b["items"])) * font_scale)
    return w, h
