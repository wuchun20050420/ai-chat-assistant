  # 小吴 AI 聊天小助手 (AI Chat Assistant)

  一个用 FastAPI 搭建的 AI 聊天小作品：在网页里输入问题，后端调用 DeepSeek 大模型，返回 AI 回答，并支持多轮对话记忆。

  ## 功能
  - 🖥️ 网页聊天界面：输入 → 发送 → 显示回答
  - 🧠 多轮对话记忆：能记住你之前说过的话
  - 🔌 通过 DeepSeek API 接入大模型

  ## 技术栈
  Python · FastAPI · DeepSeek API · HTML + JavaScript

  ## 本地运行
  1. 安装依赖：`pip install fastapi uvicorn requests`
  2. 创建 `config.py`，填入你自己的 DeepSeek API Key：
     ```python
     API_KEY = "sk-你的key"
  3. 运行：python main.py
  4. 浏览器打开 http://127.0.0.1:8000

  说明

  config.py 包含个人密钥，不会提交到仓库，需要使用时请自行创建。
