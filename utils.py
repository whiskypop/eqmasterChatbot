from ebooklib import epub  
import ebooklib
from bs4 import BeautifulSoup  

def epub_to_txt(epub_path, txt_path):  
    # 打开EPUB文件  
    book = epub.read_epub(epub_path)  

    # 用于存储EPUB内容的列表  
    text_content = []  

    # 遍历所有的文档内容  
    for item in book.get_items():  
        if item.get_type() == ebooklib.ITEM_DOCUMENT:  
            # 使用BeautifulSoup解析HTML内容  
            soup = BeautifulSoup(item.get_content(), 'html.parser')  
            # 获取文本内容并添加到列表中
            content = [i.strip() for i in soup.get_text().split("\n\n") if len(i.strip()) != 0]
            if soup.get_text().strip():
                text_content += content

    # 将所有文本内容连接成一个字符串  
    full_text = '\n\n'.join(text_content)  

    # 将文本内容写入TXT文件  
    with open(txt_path, 'w', encoding='utf-8') as txt_file:  
        txt_file.write(full_text)  

# 调用函数进行转换  
epub_to_txt('data.epub', 'data.txt')  