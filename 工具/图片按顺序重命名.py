import os


def rename_images_in_folder(folder_path):
    # 获取文件夹中的所有文件
    files = os.listdir(folder_path)

    # 过滤出所有图片文件（这里只考虑扩展名为 .jpg, .jpeg, .png, .bmp 的图片）
    image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

    # 按文件名排序，确保重命名是有序的
    image_files.sort()

    # 循环遍历所有图片文件，并重新命名
    for index, old_name in enumerate(image_files):
        # 构造新的文件名
        new_name = f"{index + 1:04d}.png"  # 格式化为 4 位数，保留前导零
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)

        # 重命名文件
        os.rename(old_path, new_path)
        print(f"Renamed: {old_name} -> {new_name}")

# 输入目标文件夹路径
folder_path = input("请输入文件夹路径: ")

# 调用函数进行图片重命名
rename_images_in_folder(folder_path)
