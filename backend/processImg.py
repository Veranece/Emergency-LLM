import os
from paddleocr import PaddleOCR

# def prosess(filePath)
#     # 输入图片目录
#     img_dir = "/home/liziwei/Emergency-LLM/backend/resource/data/应急管理——安徽省应急管理厅/10-28 135205/图片链接"

#     # 初始化 OCR（中文）
#     ocr = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=True)  # 如果有GPU，use_gpu=True

#     # 遍历图片
#     for filename in os.listdir(img_dir):
#         if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
#             img_path = os.path.join(img_dir, filename)
#             print(f"正在识别：{img_path}")

#             # 执行 OCR
#             result = ocr.ocr(img_path, cls=True)

#             # 生成同名 txt 文件
#             txt_file = os.path.splitext(img_path)[0] + ".txt"

#             with open(txt_file, "w", encoding="utf-8") as f:
#                 if result:
#                     for line in result[0]:
#                         text = line[1][0]
#                         f.write(text + "\n")

#             print(f"已生成：{txt_file}")

#     print("OCR 批量处理完成！")
