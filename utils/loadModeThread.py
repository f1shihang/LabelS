from PyQt5.QtCore import QThread, pyqtSignal
from common_fun import root
root = root.parent


class loadModel(QThread):
    signal_image_loaded = pyqtSignal(str)

    def __init__(self, parent, file_path):
        super().__init__()
        self.parent = parent
        self.file_path = file_path

    def run(self):
        from ultralytics import YOLO
        self.parent.yolov8_model = YOLO(self.file_path)
        self.parent.yolov8_model(str(root / "utils/material/warm_up.png"))  # 预热
        self.signal_image_loaded.emit("模型加载完成")


