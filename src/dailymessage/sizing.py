"""Estimativa do tamanho inicial da janela a partir do conteúdo (sem dependências de GUI)."""
from __future__ import annotations

import math

BASE_W, BASE_H = 640, 240  # largura padrão; altura = título + rodapé + margens


def estimate_size(blocks: list[dict]) -> tuple[int, int]:
    w, h = BASE_W, BASE_H
    for b in blocks:
        kind = b.get("type")
        if kind == "text":
            heading = b.get("style") == "heading"
            per_line = 55 if heading else 75
            lines = sum(max(1, math.ceil(len(p) / per_line)) for p in b["text"].split("\n"))
            h += lines * (32 if heading else 26) + 16
        elif kind == "image":
            w = max(w, 780)
            h += 340
        elif kind == "checklist":
            h += 70 + 40 * len(b["items"])
    return w, h
