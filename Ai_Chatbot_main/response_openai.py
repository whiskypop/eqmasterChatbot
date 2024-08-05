import requests
from openai import AzureOpenAI

# Configuration
GPT4V_KEY = ""

# IMAGE_PATH = ""
# encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')

headers = {
    "Content-Type": "application/json",
    "api-key": GPT4V_KEY,
}

GPT4V_ENDPOINT = ""


def get_response( message ):
    # Payload for the request
    payload = {
    "messages": message,
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800
    }
    
    try:
        response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        response = response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        print("Failed to make the request. Error: {e}")
        response = "The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry"
    return response


# from openai import AsyncOpenAI

# def init_aclient():
#     # 将aclient设置为全局变量，以便在其他函数中使用
#     global aclient

#     # 检查是否存在API_KEY环境变量
#     api_key = os.getenv("AZURE_OPENAI_KEY")
#     if api_key is None:
#         raise ValueError("环境变量'AZURE_OPENAI_KEY'未设置。请确保已经定义了API密钥。")
    
#     # 检查是否存在API_BASE环境变量，并据此设置base_url参数
#     api_base = os.getenv("AZURE_OPENAI_URL")
#     if api_base:
#         aclient = AsyncOpenAI(base_url=api_base, api_key=api_key)
#     else:
#         aclient = AsyncOpenAI(api_key=api_key)

# async def async_get_response( message ):
#     if aclient is None:
#         init_aclient()
#     try:
#         response = await aclient.chat.completions.create(\
#             model="gpt4o",\
#             messages = message, \
#             max_tokens = 1000, \
#             temperature = 0.1 ).choices[0].message.content
#     except:
#         print("违规query：", message)
#         response = "The response was filtered due to the prompt triggering Azure OpenAI's content management policy. Please modify your prompt and retry"
#     return response
    