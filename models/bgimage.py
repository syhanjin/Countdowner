# -*- coding: utf-8 -*-
import os
import random
import shutil
from datetime import datetime
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap

from configs.config import Config, Runtime
from configs.path_config import TEXTS_FILE, WALLPAPER_ROOT
from utils import load_json, save_json, text_wrapper


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

    edit = False
    name = "default"
    image = None
    image_path = None
    timebox = {
        "pos": [710, 240]
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
        "pos": [560, 900, 800, 150],
        "stylesheet": "font: 14pt \"微软雅黑\";",
        "align": "center",
        "use_global_texts": False,
        "texts": []
    }
    fields = ["name", "image", "timebox", "countdownbox", "textbox"]
    required = ["name", "image"]

    def __init__(self, path=None, edit=False):
        super().__init__()
        if path is None and not edit:
            raise ValueError("必须提供路径")
        self.edit = edit
        self.path = path
        if path is None:
            return
        # print(os.path.exists(os.path.join(self.path, "config.json")))
        # try:
        config = load_json(os.path.join(self.path, "config.json"))
        # except Exception as e:
        #     print(e)
        # print(config)
        for key in self.fields:
            if key in config:
                setattr(self, key, config[key])
        if self.name is None:
            raise ValueError("必须提供名称")
        if self.image is None:
            raise ValueError("必须提供图片路径")
        self.image_path = os.path.join(self.path, self.image)
        # self.setImage()

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
        # textbox = random.choice(self.textbox["pos"])
        # self.setTextBoxSignal.emit(*textbox)
        # 0.1.6 重大修改，文本框只允许一个位点，配置文件需要修改
        self.setTextBoxSignal.emit(*self.textbox["pos"])
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

    def save(self, path=None):
        if not self.edit:
            raise RuntimeError()
        if not self.path and path is None:
            raise ValueError()
        if path is not None:
            self.path = path
        if self.image_path is None:
            return False
        fn = f"image{os.path.splitext(self.image_path)[1]}"
        image_path_new = os.path.join(path, fn)
        if not os.path.exists(image_path_new) or not os.path.samefile(image_path_new, self.image_path):
            shutil.copy(self.image_path, image_path_new)
            self.image_path = image_path_new
        self.image = fn
        config = os.path.join(self.path, "config.json")
        config_json = {
            "version": "0.1.6",
            "name": self.name,
            "image": self.image,
            "timebox": self.timebox,
            "countdownbox": self.countdownbox,
            "textbox": self.textbox
        }
        save_json(config_json, config)
        return True


class WallpaperSwitcher(QObject):
    setOpacity = pyqtSignal(float)

    class SwitchStatus:
        Waiting = 0
        Darkening = 1
        Lightening = 3
        Finished = 4

    class ToChoices:
        Previous = "Previous"
        Next = "Next"

    def __init__(self, wallpapers, functions, setOpacity, duration=1800, frames=80):
        super().__init__()
        self.wallpapers = wallpapers
        self.total = len(self.wallpapers)
        self.functions = functions
        # self.queue: List = self.wallpapers.copy()
        self._current: Optional[int] = None
        self.duration = duration
        self.wp = None
        if self.activated:
            if Runtime.image_current is None or Runtime.image_current not in self.wallpapers:
                self.current = 0
            self._current = self.wallpapers.index(Runtime.image_current)
        self.setOpacity.connect(setOpacity)
        self.status = self.SwitchStatus.Lightening
        self.switchTo = self.ToChoices.Next
        self.opacity = 1.0
        self.frames = frames
        if Runtime.image_time is None:
            self.last = None
        else:
            self.last = Runtime.image_time  # datetime.strptime(Runtime.image_time, CONFIG_TIME_FORMAT)
            if (datetime.now() - self.last).total_seconds() > self.duration:
                self._switchNext()
            self.setImage()
        # print(self.last)

    @property
    def current_path(self):
        return self.wallpapers[self._current]

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        if isinstance(value, int):
            self._current = value
            Runtime.image_current = self.wallpapers[value]
        else:
            self._current = self.wallpapers.index(value)
            Runtime.image_current = value
        Runtime.save()

    def path(self, dirname):
        return os.path.join(WALLPAPER_ROOT, dirname)

    def _switchPrevious(self):
        if not self.activated:
            return
        if self.current <= 0:
            self.current = self.total - 1
        else:
            self.current -= 1
        self.setImage()

    def _switchNext(self):
        if not self.activated:
            return
        if self.current + 1 >= self.total:
            self.current = 0
        else:
            self.current += 1
        self.setImage()

    def setImage(self):
        self.wp = BgImage(self.path(self.current_path))
        self.wp.connectSignals(**self.functions)
        self.wp.setAll()

    def previous(self):
        self.status = self.SwitchStatus.Darkening
        self.switchTo = self.ToChoices.Previous

    def next(self):
        self.status = self.SwitchStatus.Darkening
        self.switchTo = self.ToChoices.Next

    def progress(self, now):
        if self.status == self.SwitchStatus.Darkening:
            self.opacity += 2.0 / self.frames
            if self.opacity >= 1.0:
                self.opacity = 1
                self.setOpacity.emit(1)
                self.status = self.SwitchStatus.Lightening
                getattr(self, f"_switch{self.switchTo}")()
            else:
                self.setOpacity.emit(self.opacity)
        elif self.status == self.SwitchStatus.Lightening:
            self.opacity -= 2.0 / self.frames
            if self.opacity <= 0.0:
                self.opacity = 0
                self.setOpacity.emit(0)
                self.status = self.SwitchStatus.Waiting
                if self.activated:
                    self.setLast(now)
            else:
                self.setOpacity.emit(self.opacity)
        elif not self.activated:
            return
        elif self.last is None:
            self.setImage()
            self.setLast(now)
            self.status = self.SwitchStatus.Lightening
        elif self.total <= 1:
            pass
        elif (now - self.last).total_seconds() > self.duration:
            self.next()

    def setLast(self, now):
        self.last = now
        Runtime.image_time = now  # .__format__(CONFIG_TIME_FORMAT)
        Runtime.save()

    @property
    def activated(self):
        return self.wallpapers and Config.image
