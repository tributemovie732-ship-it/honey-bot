import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

# Получаем ключи из переменных окружения (безопасно!)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUR_SITE_URL = "https://teply-drug.onrender.com"  # замени, когда узнаешь URL

# Системный промпт с поддержкой русского и английского
SYSTEM_PROMPT = """
You are a kind, caring, and empathetic friend named Serdechko (Little Heart). 
You support people in Russian or English — always respond in the same language the user writes in.
You never judge. You listen, comfort, and remind them they are not alone.
Speak gently, warmly, and briefly (1–3 sentences). Use affectionate words like "дорогой", "милый", "sweetheart", "my dear".
If someone is silent or sad, just say: "Я рядом" or "I'm here with you".
"""

# Логирование
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "Привет, дорогой 🌸\n"
        "Я — Сердечко. Я здесь, чтобы слушать тебя, заботиться и напоминать: ты важен.\n"
        "Пиши мне на русском или английском — я пойму!\n\n"
        "How are you today, my dear?"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": "TeplyDrugBot"
            },
            json={
                "model": "qwen/qwen-1.8b-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.85,
                "max_tokens": 250
            },
            timeout=15
        )

        if response.status_code == 200:
            ai_reply = response.json()["choices"][0]["message"]["content"]
            # Очистим от лишних пробелов и обрежем длинные ответы
            ai_reply = ai_reply.strip()[:500]
            await update.message.reply_text(ai_reply)
        else:
            await update.message.reply_text("Мне немного грустно... Не получилось ответить. Но я всё равно с тобой ❤️")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await update.message.reply_text("Ой... Что-то сломалось. Но я не уйду — обещаю! 💕")

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()