"""Chamadas Win32 via ctypes (no-op fora do Windows)."""
from __future__ import annotations

import ctypes
import logging
import sys
from ctypes import wintypes

log = logging.getLogger(__name__)

IS_WINDOWS = sys.platform == "win32"

SC_CLOSE = 0xF060
MF_BYCOMMAND, MF_ENABLED, MF_GRAYED = 0x0, 0x0, 0x1
GWL_STYLE = -16
WS_MAXIMIZEBOX, WS_MINIMIZEBOX = 0x00010000, 0x00020000
SWP_NOSIZE, SWP_NOMOVE, SWP_NOZORDER, SWP_FRAMECHANGED = 0x1, 0x2, 0x4, 0x20
SW_RESTORE = 9
ERROR_ALREADY_EXISTS = 183
APPMODEL_ERROR_NO_PACKAGE = 15700

_user32 = None


def _u32():
    global _user32
    if _user32 is None:
        u = ctypes.WinDLL("user32", use_last_error=True)
        u.GetSystemMenu.argtypes = [wintypes.HWND, wintypes.BOOL]
        u.GetSystemMenu.restype = wintypes.HMENU
        u.EnableMenuItem.argtypes = [wintypes.HMENU, wintypes.UINT, wintypes.UINT]
        u.EnableMenuItem.restype = wintypes.BOOL
        u.DrawMenuBar.argtypes = [wintypes.HWND]
        u.DrawMenuBar.restype = wintypes.BOOL
        u.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
        u.GetWindowLongW.restype = ctypes.c_long
        u.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_long]
        u.SetWindowLongW.restype = ctypes.c_long
        u.SetWindowPos.argtypes = [
            wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, wintypes.UINT,
        ]
        u.SetWindowPos.restype = wintypes.BOOL
        u.SetForegroundWindow.argtypes = [wintypes.HWND]
        u.SetForegroundWindow.restype = wintypes.BOOL
        u.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        u.ShowWindow.restype = wintypes.BOOL
        _user32 = u
    return _user32


def toplevel_hwnd(win) -> int:
    """HWND real da janela de topo (moldura) de um widget Tk."""
    win.update_idletasks()
    return int(win.wm_frame(), 16)


def set_close_enabled(hwnd: int, enabled: bool) -> None:
    """Habilita/esmaece o botão X (e o item Fechar do menu de sistema / Alt+F4)."""
    if not IS_WINDOWS:
        return
    u = _u32()
    hmenu = u.GetSystemMenu(hwnd, False)
    if hmenu:
        u.EnableMenuItem(hmenu, SC_CLOSE, MF_BYCOMMAND | (MF_ENABLED if enabled else MF_GRAYED))
        u.DrawMenuBar(hwnd)


def set_caption_boxes(hwnd: int, *, minimize: bool, maximize: bool) -> None:
    """Liga/desliga os botões Minimizar e Maximizar da barra de título."""
    if not IS_WINDOWS:
        return
    u = _u32()
    style = u.GetWindowLongW(hwnd, GWL_STYLE)
    for flag, allowed in ((WS_MINIMIZEBOX, minimize), (WS_MAXIMIZEBOX, maximize)):
        style = (style | flag) if allowed else (style & ~flag)
    u.SetWindowLongW(hwnd, GWL_STYLE, style)
    u.SetWindowPos(hwnd, None, 0, 0, 0, 0,
                   SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED)


def bring_to_front(hwnd: int) -> None:
    if not IS_WINDOWS:
        return
    try:
        u = _u32()
        u.ShowWindow(hwnd, SW_RESTORE)
        u.SetForegroundWindow(hwnd)
    except Exception:
        log.debug("SetForegroundWindow falhou", exc_info=True)


def is_packaged() -> bool:
    """True se rodando como app MSIX (com identidade de pacote)."""
    if not IS_WINDOWS:
        return False
    try:
        length = ctypes.c_uint32(0)
        rc = ctypes.windll.kernel32.GetCurrentPackageFullName(ctypes.byref(length), None)
        return rc != APPMODEL_ERROR_NO_PACKAGE
    except Exception:
        return False


def set_app_user_model_id(app_id: str = "DailyMessage.App") -> None:
    if IS_WINDOWS and not is_packaged():
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass


class SingleInstance:
    """Mutex nomeado para impedir instâncias duplicadas."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._handle = None

    def acquire(self) -> bool:
        if not IS_WINDOWS:
            return True
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
        k32.CreateMutexW.restype = wintypes.HANDLE
        self._handle = k32.CreateMutexW(None, False, self.name)
        return ctypes.get_last_error() != ERROR_ALREADY_EXISTS

    def release(self) -> None:
        if IS_WINDOWS and self._handle:
            ctypes.windll.kernel32.CloseHandle(self._handle)
            self._handle = None
