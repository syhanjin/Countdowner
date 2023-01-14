# -*- coding: utf-8 -*-
import os
import sys

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import (
    QApplication,
)
from win32api import CloseHandle, GetLastError
from win32event import CreateMutex
from winerror import ERROR_ALREADY_EXISTS

from configs.path_config import FONT_ROOT
from windows import Tray
from windows.bg import BgWindow


class Singleinstance:

    def __init__(self):
        self.mutexname = "countdown_{D0E858DF-985E-4907-B7FB-8D732C3FC3B9}"
        self.mutex = CreateMutex(None, False, self.mutexname)
        self.lasterror = GetLastError()

    def aleradyrunning(self):
        return self.lasterror == ERROR_ALREADY_EXISTS

    def __del__(self):
        if self.mutex:
            CloseHandle(self.mutex)


def load_fonts():
    for fn in os.listdir(FONT_ROOT):
        QFontDatabase.addApplicationFont(os.path.join(FONT_ROOT, fn))


def init():
    load_fonts()


def main(tray_):
    MainWindow = BgWindow()
    tray_.setContextMenu(MainWindow.menu)
    MainWindow.show()
    tray_.setVisible(True)


# 程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mutex = Singleinstance()
    if mutex.aleradyrunning():
        sys.exit()
    init()
    tray = Tray()
    main(tray)
    sys.exit(app.exec_())
