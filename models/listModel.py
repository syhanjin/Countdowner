# -*- coding: utf-8 -*-
import os.path

from PyQt5.QtCore import QModelIndex, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu, QWidget


class WallpaperListItem(QListWidgetItem):
    path: str = None

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.widget = QWidget()
        self.pathLabel = QLabel()
        self.pathLabel.setText(self.text)
        self.fullpathLabel = QLabel()
        self.fullpathLabel.setText(self.path)
        self.fullpathLabel.setStyleSheet("color: \"red\";")
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.pathLabel)
        self.hbox.addWidget(self.fullpathLabel)
        self.hbox.addStretch(1)
        # 设置widget的布局
        self.widget.setLayout(self.hbox)
        # 设置自定义的QListWidgetItem的sizeHint，不然无法显示
        self.setSizeHint(self.widget.sizeHint())

    def setPath(self, path):
        self.path = path
        self.pathLabel.setText(self.text)

    @property
    def text(self):
        return os.path.basename(self.path)


class WallpaperListWidget(QListWidget):
    ContextMenuCustomAction = pyqtSignal(dict)
    ItemDeleted = pyqtSignal(QListWidgetItem)

    def __init__(self, parent, menu):
        super().__init__(parent)
        self.setDragDropMode(self.InternalMove)  # 设置拖放

        self.menu = menu

        # 双击可编辑
        self.doubleClicked.connect(self.itemEdit)

        # 右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.custom_right_menu)

    def custom_right_menu(self, pos):
        menu = QMenu()
        for item in self.menu:
            item["opt"] = menu.addAction(item["title"])

        action = menu.exec_(self.mapToGlobal(pos))

        for item in self.menu:
            if action != item["opt"]:
                continue
            if item["action"] == "add":
                self.itemAdd()
            elif item["action"] == "delete":
                for j in range(len(self.selectedIndexes()) - 1, -1, -1):  # 反向删除
                    item = self.takeItem(self.selectedIndexes()[j].row())
                    self.ItemDeleted.emit(item)
            elif item["action"] == "clear":
                self.clear()
            elif item["action"] == "shuffle":
                pass
            elif item["action"] == "custom":
                self.ContextMenuCustomAction.emit(item)

    @pyqtSlot()
    def itemAdd(self):
        item = QListWidgetItem("新增")
        self.addItem(item)
        self.itemEdit(item=item)

    def itemEdit(self, modelindex: QModelIndex = None, item: QListWidgetItem = None) -> None:
        if item is None:
            item = self.item(modelindex.row())
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.editItem(item)

    # def dropEvent(self, QDropEvent):
    #     """拖拽结束以后触发的事件"""
    #     source_Widget = QDropEvent.source()  # 获取拖入元素的父组件
    #     items = source_Widget.selectedItems()
    #     # print(items)
    #     for i in items:
    #         source_Widget.takeItem(source_Widget.indexFromItem(i).row())
    #         self.addItem(i)
    #         self.setItemWidget(i, i.widget)
