import os
from PIL import Image


def convert_bmp_to_png(folder_path):
    """
    将指定文件夹中的所有.bmp文件转换为.png格式

    参数:
        folder_path: 包含.bmp文件的文件夹路径
    """
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在")
        return

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否为.bmp格式
        if filename.lower().endswith('.jpg'):
            # 构建完整的文件路径
            bmp_path = os.path.join(folder_path, filename)

            # 构建输出的png文件名（替换扩展名）
            png_filename = os.path.splitext(filename)[0] + '.png'
            png_path = os.path.join(folder_path, png_filename)

            try:
                # 打开bmp文件并保存为png
                with Image.open(bmp_path) as img:
                    # 确保图像以RGBA模式保存，避免透明通道问题
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new(img.mode[:-1], img.size, (255, 255, 255))
                        background.paste(img, img.split()[-1])
                        img = background
                    img.save(png_path, 'PNG')
                print(f"已转换: {filename} -> {png_filename}")

                # 如果需要删除原bmp文件，可以取消下面这行的注释
                # os.remove(bmp_path)
                # print(f"已删除原文件: {filename}")

            except Exception as e:
                print(f"转换 {filename} 时出错: {str(e)}")


if __name__ == "__main__":
    # 在这里指定要处理的文件夹路径
    target_folder = "D:\Data_Label\JK_YI_2025_8_11\images"  # 可以替换为实际的文件夹路径，如 "C:/images"

    # 调用转换函数
    convert_bmp_to_png(target_folder)
    print("转换完成！")
