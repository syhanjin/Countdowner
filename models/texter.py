# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal


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
