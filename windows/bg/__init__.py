# -*- coding: utf-8 -*-
import os
from datetime import datetime
from typing import Optional

import win32gui
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import (
    QApplication, QGraphicsOpacityEffect, QMenu, QWidget,
)

from configs.config import Config
from configs.path_config import TEXTS_FILE, WALLPAPER_LIST_FILE, WALLPAPER_ROOT
from models.bgimage import WallpaperSwitcher
from models.texter import DailySentenceTexter, DaysTexter, TimeTexter
from utils import is_wallpaper, load_json, save_json
from .bg import Ui_BgWindow
from ..utils import pretreatmentHandle


class BgWindow(QWidget, Ui_BgWindow):

    def __init__(self):
        super().__init__()
        self.wallpaper_switcher: Optional[WallpaperSwitcher] = None
        self.progress_list = []
        self.menu = QMenu(self)
        self.markOpacity = QGraphicsOpacityEffect(self)
        self._size = (0, 0)
        self.wallpapers = []
        self.initBeforeUi()
        self.setupUi(self)
        self.initAfterUi()
        self.startTimer(20)

    def initBeforeUi(self):
        desktop = QApplication.desktop()
        self._size = (desktop.width(), desktop.height())
        win32gui.SetParent(self.winId(), pretreatmentHandle())
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint
        )
        self.lower()
        self.load_wallpapers()

    def initAfterUi(self):
        self.setStyleSheet(
            f"#WallPaperBg{{background-color: rgb(0,0,0)}}"
        )
        self.setGeometry(QRect(0, 0, *self._size))
        # 为mark添加透明度
        self.markOpacity.setOpacity(1.0)
        self.mark.setGraphicsEffect(self.markOpacity)
        # 时间显示，文本框，大小 500 * 200
        self.progress_list += [
            TimeTexter(["hour", "minute", "second"], self.Time.setText, "%H:%M:%S"),
            TimeTexter(["year", "month", "day"], self.Date.setText, "%Y-%m-%d %a")
        ]
        if Config.target:
            self.CountDown.show()
            self.target.setText(Config.target_name)
            self.progress_list += [
                DaysTexter(Config.target_time, self.days.setText)
            ]
        else:
            self.CountDown.hide()
        self.create_wallpaper_switcher()
        if os.path.exists(TEXTS_FILE):
            texts_json = load_json(TEXTS_FILE)
            if Config.daily_sentence and len(texts_json["texts"]) > 0:
                self.progress_list.append(
                    DailySentenceTexter(self.Text.setText)
                )
        # 任务栏图标
        if self.wallpaper_switcher.activated:
            self.menu.addAction('上一张').triggered.connect(self.wallpaper_switcher_previous)
            self.menu.addAction('下一张').triggered.connect(self.wallpaper_switcher_next)
        self.menu.addAction('重载壁纸').triggered.connect(self.reload_wallpapers)
        self.menu.addAction('退出').triggered.connect(self.close)

    def setTextBoxAlign(self, align):
        if align == "left":
            self.Text.setAlignment(Qt.AlignLeft)
        elif align == "center":
            self.Text.setAlignment(Qt.AlignHCenter)
        elif align == "right":
            self.Text.setAlignment(Qt.AlignRight)

    def create_wallpaper_switcher(self):
        # if self.wallpapers and Config.image:
        self.wallpaper_switcher = WallpaperSwitcher(
            self.wallpapers,
            {
                "setTimeBox": self.DateTime.move,
                "setCountDownBox": self.CountDown.move,
                "setCountDownTextColor": self.CountDown.setStyleSheet,
                "setCountDownDaysColor": self.days.setStyleSheet,
                "setCountDownTargetColor": self.target.setStyleSheet,
                "setTextBox": self.Text.setGeometry,
                "setTextBoxStyleSheet": self.Text.setStyleSheet,
                "setTextBoxAlign": self.setTextBoxAlign,
                "setText": self.Text.setText,
                "setImage": self.image.setPixmap
            },
            duration=Config.image_duration,
            setOpacity=self.markOpacity.setOpacity
        )
        self.progress_list.append(self.wallpaper_switcher)

    def wallpaper_switcher_previous(self):
        self.wallpaper_switcher.previous()

    def wallpaper_switcher_next(self):
        self.wallpaper_switcher.next()

    # else:
    #     self.markOpacity.setOpacity(0)

    def reload_wallpapers(self):
        self.progress_list.remove(self.wallpaper_switcher)
        del self.wallpaper_switcher
        self.wallpapers = []
        self.load_wallpapers()
        self.create_wallpaper_switcher()

    def load_wallpapers(self):

        if os.path.exists(WALLPAPER_LIST_FILE):
            list_ = load_json(WALLPAPER_LIST_FILE)
        else:
            list_ = {"wallpapers": []}
        wallpapers = os.listdir(WALLPAPER_ROOT)
        for item in list_["wallpapers"]:
            is_wp, path = is_wallpaper(item)
            if is_wp:
                self.wallpapers.append(item)
        for item in wallpapers:
            if item in self.wallpapers:
                continue
            is_wp, path = is_wallpaper(item)
            if is_wp:
                self.wallpapers.append(item)
        list_["wallpapers"] = self.wallpapers
        save_json(list_, WALLPAPER_LIST_FILE)

    def timerEvent(self, *args, **kwargs):
        """
        progress
        """
        now = datetime.now()
        for progress in self.progress_list:
            progress.progress(now)
