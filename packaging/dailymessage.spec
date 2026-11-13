# -*- mode: python ; coding: utf-8 -*-
# Gera DOIS executáveis na mesma pasta (onedir):
#   DailyMessage.exe        -> janela de configurações
#   DailyMessageRunner.exe  -> exibe a mensagem (boot / startupTask do MSIX)
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH).parent
ICON = str(ROOT / "assets" / "icon.ico")

datas = collect_data_files("customtkinter")
datas += [(str(ROOT / "assets" / "icon.ico"), "assets"), (str(ROOT / "assets" / "icon.png"), "assets")]
hidden = collect_submodules("winrt")  # projeções WinRT (StartupTask)

a = Analysis(
    [str(ROOT / "launcher.py")],
    pathex=[str(ROOT / "src")],
    datas=datas,
    hiddenimports=hidden,
    excludes=["numpy", "matplotlib", "scipy", "pandas", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)

common = dict(exclude_binaries=True, debug=False, strip=False, upx=False, console=False, icon=ICON)
exe_settings = EXE(pyz, a.scripts, [], name="DailyMessage", **common)
exe_runner = EXE(pyz, a.scripts, [], name="DailyMessageRunner", **common)

coll = COLLECT(exe_settings, exe_runner, a.binaries, a.datas, strip=False, upx=False, name="DailyMessage")
