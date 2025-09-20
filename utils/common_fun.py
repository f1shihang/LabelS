import cv2
import numpy as np
from PIL import Image
from pathlib import Path

root = Path(__file__).parent


def distance(x1y1, x2y2):
    return ((x1y1[0] - x2y2[0]) ** 2 + (x1y1[1] - x2y2[1]) ** 2) ** 0.5


def read_img(img_path):
    # 使用Pillow打开图像, 防止出现中文路径错误
    pil_image = Image.open(img_path)

    # 将Pillow图像转换为NumPy数组
    image_np = np.array(pil_image)

    # 将NumPy数组转换为OpenCV格式的图像
    opencv_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    return opencv_image


def resize_img(img: np.ndarray, resize_img):
    """
    调整图像大小，填充黑色边框不改变图像的原始比例，缩放为窗口大小的scale倍
    """

    h, w = resize_img

    # 把图像按照原始的比例显示在Qt_label中
    scale_h = img.shape[0] / h
    scale_w = img.shape[1] / w

    scale_ = max(scale_w, scale_h)
    # 双线性插值
    zoom_img = cv2.resize(img,
                          (int(img.shape[1] / scale_), int(img.shape[0] / scale_))
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
