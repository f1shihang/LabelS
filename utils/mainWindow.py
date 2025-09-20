import os
import shutil
import yaml

from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidget, QMessageBox, QColorDialog, QShortcut

from CategoryApp import CategoryApp
from tempCatewidget import CategoryApp as tempWidget
from LabelApp import LabelApp
from ImageApp import Image
from thumbnailApp import thumbnailApp
from modificationCls import modificationCls
from common_fun import distance, root

root = root.parent


class MainWin(QMainWindow):
    # 总窗口
    def __init__(self):
        super().__init__()

        # -———————————————————————————————— UI相关变量 ————————————————————————————————#

        # *** 从这里加载ui文件，搭建界面 ***
        self.ui = uic.loadUi(str(root / "utils/qt_ui_file/main.ui"), self)

        # *** 显示用的label, 主屏幕 ***
        self.label = self.ui.label
        self.label.installEventFilter(self)

        # *** 显示用的label, 用来显示当前图片的名字， 在最下方 ***
        self.current_label_name_show = self.ui.character_label  # 用来展示当前图片的名字

        # *** 显示当前文件夹下所有图片的名字,  变成缩略图 ***
        self.thumbnail_widget = None

        self.temp_widget = None

        # *** 用来显示选中哪个框,用来切换框 ***
        self.boxShowWidget = LabelApp(self)

        # *** 如果鼠标选中了某个框, 用来显示和更新类别名 ***
        self.categoryShowWidget = CategoryApp(self)

        # *** UI界面上的按钮 ***
        self.arrows_button = self.ui.arrows  # 切换鼠标样式->箭头
        self.hand_button = self.ui.hand  # 切换鼠标样式->手
        self.open_folder = self.ui.openFolder  # 打开文件夹
        self.open_file = self.ui.openFile  # 打开文件
        self.imgUP = self.ui.imgUP  # 放大图片
        self.imgDOWN = self.ui.imgDOWN  # 缩小图片
        self.readFolderLabel = self.ui.readFolderLabel  # 读取文件夹的中的标签
        self.resetShowImg = self.ui.resetShowImg  # 重置图片显示
        self.save_label = self.ui.save  # 保存
        self.deleteBox = self.ui.deleteBox  # 删除选则的框
        self.cls_color = self.ui.cls_color  # 从轮盘中选则颜色, 并且更改当前类别的颜色
        self.renew_cls = self.ui.renewCls  # 修改类别名

        self.show_box_circle = self.ui.checkBox1  # 显示框和点
        self.show_other = self.ui.checkBox  # 显示其他类别的框和点
        self.show_box_fill = self.ui.checkBox2  # 显示框的填充
        self.show_box_text = self.ui.checkBox3  # 显示框的文字

        self.load_model = self.ui.load_model  # 导入模型
        self.detect = self.ui.detect  # 检测
        self.lineEdit = self.ui.lineEdit  # 检测置信度

        # —————————————————————————————   素材   ————————————————————————————#
        folder = QtGui.QPixmap(str(root / "utils/material/folder.png"))
        file = QtGui.QPixmap(str(root / "utils/material/file.png"))
        label = QtGui.QPixmap(str(root / "utils/material/label.png"))
        hand = QtGui.QPixmap(str(root / "utils/material/hand.png"))
        arrows = QtGui.QPixmap(str(root / "utils/material/arrow.png"))
        Down = QtGui.QPixmap(str(root / "utils/material/down.png"))
        Up = QtGui.QPixmap(str(root / "utils/material/Up.png"))
        reset = QtGui.QPixmap(str(root / "utils/material/reset.png"))
        export = QtGui.QPixmap(str(root / "utils/material/export.png"))
        color = QtGui.QPixmap(str(root / "utils/material/color.png"))

        self.open_folder.setIcon(QtGui.QIcon(folder.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.open_file.setIcon(QtGui.QIcon(file.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.readFolderLabel.setIcon(QtGui.QIcon(label.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.hand_button.setIcon(QtGui.QIcon(hand.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.arrows_button.setIcon(QtGui.QIcon(arrows.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.imgDOWN.setIcon(QtGui.QIcon(Down.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.imgUP.setIcon(QtGui.QIcon(Up.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.resetShowImg.setIcon(QtGui.QIcon(reset.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.save_label.setIcon(QtGui.QIcon(export.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        self.cls_color.setIcon(QtGui.QIcon(color.scaled(15, 15, Qt.KeepAspectRatio, Qt.SmoothTransformation)))

        # ————————————————————————————— 快捷键相关变量 ————————————————————————————#
        self.shortcut1 = QShortcut(QKeySequence("Z"), self)  # 上一张
        self.shortcut2 = QShortcut(QKeySequence("X"), self)  # 下一张
        self.shortcut5 = QShortcut(QKeySequence("C"), self)  # 标注
        # self.shortcut3 = QShortcut(QKeySequence("Ctrl+C"), self)  # 复制框
        # self.shortcut4 = QShortcut(QKeySequence("Ctrl+V"), self)  # 粘贴框
        self.shortcut1.activated.connect(self.handleShortcut1_)
        self.shortcut2.activated.connect(self.handleShortcut2_)
        self.shortcut5.activated.connect(self.detect_)
        # self.shortcut3.activated.connect(self.handleShortcut3_)
        # self.shortcut4.activated.connect(self.handleShortcut4_)

        # ———————————————————————————————— 信号槽 ————————————————————————————————#

        self.arrows_button.clicked.connect(self.arrows_button_)
        self.hand_button.clicked.connect(self.hand_button_)
        self.open_folder.clicked.connect(self.select_folder)
        self.open_file.clicked.connect(self.select_file)
        self.readFolderLabel.clicked.connect(self.readFolderLabel_)
        self.imgUP.clicked.connect(self.imgUp_)
        self.imgDOWN.clicked.connect(self.imgDown_)
        self.resetShowImg.clicked.connect(self.resetShowImg_)
        self.save_label.clicked.connect(self.save_)
        self.deleteBox.clicked.connect(self.deleteBox_)
        self.cls_color.clicked.connect(self.cls_color_)
        self.renew_cls.clicked.connect(self.renew_cls_)
        self.show_box_circle.stateChanged.connect(self.show_box_circle_)
        self.show_other.stateChanged.connect(self.show_other_)
        self.show_box_fill.stateChanged.connect(self.show_box_fill_)
        self.show_box_text.stateChanged.connect(self.show_box_text_)
        self.load_model.clicked.connect(self.load_model_)
        self.detect.clicked.connect(self.detect_)

        # ———————————————————————————————— 事件相关变量 ————————————————————————————————#

        self.mouse_left_press = False  # 鼠标左键按下
        self.mouse_right_press = False  # 鼠标右键按下
        self.mouse_pos = None  # 鼠标当前位置
        self.mouse_press_pos = None  # 鼠标按下的位置(左键按下的位置)
        self.move_pos_track = []  # 移动轨迹(用来绘制鼠标操作的移动轨迹，最多保存8个点)
        self.key_press = False  # 键盘按键是否按下了Ctrl

        # ———————————————————————————————— 按钮相关变量 ————————————————————————————————#

        self.hand = False  # 手型鼠标的标记
        self.temp_hand = False  # 临时手型鼠标的标记
        self.hand_flag = False  # 握紧手型鼠标的标记
        self.arrows = True  # 箭头鼠标的标记
        self.cross = False  # 十字鼠标的标记, 鼠标悬停在点上面的时候使用
        self.hover = False  # 悬停鼠标的标记

        # ———————————————————————————————— 图像相关变量 ————————————————————————————————#

        self.img_is_load = False  # 图片是否加载
        self.img = None  # 当前操作的图片

        self.is_update_label = False  # 是否正在更新框的label
        self.is_update_label_save = None  # 保存更新框的label的信息 [box_index, img.label_save[index], img.basedata[index]]
        self.is_first_update_label = True  # 是否是第一次更新label

        self.is_add_box = False  # 是否在添加框
        self.is_first_add_box = True  # 是否是第一次更新label, 因为第一次添加框，后面都是修改框的label,用来区分是添加还是修改
        self.add_label_save = None  # 添加框的label的信息 [box_index, img.label_save[index], img.basedata[index]]

        self.is_open_folder = False  # 是否加载了了文件夹中的图片
        self.is_open_file = False  # 是否打加载了图片
        self.is_choose_rect = False  # 是否选择了框
        self.is_choose_rect_index = None  # 选择的框的索引
        self.is_choose_rect_over_striking = False  # 是否框已经加粗了

        self.is_hover_move_allow = False  # 是否可以移动框
        self.is_hover_move_rect = False  # 是否在移动框

        self.default_save_path = root / 'utils/temp_folder'  # 默认保存路径
        self.choose_save_path = None  # 选择的保存路径
        self.label_list = set()  # 第一次加载的时候, 要初始化本地标签文件到图片上, 存放所有标签全路径
        self.label_list_only_name = set()
        self.img_list = set()  # 存放所有图片全路径
        self.img_list_only_name = set()

        self.mouse_save_temp = None  # 临时记录显示的图片的中心在label中的位置
        self.circle_save = None  # 保存鼠标悬停的点的的信息 [box_index, circle_index, img.label_save[index], img.basedata[index]]
        self.rect_save = None  # 保存鼠标悬停的框的信息 [box_index, img.label_save[index], img.basedata[index]]
        self.rect_save_current = None  # 保存当前选中的框的信息 [box_index, img.label_save[index], img.basedata[index]]
        self.rect_save = None  # 保存鼠标悬停的框的信息 [box_index, img.label_save[index], img.basedata[index]]

        self.mouse_with_nine_circle = None  # 保存鼠标悬停的点的的信息 [box_index, circle_index, img.label_save[index], img.basedata[index]]
        self.mouse_with_box = None  # 保存鼠标悬停的框的信息 [box_index, img.label_save[index], img.basedata[index]]

        self.wheel_scale = 1  # 图片放大的倍数, 当前图片相对于label尺寸的缩放倍数
        self.cls = 0  # 当前类别, 新添加的标签默认使用上一次的标签名
        self.names = None  # 类别名字列表
        self.colors = dict()  # 类别颜色列表

        self.len_rect = 0  # 当前图片已经添加的框的总数量

        self.label_height = self.label.size().height()  # label的高度
        self.label_width = self.label.size().width()  # label的宽度

        self.change_label_name = None

        self.yolov8_model = None
        self.conf = 0.5

        # ———————————————————————————————— 初始化 ————————————————————————————————#
        self.init()

    def init(self, img_path=None):
        # 先加载本地的配置文件
        # names : 类别名字 list, colors : 类别颜色 list, cls : 默认类别 int, save_path : 默认保存路径 str
        with open(root / 'Detection.yaml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        self.names = data['names']
        self.colors = self.colors if data['colors'] is None else data['colors']
        self.cls = int(data['default_cls'])
        self.default_save_path = data['save_path'] if data['save_path'] != 'temp_folder' else self.default_save_path

        self.wheel_scale = 1  # 滚轮放大的倍数, 当前图片相对于label尺寸的缩放倍数
        self.img_is_load = False  # 图片是否加载
        self.mouse_pos = [0, 0]  # 鼠标在label中的坐标
        self.mouse_save_temp = [0, 0]  # 鼠标在label中的坐标

        self.is_add_box, self.is_update_label, self.len_rect, self.is_choose_rect, self.rect_save, self.rect_save_current = False, False, 0, False, None, None
        self.mouse_press_pos, self.is_first_add_box = None, True
        self.is_choose_rect_index, self.is_choose_rect_over_striking = None, False
        self.cross, self.hover, self.hand, self.arrows, self.hand_flag, self.temp_hand = False, False, False, True, False, False
        self.mouse_press_pos, self.mouse_left_press, self.mouse_right_press = None, False, False

        for i in os.listdir(self.default_save_path):
            if i.endswith('.txt'):
                self.label_list.add(str(self.default_save_path / i))
                self.label_list_only_name.add(os.path.basename(str(self.default_save_path / i)).split('.')[0])

        # 初始化图片, 如果有图片路径, 就加载图片
        if img_path is not None:
            img_name = os.path.basename(img_path).split('.')[0]
            p = str(self.default_save_path / img_name) + '.txt' if img_name in self.label_list_only_name else None
            self.init_image(img_path, p)
            self.categoryShowWidget.init()

    # 从本地加载图片，有标签就添加标签
    def init_image(self, img_path, label_path):
        self.img = Image(self.label, img_path, label_path, parent=self)

        self.img.show_box_circle = self.show_box_circle.isChecked()
        self.img.show_other = self.show_other.isChecked()
        self.img.show_box_fill = self.show_box_fill.isChecked()
        self.img.show_box_text = self.show_box_text.isChecked()

        self.img_is_load = True

    def resizeEvent(self, event):
        if self.img_is_load:
            self.label_height = self.label.size().height()
            self.label_width = self.label.size().width()
            if self.img_is_load:
                self.init(self.img.img_path)
                self.categoryShowWidget = CategoryApp(self)
                self.boxShowWidget = LabelApp(self)

    # 事件过滤器, 用来处理鼠标事件
    def eventFilter(self, source, event):
        if self.change_label_name:
            return True
        # 鼠标移动事件
        if event.type() == QEvent.MouseMove:
            # 记录鼠标每次移动到的位置
            self.mouse_pos = [event.pos().x() - 12, event.pos().y()]

            self.mouse_state()

            self.get_cross_or_hover()

            # 悬停显示颜色加深, 但是不常亮
            self.mouse_hover_display()

            # 移动图像
            if self.hand and self.mouse_left_press:
                self.moveImage()

            # 更新label
            if self.is_update_label:
                self.updDatalabel()

            # 添加框
            elif self.is_add_box:
                self.addBox()

        # ———————————————————————————————— 鼠标事件 ————————————————————————————————#

        # 点击左键
        if event.type() == QEvent.MouseButtonPress and event.type() != QEvent.MouseButtonDblClick:
            if event.button() == Qt.LeftButton:  # 鼠标左键按下, 双击也会触发
                self.temp_widget = None

                if self.mouse_left_press is False and self.img_is_load:

                    self.mouse_left_press = True
                    self.mouse_press_pos = self.limit_xy(event.pos().x() - 12, event.pos().y())
                    self.mouse_save_temp = self.mouse_press_pos

                    if self.arrows and self.cross and not self.is_add_box:
                        self.img.only_index = True
                        # 按下鼠标左键时，更新label
                        self.is_add_box = False
                        self.is_update_label = True

                    elif self.arrows and not self.is_update_label and self.pos_in_org(
                            self.mouse_press_pos):

                        self.img.only_index = True
                        # 按下鼠标左键时，添加框
                        self.is_update_label = False
                        self.is_add_box = True

            if event.button() == Qt.RightButton:
                self.deleteBox_()
        if event.type() == QEvent.MouseButtonPress and event.type() == QEvent.MouseButtonDblClick:
            self.mouse_left_press = False

        # 释放
        if event.type() == QEvent.MouseButtonRelease:
            # 鼠标左键释放
            if event.button() == Qt.LeftButton:
                if not self.img_is_load:
                    return False

                if self.img_is_load:
                    self.img.save()

                if self.is_add_box and self.is_choose_rect and self.is_choose_rect_index:
                    x1y1 = self.img.org_xy_to_new_xy(self.img.label_save[-1][1:3])
                    x2y2 = self.img.org_xy_to_new_xy(self.img.label_save[-1][3:])
                    if distance(x1y1, x2y2) < 25:
                        self.deleteBox_(-1)
                        self.is_add_box = False

                if self.img_is_load and distance(self.mouse_press_pos, (event.pos().x() - 12, event.pos().y())) < 10:
                    if not self.cross and not self.hover:
                        # 没有悬停在框上, 没有悬停在点上, 就取消选中框
                        self.is_choose_rect_index = None
                        self.is_choose_rect = False
                        self.is_hover_move_allow = False
                        self.rect_save_current = None
                        self.move_xy()
                        self.is_add_box = False

                    else:
                        self.is_choose_rect_index = self.rect_save_current[0]
                        self.is_choose_rect = True
                        self.move_xy(index=self.is_choose_rect_index)

                        if not self.mouse_left_press:
                            # 弹出类别框
                            self.temp_widget = tempWidget(self, QListWidget())
                            self.temp_widget.set_rect_cls(self.rect_save_current[2][0], 1)
                            self.temp_widget.show()
                            global_pos = self.mapToGlobal(event.pos())
                            self.temp_widget.move(global_pos.x() + 100, global_pos.y())

                self.categoryShowWidget.clear()
                self.categoryShowWidget = CategoryApp(self)
                if self.is_choose_rect:
                    self.categoryShowWidget.set_rect_cls(self.cls)

                self.img.only_index = False
                self.is_update_label = False
                self.is_add_box = False
                self.mouse_left_press = False
                self.mouse_save_temp = None
                self.hand_flag = False

                self.rect_save = None
                self.is_first_add_box = True
                self.is_first_update_label = True

                if self.rect_save_current and not self.is_hover_move_allow:
                    index_ = self.rect_save_current[0] if self.rect_save_current else None

                    self.move_xy(index=index_)
                    self.categoryShowWidget.set_rect_cls(self.rect_save_current[2][0], 1)
                    self.boxShowWidget.set_rect_box(self.rect_save_current[0])
            else:
                return False

        return super().eventFilter(source, event)

    # ———————————————————————————————— 键盘事件 ————————————————————————————————#

    def keyReleaseEvent(self, event):
        if self.temp_hand:
            self.key_press = False
            self.temp_hand = False
            self.arrows = True
            self.cross = False
            self.hand = False

    def keyPressEvent(self, event):
        if self.img_is_load and event.key() == Qt.Key_Delete:
            self.deleteBox_()
        if self.img_is_load and event.modifiers() & Qt.ControlModifier:
            # Ctrl键被按下 event.modifiers()是一个int类型的值, 用来判断Ctrl键是否被按下
            self.temp_hand, self.key_press, self.hand = True, True, True
            self.cross, self.arrows = False, False
        else:
            self.key_press = False

    # ———————————————————————————————— 鼠标滚轮事件 ————————————————————————————————#
    def wheelEvent(self, event):
        if self.arrows and self.img_is_load:
            self.img.is_trans = True
            self.move_xy(0, int(event.angleDelta().y() / 4))

        elif self.hand and self.img_is_load:
            self.hand_flag = False
            angle_delta = event.angleDelta().y() / 8  # 获取滚动距离
            if 0.2 <= self.wheel_scale <= 3:
                self.wheel_scale += round(angle_delta / 150, 2)
            else:
                self.wheel_scale = min(max(0.5, self.wheel_scale), 3)
            if self.wheel_scale < 0.1:
                self.wheel_scale = 0.2
            self.img.is_trans = True
            self.move_xy()

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            if self.arrows:
                self.hand = True
                self.arrows = False
                self.setCursor(Qt.OpenHandCursor)
            elif self.hand:
                self.hand = False
                self.arrows = True
                self.setCursor(Qt.ArrowCursor)
        # 确保继续处理其他鼠标事件
        super().mousePressEvent(event)

    # ———————————————————————————————— 状态辅助函数 ————————————————————————————————#
    def mouse_state(self):
        # 鼠标样式
        if self.hand and self.hand_flag:
            self.setCursor(Qt.ClosedHandCursor)
        if self.hand and not self.hand_flag:
            self.setCursor(Qt.OpenHandCursor)
        if self.arrows and self.cross:
            self.setCursor(Qt.CrossCursor)
        if self.arrows and not self.cross:
            self.setCursor(Qt.ArrowCursor)
        if self.arrows and not self.cross and self.hover:
            self.setCursor(Qt.SizeAllCursor)

    # ———————————————————————————————— 辅助函数 ————————————————————————————————#

    def limit_xy(self, x, y):
        # 限制x, y的范围 不要跑出qt label的范围
        x = max(min(x, self.label.size().width()), 0)
        y = max(min(y, self.label.size().height()), 0)
        return x, y

    def limit_center(self, x, y):
        # 限制x, y的范围 不要跑出加载的图像在label上的范围
        if x <= - self.img.label_width * self.wheel_scale // 2:
            x = - self.img.label_width * self.wheel_scale // 2 + 1
        if x >= self.img.label_width + self.img.label_width * self.wheel_scale // 2:
            x = self.img.label_width + self.img.label_width * self.wheel_scale // 2 - 1
        if y <= - self.img.label_height * self.wheel_scale // 2:
            y = - self.img.label_height * self.wheel_scale // 2 + 1
        if y >= self.img.label_height + self.img.label_height * self.wheel_scale // 2:
            y = self.img.label_height + self.img.label_height * self.wheel_scale // 2 - 1
        return int(x), int(y)

    def move_xy(self, bias_x=0, bias_y=0, index=None):
        if self.img_is_load:
            # 图片移动bias_x, bias_y个像素

            x = self.img.center[0] + bias_x
            y = self.img.center[1] + bias_y

            x, y = self.limit_center(x, y)

            self.img.show(int(x), int(y), scale=self.wheel_scale)  # 显示图片
            self.img.label_show(index)  # 显示标签

    def mouse_track(self):
        if self.img_is_load:
            if len(self.move_pos_track) < 8:
                self.move_pos_track.append(self.mouse_pos)
            else:
                self.move_pos_track.append(self.mouse_pos)
                self.move_pos_track.pop(0)
                for i in range(8):
                    self.img.add_circle(self.move_pos_track[7 - i], (100, 255, 255, 100 - i * 10), 5 - i // 2,
                                        is_ball=True)

    def get_cross_or_hover(self):
        if self.img_is_load:
            is_in_circle_ = self.img.is_in_circle(*self.mouse_pos, 15)
            is_in_box_ = self.img.is_in_rect(*self.mouse_pos)
            self.cross = is_in_circle_[0]  # 是否在圆内
            self.hover = is_in_box_[0]  # 是否在框内

            if not self.is_add_box and not self.is_update_label:
                if self.cross or self.hover:
                    index = is_in_circle_[1] if self.cross else is_in_box_[1]
                    self.rect_save = [index, is_in_circle_[2], self.img[index][0]]  # 添加旧框信息
                    self.rect_save_current = self.rect_save

    def pos_in_org(self, pos):
        x, y = self.img.new_xy_to_org_xy(pos)
        return 0 < x < self.img.org_width and 0 < y < self.img.org_height

    def computer_new_label(self):
        new_label = self.rect_save_current[2]
        pos = self.img.new_xy_to_org_xy(self.mouse_pos)
        circle_index = self.rect_save_current[1]

        self.computer_new_label_assist(new_label, circle_index, pos)

        x1, y1, x2, y2 = new_label[1:5]

        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        # TODO: 限制框的大小
        new_label[1:5] = x1, y1, x2, y2
        return new_label

    @staticmethod
    def computer_new_label_assist(new_label, index, pos):
        mapping = {
            0: lambda: new_label.__setitem__(slice(1, 3), pos),
            1: lambda: new_label.__setitem__(slice(2, 4), pos[::-1]),
            2: lambda: new_label.__setitem__(slice(1, None, 3), pos),
            3: lambda: new_label.__setitem__(slice(3, 5), pos),
            4: lambda: new_label.__setitem__(1, pos[0]),
            5: lambda: new_label.__setitem__(4, pos[1]),
            6: lambda: new_label.__setitem__(3, pos[0]),
            7: lambda: new_label.__setitem__(2, pos[1]),
            8: lambda: handle_case_8(pos)
        }

        def handle_case_8(pos):
            x_, y_ = (new_label[1] + new_label[3]) / 2, (new_label[2] + new_label[4]) / 2
            bias_x, bias_y = int(pos[0] - x_), int(pos[1] - y_)
            new_label[1:5] = [new_label[1] + bias_x, new_label[2] + bias_y, new_label[3] + bias_x,
                              new_label[4] + bias_y]

        return mapping[index]()

    def add_box(self):
        if self.is_first_add_box and self.pos_in_org(self.mouse_press_pos):
            self.is_first_add_box = False

            x1y1 = self.img.new_xy_to_org_xy(self.mouse_press_pos)

            self.img.append([self.cls, *x1y1, *x1y1])
            self.len_rect += 1
            self.is_choose_rect = True
            self.is_choose_rect_index = self.len_rect - 1
            self.rect_save_current = [self.len_rect - 1, -1, self.img.basedata[-1]]

            self.categoryShowWidget.set_rect_cls(self.rect_save_current[2][0], 1)
            self.boxShowWidget.set_rect_box(self.rect_save_current[0])

        elif not self.is_first_add_box and self.pos_in_org(self.mouse_pos):

            x1, y1 = self.mouse_press_pos
            x2, y2 = self.mouse_pos

            # 转换坐标
            x1, y1 = self.img.new_xy_to_org_xy((x1, y1))
            x2, y2 = self.img.new_xy_to_org_xy((x2, y2))

            # 调整坐标，确保(x1, y1)为左上角，(x2, y2)为右下角
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])

            # 更新标签信息
            self.cls = self.img.label_save[-1][0]
            new_label = [self.cls, x1, y1, x2, y2]

            self.img.change(-1, new_label)
            self.rect_save_current = [self.len_rect - 1, -1, self.img.basedata[-1]]
            self.is_choose_rect_index = self.len_rect - 1

    # ———————————————————————————————— 槽函数 ————————————————————————————————#

    def hand_button_(self):
        self.hand = True
        self.arrows = False
        self.setCursor(Qt.OpenHandCursor)

    def arrows_button_(self):
        self.hand = False
        self.arrows = True
        self.setCursor(Qt.ArrowCursor)

    # def select_folder(self):
    #     # 选择获取文件夹路径
    #     options = QFileDialog.Options()
    #     options |= QFileDialog.ShowDirsOnly
    #     folder = QFileDialog.getExistingDirectory(self, "Select Folder", "/home", options=options)
    #
    #     if os.path.isdir(folder) and os.path.exists(folder):
    #         img_path = [os.path.join(folder, i) for i in os.listdir(folder)]
    #         img_path = [i for i in img_path if i.endswith('.jpg') or i.endswith('.png') or i.endswith('.jpeg')]
    #         self.reset_thumbnail(img_path)
    #
    #         self.img_list = set(img_path)
    #         self.img_list_only_name = set([os.path.basename(i).split('.')[0] for i in img_path])
    #         if len(self.img_list):
    #             self.is_open_file = False
    #             self.is_open_folder = True

    def select_folder(self):
        # 选择获取文件夹路径
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "./", options=options)

        if os.path.isdir(folder) and os.path.exists(folder):
            # 获取文件夹中所有文件
            all_files = os.listdir(folder)
            # 按文件名排序（关键添加的排序步骤）
            all_files.sort()

            # 筛选图片文件并保持排序
            img_path = [os.path.join(folder, i) for i in all_files
                        if i.endswith(('.jpg', '.png', '.jpeg'))]

            self.reset_thumbnail(img_path)

            self.img_list = set(img_path)
            self.img_list_only_name = set([os.path.basename(i).split('.')[0] for i in img_path])
            if len(self.img_list):
                self.is_open_file = False
                self.is_open_folder = True

    def select_file(self):
        # 选择获取文件路径
        file_path, _ = QFileDialog.getOpenFileNames(None, "选择文件", "", "All Files (*);;Text Files (*.txt)")
        p = []
        for file_path in file_path:
            if os.path.isfile(file_path) and len(file_path) and file_path.endswith('.png') or file_path.endswith('.jpg') \
                    or file_path.endswith('.jpeg'):
                self.is_open_file = True
                self.is_open_folder = False
                p += [file_path]
        self.img_list = set(p)
        self.img_list_only_name = set([os.path.basename(i).split('.')[0] for i in p])
        if len(p):
            self.reset_thumbnail(p)
            self.is_open_file = True
            self.is_open_folder = False

    def readFolderLabel_(self):
        txt_path_ = []
        folder = ''
        if self.is_open_folder:
            options = QFileDialog.Options()
            options |= QFileDialog.ShowDirsOnly
            folder = QFileDialog.getExistingDirectory(self, "Select Folder", "/home", options=options)

            if os.path.isdir(folder) and os.path.exists(folder):
                txt_path = [os.path.join(folder, i) for i in os.listdir(folder)]
                txt_path = [i for i in txt_path if i.endswith('.txt')]
                txt_path_ = set([os.path.basename(i).replace('.txt', '') for i in txt_path])
            else:
                return

        elif self.is_open_file:
            file_path, _ = QFileDialog.getOpenFileNames(None, "选择文件", "", "All Files (*);;Text Files (*.txt)")
            txt_path = []
            txt_path_ = []
            folder = os.path.dirname(file_path[0]) if len(file_path) else None
            for file_path in file_path:
                if os.path.isfile(file_path) and file_path.endswith('.txt'):
                    self.ui.thumbnailWidget.clear()
                    txt_path += [file_path]
                    txt_path_ += [os.path.basename(file_path).replace('.txt', '')]
            if not len(txt_path):
                return

        for i in txt_path_:
            if i not in self.label_list_only_name and i in self.img_list_only_name:
                shutil.copy(os.path.join(folder, i + '.txt'), self.default_save_path)
            elif i in self.label_list_only_name and i in self.img_list_only_name:
                with open(os.path.join(folder, i + '.txt'), 'r', encoding='utf-8') as file:
                    data = file.read()
                with open(os.path.join(self.default_save_path, i + '.txt'), 'r+', encoding='utf-8') as f:
                    data1 = f.read()
                    if len(data1):
                        f.write('\n' + data)
                    else:
                        f.write(data)
        if len(txt_path_):
            self.ui.thumbnailWidget.clear()
            self.thumbnail_widget.init()
            self.thumbnail_widget.screen_list_widget.setCurrentRow(self.thumbnail_widget.index)
            self.thumbnail_widget.screen_label.setText(
                '{} / {}  :  图像: {}'.format(self.thumbnail_widget.index + 1,
                                              len(self.thumbnail_widget.show_list_temp),
                                              self.thumbnail_widget.show_list_temp[self.thumbnail_widget.index]))
            self.thumbnail_widget.screen_label.setAlignment(Qt.AlignCenter)
            self.init(img_path=self.thumbnail_widget.show_list[self.thumbnail_widget.index])

    def imgUp_(self):
        if self.img_is_load:
            if self.wheel_scale <= 6:
                self.wheel_scale = self.wheel_scale * 1.5
            self.img.is_trans = True
            self.move_xy()

    def imgDown_(self):
        if self.img_is_load:
            if self.wheel_scale >= 0.2:
                self.wheel_scale = self.wheel_scale * 0.5
            self.img.is_trans = True
            self.move_xy()

    def resetShowImg_(self):
        if self.img_is_load:
            self.wheel_scale = 1
            self.img.is_trans = True
            self.img.show()
            self.img.label_show()

    def deleteBox_(self, index=False):
        if self.is_choose_rect and self.is_choose_rect_index is not None:
            self.img.pop(index if index else self.is_choose_rect_index)
            self.is_choose_rect_index = None
            self.is_choose_rect = False
            self.hover = False
            self.cross = False
            self.arrows = True
            self.is_hover_move_allow = False
            self.is_update_label = False
            self.is_add_box = False
            self.categoryShowWidget.clear()
            self.boxShowWidget.clear()
            self.len_rect -= 1

            self.move_xy()
            self.img.save()

    # ———————————————————————————————— 快捷键 ————————————————————————————————#
    def handleShortcut1_(self):
        if self.img_is_load:
            if self.thumbnail_widget.index > 0:
                index = self.thumbnail_widget.index - 1
                self.thumbnail_widget.up_dowm(index)
                self.thumbnail_widget.screen_list_widget.setCurrentRow(index)
                self.boxShowWidget.clear()
                self.move_xy()

    def handleShortcut2_(self):
        if self.img_is_load:
            if self.thumbnail_widget.index < len(self.thumbnail_widget.show_list) - 1:
                index = self.thumbnail_widget.index + 1
                self.thumbnail_widget.up_dowm(index)
                self.thumbnail_widget.screen_list_widget.setCurrentRow(index)
                self.boxShowWidget.clear()
                self.move_xy()

    def handleShortcut3_(self):
        if self.img_is_load:
            if self.thumbnail_widget.index > 0:
                index = 0
                self.thumbnail_widget.up_dowm(index)
                self.thumbnail_widget.screen_list_widget.setCurrentRow(index)

    def handleShortcut4_(self):
        if self.img_is_load:
            if self.thumbnail_widget.index < len(self.thumbnail_widget.show_list) - 1:
                index = len(self.thumbnail_widget.show_list) - 1
                self.thumbnail_widget.up_dowm(index)
                self.thumbnail_widget.screen_list_widget.setCurrentRow(index)

    def cls_color_(self):
        if self.is_choose_rect and self.is_choose_rect_index is not None:
            color = QColorDialog.getColor()
            red = color.red()
            green = color.green()
            blue = color.blue()
            color = f'({red}, {green}, {blue}, {50})'
            self.colors[self.cls] = color
            with open((root / 'Detection.yaml'), 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            data['colors'] = self.colors
            with open((root / 'Detection.yaml'), 'w', encoding='utf-8') as file:
                yaml.dump(data, file, allow_unicode=True)
            self.img.show()
            self.img.label_show(self.is_choose_rect_index)

    def renew_cls_(self):
        if not self.img_is_load:
            self.renew_cls_ = modificationCls()
        else:
            QMessageBox.question(None, '无效', '请在图片加载前修改类别',
                                 QMessageBox.Yes | QMessageBox.No)

    def show_box_circle_(self, state):
        if self.img_is_load:
            self.img.show_box_circle = True if state else False
            self.move_xy()

    def show_other_(self, state):
        if self.img_is_load:
            self.img.show_other = True if state else False
            self.move_xy()

    def show_box_fill_(self, state):
        if self.img_is_load:
            self.img.show_box_fill = True if state else False
            self.move_xy()

    def show_box_text_(self, state):
        if self.img_is_load:
            self.img.show_box_text = True if state else False
            self.move_xy()

    def load_model_(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "选择文件", "", "All Files (*);;Text Files (*.txt)")
        if os.path.isfile(file_path) and len(file_path) and file_path.endswith('.pt'):
            res = QMessageBox.question(None, '加载模型', '请耐心等待？',
                                       QMessageBox.Yes | QMessageBox.No)
            if res == QMessageBox.Yes:
                from loadModeThread import loadModel
                os.environ['YOLO_VERBOSE'] = str(False)
                self.load_model_thread = loadModel(self, file_path)
                self.load_model_thread.signal_image_loaded.connect(self.show_prompt)
                self.load_model_thread.start()
    def show_prompt(self, res):
        QMessageBox.question(None, '', res,
                             QMessageBox.Yes | QMessageBox.No)

    def detect_(self):
        if self.img_is_load:
            if self.yolov8_model is None:
                QMessageBox.question(None, '无效', '请先加载模型',
                                     QMessageBox.Yes | QMessageBox.No)
            else:
                text = self.lineEdit.text()
                if text:
                    try:
                        # 转换输入为浮点数并显示
                        floatValue = float(text)
                        if 0 <= floatValue <= 1:
                            self.conf = floatValue
                        else:
                            self.conf = 0.5
                    except ValueError:
                        # 如果输入不是一个小数，弹出错误提示
                        self.conf = 0.5
                result = self.yolov8_model(self.img.org_img, conf=self.conf)[0]
                box = result.boxes.xywhn.tolist()
                cls = result.boxes.cls.tolist()
                for j, i in enumerate(box):
                    self.img.basedata.append([int(cls[j]), *i])
                self.img.save()
                self.img.label_save = []
                self.img.load_new_labels()
                self.move_xy()
                self.boxShowWidget.clear()

    def save_(self):
        # 选择获取文件夹路径
        if self.is_open_file or self.is_open_folder:
            options = QFileDialog.Options()
            options |= QFileDialog.ShowDirsOnly
            folder = QFileDialog.getExistingDirectory(self, "Select Folder", "/home", options=options)
            if os.path.isdir(folder) and os.path.exists(folder):
                for i in self.img_list_only_name:
                    p = os.path.join(self.default_save_path, i + '.txt')
                    if os.path.exists(p) and os.path.getsize(p) > 0:
                        shutil.copy(p, folder)

    # 鼠标放到框上显示框的颜色加深， 不悬浮的时候颜色恢复
    def mouse_hover_display(self):
        if self.img_is_load and self.len_rect and (self.hover or self.cross) and not self.is_choose_rect:
            index_ = self.rect_save_current[0] if self.rect_save_current else None
            self.move_xy(index=index_)

            if not self.is_choose_rect and not self.is_add_box and not self.is_update_label \
                    and self.rect_save_current is not None:
                self.categoryShowWidget.set_rect_cls(self.rect_save_current[2][0])
                self.boxShowWidget.set_rect_box(self.rect_save_current[0])

        elif self.img_is_load and not self.is_choose_rect:
            self.categoryShowWidget.clear()
            self.boxShowWidget.clear()
            self.move_xy()

    # 鼠标点击框则算是选中框， 框加粗，保持常亮， 点击其他框或者点击空白处恢复
    def already_choose_rect_display(self):
        if self.img_is_load and self.arrows and self.is_choose_rect:
            self.move_xy(index=self.is_choose_rect_index)

            if not self.is_choose_rect_over_striking:
                self.categoryShowWidget.set_rect_cls(self.rect_save_current[2][0], 1)
                self.boxShowWidget.set_rect_box(self.rect_save_current[0])

                self.is_choose_rect_over_striking = True
        else:
            self.is_choose_rect_over_striking = False

    def moveImage(self):
        if self.hand and not self.hand_flag:
            self.hand_flag = True
        self.img.is_trans = True
        self.move_xy(self.mouse_pos[0] - self.mouse_save_temp[0], self.mouse_pos[1] - self.mouse_save_temp[1])
        self.mouse_track()
        self.mouse_save_temp = self.mouse_pos
        self.is_choose_rect_index = None
        self.is_choose_rect = False

    def updDatalabel(self, index=None):
        # TODO: 优化
        new_label = self.computer_new_label()

        if self.is_first_update_label:
            self.is_choose_rect = True

            self.categoryShowWidget.set_rect_cls(self.rect_save_current[2][0], 1)
            self.boxShowWidget.set_rect_box(self.rect_save_current[0])
            self.is_first_update_label = False

        self.rect_save_current[-1] = new_label  # 框索引, label
        self.rect_save = self.rect_save_current

        self.img.change(self.rect_save_current[0], new_label)

        self.is_choose_rect = True
        self.is_choose_rect_index = self.rect_save_current[0]

    def addBox(self):
        if self.pos_in_org(self.mouse_pos):
            self.add_box()
            self.rect_save_current = [len(self.img.label_save) - 1, -1, self.img.label_save[-1]]
            self.is_choose_rect = True
            self.is_choose_rect_index = len(self.img.label_save) - 1

    def reset_thumbnail(self, img_list):
        self.label.clear()
        self.ui.thumbnailWidget.clear()
        self.thumbnail_widget = thumbnailApp(self.ui.thumbnailWidget, self.current_label_name_show, self, img_list,
                                             self.label_list)
        self.thumbnail_widget.screen_list_widget.setDragDropMode(QListWidget.NoDragDrop)

        self.is_open_file = False
        self.is_choose_rect_index = None
        self.is_update_label = False
        self.is_add_box = False

        if self.img_is_load:
            self.len_rect = len(self.img.label_save)
            self.thumbnail_widget.screen_list_widget.setCurrentRow(0)
            self.thumbnail_widget.screen_label.setText(
                '{} / {}  :  图像: {}'.format(self.thumbnail_widget.index + 1,
                                              len(self.thumbnail_widget.show_list_temp),
                                              self.thumbnail_widget.show_list_temp[0]))
            self.thumbnail_widget.screen_label.setAlignment(Qt.AlignCenter)
