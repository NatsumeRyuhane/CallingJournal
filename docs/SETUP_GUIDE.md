# CallingJournal 开发环境设置指南

本文档帮助你快速设置开发环境，运行实时语音转录系统。

## 🎯 当前功能

- ✅ 拨打电话到手机
- ✅ 实时语音转录（Deepgram Nova-3）
- ✅ 自动 VAD（静音检测）
- ✅ Beep 反馈确认收到
- ⏳ **待完成：LLM 回复 + TTS 输出**

---

## 📋 准备工作

### 1. 安装 ngrok

ngrok 用于将本地服务器暴露到公网，让 Twilio 能够回调。

```bash
# macOS
brew install ngrok

# 或直接下载
# https://ngrok.com/download
```

注册 ngrok 账号并配置 authtoken：
```bash
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

### 2. 获取 API Keys

需要以下 API Keys（私聊获取或自己注册）：

| 服务 | 用途 | 注册地址 |
|------|------|----------|
| **Twilio** | 打电话 | https://www.twilio.com |
| **Deepgram** | 语音转录 | https://deepgram.com |
| **OpenAI** | LLM 回复 | https://platform.openai.com |

### 3. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# Twilio（打电话）
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+17752547971

# Deepgram（语音转录）
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

```

---

## 🚀 运行步骤

### Step 1: 安装依赖

```bash
cd CallingJournal
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: 启动 ngrok

在一个终端窗口：
```bash
ngrok http 8000
```

你会看到类似输出：
```
Forwarding    https://xxxx-xxxx.ngrok-free.dev -> http://localhost:8000
```

**记住这个 https URL！**

### Step 3: 配置 ngrok URL

在 `.env` 文件中添加（或修改 `src/config.py`）：
```env
CALLBACK_URL=https://xxxx-xxxx.ngrok-free.dev
```

或者直接修改 `src/api/webhooks.py` 中的 URL。

### Step 4: 启动服务器

在另一个终端窗口：
```bash
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: 发起测试电话

```bash
# 使用 curl, 给自己手机打电话, 替换下面的手机号
curl -X POST "http://localhost:8000/api/calls/outbound" \
  -H "Content-Type: application/json" \
  -d '{"to_number": "+1XXXXXXXXXX"}'
```

或者用 Python：
```python
import requests

response = requests.post(
    "http://localhost:8000/api/calls/outbound",
    json={"to_number": "+1XXXXXXXXXX"}  # 你的手机号
)
print(response.json())
```

---

## 📞 测试流程

1. 运行上面的脚本，手机会收到来电
2. 接听后会听到 "Connecting to your AI assistant"
3. **按任意数字键**（Trial 账号限制）
4. 开始说话，你会看到实时转录
5. 停顿 ~500ms 后会听到 "嘟" 声
6. 继续说话，重复循环
7. 挂断后看到对话总结

---

## 🔧 后续开发：LLM 集成

### 推荐方案：GPT-4o Audio Streaming

使用 OpenAI 的 audio streaming output，可以直接输出音频，不需要单独的 TTS。

Good luck! 🚀

