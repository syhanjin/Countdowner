# -*- coding: utf-8 -*-
"""
0.1.5 -> 0.1.6
"""

from updates.update import get_wallpapers
from utils import save_json


def update():
    for path, wallpaper in get_wallpapers():
        pos = wallpaper["textbox"]["pos"]
        if len(pos) > 0 and type(pos[0]) == list:
            wallpaper["textbox"]["pos"] = wallpaper["textbox"]["pos"][0]
            save_json(wallpaper, path)


if __name__ == "__main__":
    update()
