# -*- coding: utf-8 -*-
import json


def load_json(path):
    return json.load(open(path, "r", encoding="utf-8"))


def save_json(obj, path):
    json.dump(obj, open(path, "w", encoding="utf-8"))


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
