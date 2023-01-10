# -*- coding: utf-8 -*-
import json


def load_json(path):
    return json.load(open(path, "r", encoding="utf-8"))


def save_json(obj, path):
    json.dump(obj, open(path, "w", encoding="utf-8"))
