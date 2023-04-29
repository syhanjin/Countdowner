# -*- coding: utf-8 -*-
from PyQt5.QtCore import QEvent, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QButtonGroup, QFileDialog, QMainWindow, QWidget

from configs.path_config import WALLPAPER_ROOT
from models.bgimage import BgImage
from .wallpaper_designer import Ui_WallpaperDesigner


class OptionData:
    class CountDown:
        movable = True
        editable = True
        pos = True
        size = False
        color = True
        colorFields = {"Days": "days", "Target": "target", "Text": "CountDown"}
        stylesheet = False
        align = False
        key = "countdownbox"

    class DateTime:
        movable = True
        editable = True
        pos = True
        size = False
        color = False
        stylesheet = False
        align = False
        key = "timebox"

    class Text:
        movable = True
        editable = True
        pos = True
        size = True
        color = False
        stylesheet = True
        align = True
        key = "textbox"

    class Options:
        movable = True
        editable = False
        pos = False
        size = False
        color = False
        align = False
        stylesheet = False
        key = ""

    objects = ["CountDown", "DateTime", "Text", "Options"]

    def __getitem__(self, item):
        return getattr(self, item, None)


class WallpaperDesigner(QMainWindow, Ui_WallpaperDesigner):
    Saved = pyqtSignal(str)

    def __init__(self, path=None):
        super().__init__()
        self.TextAlignGroup = QButtonGroup(self)
        self.TextAlignChoices = {}
        self._size = (0, 0)
        self.path = path
        self.bgImage = None
        self.Pos0 = None
        self.optionData = OptionData()
        self.initBeforeUi()
        self.setupUi(self)
        self.initAfterUi()

    def initBeforeUi(self):
        desktop = QApplication.desktop()
        self._size = (desktop.width(), desktop.height())
        # win32gui.SetParent(self.winId(), pretreatmentHandle())
        self.setWindowFlags(
            Qt.FramelessWindowHint  # | Qt.WindowStaysOnBottomHint
        )
        # self.lower()
        # print(self.path)
        self.bgImage = BgImage(self.path, True)
        self.bgImage.textbox['use_global_texts'] = True
        # print(self.bgImage)
        # self.setAcceptDrops(True)

    def initAfterUi(self):
        self.setStyleSheet(
            f"#WallPaperBg{{background-color: rgb(0,0,0)}}"
        )
        self.setGeometry(QRect(0, 0, *self._size))
        self.TextAlignChoices = {
            "left": self.TextAlignLeft,
            "center": self.TextAlignCenter,
            "right": self.TextAlignRight
        }
        for index, value in enumerate(self.TextAlignChoices.values()):
            self.TextAlignGroup.addButton(value, index)
            # print(self.TextAlignGroup.id(value))
        if self.bgImage.path is not None:
            self.image.setPixmap(QPixmap(self.bgImage.image_path))
        # 初始化数值并绑定事件
        for objName in self.optionData.objects:
            obj = self.optionData[objName]
            if not obj.editable:
                continue
            obj_data = getattr(self.bgImage, obj.key)
            if obj.pos:
                self.updatePosValue(objName, *obj_data["pos"][0:2])
                self.moveObject(objName)
            # 没有办法实时处理，会死循环
            # for v in ["PosX", "PosY"]:
            #     getattr(self, f"{obj}{v}").valueChanged.connect(lambda *args: print(args))  # self.moveObject(obj))
            if obj.size:
                self.updateSizeValue(objName, *obj_data["pos"][2:4])
                self.resizeObject(objName)
                # for v in ["Width", "Height"]:
                #     getattr(self, f"{obj}{v}").valueChanged.connect(lambda *args: self.resizeObject(obj))
            if obj.color:
                for k in obj.colorFields.keys():
                    getattr(self, f"{objName}Color{k}").setText(obj_data['color'][k.lower()])
                self.colorObject(objName, obj.colorFields)
            if obj.stylesheet:
                # print(obj_data['stylesheet'])
                getattr(self, f"{objName}StyleSheet").setText(obj_data['stylesheet'])
                self.styleSheetObject(objName)
            if obj.align:
                getattr(self, f"{objName}AlignChoices")[obj_data["align"]].setChecked(True)
        # self.set_image.clicked.connect(self.setImage)
        # 安装事件过滤器
        for obj in self.optionData.objects:
            getattr(self, obj).installEventFilter(self)

        self.TextAlignGroup.buttonToggled.connect(lambda *args: self.alignObject("Text"))
        self.Apply.clicked.connect(self.updateAll)
        self.setImageButton.clicked.connect(self.setImage)
        self.Save.clicked.connect(self.save)
        self.Quit.clicked.connect(self.close)

    # def mousePressEvent(self, a0: QMouseEvent) -> None:
    #     print(a0.x(), a0.y())
    #     print(a0.__dir__())
    #     print(self.sender(), a0.flags(), a0.button(), a0.buttons(), a0.source())

    def updatePosValue(self, name, x, y):
        getattr(self, f"{name}PosX").setValue(x)
        getattr(self, f"{name}PosY").setValue(y)

    def updateSizeValue(self, name, width, height):
        getattr(self, f"{name}Width").setValue(width)
        getattr(self, f"{name}Height").setValue(height)

    def updateAll(self):
        for objName in self.optionData.objects:
            obj = self.optionData[objName]
            if not obj.editable:
                continue
            if obj.pos:
                self.moveObject(objName)
            if obj.size:
                self.resizeObject(objName)
            if obj.color:
                self.colorObject(objName, obj.colorFields)
            if obj.stylesheet:
                self.styleSheetObject(objName)
            if obj.align:
                self.alignObject(objName)
        self.Text.setText(self.TextContent.text())

    def alignObject(self, name):
        # try:
        obj = getattr(self, name)
        align = list(self.TextAlignChoices.keys())[self.TextAlignGroup.checkedId()]
        if align == "left":
            obj.setAlignment(Qt.AlignLeft)
        elif align == "center":
            obj.setAlignment(Qt.AlignHCenter)
        elif align == "right":
            obj.setAlignment(Qt.AlignRight)
        obj_data = getattr(self.bgImage, self.optionData[name].key)
        obj_data['align'] = align

    # except Exception as e:
    #     print(e)

    def moveObject(self, name):
        obj = getattr(self, name)
        x = getattr(self, f"{name}PosX").value()
        y = getattr(self, f"{name}PosY").value()
        obj.move(x, y)
        # 同时更新变量
        data = getattr(self.bgImage, self.optionData[name].key)
        data["pos"][0] = x
        data["pos"][1] = y
        # print(data)
        # print(getattr(self.bgImage, self.name2key[name]))

    def resizeObject(self, name):
        obj = getattr(self, name)
        width = getattr(self, f"{name}Width").value()
        height = getattr(self, f"{name}Height").value()
        obj.resize(width, height)
        # 同时更新变量
        data = getattr(self.bgImage, self.optionData[name].key)
        data["pos"][2] = width
        data["pos"][3] = height
        # print(getattr(self.bgImage, self.name2key[name]))

    def colorObject(self, name, fields):
        obj_data = getattr(self.bgImage, self.optionData[name].key)
        for k, v in fields.items():
            color = getattr(self, f"{name}Color{k}").text()
            obj_data['color'][k.lower()] = color
            getattr(self, v).setStyleSheet(f"color: \"{color}\"")

    def styleSheetObject(self, name):
        # print(getattr(self, f"{objName}StyleSheet").toPlainText())
        stylesheet = getattr(self, f"{name}StyleSheet").toPlainText()
        # print(stylesheet)
        getattr(self, name).setStyleSheet(stylesheet)
        getattr(self.bgImage, self.optionData[name].key)["stylesheet"] = stylesheet

    def eventFilter(self, watched: QWidget, event: QEvent):
        if event.type() == event.MouseButtonPress:
            # print(watched.objectName())
            self.Pos0 = event.globalPos() - watched.pos()
            # print(self.Pos0)
        elif event.type() == event.MouseMove:
            toPos, name = event.globalPos() - self.Pos0, watched.objectName()
            watched.move(toPos)
            # print(self.movableObjects)
            if self.optionData[name].pos:
                self.updatePosValue(name, toPos.x(), toPos.y())
            # print()
        return False

    def connectSignals(self, **kwargs):
        self.bgImage.connectSignals(**kwargs)
        # for k, v in kwargs.items():
        #     getattr(self, f"{k}Signal").connect(v)

    def setImage(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image Files (*.png *.jpg *.bmp)")
        self.bgImage.image_path = file_path
        self.image.setPixmap(QPixmap(file_path))

    def save(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择保存路径", directory=self.path or WALLPAPER_ROOT)
        if not dir_path:
            return
            # print(dir_path)
        # try:
        self.bgImage.save(dir_path)
        # except Exception as e:
        #     print(e)
        # print("saved")
        self.Saved.emit(dir_path)
        self.close()
