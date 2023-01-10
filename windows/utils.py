# -*- coding: utf-8 -*-
import win32gui


def pretreatmentHandle():
    """
    获得桌面壁纸窗口句柄
    """
    hwnd = win32gui.FindWindow("Progman", "Program Manager")
    win32gui.SendMessageTimeout(hwnd, 0x052C, 0, None, 0, 0x03E8)
    hwnd_WorkW = None
    while True:
        hwnd_WorkW = win32gui.FindWindowEx(
            None, hwnd_WorkW, "WorkerW", None
        )
        if not hwnd_WorkW:
            continue
        hView = win32gui.FindWindowEx(
            hwnd_WorkW, None, "SHELLDLL_DefView", None
        )
        # print('hwmd_hView: ', hView)
        if not hView:
            continue
        h = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
        while h:
            win32gui.SendMessage(h, 0x0010, 0, 0)  # WM_CLOSE
            h = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
        break
    return hwnd

# win32gui.SetParent(self.winId(), pretreatmentHandle())
