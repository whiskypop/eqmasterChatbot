# from BotServer.MsgHandleServer.FriendMsgHandle import FriendMsgHandle
from BotServer.MsgHandleServer.RoomMsgHandle import RoomMsgHandle
from PushServer.PushMainServer import PushMainServer
from DbServer.DbInitServer import DbInitServer
import FileCache.FileCacheServer as Fcs
from threading import Thread
from OutPut.outPut import op
from cprint import cprint
from queue import Empty
from wcferry import Wcf
import requests
from typing import Optional
from pydantic import BaseModel
import re
import xml.etree.ElementTree as ET
import html
import json
from typing import List, Dict, Any

# 定义数据模型，用于发送聊天记录到 API
class ChatCreate(BaseModel):
    personal_name: str
    name: Optional[str] = None
    contact_id: Optional[int] = None
    chat_content: str
    tag: Optional[str] = None
    contact_relationship: Optional[str] = None

# 提取聊天记录中的消息
def extract_messages(xml_content):
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"XML 解析错误: {e}")
        return []
    
    messages = []
    for dataitem in root.findall(".//dataitem"):
        hashusername_elem = dataitem.find(".//hashusername")
        sourcename_elem = dataitem.find(".//sourcename")
        datadesc_elem = dataitem.find(".//datadesc")

        # 确保元素存在，适配图片解析
        if hashusername_elem is not None and sourcename_elem is not None and datadesc_elem is not None:
            sourcename = sourcename_elem.text
            datadesc = datadesc_elem.text
            messages.append((sourcename, datadesc))
        elif hashusername_elem is not None and sourcename_elem is not None:
            sourcename = sourcename_elem.text
            datadesc = "[图片或视频]"
            messages.append((sourcename, datadesc))
    
    return messages

# 格式化消息为字符串
def format_messages(messages):
    formatted_messages = "我把聊天记录转发给你：\n"
    for name, content in messages:
        formatted_messages += "{" + f"'role':{name}, 'content':{content}" + "}\n"
    return formatted_messages

# 提取 <datalist> 段落
def extract_datalist_segment(xml_content):
    pattern = re.compile(r'<datalist count="\d+">.*?</datalist>', re.DOTALL)
    match = pattern.search(xml_content)
    if match:
        return match.group(0)
    else:
        return None

# 解析并格式化转发的聊天记录
def get_forwarded_msg(xml_content):
    data = extract_datalist_segment(xml_content)
    if data:
        messages = extract_messages(data)
        content = format_messages(messages)
        return content
    else:
        print("无法提取 datalist 段落")
        return ""

# 提取用户昵称
def extract_user_nicknames(xml_content):
    title_pattern = r'<title>(.*?)</title>'
    title_match = re.search(title_pattern, xml_content)
    if title_match:
        title = title_match.group(1)
        users_pattern = r'(.*?)和(.*?)的聊天记录'
        users_match = re.search(users_pattern, title)
        if users_match:
            user_a = users_match.group(1).strip()
            user_b = users_match.group(2).strip()
            return user_a, user_b
    return None, None

def clean_xml(xml_content):
    # 使用正则表达式匹配出 <xml> 标签之间的内容
    xml_data = re.search(r"<xml>([\s\S]*?)<\/xml>", xml_content)
    if xml_data:
        return xml_data.group(0)
    else:
        raise ValueError("未找到有效的 XML 数据")
# 解析聊天消息
def parse_chat_message(xml_content: str) -> List[Dict[str, Any]]:
    print("before xml decode:")
    print(xml_content)
    print("====================================")
    
    # 解析XML
    xml_data = xml_content.strip()
    root = ET.fromstring(xml_data)

    # 获取消息列表中的记录项
    record_item = root.find('.//recorditem')
    
    # 存储聊天内容
    chat_content = []

    if record_item is not None:
        # recorditem 内嵌的 XML 需要再次解析
        # 处理 CDATA 内容
        record_root = ET.fromstring(record_item.text)  # 直接解析 CDATA 内容

        # 获取每条消息的时间、发送者和内容，并存放在 chat_content 中
        for dataitem in record_root.findall('.//dataitem'):
            sourcetime = dataitem.find('sourcetime')
            sourcename = dataitem.find('sourcename')
            datadesc = dataitem.find('datadesc')

            # 安全获取文本内容，避免 None 引发错误
            chat_content.append({
                'time': sourcetime.text if sourcetime is not None else "N/A",
                'sender': sourcename.text if sourcename is not None else "Unknown",
                'message': datadesc.text if datadesc is not None else "Empty message"
            })
    
    return chat_content  # 始终返回一个列表

