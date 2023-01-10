# -*- coding: utf-8 -*-
# 配置控制文件
import getopt
import os.path
import random
import sys

from configs.path_config import TEXTS_FILE
from utils import load_json, save_json

"""
image: true
image_current: '001'
image_duration: 1800
image_switch_frames: 80
target: false
target_name: 2024年高考
target_time: 2024-06-07 00:00:00:000000
"""
HELP = """
Countdown配置快速管理工具
 -h 获取帮助
 -i DIRNAME wallpaper下的文件夹名称，用于修改当前壁纸（不推荐使用）
 -d --duration DURATION 壁纸切换时间(s)
 -f --image_switch_frames FRAMES 切换壁纸长度（建议为偶数，不推荐修改）
 --hide_image 隐藏壁纸
 --show_countdown 显示倒计时
 --target_name 目标名称，5字最佳（中文算1个字，数字和英文算0.5个字）
 --target_time 倒计时时间 格式 %Y-%m-%d-%H-%M-%S
又，以上功能全部没做
 --load_texts PATH 导入句子 传文本文件路径 一行一句，不超过100字 \n将会被替换为换行符
 --show_texts 显示已导入的句子
 --del_texts ID 删除句子，ID由逗号分隔，传入all则删除全部
 --shuffle_texts 随机排序句子
""".strip()


def get_texts_json():
    if not os.path.exists(TEXTS_FILE):
        return {"texts": []}
    return load_json(TEXTS_FILE)


def main(argv):
    try:
        opts, args = getopt.getopt(
            argv, "hi:d:f:",
            [
                "hide_image", "duration=", "image_switch_frames=",
                "show_countdown", "target_name=", "target_time=",
                "load_texts=", "show_texts", "del_texts=", "shuffle_texts"
            ]
        )
    except getopt.GetoptError:
        print(HELP)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(HELP)
        elif opt == "--load_texts":
            path = arg
            if not os.path.exists(path):
                print(f"{path}不存在")
                sys.exit()
            with open(path, "r", encoding="utf-8") as f:
                texts = f.readlines()
            cnt = 0
            texts_json = get_texts_json()
            for text in texts:
                if text.strip():
                    texts_json["texts"].append(text.strip().replace("\\n", "\n"))
                    cnt += 1
            save_json(texts_json, TEXTS_FILE)
            print(f"导入完毕，共{cnt}条")
        elif opt == "--show_texts":
            texts_json = get_texts_json()
            for index, text in enumerate(texts_json["texts"]):
                print(f"{index}. {text}")
            print(f"共{len(texts_json['texts'])}条")
        elif opt == "--del_texts":
            if arg == "all":
                os.remove(TEXTS_FILE)
                continue
            texts_json = get_texts_json()
            ids = [int(x) for x in arg.split(",")]
            ids = sorted(ids, reverse=True)
            current = texts_json.get("current")
            for id in ids:
                if current is None:
                    pass
                elif id == current:
                    current = None
                elif id < current:
                    current -= 1
                print(f"删除\"{texts_json['texts'][id]}\"成功")
                texts_json["texts"].pop(id)
            print(f"删除完毕，共{len(ids)}条")
            texts_json['current'] = current
            save_json(texts_json, TEXTS_FILE)
        elif opt == "--shuffle_texts":
            texts_json = get_texts_json()
            current = texts_json.get("current")
            if current is None:
                random.shuffle(texts_json["texts"])
            else:
                current_text = texts_json["texts"].pop(current)
                random.shuffle(texts_json["texts"])
                texts_json["texts"].insert(0, current_text)
                texts_json["current"] = 0
            print(f"已打乱，共{len(texts_json['texts'])}句")
            save_json(texts_json, TEXTS_FILE)


if __name__ == "__main__":
    main(sys.argv[1:])
