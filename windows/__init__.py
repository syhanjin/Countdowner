# -*- coding: utf-8 -*-
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon


# 托盘图标
class Tray(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        self.setIcon(QIcon("./wallpaper.ico"))
        self.setVisible(False)
