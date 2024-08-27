# 环境安装

安装命令：pip install -r requirements.txt

## Ai_Chatbot环境 注意事项

安装命令：pip install -r Ai_Chatbot_main\requirements.txt

*Notes：build报错需要先安装c++工具包 Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
需要在conda安装ffmpeg（pip安装可能报错）：
conda install -c conda-forge ffmpeg
conda install -c conda-forge libiconv*

## 微信个人号Bot环境 注意事项

安装：pip install -r NGCBot_main\requirements.txt

*Notes：不支持linux，必须在windows上登录微信才能使用
需要更新到特定微信版本，并将wcferry包的版本也一同更新
如微信3.9.10.27：https://github.com/lich0821/WeChatFerry/releases/download/v39.2.4/WeChatSetup-3.9.10.27.exe
需要更新weferry==39.2.4.0
进一步信息请参考项目github地址：https://github.com/ngc660sec/NGCBot/releases/tag/V2.1*~

# Quick start

启动命令：python WechatBot.py  /  python NGCBot_main\main.py

# 项目结构

- Ai\_Chatbot\_main         *Chatbot相关代码*

  - EQmaster.py    高情商小助手Chat Bot的具体实现代码
  - AiChatbot.py    Ai虚拟人，包括角色扮演agent，幕后agent，自动保存记忆，RAG召回等具体实现
  - response_doubao.py  *豆包基座模型接口*
  - response_openai.py  *openai基座模型接口*
- database                      *数据库*

  - mydata.db       本地数据库（sqlite）
- logs
- NGCBot\_main              *微信个人号Bot相关代码*
- create\_chatbot.py
- data.epub
- data.txt                        *高情商对话参考数据（由epub转出）*
- NGCBot-master.zip
- Readme.md
- requirements.txt
- utils.py
- WechatBot.py              *启动微信Bot*
