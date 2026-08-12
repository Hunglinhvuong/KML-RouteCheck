# core/khoangcach.py
async def handle_khoangcach(update, context, sessions):
    chat_id = update.effective_chat.id
    session = sessions.get(chat_id)

    if not session or "route" not in session:
        await update.message.reply_text("⚠️ Chưa chọn tuyến.")
        return None

    try:
        D = float(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text(
            "❌ Vui lòng nhập khoảng cách hợp lệ. Ví dụ: /khoangcach 500"
        )
        return None

    if D < 100:
        await update.message.reply_text(
            "⚠️ Khoảng cách quá nhỏ (tối thiểu 100m)."
        )
        return None
    
    if D > 4000:
        num_blocks = D // 4000
        adjusted_d = D - (num_blocks * 100)
        final_distance = adjusted_d / 1.03
    else:
        final_distance = (D - 30) / 1.02

    return {
        "route_file": session["route"],
        "distance": final_distance,
        "distance_goc": D
    }

