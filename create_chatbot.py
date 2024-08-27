import sqlite3
from Ai_Chatbot_main.response_openai import get_response
from Ai_Chatbot_main.AiChatbot import AiChatbot
from Ai_Chatbot_main.EQmaster import EQmaster

import re
from html import unescape
import os

import azure.cognitiveservices.speech as speechsdk

from azure.cognitiveservices.speech import AudioConfig
from pydub import AudioSegment


def split_sentences(text):
    # 使用正则表达式来匹配中文句子结束的标点符号
    sentence_endings = r'。|？|！|；'
    
    # 分割文本
    sentences = re.split(sentence_endings, text)
    
    sentence_sup_endings = r',|，'
    tmp = []
    for i in sentences:
        if len(i) < 30:
            tmp.append(i)
        else:
            i = [i[:int(len(i)/2)], i[int(len(i)/2):]]
            tmp += i
    sentences = tmp[:]
    # 移除空字符串并返回
    return [s.strip() for s in sentences if s.strip()]


# ==================测试接口=================== #
def get_id(rolename, username):
    # 默认数据,用于新用户  
    default_relationship = "陌生人"  
    default_intimacy = 0
    default_userinfo = "未知"

    # 获取userid，若不存在则新建用户信息   
    conn = sqlite3.connect('./database/mydata.db')
    cur = conn.cursor()

    roleid = cur.execute("SELECT roleid FROM role_info WHERE rolename = ?", (rolename,)).fetchone()[0]
    userid = cur.execute("SELECT userid FROM user WHERE username = ?", (username,)).fetchone()
    if not userid:
        max_rowid = cur.execute(f"SELECT MAX(rowid) FROM user").fetchone()[0]
        cur.execute("INSERT INTO user (userinfo, username) VALUES (?, ?)", (default_userinfo, username))
        cur.execute("INSERT INTO relationship (userid, roleid, relationship, intimacy) VALUES (?, ?, ?, ?)", (int(max_rowid)+1, roleid, default_relationship, default_intimacy))
        userid = int(max_rowid)+1
    else:
        userid = userid[0]
    
    conn.commit() 
    conn.close()
    return roleid, userid


def create_chatbot(rolename, username, verbose=False):
    """
    创建角色chatbot
    """
    roleid, userid = get_id(rolename, username)
    
    # 从数据库中读取数据
    conn = sqlite3.connect('./database/mydata.db')
    cur = conn.cursor()
    
    persona = cur.execute("SELECT persona FROM role_info WHERE roleid = ?", (roleid,)).fetchone()[0]


    stories = cur.execute("SELECT story, story_vec FROM memories WHERE roleid = ? and userid = ?", (roleid, userid)).fetchall()
    if stories:
        stories, story_vecs = zip(*stories)
        story_vecs = [eval(i)[0] if i else None for i in story_vecs]
    else:
        stories, story_vecs = None, None

    relationship, intimacy = cur.execute("SELECT relationship, intimacy FROM relationship WHERE roleid = ? and userid = ?", (roleid, userid)).fetchone()
    context = cur.execute("SELECT plot FROM plots WHERE roleid = 1 ORDER BY rowid DESC LIMIT 1").fetchone()[0]
    userinfo = cur.execute("SELECT userinfo FROM user WHERE userid = ?", (userid,)).fetchone()[0]
    conn.close()

    # 自定义角色的载入
    chatbot = AiChatbot(
        roleid = roleid,
        userid= userid,
        rolename = rolename,
        username= username,
        userinfo = userinfo,
        persona=persona,
        stories=stories, 
        story_vecs=story_vecs,
        llm = get_response,
        verbose=verbose,
        max_input_token = 1800,
        max_len_story = 600,
        max_story_n = 3,
        intimacy = intimacy,
        context = context,
        relationship = relationship,
        )

    return chatbot

def create_eqmaster(username, verbose=False):
    """
    创建角色chatbot
    """
    # 自定义角色的载入
    chatbot = EQmaster(
        username=username,
        llm = get_response,
        verbose=verbose,
        )

    return chatbot
# ============================================ #

if __name__ == "__main__":   
    # 对话场景分析
    # 询问回复倾向
    # 根据场景分析和回复倾向，在prompt中细化，提取对应场景的参考数据
    # 给出高情商回复建议

    # 多agent 游戏机制（自己回复后，模型分析回复的质量，有没有改进点）（求助模型，模型给出建议）
    
    username = "王佩佩"
    ai_chatbot = create_eqmaster(username=username, verbose=True)

    while True:
        message = input("用户：")
        print()
        if message[:5] == "对话记录：":
            response = ai_chatbot.get_response(chat_history=message)
        else:
             # 获取用户选择的回应选项
            choice = input("\n请选择回应选项（1-4）：")
            
            # 根据选择生成最终回复
            if choice.isdigit() and 1 <= int(choice) <= 4:
                response = ai_chatbot.generate_final_response(int(choice))
                print("\nEQmaster：", response)
            else:
                print("\n无效输入，请选择1到4之间的数字。")
        print("EQmaster：",response)
        print()