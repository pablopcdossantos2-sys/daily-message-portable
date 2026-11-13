"""Gera ícones PLACEHOLDER (substitua pela arte final antes de publicar na Store).

Uso: python packaging/make_assets.py [--force]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MSIX_ASSETS = ROOT / "packaging" / "Assets"
S = 1024


def master() -> Image.Image:
    top, bottom = (99, 102, 241), (139, 92, 246)
    grad = Image.new("RGB", (S, S))
    gd = ImageDraw.Draw(grad)
    for y in range(S):
        t = y / (S - 1)
        gd.line([(0, y), (S, y)], fill=tuple(round(top[i] * (1 - t) + bottom[i] * t) for i in range(3)))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * 0.22), fill=255)
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((210, 250, 814, 654), radius=110, fill=(255, 255, 255, 255))
    d.polygon([(330, 640), (330, 780), (470, 650)], fill=(255, 255, 255, 255))
    for cx in (370, 512, 654):
        d.ellipse((cx - 38, 422, cx + 38, 498), fill=(99, 102, 241, 255))
    return img


def main() -> None:
    if (ASSETS / "icon.ico").exists() and "--force" not in sys.argv:
        print("Assets já existem (use --force para sobrescrever).")
        return
    ASSETS.mkdir(exist_ok=True)
    MSIX_ASSETS.mkdir(parents=True, exist_ok=True)
    img = master()
    img.save(ASSETS / "icon.png")
    img.save(ASSETS / "icon.ico", sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
    sizes = {"StoreLogo": 50, "Square44x44Logo": 44, "Square71x71Logo": 71,
             "Square150x150Logo": 150, "Square310x310Logo": 310}
    for name, size in sizes.items():
        img.resize((size, size), Image.Resampling.LANCZOS).save(MSIX_ASSETS / f"{name}.png")
    wide = Image.new("RGBA", (310, 150), (0, 0, 0, 0))
    icon = img.resize((130, 130), Image.Resampling.LANCZOS)
    wide.paste(icon, ((310 - 130) // 2, 10), icon)
    wide.save(MSIX_ASSETS / "Wide310x150Logo.png")
    print("Assets gerados.")


if __name__ == "__main__":
    main()
