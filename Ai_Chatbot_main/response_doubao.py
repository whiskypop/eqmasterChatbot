import os
from openai import OpenAI

ARK_API_KEY = "a7d6f528-2dca-43db-ab3c-97bd6fae9e8b"
client = OpenAI(
    api_key = os.environ.get("ARK_API_KEY"),
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)

# # Non-streaming:
# print("----- standard request -----")
# completion = client.chat.completions.create(
#     model = "ep-20240806155557-d684g",  # your model endpoint ID
#     messages = [
#         {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
#         {"role": "user", "content": "常见的十字花科植物有哪些？"},
#     ],
# )
# print(completion.choices[0].message.content)


def get_response( message ):
    try:
        completion = client.chat.completions.create(
            model = "ep-20240806155557-d684g",  # your model endpoint ID
            messages = message,
            temperature = 0.7,
            top_p = 0.95,
            max_tokens = 800,
        )
        response = completion.choices[0].message.content
    except Exception as e:
        print(f"Failed to make the request. Error: {e}")
        response = "Error"
    return response


# # Streaming:
# print("----- streaming request -----")
# stream = client.chat.completions.create(
#     model = "ep-20240806155557-d684g",  # your model endpoint ID
#     messages = [
#         {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
#         {"role": "user", "content": "常见的十字花科植物有哪些？"},
#     ],
#     stream=True
# )

# for chunk in stream:
#     if not chunk.choices:
#         continue
#     print(chunk.choices[0].delta.content, end="")
# print()