# MainServer 类
class MainServer:
    def __init__(self):
        self.wcf = Wcf()
        self.Dis = DbInitServer()
        self.wcf.enable_receiving_msg()
        self.Rmh = RoomMsgHandle(self.wcf)
        # self.Fmh = FriendMsgHandle(self.wcf)
        self.Pms = PushMainServer(self.wcf)
        # 初始化配置
        Thread(target=self.initConfig, name='初始化服务以及配置').start()

    def isLogin(self):
        """ 判断是否登录 """
        ret = self.wcf.is_login()
        if ret:
            userInfo = self.wcf.get_user_info()
            cprint.info(f"""
            \t========== NGCBot V2.1 ==========
            \t微信名：{userInfo.get('name')}
            \t微信ID：{userInfo.get('wxid')}
            \t手机号：{userInfo.get('mobile')}
            \t========== NGCBot V2.1 ==========
            """.replace(' ', ''))

    def processMsg(self):
        """ 处理接收到的消息 """
        from BotServer.MsgHandleServer.FriendMsgHandle import FriendMsgHandle  # 延迟导入
        self.Fmh = FriendMsgHandle(self.wcf)
        self.isLogin()
        while self.wcf.is_receiving_msg():
            try:
                msg = self.wcf.get_msg()
                op(f'[*]: 接收到消息\n[*]: 发送人ID: {msg.sender}\n[*]: 发送内容: {msg.content}\n[*]: RoomId: {msg.roomid}\n--------------------')
                
                # 群聊消息处理
                if '@chatroom' in msg.roomid and "@高情商回复小助手" in msg.content:
                    user_nick_name = msg.sender
                    Thread(target=self.Rmh.mainHandle, args=(msg, user_nick_name)).start()

                # 好友消息处理
                elif '@chatroom' not in msg.roomid and 'gh_' not in msg.sender:
                    user_nick_name = msg.sender
                    isChatHistory = False

                    if '</datalist>' in msg.content:
                        user_nick_name, contact_nick_name = extract_user_nicknames(msg.content)
                        chat_content: List[Dict[str, Any]]
                        chat_content = parse_chat_message(msg.content)
                        # 转换为 JSON 字符串
                        chat_content_json = json.dumps(chat_content, ensure_ascii=False)
                        # msg.content += f"\n我是这段对话记录中的{user_nick_name}"
                        msg.type = 1
                        isChatHistory = True
                        # Assuming chat_content is your list of dictionaries                        
                        chat_record = ChatCreate(
                            personal_name=user_nick_name,
                            name=contact_nick_name,
                            chat_content=chat_content_json,
                            tag="摸鱼达人",
                            contact_relationship="subordinate"
                        )
                        print(chat_record)

                        # 发送 API 请求
                        api_url = "https://eqmaster.azurewebsites.net/create_subordinate_by_chat"
                        response = requests.post(api_url, json=chat_record.dict())

                        if response.status_code == 200:
                            print("聊天记录成功发送到API")
                        else:
                            print(f"发送失败，状态码: {response.status_code}, 响应内容: {response.text}")
                    
                    # 启动好友消息处理线程
                    Thread(target=self.Fmh.mainHandle, args=(msg, user_nick_name, isChatHistory)).start()

            except Empty:
                continue

    def initConfig(self):
        """ 初始化数据库 缓存文件夹 开启定时推送服务 """
        self.Dis.initDb()
        Fcs.initCacheFolder()
        Thread(target=self.Pms.run, name='定时推送服务').start()


if __name__ == '__main__':
    Ms = MainServer()
    Ms.processMsg()
