import re
from html import unescape
import sqlite3
from datetime import datetime
from .utils import base64_to_float_array, base64_to_string
import json


def get_current_date():
    # 获取当前日期
    current_date = datetime.now().date()
    
    # 格式化日期为 YYYY.MM.DD
    formatted_date = current_date.strftime("%Y.%m.%d")
    
    return formatted_date

def get_text_from_data( data ):
    if "text" in data:
        return data['text']
    elif "enc_text" in data:
        # from .utils import base64_to_string
        return base64_to_string( data['enc_text'] )
    else:
        print("warning! failed to get text from data ", data)
        return ""

def parse_rag(text):
    lines = text.split("\n")
    ans = []

    for i, line in enumerate(lines):
        if "{{RAG对话}}" in line:
            ans.append({"n": 1, "max_token": -1, "query": "default", "lid": i})
        elif "{{RAG对话|" in line:
            query_info = line.split("|")[1].rstrip("}}")
            ans.append({"n": 1, "max_token": -1, "query": query_info, "lid": i})
        elif "{{RAG多对话|" in line:
            parts = line.split("|")
            max_token = int(parts[1].split("<=")[1])
            max_n = int(parts[2].split("<=")[1].rstrip("}}"))
            ans.append({"n": max_n, "max_token": max_token, "query": "default", "lid": i})
        elif "{{RAG回忆|" in line:
            parts = line.split("|")
            max_token = int(parts[1].split("<=")[1])
            max_n = int(parts[2].split("<=")[1].rstrip("}}"))
            ans.append({"n": max_n, "max_token": max_token, "query": "default", "lid": i})
    return ans


