# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal

from configs.config import CONFIG_TIME_FORMAT, Config
from configs.path_config import TEXTS_FILE
from utils import load_json, save_json, text_wrapper


class TimeTexter(QObject):
    update = pyqtSignal(str)

    def __init__(self, attrs, function, format="%Y-%m-%d %H:%M:%S"):
        """
        时间文本更新器·时刻datetime
        :param attrs: 关注的属性，当这些属性发生变化时，定时器会按照format发送update信号
        :param format:
        """
        super().__init__()
        self.last: Optional[datetime] = None
        self.format = format
        self.attrs = attrs
        self.update.connect(function)

    def progress(self, now: datetime):
        if self.last is None:
            self.update.emit(now.__format__(self.format))
            self.last = now
            return
        for attr in self.attrs:
            if getattr(now, attr, None) != getattr(self.last, attr, None):
                self.update.emit(now.__format__(self.format))
                self.last = now
                return


class DaysTexter(QObject):
    update = pyqtSignal(str)

    def __init__(self, target, function, ):
        """
        时间文本更新器·时间间隔·距离目标时间的天数
        :param target: 目标时间
        """
        super().__init__()
        self.last: Optional[timedelta] = None
        self.target: datetime = target.date()
        self.update.connect(function)

    def progress(self, now: datetime):
        delta = self.target - now.date()
        if self.last is None or delta.days != self.last.days:
            self.update.emit(str(delta.days))
            self.last = delta


class DailySentenceTexter(QObject):
    update = pyqtSignal(str)

    def __init__(self, function, ):
        """
        每日一句文本更新器
        使用全局文本库
        """
        super().__init__()
        self.update.connect(function)
        if Config.text_time is None:
            self.last = None
        else:
            self.last: Optional[datetime] = datetime.strptime(Config.text_time, CONFIG_TIME_FORMAT)
            texts_json = load_json(TEXTS_FILE)
            if texts_json.get("current") is None:
                self.switchText()
            else:
                self.setText(texts_json["texts"][texts_json["current"]])

    def switchText(self):
        texts_json = load_json(TEXTS_FILE)
        id_ = texts_json.get("current")
        if id_ is None or id_ + 1 >= len(texts_json["texts"]):
            id_ = 0
        else:
            id_ += 1
        texts_json["current"] = id_
        self.setText(texts_json["texts"][id_])
        save_json(texts_json, TEXTS_FILE)

    def setText(self, text):
        self.update.emit(text_wrapper(text))

    def progress(self, now: datetime):
        if self.last is None or self.last.date() != now.date():
            self.switchText()
            self.last = now
            Config.text_time = self.last.__format__(CONFIG_TIME_FORMAT)
            Config.save()
