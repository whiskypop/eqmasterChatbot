"""
使用前先安装 pip install python-docx --upgrade

python版本为3.10

使用方法为  `python convert_docs_to_txt.py doc来源文件夹 txt目标文件夹`
"""
import os
import sys
from docx import Document

input_directory = './docs'
output_directory = './txt'
import os
import sys
from docx import Document

def convert_docs_to_txt(source_folder, destination_folder):
    # 检查源文件夹是否存在
    if not os.path.exists(source_folder):
        print("源文件夹不存在。请提供有效的源文件夹路径。")
        exit()

    # 创建保存 TXT 文件的目标文件夹
    os.makedirs(destination_folder, exist_ok=True)

    # 遍历源文件夹中的所有 DOC 文件
    for file_name in os.listdir(source_folder):
        if file_name.endswith(".docx"):  # 只处理 .docx 文件
            doc_file = os.path.join(source_folder, file_name)
            txt_file = os.path.join(
                destination_folder, os.path.splitext(file_name)[0] + ".txt"
            )

            # 使用 python-docx 库打开 DOCX 文件
            document = Document(doc_file)

            # 逐段写入 TXT 文件
            with open(txt_file, "w", encoding="utf-8") as txt:
                for paragraph in document.paragraphs:
                    txt.write(paragraph.text)
                    txt.write("\n")

            print(f"已将 {file_name} 转换为 {os.path.basename(txt_file)}")

    print("转换完成！")


if __name__ == "__main__":
   
    convert_docs_to_txt(input_directory, output_directory)
