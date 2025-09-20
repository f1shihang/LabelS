import os
import random


def split_train_val(image_folder, train_ratio=0.8):
    """
    将指定文件夹中的图片数据划分成训练集和测试集，并生成Yolo所需的train.txt和val.txt
    参数:
        image_folder: 包含图片文件的文件夹路径
        train_ratio: 训练集占比，默认0.8
    """
    # 支持的图片文件扩展名
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    # image_extensions = ('.txt')

    # 获取文件夹中所有图片文件的路径
    image_paths = []
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(image_extensions):
            # 获取图片的绝对路径
            img_path = os.path.abspath(os.path.join(image_folder, filename))
            image_paths.append(img_path)

    if not image_paths:
        print(f"错误: 在文件夹 '{image_folder}' 中未找到任何图片文件")
        return

    # 打乱图片顺序
    random.shuffle(image_paths)

    # 计算划分点
    split_index = int(len(image_paths) * train_ratio)

    # 划分训练集和测试集
    train_images = image_paths[:split_index]
    val_images = image_paths[split_index:]

    # 生成train.txt
    with open('train.txt', 'w', encoding='utf-8') as f:
        for path in train_images:
            f.write(f"{path}\n")

    # 生成val.txt
    with open('val.txt', 'w', encoding='utf-8') as f:
        for path in val_images:
            f.write(f"{path}\n")

    print(f"数据划分完成！")
    print(f"总图片数量: {len(image_paths)}")
    print(f"训练集数量: {len(train_images)}")
    print(f"测试集数量: {len(val_images)}")
    print(f"train.txt 和 val.txt 已生成在当前目录")


if __name__ == "__main__":
    # 指定图片文件夹路径
    image_folder = "D:\Data_Label\Y1_data_annonation/biaozhu_data\images"  # 替换为你的图片文件夹路径
    # txt_folder = "D:\My_job\Jack\Y1\datasets\collect_data_0826_yolov8\labels"  # 替换为你的图片文件夹路径

    # 调用函数进行划分，训练集占比0.8，测试集占比0.2
    split_train_val(image_folder, train_ratio=0.8)
