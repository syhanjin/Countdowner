# -*- coding: utf-8 -*-
import json
import os
import shutil
from datetime import time

from PyQt5.QtCore import QDateTime

from configs.path_config import WALLPAPER_DEFAULT_CONFIG_FILE, WALLPAPER_ROOT


def load_json(path):
    return json.load(open(path, "r", encoding="utf-8"))


def save_json(obj, path):
    json.dump(obj, open(path, "w", encoding="utf-8"), sort_keys=True, indent=4, ensure_ascii=False)


def text_wrapper(text):
    lines = text.strip().split("\n")
    if len(lines) == 1:
        return f"「{lines[0]}」"
    else:
        wrapped = f"「{lines[0]}　\n"
        for index in range(1, len(lines) - 1):
            wrapped += f"　{lines[index]}\n"
        wrapped += f"　　{lines[-1]}」"
        return wrapped


def is_wallpaper(item):
    if item.startswith("."):
        return False, ""
    _path = os.path.join(WALLPAPER_ROOT, item)
    if not os.path.exists(_path) or not os.path.isdir(_path):
        return False, _path
    config_path = os.path.join(_path, "config.json")
    if not os.path.exists(config_path):
        config_path = config_path + ".default"
        if not os.path.exists(config_path):
            shutil.copy(WALLPAPER_DEFAULT_CONFIG_FILE, config_path)
        return False, _path
    return True, _path


def wallpapers():
    for item in os.listdir(WALLPAPER_ROOT):
        is_wp, path = is_wallpaper(item)
        if not is_wp:
            continue
        yield path


def QDateTime2Seconds(time_: QDateTime) -> int:
    time_ = time_.toPyDateTime().time()
    return time_.hour * 3600 + time_.minute * 60 + time_.second


def Second2Time(second: int) -> time:
    hour = second // 3600
    second %= 3600
    minute = second // 60
    second %= 60
    return time(hour=hour, minute=minute, second=second)
