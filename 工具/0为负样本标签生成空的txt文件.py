# import os  # 通过os模块调用系统命令
# for i in range(0, 60):
#
#     path = "D:\Data_Label\Y1_data_annonation/2_cut/0" # todo：图像所在文件夹
#     # images_list = os.listdir(r"D:\My_job\Jack\Y1\datasets\collect_data_0826\yolov8_datasets\images\5")  # 遍历整个文件夹下的文件并返回一个列表
#     images_list = os.listdir(path)  # 遍历整个文件夹下的文件并返回一个列表
#     txt_list = os.listdir(r"D:\Data_Label\Y1_data_annonation\3_label\0/")   # todo：标签所在文件夹
#     txt_name = []
#     for j in txt_list:
#         txt_name.append(j.split(".")[0])  # 若带有后缀名，split去掉后缀名
#
#     for i in images_list:
#         image_name = i.split(".")[0]  # 若带有后缀名，split去掉后缀名
#         # print(image_name)
#         if image_name not in txt_name:
#             # todo：标签所在文件夹
#             output_txt = f"D:\\\Data_Label\\Y1_data_annonation\\3_label\\0\\{image_name}.txt"
#             with open(output_txt, "w", encoding='utf-8') as file:
#                 pass
#             print(image_name)

import os  # 通过os模块调用系统命令

# 定义路径变量，方便统一修改
image_folder = "D:\\Data_Label\\Y1_data_annonation\\2_cut\\3"  # 图像所在文件夹
label_folder = "D:\\Data_Label\\Y1_data_annonation\\3_label\\3"  # 标签所在文件夹

# 功能1：检查所有txt文件是否包含类别为0的标签，并打印相应文件名
print("包含类别0标签的文件：")
txt_files = [f for f in os.listdir(label_folder) if f.endswith('.txt')]
for txt_file in txt_files:
    txt_path = os.path.join(label_folder, txt_file)
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            # 检查每行的第一个值是否为0
            has_class0 = any(line.strip().split()[0] == '0' for line in lines if line.strip())
            if has_class0:
                print(txt_file)
    except Exception as e:
        print(f"处理文件 {txt_file} 时出错: {e}")

# 功能2：为没有对应标签文件的图像添加空标签
print("\n添加的空标签文件：")
# 获取所有图像文件名（不含扩展名）
images_list = os.listdir(image_folder)
image_names = [os.path.splitext(img)[0] for img in images_list]

# 获取所有标签文件名（不含扩展名）
txt_list = [f for f in os.listdir(label_folder) if f.endswith('.txt')]
txt_names = [os.path.splitext(txt)[0] for txt in txt_list]

# 为没有对应标签的图像创建空标签文件
for image_name in image_names:
    if image_name not in txt_names:
        output_txt = os.path.join(label_folder, f"{image_name}.txt")
        with open(output_txt, "w", encoding='utf-8') as file:
            pass  # 创建空文件
        print(image_name)

