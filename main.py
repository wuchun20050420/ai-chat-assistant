  import requests
  import uuid
  from fastapi import FastAPI
  from fastapi.responses import HTMLResponse
  from pydantic import BaseModel

  app = FastAPI()

  # DeepSeek 的 key 在本地 config.py 里,别上传到 GitHub
  from config import API_KEY

  # 会话大柜子: { 会话编号: [这句话, 那句话, ...] }
  # 每个编号对应一段独立的对话
  histories = {}


  # /chat 接口收到的数据
  class ChatMessage(BaseModel):
      message: str
      session_id: str = ""   # 这段对话的编号(前端传来的)


  # 真正去问 DeepSeek 的函数
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
      # 找到这个会话的格子;没有就新建一个空格子
      if body.session_id not in histories:
          histories[body.session_id] = []
      history = histories[body.session_id]

      # 把这次说的话记进这个格子
      history.append({"role": "user", "content": body.message})
      # 拿这个格子的整本记录去问 DeepSeek
      reply = call_deepseek(history)
      # 把 AI 的回答也记进格子
      history.append({"role": "assistant", "content": reply})
      return {"reply": reply}


  # 取某个会话的聊天记录(页面刷新后用来恢复显示)
  @app.get("/history")
  async def get_history(session_id: str = ""):
      return {"messages": histories.get(session_id, [])}


  # 首页：点开就能聊天的网页
  @app.get("/", response_class=HTMLResponse)
  async def index():
      return """
      <!DOCTYPE html>
      <html>
      <head>
          <meta charset="utf-8">
          <title>小吴的 AI 小助手</title>
          <style>
              body { font-family: "微软雅黑", Arial; max-width: 640px; margin: 40px auto; padding: 0 20px; }
              .head { display: flex; justify-content: space-between; align-items: center; }
              h2 { text-align: center; }
              #chat { border: 1px solid #ddd; height: 360px; overflow-y: auto; padding: 12px; margin-bottom: 10px;
                      background: #fafafa; border-radius: 8px; }
              .msg { margin: 6px 0; padding: 8px 12px; border-radius: 10px; white-space: pre-wrap; line-height: 1.5;
                     max-width: 85%; }
              .user { background: #d0e6ff; margin-left: auto; text-align: left; }
              .ai { background: #ffffff; border: 1px solid #eee; }
              #row { display: flex; }
              #input { flex: 1; padding: 10px; font-size: 15px; border: 1px solid #ccc; border-radius: 6px; }
              button { padding: 10px 16px; margin-left: 6px; border: none; border-radius: 6px; cursor: pointer; }
              #sendBtn { background: #2f6fed; color: white; }
              #newBtn { background: #e7e7e7; color: #333; }
          </style>
      </head>
      <body>
          <div class="head">
              <h2>小吴的 AI 助手</h2>
              <button id="newBtn" onclick="newChat()">➕ 新对话</button>
          </div>
          <div id="chat"></div>
          <div id="row">
              <input id="input" placeholder="在这里输入你的问题,回车发送...">
              <button id="sendBtn" onclick="send()">发送</button>
          </div>

          <script>
          // 当前会话编号:记录在浏览器本地,刷新页面也不会丢
          function newId() {
              return "c" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
          }
          let sid = localStorage.getItem("ai_sid");
          if (!sid) { sid = newId(); localStorage.setItem("ai_sid", sid); }

          // 往聊天区加一条消息
          function addMsg(role, text) {
              const chat = document.getElementById("chat");
              const d = document.createElement("div");
              d.className = "msg " + role;
              d.textContent = text;
              chat.appendChild(d);
              chat.scrollTop = chat.scrollHeight;
          }

          // 发送消息
          async function send() {
              const input = document.getElementById("input");
              const text = input.value.trim();
              if (!text) return;
              addMsg("user", text);
              input.value = "";

              try {
                  const resp = await fetch("/chat", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ "message": text, "session_id": sid })
                  });
                  const data = await resp.json();
                  addMsg("ai", data.reply);
              } catch (err) {
                  addMsg("ai", "出错了: " + err);
              }
          }

          // 开启新对话:换一个新编号,清空页面
          function newChat() {
              if (!confirm("开启新对话?当前这组对话会保留,但页面会清空。")) return;
              sid = newId();
              localStorage.setItem("ai_sid", sid);
              document.getElementById("chat").innerHTML = "";
          }

          // 页面一打开,把当前会话以前的记录显示出来
          async function loadHistory() {
              try {
                  const resp = await fetch("/history?session_id=" + encodeURIComponent(sid));
                  const data = await resp.json();
                  for (const m of data.messages) {
                      addMsg(m.role === "user" ? "user" : "ai", m.content);
                  }
              } catch (err) {}
          }
          loadHistory();

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
