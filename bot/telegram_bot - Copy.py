import os, sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio
from core.khoangcach import handle_khoangcach
from core.geo_calc import calculate_points
from core.route_manager import list_routes, parse_route_name

def get_data_dir():
    """
    data/ luôn nằm cạnh file .exe hoặc thư mục project
    """
    if getattr(sys, 'frozen', False):
        # chạy từ exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # chạy từ python
        base_dir = os.path.abspath(".")

    return os.path.join(base_dir, "data")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

load_dotenv("config.env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_CHAT_IDS = [int(x) for x in os.getenv("ALLOWED_CHAT_IDS").split(",")]

sessions = {}

def allowed(update: Update):
    return update.effective_chat.id in ALLOWED_CHAT_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    await update.message.reply_text(
        "🤖 BOT TRA CỨU TUYẾN KML\n"
        "👉 /tuyen <từ khóa>\n"
        "👉 /chon <số>\n"
        "👉 /khoangcach <mét>"
    )

async def tuyen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    keyword = " ".join(context.args).strip()
    # ✅ GIỚI HẠN ĐỘ DÀI
    if len(keyword) < 5:
        await update.message.reply_text(
            "⚠️ Từ khóa quá ngắn.\n"
            "👉 Vui lòng nhập ít nhất 5 ký tự.\n"
            "Ví dụ: /tuyen quynh"
        )
        return

    keyword = " ".join(context.args)
    routes = list_routes(keyword)
    if not routes:
        await update.message.reply_text("❌ Không tìm thấy tuyến")
        return

    msg = "📍 Các tuyến:\n"
    for i, r in enumerate(routes, 1):
        msg += f"{i}. {r}\n"

    sessions[update.effective_chat.id] = {"routes": routes}
    await update.message.reply_text(msg + "\n👉 /chon <số>")

async def chon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    session = sessions.get(update.effective_chat.id)
    if not session or "routes" not in session:
        await update.message.reply_text("⚠️ Chưa có danh sách tuyến. Dùng /tuyen trước.")
        return

    try:
        idx = int(context.args[0]) - 1
        route = session["routes"][idx]
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Số tuyến không hợp lệ.")
        return

    session["route"] = route
    await update.message.reply_text(f"✅ Đã chọn tuyến: {route}\n👉 /khoangcach <mét>")

async def khoangcach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    try:
        result = await asyncio.wait_for(
            handle_khoangcach(update, context, sessions),
            timeout=300
        )
        if not result:
            return

        route_file = result["route_file"]
        D = result["distance"]

        data_dir = get_data_dir()
        kml_path = os.path.join(data_dir, route_file)

        p_start, p_end = calculate_points(kml_path, D)
        start_name, end_name = parse_route_name(route_file)

        msg = (
            f"🛣️ <b>Tuyến:</b> {start_name} → {end_name}\n"
            f"📏 <b>Khoảng cách:</b> {int(D)} m\n\n"
            f"▶️ <b>Từ điểm {start_name}:</b>\n"
            f"<code>{p_start[0]:.6f}, {p_start[1]:.6f}</code>\n\n"
            f"◀️ <b>Từ điểm {end_name}:</b>\n"
            f"<code>{p_end[0]:.6f}, {p_end[1]:.6f}</code>"
        )

        await update.message.reply_text(msg, parse_mode="HTML")

    except asyncio.TimeoutError:
        await update.message.reply_text(
            "⏱️ Quá thời gian xử lý (5 phút)."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi xử lý: {e}")

async def notify_startup(app):
    for chat_id in ALLOWED_CHAT_IDS:
        try:
            await app.bot.send_message(
                chat_id=chat_id,
                text=(
                    "🤖 **KML ROUTE CHECKER BOT ĐÃ KHỞI ĐỘNG**\n\n"
                    "✅ Hệ thống sẵn sàng phục vụ\n"
                    "📍 Tra cứu tuyến KML\n"
                    "📏 Tính tọa độ theo khoảng cách\n\n"
                    "👉 Gõ /start để xem hướng dẫn"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"⚠️ Không gửi được thông báo tới chat {chat_id}: {e}")

def main():
    print("======================================")
    print("🚀 TELEGRAM KML ROUTE CHECKER BOT")
    print("✅ Bot is starting...")
    print(f"📡 Allowed chat IDs: {ALLOWED_CHAT_IDS}")
    print("======================================")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tuyen", tuyen))
    app.add_handler(CommandHandler("chon", chon))
    app.add_handler(CommandHandler("khoangcach", khoangcach))

    app.post_init = notify_startup

    print("🤖 Bot started successfully. Waiting for messages...")

    app.run_polling(
        drop_pending_updates=True,
        stop_signals=None
    )

if __name__ == "__main__":
    main()
