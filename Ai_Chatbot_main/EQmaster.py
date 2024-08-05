import re
from html import unescape
import sqlite3
from datetime import datetime
from .utils import base64_to_float_array, base64_to_string
import json

workplace = """
在职场上通过聊天软件与上级对话时，表现出高情商同样非常重要。以下是一些在聊天内容方面的注意点和要点：
    用词谨慎：
    使用礼貌和专业的语言，避免使用俚语或过于随意的表达。
    确保语气友好但不失专业性。
    简明扼要：
    信息要清晰、简洁，不要绕圈子。
    直接回答上级的问题，不要含糊其辞。
    确认理解：
    确保你理解了上级的意图，可以通过复述或确认性问题来验证。
    避免误解，确保沟通清晰。
    积极回应：
    对上级的指示或建议表示认可和感谢。
    在合适的情况下，提供你的观点或建议，但要注意方式。
    保持专业：
    避免在工作群聊中讨论私人话题，保持对话的专业性。
    在适当的场合表达幽默，但不要过度。
    正面表达：
    尽量用正面的语言表达，即使在讨论问题或困难时，也要表现出解决问题的态度。
    避免抱怨或负面情绪的表达。
    提供解决方案：
    当讨论问题时，尽量提供可行的解决方案，而不仅仅是指出问题。
    表现出你的主动性和责任感。
    尊重隐私：
    不要在公共聊天中讨论敏感或机密信息，必要时可以转为私聊。
    尊重对方的隐私和时间，不在非工作时间发送工作信息（除非紧急）。
    使用表情符号：
    适当使用表情符号可以增加对话的亲和力，但要避免过度使用，保持专业性。
    注意表情符号的使用场合和频率，确保不会引起误解。
通过以上这些注意点和要点，你可以在通过聊天软件与上级对话时表现出高情商，建立良好的沟通和信任关系。
"""
daily = """
在日常聊天时，通过聊天软件表现出高情商是建立良好人际关系的重要因素。以下是一些注意点和要点，可以帮助你在日常聊天中表现得更加高情商：
    积极倾听：
    展示出你在认真阅读朋友的信息，通过简短的回应或表情符号表示理解。
    理解朋友的观点，即使你可能不同意，也要表现出你在认真考虑。
    保持礼貌和尊重：
    即使是随意的聊天，也要保持基本的礼貌和尊重。
    避免使用可能引起误解或冒犯的词语和表情符号。
    真诚和开放：
    表现出你的真诚和开放，不要刻意隐瞒或虚伪。
    分享一些你的真实感受和想法，增进彼此的了解。
    幽默感：
    适当使用幽默可以增加聊天的趣味性，但要注意分寸，避免让对方感到不适。
    确保幽默是积极和友善的，不涉及敏感话题。
    情绪控制：
    即使在面对争议或不快时，也要保持冷静，不要在情绪激动时发送信息。
    使用冷静和理性的语言，避免表现出愤怒或沮丧。
    同理心：
    设身处地为朋友着想，理解他们的感受和处境。
    表现出你对朋友的关心和支持。
    正面表达：
    尽量用正面的语言表达，保持积极的态度。
    避免抱怨或负面情绪的表达。
    适当使用表情符号和GIF：
    表情符号和GIF可以增加对话的亲和力和趣味性。
    注意表情符号和GIF的使用场合和频率，确保不会引起误解。
    给予适时的鼓励和支持：
    当朋友遇到困难或心情不好时，给予适时的鼓励和支持。
    表现出你对朋友的关心和理解。
    尊重隐私和边界：
    避免在公共聊天中讨论朋友的私人或敏感话题，尊重他们的隐私。
通过以上这些注意点和要点，你可以在日常聊天中表现出高情商，同时保持随意和轻松的聊天风格，增进彼此的友谊和理解。
"""
scene_data = {
    "职场": workplace,
    "日常聊天": daily,
}



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


