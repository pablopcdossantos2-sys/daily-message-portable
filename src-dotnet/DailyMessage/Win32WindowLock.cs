using System.Runtime.InteropServices;

namespace DailyMessage;

internal static class Win32WindowLock
{
    private const uint MF_BYCOMMAND = 0x00000000;
    private const uint MF_ENABLED = 0x00000000;
    private const uint MF_GRAYED = 0x00000001;
    private const uint SC_CLOSE = 0xF060;
    private const int GWL_STYLE = -16;
    private const long WS_MINIMIZEBOX = 0x00020000L;
    private const uint SWP_NOSIZE = 0x0001;
    private const uint SWP_NOMOVE = 0x0002;
    private const uint SWP_NOZORDER = 0x0004;
    private const uint SWP_FRAMECHANGED = 0x0020;
    private static readonly nint HWND_TOPMOST = new(-1);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern nint GetSystemMenu(nint hWnd, bool bRevert);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern uint EnableMenuItem(nint hMenu, uint uIDEnableItem, uint uEnable);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool DrawMenuBar(nint hWnd);

    [DllImport("user32.dll", EntryPoint = "GetWindowLongPtrW", SetLastError = true)]
    private static extern nint GetWindowLongPtr(nint hWnd, int nIndex);

    [DllImport("user32.dll", EntryPoint = "SetWindowLongPtrW", SetLastError = true)]
    private static extern nint SetWindowLongPtr(nint hWnd, int nIndex, nint dwNewLong);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetWindowPos(nint hWnd, nint hWndInsertAfter, int x, int y, int cx, int cy, uint flags);

    public static void SetLocked(nint hwnd, bool locked)
    {
        if (hwnd == 0) return;

        var menu = GetSystemMenu(hwnd, false);
        if (menu != 0)
        {
            EnableMenuItem(menu, SC_CLOSE, MF_BYCOMMAND | (locked ? MF_GRAYED : MF_ENABLED));
            DrawMenuBar(hwnd);
        }

        var style = GetWindowLongPtr(hwnd, GWL_STYLE).ToInt64();
        style = locked ? style & ~WS_MINIMIZEBOX : style | WS_MINIMIZEBOX;
        SetWindowLongPtr(hwnd, GWL_STYLE, new nint(style));
        SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED);
    }

    public static void SetTopMost(nint hwnd)
    {
        if (hwnd == 0) return;
        SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
    }
}
