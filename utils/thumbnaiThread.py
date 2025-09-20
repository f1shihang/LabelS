from PyQt5 import QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap,  QImage

from common_fun import read_img, resize_img


class ImageLoader(QThread):
    signal_image_loaded = pyqtSignal(QPixmap, int)

    def __init__(self, image_paths):
        super().__init__()
        self.image_paths = image_paths

    def run(self):
        for index, path in enumerate(self.image_paths):
            pixmap = self.load_image(path)
            self.signal_image_loaded.emit(pixmap, index)

    def load_image(self, file):
        pixmap = read_img(file)
        s = 80
        temp = resize_img(pixmap, (s, s))

        pixmap = QPixmap.fromImage(QtGui.QImage(temp.data, s,
                                                s, s * 3,
                                                QImage.Format_RGB888).rgbSwapped())  # 加载图像
        return pixmap
