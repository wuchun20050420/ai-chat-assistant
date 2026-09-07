import requests
from config import API_KEY


# 这个文件只负责一件事：拿整段对话去问 DeepSeek
def call_deepseek(messages: list) -> str:
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",
        "messages": messages,
    }
    resp = requests.post(url, headers=headers, json=data)
    return resp.json()["choices"][0]["message"]["content"]
