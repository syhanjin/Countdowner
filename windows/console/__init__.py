# -*- coding: utf-8 -*-
import os

from PyQt5.QtCore import QModelIndex, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QFileDialog, QFormLayout, QListView, QMainWindow, QMessageBox, QSizePolicy

from configs.config import Config, DEFAULT_TEXTS_JSON
from configs.path_config import TEXTS_FILE, WALLPAPER_LIST_FILE
from models.listModel import WallpaperListItem, WallpaperListWidget
from utils import QDateTime2Seconds, Second2Time, load_json, save_json, wallpapers
from windows.wallpaper_designer import WallpaperDesigner
from .console import Ui_Console


class Console(QMainWindow, Ui_Console):
    def __init__(self):
        super().__init__()
        if os.path.exists(TEXTS_FILE):
            self.text_json = load_json(TEXTS_FILE)
        else:
            self.text_json = DEFAULT_TEXTS_JSON
        self.setupUi(self)
        self.initAfterUi()
        # 配置将从全局Config对象修改

    def initAfterUi(self):
        self.ImageListAdd.clicked.connect(self.openDesigner)
        self.ImageListLoad.clicked.connect(self.ImageListLoadClicked)

        self.createImageList()
        self.createTextList()
        self.configLoad()

        # QStringListModel
        self.imageList = []
        # self.imageList = [WallpaperListItem("D:\\workspace\\programs\\Countdowner\\assets\wallpapers\\001")]
        # self.ImageList.doubleClicked.connect(self.ImageList.openPersistentEditor)
        for path in wallpapers():
            itemWidget = WallpaperListItem(path)
            self.imageList.append(itemWidget)
            self.ImageList.addItem(itemWidget)
            self.ImageList.setItemWidget(itemWidget, itemWidget.widget)
        self.ImageList.ItemDeleted.connect(self.imageList.remove)
        if len(self.text_json["texts"]) > 0:
            self.TextList.addItems(self.text_json["texts"])
            self.TextList.item(self.text_json.get('current') or 0).setSelected(True)
        # print(self.ImageList.item())
        self.ImageList.doubleClicked.connect(self.openDesigner)
        self.Save.clicked.connect(self.save)
        self.Apply.clicked.connect(self.configSave)
        self.Help.triggered.connect(self.openHelp)
        # self.ImageListEdit.setDisabled(True)

    def openHelp(self):
        QDesktopServices.openUrl(QUrl('http://docs.sakuyark.com/app/countdowner/'))

    def configLoad(self):
        self.Image.setChecked(Config.image)
        self.ImageDuration.setTime(Second2Time(Config.image_duration))
        self.ImageFrames.setValue(Config.image_switch_frames)

        self.Target.setChecked(Config.target)
        self.TargetName.setText(Config.target_name)
        self.TargetTime.setDateTime(Config.target_time)

        self.DailySentence.setChecked(Config.daily_sentence)

    def configSave(self):
        Config.image = self.Image.isChecked()
        Config.image_duration = QDateTime2Seconds(self.ImageDuration.dateTime())
        Config.image_switch_frames = self.ImageFrames.value()

        Config.target = self.Target.isChecked()
        Config.target_name = self.TargetName.text()
        Config.target_time = self.TargetTime.dateTime().toPyDateTime()

        Config.daily_sentence = self.DailySentence.isChecked()

        Config.save()
        self.applyTextList()
        self.applyWallpaperList()

    def save(self):
        self.configSave()
        self.close()

    def applyTextList(self):
        text_items = []
        for i in range(self.TextList.count()):
            text_items.append(self.TextList.item(i).text())
        selected = self.TextList.selectedIndexes()
        if len(selected) > 0:
            # self.text_json['current']
            # print(selected[0].row())
            self.text_json['current'] = selected[0].row()
        elif len(text_items) >= self.text_json['current']:
            self.text_json['current'] = 0
        self.text_json['texts'] = text_items
        save_json(self.text_json, TEXTS_FILE)

    def applyWallpaperList(self):
        wallpaper_names = []
        for i in self.imageList:
            wallpaper_names.append(i.text)
        for path in wallpapers():
            basename = os.path.basename(path)
            if basename not in wallpaper_names:
                config = os.path.join(path, 'config.json')
                os.rename(
                    config,
                    f"{config}.default"
                )
        save_json({"wallpapers": wallpaper_names}, WALLPAPER_LIST_FILE)

    def createImageList(self):
        self.ImageList = WallpaperListWidget(
            self.wallpaper, [
                {"title": "新增", "action": "custom", "custom": "add"},
                {"title": "删除", "action": "delete"},
                {"title": "清空", "action": "clear"},
            ]
        )
        self.ImageList.ContextMenuCustomAction.connect(self.ImageListContext)
        self.ImageList.setViewMode(QListView.ListMode)
        self.ImageList.setObjectName("ImageList")
        self.wallpaper_layout.setWidget(3, QFormLayout.FieldRole, self.ImageList)

    def ImageListContext(self, item):
        if item["custom"] == "add":
            self.openDesigner()

    def createTextList(self):
        self.TextList = WallpaperListWidget(
            self.text, [
                {"title": "新增", "action": "add"},
                {"title": "删除", "action": "delete"},
                {"title": "打乱", "action": "shuffle"},
                {"title": "清空", "action": "clear"},
            ]
        )
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TextList.sizePolicy().hasHeightForWidth())
        self.TextList.setSizePolicy(sizePolicy)
        self.TextList.setObjectName("TextList")
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.TextList)
        self.TextAdd.clicked.connect(self.TextList.itemAdd)

    def loadImage(self, path):
        config = os.path.join(path, "config.json")
        if not os.path.exists(config):
            config_default = config + ".default"
            if not os.path.exists(config_default):
                return False
            os.rename(config_default, config)
        self.addImageListItem(path)
        return True

    def ImageListLoadClicked(self):
        dir_path = QFileDialog.getExistingDirectory(self, "导入壁纸")
        if not dir_path:
            return
        if not self.loadImage(dir_path):
            QMessageBox().critical(self, '错误', '导入失败', QMessageBox.Yes)

    def openDesigner(self, index: QModelIndex = None):
        path = None
        if isinstance(index, QModelIndex):
            # print(index)
            item = self.ImageList.item(index.row())
            path = item.path
        image = WallpaperDesigner(path)
        image.Saved.connect(lambda new_path: self.imageSaved(new_path, path))
        image.show()

    def imageSaved(self, new_path, path):
        if new_path is None:
            return
        if new_path == path:
            return
        self.addImageListItem(new_path)

    def addImageListItem(self, path):
        itemWidget = WallpaperListItem(path)
        self.imageList.append(itemWidget)
        self.ImageList.addItem(itemWidget)
        self.ImageList.setItemWidget(itemWidget, itemWidget.widget)
