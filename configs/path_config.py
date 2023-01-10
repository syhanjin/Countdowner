# -*- coding: utf-8 -*-
from pathlib import Path

CONFIG_FILE = Path("./config.yaml")

ASSETS_ROOT = Path("./assets")

WALLPAPER_ROOT = ASSETS_ROOT / "wallpapers"
WALLPAPER_LIST_FILE = WALLPAPER_ROOT / "list.json"
WALLPAPER_DEFAULT_CONFIG_FILE = WALLPAPER_ROOT / "default.json"

TEXTS_FILE = ASSETS_ROOT / "texts.json"


def init_path():
    for key in globals().keys():
        if key.endswith('_ROOT'):
            value = globals()[key]
            value.mkdir(parents=True, exist_ok=True)
            globals()[key] = str(value.absolute()) + '/'
        elif key.endswith('_ROOT'):
            value = globals()[key]
            value.parent.mkdir(parents=True, exist_ok=True)
            globals()[key] = str(value.absolute())


init_path()
