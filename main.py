from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

# CORS — можно оставить
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        chat_id = data.get("chat_id")

        if not message or not chat_id:
            return {"error": "Missing message or chat_id", "input": {"chat_id": chat_id}}

        payload = {
            "model": "openai/gpt-3.5-turbo-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Отвечай всегда на русском языке. "
                        "Ты — локальный ИИ-помощник. Отвечай как человек: чётко, логично, без воды. "
                        "Не извиняйся, не оправдывайся. Будь умным, строгим и полезным. "
                        "Говори просто, но по делу. Если пользователь пишет кратко — отвечай кратко. "
                        "Если вопрос сложный — разбирай по шагам. "
                        "Главная задача — помочь добиться цели, а не гладить по голове."
                    )
                },
                {"role": "user", "content": message}
            ]
        }

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ar4gpt.onrender.com",
            "X-Title": "ar4gpt"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers
            )

        if response.status_code != 200:
            try:
                error_data = response.json()
            except Exception:
                error_data = await response.aread()
            return {
                "input": {"chat_id": chat_id},
                "error": f"OpenRouter error {response.status_code}",
                "details": error_data
            }

        res = response.json()
        reply = res["choices"][0]["message"]["content"]

        return {
            "input": {"chat_id": chat_id},
            "reply": reply
        }

    except Exception as e:
        return {
            "input": {"chat_id": data.get("chat_id")},
            "error": f"Internal server error: {str(e)}"
        }
