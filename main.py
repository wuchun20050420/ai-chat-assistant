  import requests
  from fastapi import FastAPI
  from fastapi.responses import HTMLResponse
  from pydantic import BaseModel
  from config import API_KEY    # key 从 config.py 拿（已挪到顶部 import 区）

  app = FastAPI()

  # 对话记录本：记下用户和 AI 说过的每句话
  history = []


  # /chat 接口收到的数据
  class ChatMessage(BaseModel):
      message: str


  # 真正去问 DeepSeek 的函数（接收整本对话记录）
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


  # /chat 接口
  @app.post("/chat")
  async def chat(body: ChatMessage):
      # 1. 把用户这次说的话记进本子
      history.append({"role": "user", "content": body.message})
      # 2. 把整本本子交给 DeepSeek
      reply = call_deepseek(history)
      # 3. 把 AI 的回答也记进本子
      history.append({"role": "assistant", "content": reply})
      return {"reply": reply}


  # 首页：点开就能聊天的网页
  @app.get("/", response_class=HTMLResponse)
  async def index():
      return """
      <!DOCTYPE html>
      <html>
      <head>
          <meta charset="utf-8">
          <title>我的 AI 小助手</title>
          <style>
              body { font-family: "微软雅黑", Arial; max-width: 600px; margin: 40px auto; padding: 0 20px; }
              h2 { text-align: center; }
              #chat { border: 1px solid #ddd; height: 320px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
              .msg { margin: 5px 0; padding: 8px; border-radius: 6px; white-space: pre-wrap; }
              .user { background: #e3f2fd; text-align: right; }
              .ai { background: #f1f1f1; }
              #row { display: flex; }
              #input { flex: 1; padding: 10px; font-size: 15px; }
              button { padding: 10px 18px; margin-left: 6px; }
          </style>
      </head>
      <body>
          <h2>小吴 AI 助手</h2>
          <div id="chat"></div>
          <div id="row">
              <input id="input" placeholder="在这里输入你的问题...">
              <button onclick="send()">发送</button>
          </div>

          <script>
          async function send() {
              const input = document.getElementById("input");
              const chat = document.getElementById("chat");
              const text = input.value;
              if (!text) return;

              chat.innerHTML += '<div class="msg user">' + text + '</div>';
              input.value = "";

              const resp = await fetch("/chat", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ "message": text })
              });
              const data = await resp.json();

              chat.innerHTML += '<div class="msg ai">' + data.reply + '</div>';
              chat.scrollTop = chat.scrollHeight;
          }

          document.getElementById("input").addEventListener("keypress", function (e) {
              if (e.key === "Enter") send();
          });
          </script>
      </body>
      </html>
      """


  if __name__ == "__main__":
      import uvicorn
      uvicorn.run(app, host="127.0.0.1", port=8000)
