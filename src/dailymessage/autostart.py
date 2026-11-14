"""Inicialização com o Windows via WinRT StartupTask (somente MSIX)."""
from __future__ import annotations

import asyncio
import logging
import threading
from dataclasses import dataclass

from . import winapi

log = logging.getLogger(__name__)

STARTUP_TASK_ID = "DailyMessageTask"  # deve ser igual ao TaskId do AppxManifest


@dataclass(frozen=True)
class Status:
    enabled: bool
    can_change: bool = True
    note_key: str | None = None  # chave i18n explicando o estado


# ---------- modo MSIX (WinRT StartupTask) ----------

def _run_winrt(coro_factory, timeout: float = 15.0):
    """Executa corrotina WinRT em thread própria (evita conflito de apartment com o Tk)."""
    box: dict = {}

    def worker():
        try:
            box["v"] = asyncio.run(coro_factory())
        except BaseException as exc:  # noqa: BLE001
            box["e"] = exc

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        raise TimeoutError("WinRT StartupTask não respondeu")
    if "e" in box:
        raise box["e"]
    return box.get("v")


def _state_to_status(state: int) -> Status:
    # Valores oficiais de Windows.ApplicationModel.StartupTaskState:
    # 0 Disabled, 1 DisabledByUser, 2 Enabled, 3 DisabledByPolicy, 4 EnabledByPolicy.
    if state == 2:
        return Status(True)
    if state == 4:
        return Status(True, False, "autostart.managed_policy")
    if state == 1:
        return Status(False, False, "autostart.blocked_user")
    if state == 3:
        return Status(False, False, "autostart.blocked_policy")
    return Status(False)


def _winrt_status() -> Status:
    async def go() -> int:
        from winrt.windows.applicationmodel import StartupTask

        task = await StartupTask.get_async(STARTUP_TASK_ID)
        return int(task.state)

    return _state_to_status(_run_winrt(go))


def _winrt_set(enabled: bool) -> Status:
    async def go() -> int:
        from winrt.windows.applicationmodel import StartupTask

        task = await StartupTask.get_async(STARTUP_TASK_ID)
        if enabled:
            return int(await task.request_enable_async())
        task.disable()
        return int(task.state)

    return _state_to_status(_run_winrt(go))


# ---------- API pública ----------

def get_status() -> Status:
    if not winapi.IS_WINDOWS:
        return Status(False, False, "autostart.unsupported")
    try:
        if not winapi.is_packaged():
            return Status(False, False, "autostart.store_only")
        return _winrt_status()
    except Exception:
        log.exception("Falha ao consultar inicialização automática")
        return Status(False, True)


def set_enabled(enabled: bool) -> Status:
    if not winapi.IS_WINDOWS:
        return Status(False, False, "autostart.unsupported")
    if not winapi.is_packaged():
        return Status(False, False, "autostart.store_only")
    return _winrt_set(enabled)
