# utils/message_guard.py

TELEGRAM_MAX_LEN = 3800  # an toàn < 4096

async def safe_reply(update, text: str):
    if len(text) > TELEGRAM_MAX_LEN:
        await update.message.reply_text(
            "⚠️ Kết quả quá nhiều.\n👉 Vui lòng nhập tìm kiếm chi tiết hơn."
        )
        return
    await update.message.reply_text(text)
