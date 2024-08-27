from BotServer.MsgHandleServer.FriendMsgHandle import FriendMsgHandle
from BotServer.MsgHandleServer.RoomMsgHandle import RoomMsgHandle
from PushServer.PushMainServer import PushMainServer
from DbServer.DbInitServer import DbInitServer
import FileCache.FileCacheServer as Fcs
from threading import Thread
from OutPut.outPut import op
from cprint import cprint
from queue import Empty
from wcferry import Wcf

import re  
import xml.etree.ElementTree as ET  
import html 
  
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
    pattern = re.compile(r'<datalist count="\d+">.*?</datalist>', re.DOTALL)  
    match = pattern.search(xml_content)  
    if match:
        return match.group(0)  
    else:
        return None


def get_forwarded_msg(xml_content):
    data = extract_datalist_segment(xml_content)
    messages = extract_messages(data)
    content = format_messages(messages)
    return content


import re  
  
def extract_user_nicknames(xml_content):  
    # 定义正则表达式模式  
    title_pattern = r'<title>(.*?)</title>'  
  
    # 搜索匹配  
    title_match = re.search(title_pattern, xml_content)  
  
    if title_match:  
        title = title_match.group(1)  
          
        # 假设昵称之间用 "和" 分隔  
        users_pattern = r'(.*?)和(.*?)的聊天记录'  
        users_match = re.search(users_pattern, title)  
          
        if users_match:  
            user_a = users_match.group(1).strip()  
            user_b = users_match.group(2).strip()  
            return user_a, user_b  
        else:  
            return None, None  
    else:  
        return None, None 



class MainServer:
    def __init__(self):
        self.wcf = Wcf()
        self.Dis = DbInitServer()
        # 开启全局接收
        self.wcf.enable_receiving_msg()
        self.Rmh = RoomMsgHandle(self.wcf)
        self.Fmh = FriendMsgHandle(self.wcf)
        self.Pms = PushMainServer(self.wcf)
        # 初始化服务以及配置
        Thread(target=self.initConfig, name='初始化服务以及配置').start()

    def isLogin(self, ):
        """
        判断是否登录
        :return:
        """
        ret = self.wcf.is_login()
        if ret:
            userInfo = self.wcf.get_user_info()
            # 用户信息打印
            cprint.info(f"""
            \t========== NGCBot V2.1 ==========
            \t微信名：{userInfo.get('name')}
            \t微信ID：{userInfo.get('wxid')}
            \t手机号：{userInfo.get('mobile')}
            \t========== NGCBot V2.1 ==========       
            """.replace(' ', ''))


    def processMsg(self, ):
        # 判断是否登录
        self.isLogin()
        while self.wcf.is_receiving_msg():
            try:
                msg = self.wcf.get_msg()
                # 调试专用
                # op(f'[*]: 接收到消息: {msg}')
                op(f'[*]: 接收到消息\n[*]: [*]: 发送人ID: {msg.sender}\n[*]: 发送内容: {msg.content}\n[*]: RoomId: {msg.roomid}\n--------------------')
                # 群聊消息处理
                if '@chatroom' in msg.roomid and "@高情商回复小助手" in msg.content:
                    user_nick_name = msg.sender
                    Thread(target=self.Rmh.mainHandle, args=(msg, user_nick_name)).start()
                # 好友消息处理
                if '@chatroom' not in msg.roomid and 'gh_' not in msg.sender:
                    user_nick_name = msg.sender
                    isChatHistory = False

                    # msg.content转码
                    # def decode_msg_content(content):
                    #    # 解码 HTML 实体
                    #     content = html.unescape(content)
                        
                    #     # 使用正则表达式提取 dataitem 中的内容
                    #     pattern = re.compile(r'<dataitem.*?>(.*?)</dataitem>', re.DOTALL)
                    #     items = pattern.findall(content)
                        
                    #     decoded_items = []
                    #     for item in items:
                    #         # 提取 dataid 和 datadesc
                    #         dataid_match = re.search(r'dataid="(.*?)"', item)
                    #         datadesc_match = re.search(r'<datadesc>(.*?)</datadesc>', item)
                            
                    #         if dataid_match and datadesc_match:
                    #             dataid = dataid_match.group(1)
                    #             datadesc = datadesc_match.group(1)
                    #             decoded_items.append(f"ID: {dataid}, 描述2: {datadesc}")
                        
                    #     return "\n".join(decoded_items)
                    # msg.content = decode_msg_content(msg.content)
                    print("after decode:", msg.content)
                    if '</datalist>' in msg.content:
                        print("2")
                        user_nick_name = extract_user_nicknames(msg.content)[0]
                        print(user_nick_name)
                        msg.content = msg.content + f"\n我是这段对话记录中的{user_nick_name}"
                        msg.type = 1
                        isChatHistory = True
                        print("=========转发信息内容=========")
                        print(msg.content)
                        print("==================")
                    Thread(target=self.Fmh.mainHandle, args=(msg,user_nick_name, isChatHistory)).start()
                else:
                    pass
            except Empty:
                continue

    def initConfig(self, ):
        """
        初始化数据库 缓存文件夹 开启定时推送服务
        :return:
        """
        self.Dis.initDb()
        Fcs.initCacheFolder()
        Thread(target=self.Pms.run, name='定时推送服务').start()


if __name__ == '__main__':
    Ms = MainServer()
    Ms.processMsg()
