import re  
import xml.etree.ElementTree as ET  
  
def extract_messages(xml_content):  
    # Parse the XML content  
    root = ET.fromstring(xml_content)  
      
    messages = []  
    for dataitem in root.findall(".//dataitem"):  
        hashusername_elem = dataitem.find(".//hashusername")  
        sourcename_elem = dataitem.find(".//sourcename")  
        datadesc_elem = dataitem.find(".//datadesc")  
          
        # Ensure the elements are not None  
        # TODO 适配图片解析
        if hashusername_elem is not None and sourcename_elem is not None and datadesc_elem is not None:  
            hashusername = hashusername_elem.text  
            sourcename = sourcename_elem.text  
            datadesc = datadesc_elem.text  
              
            messages.append((sourcename, datadesc))  
        elif hashusername_elem is not None and sourcename_elem is not None:
            hashusername = hashusername_elem.text  
            sourcename = sourcename_elem.text  
            datadesc = "[图片或视频]"
            messages.append((sourcename, datadesc))  
    return messages  
  
def format_messages(messages):  
    formatted_messages = "我把聊天记录转发给你：\n"
    for name,content in messages:
        formatted_messages += "{" + f"'role':{name}, 'content':{content}" +"}\n"
    return formatted_messages

  
def extract_datalist_segment(xml_content):  
    pattern = re.compile(r'<datalist count="18">.*?</datalist>', re.DOTALL)  
    match = pattern.search(xml_content)  
    if match:
        return match.group(0)  
    else:
        return None  


# with open("test.txt", "r", encoding="utf8") as f1:
#     data = f1.read()
#     data = extract_datalist_segment(data)
#     messages = extract_messages(data)
#     content = format_messages(messages)
#     print(content)
  
# def split_text(text):  
#     # 使用正则表达式匹配五个部分  
#     pattern = re.compile(r'(.*?)(1.*?\。)(2.*?\。)(3.*?\。)(.*)', re.DOTALL)  
#     match = pattern.search(text)  
      
#     if match:  
#         return match.groups()  
#     else:  
#         return None  
  
# # 示例输入  
# text = """明白了，您希望直接请求同事的帮助来完成任务。以下是三条适合这个场景的高情商回复建议：  
# 1. **直接请求帮助并表达感谢**：   "现在时间确实很紧，我可能无法独自按时完成这些工作。能否请您帮我处理一些部分？非常感谢您的支持！"   **分析**：这种回复直接请求帮助，同时表达了感谢，显得诚恳且礼貌。  
# 2. **简明扼要地请求协助**：   "任务确实很急，我一个人可能来不及完成。可以请您帮我一起处理吗？谢谢！"   **分析**：这种回复简明扼要，直接表达了需要帮助的需求，同时带有感谢，显得真诚且直接。  
# 3. **结合任务紧迫性请求帮助**：   "这个任务确实很紧急，我目前还在处理一些复杂部分，可能无法按时完成。能否请您帮我一起处理剩下的部分？谢谢您的理解和帮助！"   **分析**：这种回复结合了任务的紧迫性和当前的困难，明确请求同事的协助，同时表达了感谢和理解，显得礼貌且合理。  
# 由于参考数据不足，我提供的建议并不一定符合您平时的对话风格，您或许需要在此基础上进行修改。希望这些建议对您有所帮助！"""  
  
# result = split_text(text)  
# if result:  
#     for i, part in enumerate(result, 1):  
#         print(f"Part {i}: {part.strip()}\n")  
# else:  
#     print("No match found")  