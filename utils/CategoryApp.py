import yaml
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from common_fun import root


class CategoryApp(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.label = None
        self.main_window = main_window
        self.listWidget = self.main_window.ui.clsShow
        self.categories = None
        self.index = None
        self.cls_index = None
        self.listWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.init()

    def init(self):
        with open(root.parent / 'Detection.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        self.categories = data['names']
        self.categories = [' ' + str(i) for j, i in self.categories.items()]

    def set_rect_cls(self, cls_index=False, rect_index=False):
        self.index = rect_index
        self.cls_index = cls_index if rect_index else self.main_window.cls
        self.listWidget.clear()
        self.listWidget.addItems(self.categories)
        self.listWidget.itemClicked.connect(self.changeLabel)
        # 默认选择第一个类别，并更改QLabel为对应的索引
        self.listWidget.setCurrentRow(cls_index)
        self.main_window.cls = cls_index

    def clear(self):
        self.listWidget.clear()

    def changeLabel(self, item):
        """更改标签内容为点击的类别索引"""
        index = self.main_window.is_choose_rect_index

        if index is None or index > len(self.main_window.img.basedata) - 1:
            return
        # self.main_window.is_hover_move_allow = True
        self.cls_index = self.listWidget.currentRow()
        self.main_window.boxShowWidget.set_rect_box(index, self.main_window.names[self.cls_index])

        self.main_window.img.is_trans = False
        # self.main_window.img.only_index = True
        new_label = self.main_window.img.label_save[index]
        new_label[0] = int(self.cls_index)
        self.main_window.img.change(index, new_label)

        self.main_window.img.save()
        self.main_window.change_label_name = False

        self.main_window.cls = int(self.cls_index)