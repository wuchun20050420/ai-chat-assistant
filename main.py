from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from deepseek_client import call_deepseek

app = FastAPI()

# 会话大柜子：{ 会话编号: [这句话, 那句话, ...] }
histories = {}


class ChatMessage(BaseModel):
    message: str
    session_id: str = ""


@app.post("/chat")
async def chat(body: ChatMessage):
    if body.session_id not in histories:
        histories[body.session_id] = []
    history = histories[body.session_id]

    history.append({"role": "user", "content": body.message})
    reply = call_deepseek(history)
    history.append({"role": "assistant", "content": reply})
    return {"reply": reply}


@app.get("/history")
async def get_history(session_id: str = ""):
    return {"messages": histories.get(session_id, [])}


@app.get("/")
async def index():
    return FileResponse("index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
