import os.path

import cv2
import math
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QPen

from common_fun import read_img
from DataApp import DataApp


class Image(QMainWindow):

    def __init__(self, screen_label, img_path: str, label_path, mod=0, parent=None):
        super().__init__()
        if not label_path:
            label_path = str(parent.default_save_path) + '/' + os.path.basename(img_path).split('.')[0] + '.txt'
            open(label_path, 'w').close()
        self.basedata = DataApp(label_path)  # 图片对应的标签数据
        self.img_path = img_path
        self.label_path = label_path
        self.mod = mod  # 0: detect 1: segment 2: pose 3: OBB
        self.org_img = read_img(img_path)  # 原始图像
        self.screen_label = screen_label  # 显示图像的label
        self.label_height = self.screen_label.size().height()  # label的高度
        self.label_width = self.screen_label.size().width()  # label的宽度

        self.org_width = self.org_img.shape[1]  # 原始图像的宽度
        self.org_height = self.org_img.shape[0]  # 原始图像的高度
        self.wheel_scale = 1  # 滚轮放大的倍数, 当前图片相对于label尺寸的缩放倍数
        self.center = None  # 当前图像的中心在label中的坐标
        self.label_save = list()  # 记录存储的label信息(真实坐标，不是base_data中的相对坐标，而是图像坐标）
        self.parent = parent
        self.is_trans = False
        self.only_index = False
        self.temp_img = None

        self.show_box_circle = True  # 是否显示矩形框的9个点
        self.show_other = True  # 是否显示其他的标签, True就是添加框的时候不显示其他的框
        self.show_box_fill = True  # 是否显示矩形框的填充
        self.show_box_text = True  # 是否显示矩形框的文字
        self.init()

    def init(self):
        self.center = (self.label_width // 2, self.label_height // 2)
        self.load_new_labels()
        self.show(scale=1)
        self.label_show()

    def resize_image(self, scale=1):
        """
        调整图像大小，填充黑色边框不改变图像的原始比例，缩放为窗口大小的scale倍
        """

        h, w = int(self.label_height * scale), int(self.label_width * scale)

        # 把图像按照原始的比例显示在Qt_label中
        scale_h = self.org_img.shape[0] / h
        scale_w = self.org_img.shape[1] / w

        scale_ = max(scale_w, scale_h)
        # 双线性插值
        zoom_img = cv2.resize(self.org_img,
                              (int(self.org_img.shape[1] / scale_), int(self.org_img.shape[0] / scale_))
                              , interpolation=cv2.INTER_LINEAR)
        back = np.zeros((h, w, 3), dtype=np.uint8)

        if scale_h >= scale_w:
            # 水平填充
            x1 = (back.shape[1] - zoom_img.shape[1]) // 2
            x2 = zoom_img.shape[1] + x1
            back[0:zoom_img.shape[0], x1: x2, :] = \
                zoom_img
        else:
            # 竖直填充
            y1 = (back.shape[0] - zoom_img.shape[0]) // 2
            y2 = zoom_img.shape[0] + y1
            back[y1:y2, 0:zoom_img.shape[1], :] = zoom_img
        zoom_img = back.astype(zoom_img.dtype)
        return cv2.resize(zoom_img, (w, h), interpolation=cv2.INTER_LINEAR)

    def img_transform(self, x, y, scale):
        """
        计算图像的缩放和平移，返回缩放后的图像
        """

        # 保存当前图像的中心在qt label中的坐标，以及当前的缩放倍数(相对于pyqt的label的尺寸)
        self.center = (x, y)
        self.wheel_scale = scale

        new_img = self.resize_image(scale)
        temp = np.zeros((self.label_height, self.label_width, 3), dtype=np.uint8)
        h, w, _ = new_img.shape
        x1, y1 = int(x - w / 2), int(y - h / 2)
        x2, y2 = int(x + w / 2), int(y + h / 2)
        x1, y1 = max(x1, 0), max(y1, 0)
        x2, y2 = min(x2, self.label_width), min(y2, self.label_height)
        temp[y1: y2, x1: x2, :] = new_img[y1 - y + (h + 1) // 2: y2 - y + (h + 1) // 2,
                                  x1 - x + (w + 1) // 2: x2 - x + (w + 1) // 2, :]

        return temp

    def show(self, x=None, y=None, scale=1.0):
        #  把图像显示在对应的qt label上面 但不显示其他信息

        if x is None or y is None:
            #  如果没有指定显示的位置，则默认显示在label的中心
            x, y = self.label_width // 2, self.label_height // 2

        if self.is_trans or self.temp_img is None:
            temp = self.img_transform(x, y, scale)
            self.temp_img = QPixmap.fromImage(QtGui.QImage(temp.data, self.label_width,
                                                           self.label_height, self.label_width * 3,
                                                           QImage.Format_RGB888).rgbSwapped())  # 加载图像
            self.is_trans = False
        self.screen_label.setPixmap(self.temp_img)

    def add_rect(self, x1y1, x2y2, text, box_color, circle_color, text_color, box_thickness=3, circle_radius=1,
                 text_size=8, is_show_nine_circle=True, is_over_striking=False) -> None:
        if is_over_striking:
            box_thickness = 2 * box_thickness
            box_color = list(box_color)
            box_color[-1] = 130

        pixmap = self.screen_label.pixmap()
        painter = QPainter(pixmap)

        # 绘制矩形
        pen = QPen(QColor(*box_color[0:3], 220), 1.5, Qt.SolidLine)
        painter.setPen(pen)
        brush_color = QColor(*box_color)

        painter.setBrush(brush_color)

        if not self.show_box_fill:
            painter.setBrush(Qt.NoBrush)
        rect = QRect(QPoint(*x1y1), QPoint(*x2y2))
        painter.drawRect(rect)

        if is_show_nine_circle and self.show_box_circle:
            # 绘制点 使用setPen方法设置点的大小
            painter.setPen(QColor(*circle_color))  # 设置画笔颜色
            pen = painter.pen()
            circle_radius = circle_radius * self.wheel_scale if circle_radius * self.wheel_scale ** 2 < 1 else circle_radius
            pen.setWidth(int(circle_radius))
            painter.setPen(pen)
            for i in self.circle_nine(*x1y1, *x2y2):
                painter.drawPoint(QPoint(*i))

        font_size = int(9 * self.wheel_scale) if 9 * self.wheel_scale ** 2 < 9 else 9
        font = QFont("Arial", font_size, QFont.Bold)
        painter.setFont(font)
        text_color = QColor(255, 255, 255)  # 白色
        painter.setPen(text_color)
        if self.show_box_text:
            painter.drawText(rect.topLeft() - QPoint(0, box_thickness + 5), text)

        painter.end()

        # 将绘制完成的QPixmap重新设置给QLabel
        self.screen_label.setPixmap(pixmap)

    def add_text(self, x1y1, text, text_color, text_size=12):
        # 图像上绘制文字
        pixmap = self.screen_label.pixmap()
        painter = QPainter(pixmap)

        painter.setPen(QColor(*text_color))  # 设置画笔颜色为黑色

        # 使用drawText方法显示文本
        font = QFont("Arial", text_size)  # 设置字体和字号
        painter.setFont(font)
        painter.drawText(QPoint(*x1y1), text)

        painter.end()

        # 将绘制完成的QPixmap重新设置给QLabel
        self.screen_label.setPixmap(pixmap)

    def add_circle(self, x1y1, circle_color, circle_radius=5, is_ball=False):
        # 图像上绘制圆形
        pixmap = self.screen_label.pixmap()
        painter = QPainter(pixmap)

        if is_ball:
            # 绘制圆形, 实心
            painter.setBrush(QColor(*circle_color))
            painter.drawEllipse(QPoint(*x1y1), circle_radius, circle_radius)
        else:
            # 绘制方点 使用setPen方法设置点的大小
            painter.setPen(QColor(*circle_color))  # 设置画笔颜色为黑色
            pen = painter.pen()
            pen.setWidth(circle_radius)
            painter.setPen(pen)
            painter.drawPoint(QPoint(*x1y1))

        painter.end()

        # 将绘制完成的QPixmap重新设置给QLabel
        self.screen_label.setPixmap(pixmap)

    def add_line(self, x1y1, x2y2, line_color, line_thickness=3):
        # 图像上绘制线
        pixmap = self.screen_label.pixmap()
        painter = QPainter(pixmap)

        # 绘制线
        painter.setPen(QColor(*line_color))
        pen = painter.pen()
        pen.setWidth(line_thickness)
        painter.setPen(pen)
        painter.drawLine(QPoint(*x1y1), QPoint(*x2y2))

        painter.end()

        # 将绘制完成的QPixmap重新设置给QLabel
        self.screen_label.setPixmap(pixmap)

    def load_new_labels(self):
        temp = []
        # 从YOLO_data中加载标签, 从相对坐标转为绝对坐标（但不是qt label上的坐标）
        for j, detect_label in enumerate(self.basedata):
            cls = int(detect_label[0])
            point = detect_label[1:]

            x, y, w, h = (point[0] - point[2] / 2) * self.org_width, \
                ((point[1] - point[3] / 2) * self.org_height), \
                         point[2] * self.org_width, point[3] * self.org_height

            x1, y1, x2, y2 = x, y, x + w, y + h
            temp.append([cls, x1, y1, x2, y2])
        self.label_save = temp
        self.parent.len_rect = len(self.label_save)

    def label_show(self, index=None):
        if self.only_index and index is not None and self.show_other:
            label = self.label_save[index]
            cls, x1, y1, x2, y2 = label

            x1, y1 = self.org_xy_to_new_xy((x1, y1))  # 坐标变换, 从原始坐标转换为图像坐标
            x2, y2 = self.org_xy_to_new_xy((x2, y2))
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cls = int(cls)

            box_cls = self.parent.names[cls] if self.parent and self.parent.names.get(cls) else str(cls)

            box_color = eval(self.parent.colors[cls]) if self.parent and self.parent.colors.get(cls) else (
                0, 255, 0, 50)

            # self.add_rect((x1, y1), (x2, y2), str(
            #     len(self.label_save) - 1 if index == -1 else index) + ':类别 :' + box_cls,
            #               box_color, (255, 0, 0, 200), (255, 0, 0, 200), 2,
            #               circle_radius=8, is_over_striking=True)

            self.add_rect((x1, y1), (x2, y2), box_cls,
                          box_color, (255, 0, 0, 200), (255, 0, 0, 200), 2,
                          circle_radius=8, is_over_striking=True)
            return

        if self.mod == 0:
            # 普通检测模式
            index = index if index != -1 or None or False else len(self.label_save) - 1
            # 减少循环内的重复计算和方法调用
            label_count = len(self.label_save)
            parent_names = self.parent.names if self.parent else None
            parent_colors = self.parent.colors if self.parent else None
            # 预先定义的静态值
            red_color = (255, 0, 0, 200)
            circle_radius_val = 8

            for c, label in enumerate(self.label_save[::-1]):
                cls, x1, y1, x2, y2 = label
                # 将坐标转换和类型转换结合
                x1, y1 = map(int, self.org_xy_to_new_xy((x1, y1)))
                x2, y2 = map(int, self.org_xy_to_new_xy((x2, y2)))
                cls = int(cls)

                # 缓存方法和属性，避免点查找
                box_cls = parent_names[cls] if parent_names and cls in parent_names else str(cls)
                box_color = eval(parent_colors[cls]) if parent_colors and cls in parent_colors else (0, 255, 0, 0)

                # 字符串操作优化
                # box_label = f'{label_count - c - 1}:类别 :{box_cls}'
                box_label = f'{box_cls}'

                # 避免不必要的条件判断
                is_over_striking = index == label_count - c - 1
                border_color = red_color if is_over_striking else box_color
                border_thickness = 2 if is_over_striking else 1

                self.add_rect((x1, y1), (x2, y2), box_label, box_color, border_color, red_color, border_thickness,
                              circle_radius=circle_radius_val, is_over_striking=is_over_striking)

    def new_xy_to_org_xy(self, xy):
        """
        坐标变换 将图像坐标转换为真实坐标
        """

        x, y = xy
        x = x - (self.center[0] - self.label_width / 2)
        y = y - (self.center[1] - self.label_height / 2)

        x = (x - self.label_width / 2) / self.wheel_scale + self.label_width / 2
        y = (y - self.label_height / 2) / self.wheel_scale + self.label_height / 2

        scale_x = self.org_img.shape[1] / self.label_width
        scale_y = self.org_img.shape[0] / self.label_height

        if scale_x > scale_y:
            scale = 1 / scale_x
            y = y - (self.label_height - self.org_img.shape[0] * scale) / 2
        else:
            scale = 1 / scale_y
            x = x - (self.label_width - self.org_img.shape[1] * scale) / 2

        x, y = x / scale, y / scale

        return x, y

    def org_xy_to_new_xy(self, xy):
        """
        坐标变换 将真实坐标转换为图像坐标
        """

        x, y = xy
        scale_x = self.org_width / self.label_width
        scale_y = self.org_height / self.label_height

        if scale_x > scale_y:
            # 说明是竖直填充
            scale = 1 / scale_x
            x, y = x * scale, y * scale

            y = (self.label_height - self.org_img.shape[0] * scale) / 2 + y
        else:
            # 说明是水平填充
            scale = 1 / scale_y
            x, y = x * scale, y * scale

            x = (self.label_width - self.org_img.shape[1] * scale) / 2 + x

        x = (x - self.label_width / 2) * self.wheel_scale + self.label_width / 2
        y = (y - self.label_height / 2) * self.wheel_scale + self.label_height / 2

        x = self.center[0] - self.label_width / 2 + x
        y = self.center[1] - self.label_height / 2 + y

        return x, y

    @staticmethod
    def circle_nine(x1, y1, x2, y2):
        """
        给定矩形的左上角和右下角坐标，返回矩形上的9个点的坐标
        """
        return [(x1, y1), (x2, y1), (x1, y2), (x2, y2),
                (x1, y1 + (y2 - y1) // 2),
                (x1 + (x2 - x1) // 2, y2),
                (x2, y2 - (y2 - y1) // 2),
                (x2 - (x2 - x1) // 2, y1),
                (int(x1 + (x2 - x1) / 2), int(y1 + (y2 - y1) / 2))]

    def is_in_circle(self, x, y, circle_distance=25):
        if self.parent.is_hover_move_allow and self.parent.is_choose_rect_index is not None:
            circle = self.label_save[self.parent.is_choose_rect_index]
            circle1 = self.org_xy_to_new_xy(circle[1:3])
            circle2 = self.org_xy_to_new_xy(circle[3:5])
            for k, point in enumerate(self.circle_nine(circle1[0], circle1[1], circle2[0], circle2[1])):
                if math.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2) < circle_distance:
                    return [True, self.parent.is_choose_rect_index, k]

            return [False, -1, -1]
        # 判断鼠标是否落入了检测框的某个点
        for i, circle in enumerate(self.label_save):
            circle1 = self.org_xy_to_new_xy(circle[1:3])
            circle2 = self.org_xy_to_new_xy(circle[3:5])
            for k, point in enumerate(self.circle_nine(circle1[0], circle1[1], circle2[0], circle2[1])):
                if math.sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2) < circle_distance:
                    return [True, i, k]
        return [False, -1, -1]

    def is_in_rect(self, x, y):
        if self.parent.is_hover_move_allow and self.parent.is_choose_rect_index is not None:
            rect = self.label_save[self.parent.is_choose_rect_index]
            x1y1 = self.org_xy_to_new_xy(rect[1:3])
            x2y2 = self.org_xy_to_new_xy(rect[3:5])
            if x1y1[0] < x < x2y2[0] and x1y1[1] < y < x2y2[1]:
                return [True, self.parent.is_choose_rect_index, -1]
            else:
                return [False, -1, -1]
        # 判断鼠标是否落入了矩形框中
        for i, rect in enumerate(self.label_save):
            x1y1 = self.org_xy_to_new_xy(rect[1:3])
            x2y2 = self.org_xy_to_new_xy(rect[3:5])
            if x1y1[0] < x < x2y2[0] and x1y1[1] < y < x2y2[1]:
                return [True, i, -1]
        return [False, -1, -1]

    def pop(self, index):
        # 删除标签
        self.label_save.pop(index)
        self.basedata.pop(index)
        self.show(scale=self.wheel_scale)
        self.label_show()

    def append(self, label):
        # 添加标签
        if self.mod == 0:
            #  label为相对qt label的坐标
            cls, x1, y1, x2, y2 = label
            x1, y1 = self.new_xy_to_org_xy((x1, y1))  # 坐标变换, 从图像坐标转换为原始坐标
            x2, y2 = self.new_xy_to_org_xy((x2, y2))

            self.label_save.append((cls, x1, y1, x2, y2))

            x, y, w, h = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
            x, y, w, h = x / self.org_width, y / self.org_height, w / self.org_width, h / self.org_height
            self.basedata.append([cls, x, y, w, h])
            self.show(*self.center, scale=self.wheel_scale)
            self.label_show()

    def insert(self, index, label):
        # 添加标签
        if self.mod == 0:
            #  label为相对qt label的坐标
            cls, x1, y1, x2, y2 = label
            x1, y1 = self.new_xy_to_org_xy((x1, y1))  # 坐标变换, 从图像坐标转换为原始坐标
            x2, y2 = self.new_xy_to_org_xy((x2, y2))

            self.label_save.insert(index, [cls, x1, y1, x2, y2])

            x, y, w, h = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
            x, y, w, h = x / self.org_width, y / self.org_height, w / self.org_width, h / self.org_height

            self.basedata.insert(index, [cls, x, y, w, h])
            self.show(*self.center, scale=self.wheel_scale)
            self.label_show()

    def change(self, index, label):
        # 修改标签
        if self.mod == 0:
            self.label_save[index] = label
            #  label为相对qt label的坐标
            cls, x1, y1, x2, y2 = label
            x, y, w, h = (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1
            x, y, w, h = x / self.org_width, y / self.org_height, w / self.org_width, h / self.org_height
            self.basedata[index] = [cls, x, y, w, h]
            self.show(*self.center, scale=self.wheel_scale)
            self.label_show(index)

    def save(self):
        self.basedata.save()

    def __getitem__(self, item):
        return [self.label_save[item], self.basedata[item]]

    def __len__(self):
        return len(self.label_save)
