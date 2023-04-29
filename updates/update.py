# -*- coding: utf-8 -*-
"""
提供更新函数
"""
import os

from configs.path_config import WALLPAPER_ROOT
from utils import is_wallpaper, load_json


def get_wallpapers():
    wallpapers = os.listdir(WALLPAPER_ROOT)
    for item in wallpapers:
        is_wp, path = is_wallpaper(item)
        if is_wp:
            config_path = os.path.join(path, "config.json")
            wallpaper_json = load_json(config_path)
            yield config_path, wallpaper_json