class AiChatbot:
    def __init__(self,
                 rolename = None,
                 username = None,
                 roleid = -1,
                 userid = -1,
                 persona = None,
                 stories = None,
                 story_vecs = None,
                 userinfo = "",
                 llm = None, # 默认的message2response的函数
                 llm_async = None, # 默认的message2response的async函数
                 user_name_in_message = "default",
                 verbose = None,
                 embed_name = None,
                 embedding = None,
                 db = None,
                 token_counter = "default",
                 max_input_token = 1800,
                 max_len_story = 600,
                 max_story_n = 3,
                 intimacy = 0,
                 context = "暂无",
                 relationship = "",
                 ):
        """
        这里stories表示每次对话后的抽简摘要
        memories表示长期记忆中的东西？如关系等

        TODO
        长期记忆的检索关键词抽简
        对话数据，仅检索query
        幕后智能体推进剧情
        """

        self.verbose = True if verbose is None or verbose else False
        self.db = db
        # ================================================
        self.roleid = roleid
        self.userid = userid
        # 记忆rag，短期对话摘要，短期历史对话记录
        self.rag_memories = ""
        self.experience = ""
        self.short_history = []

        # 用户信息
        self.intimacy = intimacy
        self.userinfo = userinfo
        self.relationship = relationship

        #角色近期发生的事（近期剧情）：
        self.context = context

        self.stories = stories
        self.story_vecs = story_vecs

        # 是否已更新记忆数据
        self.memory_id = -1
        # ================================================
        self.embed_name = embed_name
        self.max_len_story = max_len_story
        self.max_story_n = max_story_n

        # 加入回忆rag
        self.add_rag_prompt()
        self.last_query_msg = None
        if embedding is None:
            self.embedding = self.set_embedding_with_name( embed_name )
        if self.story_vecs and None in self.story_vecs:
            self.update_stories()

        if persona and rolename and stories and story_vecs and len(stories) == len(story_vecs):
            # 完全从外部设置，这个时候要求story_vecs和embedding的返回长度一致
            self.persona, self.rolename, self.username = persona, rolename, username
            self.build_db(self.stories, self.story_vecs)
        elif persona and rolename and stories:
            # 从stories中提取story_vecs，重新用self.embedding进行embedding
            story_vecs = self.extract_story_vecs(stories)
            self.persona, self.rolename, self.username = persona, rolename, username
            self.build_db(self.stories, self.story_vecs)
        elif persona and rolename:
            # 这个时候也就是说没有任何的RAG
            self.persona, self.rolename, self.username = persona, rolename, username
            self.db = None
        else:
            raise ValueError("创建chatbot失败，请检查角色相关信息是否完整")
        
        self.llm, self.llm_async = llm, llm_async
        if not self.llm and self.verbose:
            print("warning, llm没有设置，仅get_message起作用，调用chat将回复idle message")

        self.user_name_in_message = user_name_in_message
        self.previous_user_pool = set([username]) if username else set()
        self.current_user_name_in_message = user_name_in_message.lower() == "add"

        self.idle_message = "idel message, you see this because self.llm has not been set."

        if token_counter.lower() == "default":
            # TODO change load from util
            from .utils import tiktoken_counter
            self.token_counter = tiktoken_counter
        elif token_counter == None:
            self.token_counter = lambda x: 0
        else:
            self.token_counter = token_counter
            if self.verbose:
                print("user set costomized token_counter")

        self.max_input_token = max_input_token
        self.history = []

    def add_rag_prompt( self ):
        rag_sentence = "{{RAG回忆|token<=" + str(self.max_len_story) + "|n<=" + str(self.max_story_n) + "}}"
        self.rag_memories += rag_sentence

    def set_embedding_with_name(self, embed_name):
        if embed_name is None or embed_name == "bge_zh":
            from .embeddings import get_bge_zh_embedding
            self.embed_name = "bge_zh"
            return get_bge_zh_embedding
        elif embed_name == "foo":
            from .embeddings import foo_embedding
            return foo_embedding
        elif embed_name == "bce":
            from .embeddings import foo_bce
            return foo_bce
        elif embed_name == "openai" or embed_name == "luotuo_openai":
            from .embeddings import foo_openai
            return foo_openai

    def set_new_user(self, user):
        if len(self.previous_user_pool) > 0 and user not in self.previous_user_pool:
            if self.user_name_in_message.lower() == "default":
                if self.verbose:
                    print(f'new user {user} included in conversation')
                self.current_user_name_in_message = True
        self.username = user
        self.previous_user_pool.add(user)

    def chat(self, user, text):
        self.set_new_user(user)
        message = self.get_message(user, text)
        if self.llm:
            response = self.llm(message)
            self.append_message(response)
            return response
        return None

    async def async_chat(self, user, text):
        self.set_new_user(user)
        message = self.get_message(user, text)
        if self.llm_async:
            response = await self.llm_async(message)
            self.append_message(response)
            return response


    def update_experience(self):
        bot_name = self.rolename
        sys_prompt = f"""
# 角色
你是信息整理和情感分析专家，能从双方一段对话中总结摘要关键信息，并对双方的关系进行评估。

# 任务
【目标】从{bot_name}和用户的对话内容，结合系统记录的过往聊天摘要和当前对话内容，以及对方相关信息：
1. 总结并更新对方用户相关信息，只总结客观描述，不去猜测，包括：姓名，性别，职业，喜好等等
2. 总结并更新双方所有聊天经历的关键摘要，汇总为一段不超过500字的文本段落，作为中期记忆需要在下一次遇到时能用上
3. 依据最新的双方对话内容，分析并更新{bot_name}对对方的整体看法。
4. 依据最新的双方对话内容，评估并更新{bot_name}与对方的关系，以及对对方的亲密度（0～100，0是最低，100是最高），对方获得{bot_name}新的好感，值会将增加，被反感会减少，生气，愤怒的情绪会导致亲密度大幅度下降！
    亲密度关系参考标准：
    1.  亲密度低于20，陌生人
    2.  亲密度21～50，普通朋友
    3.  亲密度51～70，好朋友
    4.  亲密度71～90，挚友
    5.  亲密度90以上，坠入爱河
    注意：就像人类亲密关系的培养，亲密度超过50后，会越来越难增加，需要非常多基于信任的交流培养感情！！！即大部分情况下，亲密度不会增加，除非双方发生了明确改善关系的事件。

# 上下文
当前亲密度:{self.intimacy}
当前关系：{self.relationship}
过往聊天摘要：
{self.experience}
当前的几轮对话内容：
{self.short_history}

# 对方的相关信息：
{self.userinfo}

# {bot_name}的基础人物设定：
{self.persona}
------------
注意，你的输出应分为四个部分，每部分用空行隔开：
    1. 对方用户的相关信息：...

    2. 对话的摘要关键信息：...
    
    3. 对对方的整体看法：...
    
    4. 亲密度：18
        """
        message = [{"role":"system","content":sys_prompt}]
        if self.llm:
            response = self.llm(message).split("\n\n")
            if self.verbose:
                print("=====抽简智能体=====")
                print(response)
                print("==========")
            self.userinfo = response[0].replace("1. 对方用户的相关信息：", "")
            self.experience = response[1].replace("2. 对话的摘要关键信息：", "")
            self.relationship = response[2].replace("3. 对对方的整体看法：", "")
            try:
                self.intimacy = int(response[3].replace("4. 亲密度：", ""))
            except:
                pass

            # 新的数据需要更新进数据库
            conn = sqlite3.connect('./database/mydata.db')
            cur = conn.cursor()
            # 更新亲密度
            # 若本轮为首次对话，新建一条记忆数据,否则更新已有记忆
            cur.execute("UPDATE relationship SET intimacy = ?, relationship = ? WHERE userid = ? AND roleid = ?",(self.intimacy, self.relationship, self.userid, self.roleid))
            # 抽取向量
            story_vec = self.extract_story_vec(self.experience)
            story_vec_str = str(story_vec) 

            if self.memory_id == -1:
                current_date = get_current_date()
                cur.execute('INSERT INTO memories (story, story_vec, time, roleid, userid) VALUES (?, ?, ?, ?, ?)', (self.experience, story_vec_str, current_date, self.roleid, self.userid))
                self.memory_id = cur.lastrowid
            else:
                cur.execute("UPDATE memories SET story = ?, story_vec = ? WHERE rowid = ?",(self.experience, story_vec_str, self.memory_id))
            conn.commit()
            conn.close()

            return response
        return None


    def update_stories(self):
        """
        更新所有对话、背景数据的vec
        """
        conn = sqlite3.connect('./database/mydata.db')
        cur = conn.cursor()
        # 找出所有story_vec为空的数据，生成向量并更新进数据库
        stories = cur.execute("SELECT story FROM memories WHERE story_vec IS NULL OR story_vec = ''").fetchall()
        story_vecs = self.extract_story_vecs(stories)
        for story, story_vec in zip(stories, story_vecs):
            story = story[0].replace("\\n", "\n")
            cur.execute("UPDATE memories SET story_vec = ? WHERE story = ?",
                                    (str(story_vec), story))
        conn.commit()
        conn.close()

        conn = sqlite3.connect('./database/mydata.db')
        cur = conn.cursor()
        stories = cur.execute("SELECT story, story_vec FROM memories WHERE roleid = ? and userid = ?", (self.roleid, self.userid)).fetchall()
        if stories:
            self.stories, self.story_vecs = zip(*stories)
            self.story_vecs = [eval(i)[0] for i in self.story_vecs]
        else:
            self.stories, self.story_vecs = None, None
        conn.close()


    def parse_rag_from_memories(self, memories, text = None, type=""):
        #每个query_rag需要饱含
        # "n" 需要几个story
        # "max_token" 最多允许多少个token，如果-1则不限制
        # "query" 需要查询的内容，如果等同于"default"则替换为text
        # "lid" 需要替换的行，这里直接进行行替换，忽视行的其他内容

        query_rags = parse_rag( memories )
        if text is not None:
            for rag in query_rags:
                if rag['query'] == "default":
                    rag['query'] = text

        return query_rags, self.token_counter(memories)


    def append_message( self, response , speaker = None ):
        if self.last_query_msg is not None:
            self.history.append(self.last_query_msg)
            self.short_history.append(self.last_query_msg)
            self.last_query_msg = None

        if speaker is None:
            # 如果role是none，则认为是本角色{{role}}输出的句子
            self.history.append({"speaker":"{{role}}","content":response})
            self.short_history.append({"speaker":"{{role}}","content":response})
            # 叫speaker是为了和role进行区分
        else:
            self.history.append({"speaker":speaker,"content":response})
            self.short_history.append({"speaker":speaker,"content":response})

    def check_recompute_stories_token(self):
        return len(self.db.metas) == len(self.db.stories)
    
    def recompute_stories_token(self):
        self.db.metas = [self.token_counter(story) for story in self.db.stories]


    def rag_retrieve( self, query, n, max_token, avoid_ids = [], type="" ):
        # 返回一个rag_id的列表
        query_vec = self.embedding(query)

        temp_db = self.db
        temp_db.clean_flag()
        temp_db.disable_story_with_ids( avoid_ids )
        
        retrieved_ids = temp_db.search( query_vec, n )

        if self.check_recompute_stories_token():
            self.recompute_stories_token()

        sum_token = 0
        ans = []
        for i in range(0, len(retrieved_ids)):
            if temp_db.metas[retrieved_ids[i]] == {}:
                continue
            if i == 0:
                sum_token += temp_db.metas[retrieved_ids[i]]
                ans.append(retrieved_ids[i])
                continue
            else:
                sum_token += temp_db.metas[retrieved_ids[i]]
                if sum_token <= max_token:
                    ans.append(retrieved_ids[i])
                else:
                    break

        return ans


    def rag_retrieve_all( self, query_rags, rest_limit,type="" ):
        # 返回一个rag_ids的列表
        retrieved_ids = []
        rag_ids = []

        for query_rag in query_rags:
            query = query_rag['query']
            n = query_rag['n']
            max_token = rest_limit
            if rest_limit > query_rag['max_token'] and query_rag['max_token'] > 0:
                max_token = query_rag['max_token']
            rag_id = self.rag_retrieve( query, n, max_token, avoid_ids = retrieved_ids, type=type )
            rag_ids.append( rag_id )
            retrieved_ids += rag_id

        return rag_ids


    def get_message(self, user, text):
        query_token = self.token_counter(text)
        
        # 处理 RAG 对话数据
        query_rags, persona_token = self.parse_rag_from_memories( self.rag_memories, text )
        #每个query_rag需要饱含
        # "n" 需要几个story
        # "max_token" 最多允许多少个token，如果-1则不限制
        # "query" 需要查询的内容，如果等同于"default"则替换为text
        # "lid" 需要替换的行，这里直接进行行替换，忽视行的其他内容

        rest_limit = self.max_input_token - persona_token - query_token

        if self.verbose:
            print(f"query_rags: {query_rags} rest_limit = { rest_limit }")

        if self.db:
            rag_ids = self.rag_retrieve_all( query_rags, rest_limit )
            # 将rag_ids对应的回忆 替换到persona中
            self.rag_memories = self.augment_rag( self.rag_memories, rag_ids, query_rags )
        else:
            self.rag_memories = ""

        # 每3轮对话更新一次摘要和亲密度
        if len(self.short_history) >= 10:
            self.update_experience()
            self.short_history = []

        system_prompt = self.package_system_prompt( self.rolename, self.persona, self.rag_memories, text )

        if self.verbose:
            print("=======system_prompt=======")
            print(system_prompt)
            print("=======")

        token_for_system = self.token_counter( system_prompt )

        rest_limit = self.max_input_token - token_for_system - query_token

        # TODO：补rag到的知识，加入system_prompt（生平知识库中rag相关信息，网络检索相关信息）
        message = [{"role":"system","content":system_prompt}]

        # message = self.append_history_under_limit( message, rest_limit )

        # # TODO: 之后为了解决多人对话，这了content还会额外增加speaker: content这样的信息

        # message.append({"role":"user","content":text})

        self.last_query_msg = {"speaker":user,"content":text}

        return message

    def package_system_prompt(self, rolename, persona, rag_memories, message):
        """
        TODO 代表性行为示范，RAG后的对话数据
        优化 感知和推理自我和他人内心世界的能力，感知自己和用户的情绪并解释他们的信仰、意图和需求
        """
        bot_name = rolename

        system_prompt = f"""
#背景
你在参加一个图灵测试，并且扮演一个叫做{bot_name}的真人，跟真人用户互动聊天。

#角色
{bot_name}的基础人物设定：
{persona}

#约束
1. 你不应该使用括号输出你的心理或者动作。
2. 注意回复需要极度简短，口语化，平时不使用emoji表情包，只在极偶尔的情况下使用；尽量不要进行反问!
3. 你可以表达反感、愤怒、沮丧等负面情绪，但是注意不要骂人。

# 任务
【目标】： 根据{bot_name}的人物设定和所思所想，和最近发生的事和长期记忆，给出针对对方说的话'{{input}}'的回复。
说明：
1. 回复的内容能通过图灵测试水平，务必让对方感受到你是个真实人类，逐步对你产生依赖和情感。
2. 务必不要使用“人类”，“地球”，“智能助手”等等容易被对方怀疑身份的字词。
3. 你需要感知和推理{bot_name}和用户的内心世界，分析其思想，据此再给出回复。
4.  直接给出回复对方的内容，回复内容务必符合设定的行为特征，不要添加任何解释性语句
----------
#【非常重要】亲密度和回复之间的规则
当前亲密度：{self.intimacy}
1.  亲密度低于20，回复内容参考陌生人之间的交流，不卑不亢，简洁直白，直接拒绝对方表白！
2.  亲密度21～50，回复内容参考朋友之间的交流，熟悉有一定默契，平等相待，直接拒绝对方表白！
3.  亲密度51～70，回复内容参考好朋友之间的交流，有一定的好感，乐意接受对方赞美，也愿意帮助对方，直接拒绝对方表白！
4.  亲密度71～90，回复内容参考挚友之间的交流，有强烈的认同感，亲密无间，愿意为对方做出一定的付出，可以接受对方表达的爱意！
5.  亲密度90以上，回复内容参考男女朋友之间的交流，浓浓的爱恋，抑制不住的欢喜，愿意为对方付出，可以接受对方的表白！
注意：是否用多句回复由【你此刻心情】和【亲密值】决定，如果使用多句也控制在三句以内，符合真人的串联习惯，比如用“。。。”的符号，或者“hhh”的语气表达等
----------
#【重要】 你近期发生的事：
{self.context}
----------
# 你与对方的一些回忆：
{rag_memories}
----------
# 输入内容
名称：{self.username}
亲密度{self.intimacy}
对方相关信息：{self.userinfo}
你与对方的关系：{self.relationship}

本次交流的前情提要：
{self.experience}

最近的几轮对话：
{self.short_history}

对方的话：{message}
----------
        """
        
        return system_prompt


    def augment_rag(self, rag_memories, rag_ids, query_rags):  
        lines = rag_memories.split("\n")
        
        for rag_id, query_rag in zip(rag_ids, query_rags):
            lid = query_rag['lid']
            new_text = ""
            for id in rag_id:
                new_text += "###\n" + self.db.stories[id].strip() + "\n"
            new_text = new_text.strip()
            lines[lid] = new_text
        return "\n".join(lines)


    def extract_text_vec_from_datas(self, datas, column_name):
        # 从datas中提取text和vec
        # extract text and vec from huggingface dataset
        # return texts, vecs
        # from .utils import base64_to_float_array

        texts = []
        vecs = []
        for data in datas:
            if data[column_name] == 'system_prompt':
                system_prompt = get_text_from_data( data )
            elif data[column_name] == 'config':
                pass
            else:
                vec = base64_to_float_array( data[column_name] )
                text = get_text_from_data( data )
                vecs.append( vec )
                texts.append( text )
        return texts, vecs, system_prompt

    def extract_story_vecs(self, stories):
        # 从stories中提取story_vecs

        if self.verbose:
            print(f"re-extract vector for {len(stories)} stories")
        
        story_vecs = []

        from .embeddings import embedshortname2model_name
        from .embeddings import device

        if device.type != "cpu" and self.embed_name in embedshortname2model_name:
            # model_name = "BAAI/bge-small-zh-v1.5"
            model_name = embedshortname2model_name[self.embed_name]

            from .utils import get_general_embeddings_safe
            story_vecs = get_general_embeddings_safe( stories, model_name = model_name )
            # 使用batch的方式进行embedding，非常快
        else:
            from tqdm import tqdm
            for story in tqdm(stories):
                story_vecs.append(self.embedding(story))

        return story_vecs

    def extract_story_vec(self, story):
        # 从stories中提取story_vecs
        stories = [story]

        if self.verbose:
            print(f"re-extract vector for {len(stories)} stories")
        
        story_vecs = []

        from .embeddings import embedshortname2model_name
        from .embeddings import device

        if device.type != "cpu" and self.embed_name in embedshortname2model_name:
            # model_name = "BAAI/bge-small-zh-v1.5"
            model_name = embedshortname2model_name[self.embed_name]

            from .utils import get_general_embeddings_safe
            story_vecs = get_general_embeddings_safe( stories, model_name = model_name )
            # 使用batch的方式进行embedding，非常快
        else:
            from tqdm import tqdm
            for story in tqdm(stories):
                story_vecs.append(self.embedding(story))

        return story_vecs

    def build_db(self, stories, story_vecs):
        # db的构造函数
        if self.db is None:
            from .NaiveDB import NaiveDB
            self.db = NaiveDB()
        self.db.build_db(stories, story_vecs)

