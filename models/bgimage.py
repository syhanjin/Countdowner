# -*- coding: utf-8 -*-
import os
import random
from datetime import datetime
from typing import List

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap

from configs.config import CONFIG_TIME_FORMAT, Config
from configs.path_config import TEXTS_FILE, WALLPAPER_ROOT
from utils import load_json, text_wrapper


class BgImage(QObject):
    setTimeBoxSignal = pyqtSignal(int, int)
    setCountDownBoxSignal = pyqtSignal(int, int)
    setCountDownTextColorSignal = pyqtSignal(str)
    setCountDownDaysColorSignal = pyqtSignal(str)
    setCountDownTargetColorSignal = pyqtSignal(str)
    setTextBoxSignal = pyqtSignal(int, int, int, int)
    setTextBoxStyleSheetSignal = pyqtSignal(str)
    setTextSignal = pyqtSignal(str)
    setTextBoxAlignSignal = pyqtSignal(str)
    setImageSignal = pyqtSignal(QPixmap)

    name = None
    image = None
    timebox = {
        "pos": [10, 10]
    }
    countdownbox = {
        "pos": [586, 10],
        "color": {
            "text": "black",
            "days": "red",
            "target": "green"
        }
    }
    textbox = {
        "pos": [
            [0, 0, 200, 200]
        ],
        "stylesheet": "",
        "texts": []
    }
    fields = ["name", "image", "timebox", "countdownbox", "textbox"]
    required = ["name", "image"]

    def __init__(self, path):
        super().__init__()
        self.path = path
        config = load_json(os.path.join(self.path, "config.json"))
        for key in self.fields:
            if key in config:
                setattr(self, key, config[key])
        if self.name is None:
            raise ValueError("必须提供名称")
        if self.image is None:
            raise ValueError("必须提供图片路径")
        self.image_path = os.path.join(self.path, self.image)

    def connectSignals(self, **kwargs):
        for k, v in kwargs.items():
            getattr(self, f"{k}Signal").connect(v)

    def setAll(self):
        self.setTimeBoxSignal.emit(*self.timebox["pos"])
        self.setCountDown()
        self.setText()
        self.setImage()

    def setCountDown(self):
        self.setCountDownBoxSignal.emit(*self.countdownbox["pos"])
        self.setCountDownTextColorSignal.emit(self.colorsheet(self.countdownbox["color"]["text"]))
        self.setCountDownDaysColorSignal.emit(self.colorsheet(self.countdownbox["color"]["days"]))
        self.setCountDownTargetColorSignal.emit(self.colorsheet(self.countdownbox["color"]["target"]))

    def setText(self):
        textbox = random.choice(self.textbox["pos"])
        self.setTextBoxSignal.emit(*textbox)
        self.setTextBoxAlignSignal.emit(self.textbox["align"])
        if self.textbox["stylesheet"]:
            self.setTextBoxStyleSheetSignal.emit(self.textbox["stylesheet"])
        self._setTextContent()

    def _setTextContent(self):
        if Config.daily_sentence:
            return
        if self.textbox['use_global_texts']:
            if not os.path.exists(TEXTS_FILE):
                return
            texts = load_json(TEXTS_FILE)
            if not texts.get('texts'):
                return
            text = random.choice(texts["texts"])
        else:
            if not self.textbox["texts"]:
                return
            text = random.choice(self.textbox['texts'])
        self.setTextSignal.emit(text_wrapper(text))

    def setImage(self):
        self.setImageSignal.emit(QPixmap(self.image_path))

    def colorsheet(self, color):
        return f"color: {color};"


class WallpaperSwitcher(QObject):
    setOpacity = pyqtSignal(float)

    class SwitchStatus:
        Waiting = 0
        Darkening = 1
        Lightening = 3
        Finished = 4

    def __init__(self, wallpapers, functions, setOpacity, duration=1800, frames=80):
        super().__init__()
        self.wallpapers = wallpapers
        self.functions = functions
        self.queue: List = self.wallpapers.copy()
        self.duration = duration
        self.wp = None
        if self.activated:
            if Config.image_current is None or Config.image_current not in self.wallpapers:
                Config.image_current = self.queue[0]
                Config.save()
            while self.queue[0] != Config.image_current:
                self.queue.pop(0)
        self.setOpacity.connect(setOpacity)
        self.switch = self.SwitchStatus.Lightening
        self.opacity = 1.0
        self.frames = frames
        if Config.image_time is None:
            self.last = None
        else:
            self.last = datetime.strptime(Config.image_time, CONFIG_TIME_FORMAT)
            self.switchNext()
        # print(self.last)

    def path(self, dirname):
        return os.path.join(WALLPAPER_ROOT, dirname)

    def setCurrent(self, current):
        Config.image_current = current
        Config.save()
        return current

    def switchNext(self):
        if not self.activated:
            return
        self.wp = BgImage(self.path(self.setCurrent(self.queue.pop(0))))
        self.wp.connectSignals(**self.functions)
        self.wp.setAll()
        if not self.queue:
            self.queue = self.wallpapers.copy()

    def progress(self, now):
        if self.switch == self.SwitchStatus.Darkening:
            self.opacity += 2.0 / self.frames
            if self.opacity >= 1.0:
                self.opacity = 1
                self.setOpacity.emit(1)
                self.switch = self.SwitchStatus.Lightening
                self.switchNext()
            else:
                self.setOpacity.emit(self.opacity)
        elif self.switch == self.SwitchStatus.Lightening:
            self.opacity -= 2.0 / self.frames
            if self.opacity <= 0.0:
                self.opacity = 0
                self.setOpacity.emit(0)
                self.switch = self.SwitchStatus.Waiting
                if self.activated:
                    self.setLast(now)
            else:
                self.setOpacity.emit(self.opacity)
        elif not self.activated:
            return
        elif self.last is None:
            self.switchNext()
            self.setLast(now)
            self.switch = self.SwitchStatus.Lightening
        elif (now - self.last).total_seconds() > self.duration:
            self.switch = self.SwitchStatus.Darkening

    def setLast(self, now):
        self.last = now
        Config.image_time = now.__format__(CONFIG_TIME_FORMAT)
        Config.save()

    @property
    def activated(self):
        return self.wallpapers and Config.image
