from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from .config import RQA_ST_Liyi_Chroma_Config

# 使用与构建数据库相同的嵌入模型
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

# 重新加载持久化的向量数据库
persist_directory = RQA_ST_Liyi_Chroma_Config.PERSIST_DIRECTORY
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

# 定义一个查询
query = "如何提高情商？"

# 执行查询
results = vectordb.similarity_search_with_score(query, k=3)

# for doc in results:
#     print("\n\n")
#     print("docs:", doc)

# 打印查询结果
for result in results:
    doc = result[0]  # 获取Document对象
    score = result[1]  # 获取相似度分数
    print("\n\n")
    print(f"Document: {doc.page_content}, Score: {score}")

