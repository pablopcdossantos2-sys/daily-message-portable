from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from . import config as cfgmod
from . import winapi
from .i18n import Translator


def _setup_logging() -> None:
    try:
        directory = cfgmod.config_dir()
        directory.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            directory / "dailymessage.log", maxBytes=200_000, backupCount=1, encoding="utf-8"
        )
        logging.basicConfig(
            level=logging.INFO, handlers=[handler],
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
    except Exception:
        logging.basicConfig(level=logging.WARNING)


def _is_startup_launch(argv: list[str]) -> bool:
    if "--startup" in argv:
        return True
    if "--settings" in argv:
        return False
    # No MSIX o startupTask não aceita argumentos: o exe "Runner" identifica o boot.
    return Path(sys.executable).stem.lower().endswith("runner")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    _setup_logging()
    log = logging.getLogger("dailymessage")
    startup = _is_startup_launch(argv)

    guard = winapi.SingleInstance(
        "Local\\DailyMessage.Startup" if startup else "Local\\DailyMessage.Settings"
    )
    if not guard.acquire():
        log.info("Já existe uma instância em execução; encerrando.")
        return 0
    try:
        winapi.set_app_user_model_id()
        cfg = cfgmod.load()
        if startup:
            from .message_window import run_startup_message

            delay = 0.0 if "--no-delay" in argv else 2.0
            run_startup_message(cfg, Translator(cfg.language), delay_seconds=delay)
        else:
            from .settings_window import run_settings

            run_settings(cfg)
        return 0
    except Exception:
        log.exception("Falha fatal")
        return 1
    finally:
        guard.release()
