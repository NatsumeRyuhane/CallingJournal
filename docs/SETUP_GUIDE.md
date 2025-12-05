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

# OpenAI（LLM 回复）- 后续需要
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# JWT（随便生成一个）
SECRET_KEY=your-secret-key-here
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
# 使用 curl
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

```python
# 伪代码示例
from openai import OpenAI

client = OpenAI()

# 当检测到用户说完话后
response = client.chat.completions.create(
    model="gpt-4o-audio-preview",
    modalities=["text", "audio"],
    audio={"voice": "alloy", "format": "pcm16"},
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": user_transcript}
    ],
    stream=True
)

# 流式获取音频并发送回 Twilio
for chunk in response:
    if chunk.choices[0].delta.audio:
        audio_data = chunk.choices[0].delta.audio
        # 转换格式并发送到 Twilio WebSocket
        await send_audio_to_twilio(audio_data)
```

### 需要修改的文件

主要修改 `src/api/streams.py`：

1. 在 `🔇 Utterance complete` 时调用 LLM
2. 将 LLM 的音频响应发送回 Twilio WebSocket
3. 处理用户打断（中断当前播放）

### 音频格式转换

- Twilio 发送：`mulaw 8kHz mono`
- Twilio 接收：`mulaw 8kHz mono`
- OpenAI 输出：`pcm16 24kHz` → 需要转换

```python
import audioop

# PCM16 24kHz → mulaw 8kHz
def convert_for_twilio(pcm16_24k: bytes) -> bytes:
    # 降采样 24kHz → 8kHz
    pcm16_8k = audioop.ratecv(pcm16_24k, 2, 1, 24000, 8000, None)[0]
    # PCM16 → mulaw
    mulaw_8k = audioop.lin2ulaw(pcm16_8k, 2)
    return mulaw_8k
```

---

## 📁 项目结构

```
CallingJournal/
├── main.py                 # FastAPI 入口
├── src/
│   ├── api/
│   │   ├── calls.py       # 发起呼叫 API
│   │   ├── webhooks.py    # Twilio 回调
│   │   └── streams.py     # ⭐ WebSocket 处理（重点）
│   ├── services/
│   │   ├── phone_service.py
│   │   ├── llm_service.py # LLM 服务（已有）
│   │   └── transcription_service.py
│   └── config.py          # 配置
├── .env                    # 环境变量（不要提交！）
└── requirements.txt
```

---

## ❓ 常见问题

### Q: 电话打不通？
- 检查 Twilio 账号余额
- 检查手机号是否已在 Twilio 验证（Trial 账号限制）
- 检查 ngrok 是否在运行

### Q: 没有转录结果？
- 检查 Deepgram API Key 是否正确
- 查看服务器日志有无错误

### Q: ngrok URL 变了？
- 每次重启 ngrok 会生成新 URL
- 需要更新配置或使用 ngrok 付费版固定域名

---

## 🎯 下一步目标

1. **集成 LLM** - 用户说完后调用 GPT-4o
2. **TTS 输出** - 将 AI 回复转成语音发回
3. **打断处理** - 用户说话时中断 AI 播放
4. **对话历史** - 保存完整对话记录
5. **Journal 生成** - 通话结束后生成日记

Good luck! 🚀

