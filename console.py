# -*- coding: utf-8 -*-

# 程序入口
import sys

from PyQt5.QtWidgets import QApplication

from windows.console import Console

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # main = WallpaperDesigner()
    main = Console()
    main.show()
    sys.exit(app.exec_())
