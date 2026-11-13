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


def _msix_self_test() -> int:
    """Smoke test headless, executed only after installing the MSIX package."""
    _setup_logging()
    log = logging.getLogger("dailymessage.msix_test")
    probe = None
    try:
        if not winapi.IS_WINDOWS or not winapi.is_packaged():
            return 20

        from winrt.windows.storage import ApplicationData
        from .autostart import _winrt_status, Status

        local_folder = Path(ApplicationData.current.local_folder.path).resolve()
        if cfgmod.config_dir().resolve() != local_folder:
            return 21

        startup_status = _winrt_status()
        if not isinstance(startup_status, Status):
            return 22

        probe = local_folder / ".dailymessage-msix-selftest"
        probe.write_text("ok", encoding="utf-8")
        if probe.read_text(encoding="utf-8") != "ok":
            return 23
        return 0
    except Exception:
        log.exception("MSIX integration smoke test failed")
        return 24
    finally:
        if probe is not None:
            try:
                probe.unlink(missing_ok=True)
            except OSError:
                log.warning("Could not remove temporary MSIX test file")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--msix-self-test" in argv:
        return _msix_self_test()
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
