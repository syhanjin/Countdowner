# -*- coding: utf-8 -*-

# ==============================================================================
#  Copyright (C) 2023 Sakuyark, Inc. All Rights Reserved                       =
#                                                                              =
#    @Time : 2023-1-8 13:50                                                    =
#    @Author : hanjin                                                          =
#    @Email : 2819469337@qq.com                                                =
#    @File : __init__.py                                                       =
#    @Program: Countdowner                                                     =
# ==============================================================================
from datetime import datetime

import yaml

from configs.path_config import CONFIG_FILE

CONFIG_TIME_FORMAT = "%Y-%m-%d %H:%M:%S:%f"

DEFAULT = {
    "target": False,
    "target_name": "2024年高考",
    "target_time": datetime(2024, 6, 7).__format__(CONFIG_TIME_FORMAT),
    "image_duration": 1800,
    "image": True,
    "image_current": None,
    "image_time": None,
    "image_switch_frames": 80,
    "daily_sentence": False,  # 每日一句，如果为True，会强制使用全局文本库，且每日按顺序切换下一句
    "text_time": None
}


class ConfigManager:
    target: bool = DEFAULT["target"]
    target_name: str = DEFAULT["target_name"]
    target_time: str = DEFAULT["target_time"]
    image_duration: int = DEFAULT["image_duration"]
    image: bool = DEFAULT["image"]
    image_current: str = DEFAULT["image_current"]
    image_time: str = DEFAULT["image_time"]
    image_switch_frames: int = DEFAULT["image_switch_frames"]
    daily_sentence: bool = DEFAULT["daily_sentence"]
    text_time: str = DEFAULT["text_time"]

    def __init__(self, data=None) -> None:
        if data is None:
            data = DEFAULT
        for k, v in data.items():
            self.__setattr__(k, v)

    def save(self):
        """
        保存配置
        """
        with open(CONFIG_FILE, "w", encoding="utf8") as f:
            yaml.dump(
                self.__dict__, f, indent=2, allow_unicode=True
            )


CONFIG_FILE.parent.mkdir(exist_ok=True, parents=True)
if CONFIG_FILE.exists():
    """读取配置"""
    with open(CONFIG_FILE, "r", encoding="utf8") as f:
        Config = ConfigManager(yaml.load(f, Loader=yaml.FullLoader))
else:
    """创建配置文件"""
    Config = ConfigManager()
    Config.save()