class EQmaster:
    def __init__(self,
                 username = None,
                 userid = -1,
                 stories = None,
                 story_vecs = None,
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
                 ):
        """
        回复建议：
        分析对话场景和双方关系，询问回复倾向
        调取相关数据（该场景下高情商回复的注意点）
        给出高情商回复

        判断是否已有回复倾向和相关数据，以此决定调用哪个agent
        
        游戏：
        角色设定、场景设定、回复倾向
        开场白
        求助（调用回复建议接口）
        评分（给定对话场景和双方关系，回复倾向，高情商回复注意点等数据，打分)
        """
        self.verbose = True if verbose is None or verbose else False
        self.db = db
        # ================================================
        self.userid = userid

        self.stories = stories
        self.story_vecs = story_vecs

        self.rag_memories = ""

        self.scene = ""
        self.analyse = ""
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

        if stories and story_vecs and len(stories) == len(story_vecs):
            # 完全从外部设置，这个时候要求story_vecs和embedding的返回长度一致
            self.username = username
            self.build_db(self.stories, self.story_vecs)
        elif stories:
            # 从stories中提取story_vecs，重新用self.embedding进行embedding
            story_vecs = self.extract_story_vecs(stories)
            self.username = username
            self.build_db(self.stories, self.story_vecs)
        else:
            # 这个时候也就是说没有任何的RAG
            self.username = username
            self.db = None
        
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


    def get_response_stage1(self, chat_history):
        self.chat_history = chat_history
        
        sys_prompt = f"""
# 角色
你是信息整理和情感分析专家，能从双方一段对话中分析对话发生的场景，并对双方的关系进行评估。

# 任务
【目标】从一段对话内容中：
1. 分析对话发生的场景，以及双方的意图。
2. 分析双方的关系，如上下级、老师与学生等。
3. 根据分析内容，给出场景定义，从以下几个选项中选择：“日常聊天”、“职场”
4. 询问对方是否有回复倾向或期望的回复风格

# 上下文
当前的几轮对话内容：
{self.chat_history}

------------
注意，你的输出应分为三个部分，每部分用空行隔开，下面是一个例子：
    1. 对话场景分析：对方想要用户在周五加班，要求其在下周一早上给出结果汇报。

    2. 双方关系推测：上下级关系，用户是下级，对方是上级

    3. 推测场景：职场

    请问您是否有....
"""
        message = [{"role":"system","content":sys_prompt}]
        
        # 新一轮对话，清空历史聊天记录
        self.message = []

        if self.llm:
            response = self.llm(message)
            if self.verbose:
                print("=====分析=====")
                print(response)
                print("==========")
            self.scene = response.split("\n\n")[2].replace("3. 推测场景：", "").strip()
            self.analyse = response
            return response


    def get_response_stage2(self, query, analyse=None):
        temp = ""
        if self.scene in scene_data.keys():
            temp += "# 相似场景下，高情商回复的要点：\n" + scene_data[self.scene]

        sys_prompt = f"""
# 角色
你是人际交往专家，能根据不同的对话场景，给出高情商回复的建议，并根据用户反馈实时调整内容，提供指导。

# 任务
【目标】从一段对话，场景分析，双方关系分析，以及对应场景的高情商回复要点出发：
1. 给出三条不同风格、不同角度的高情商回复建议。
2. 分析每一条回复的优势，为什么这么回复。

# 上下文
当前的几轮对话内容：
{self.chat_history}

# 分析
{analyse}

# 用户回复的倾向与期望风格
{query}

{temp}
------------
注意，你的输出应分为三个部分，每部分用空行隔开，下面是一个例子：
    1. **参考回复1：尊重需求、注重结果**：
        - 收到，考虑到今天是周五，且周末我可能无法全力投入工作，能否将汇报时间推迟到周二上午？这样我可以确保汇报内容的质量和准确性。

    2. **参考回复2：...**：
        ...

    3. **参考回复3：...**：
        ...
"""
        self.message = [{"role":"system","content":sys_prompt}]
        if self.llm:
            response = self.llm(self.message)
            if self.verbose:
                print("=====回复=====")
                print(response)
                print("==========")
            self.message += [{"role":"assistant","content":response}]
            return response


    def get_response(self, chat_history=None, query=None):
        if chat_history:
            analyse = self.get_response_stage1(chat_history)
            return analyse
        if query and not self.message:
            response = self.get_response_stage2(query, self.analyse)
            return response
        if query and self.message:
            self.message += [{"role":"user","content":query}]
            response = self.llm(self.message)
            if self.verbose:
                print("=====调整后的回复=====")
                print(response)
                print("==========")
            return response
        return "出错，请稍后再试，或联系开发人员"


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


    def update_stories(self):
        """
        TODO 未重写为EQmaster的RAG
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
        system_prompt = ""
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

