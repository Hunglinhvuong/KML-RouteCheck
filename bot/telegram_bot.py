import os
import sys
import asyncio
import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from core.khoangcach import handle_khoangcach
from core.geo_calc import calculate_points
from core.route_manager import list_routes, parse_route_name
from core.map_link import calc_center_zoom
from utils.message_guard import safe_reply
from utils.pathing import resolve_config_path, resolve_data_path


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


load_dotenv(resolve_config_path(), override=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN:
    logger.info("Token loaded thành công: %s...", BOT_TOKEN[:20])
else:
    logger.error("Không tìm thấy BOT_TOKEN trong file cấu hình: %s", resolve_config_path())

def parse_allowed_chat_ids(raw_value: str | None = None):
    raw_value = os.getenv("ALLOWED_CHAT_IDS", "") if raw_value is None else raw_value
    raw_value = (raw_value or "").strip()

    if not raw_value or raw_value.lower() in {"all", "*", "any"}:
        return None

    chat_ids = []
    for item in raw_value.split(","):
        candidate = item.strip()
        if not candidate:
            continue
        try:
            chat_ids.append(int(candidate))
        except ValueError:
            logger.warning("⚠️ Bỏ qua chat ID không hợp lệ: %s", candidate)

    return chat_ids or None


ALLOWED_CHAT_IDS = parse_allowed_chat_ids()
ALLOW_ALL_CHATS = ALLOWED_CHAT_IDS is None
sessions = {}


def allowed(update: Update):
    if ALLOW_ALL_CHATS:
        return True
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
    
    msg += "\n👉 /chon <số>"
    await safe_reply(update, msg)
    
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

def google_maps_direction_link(lat, lon):
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&destination={lat},{lon}"
        "&travelmode=driving"
    )

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
        D = result["distance_goc"]

        kml_path = resolve_data_path(route_file)

        p_start, p_end = calculate_points(kml_path, D)
        start_name, end_name = parse_route_name(route_file)

        lat1, lon1 = p_start
        lat2, lon2 = p_end

        gmaps_link_start = google_maps_direction_link(lat1, lon1)
        gmaps_link_end = google_maps_direction_link(lat2, lon2)

        msg = (
            f"🛣️ <b>Tuyến:</b> {start_name} → {end_name}\n"
            f"📏 <b>Khoảng cách:</b> {int(D)} m\n\n"
            f"▶️ <b>Từ điểm {start_name}:</b>\n"
            f"<code>{p_start[0]:.6f}, {p_start[1]:.6f}</code>\n"
            f"🧭 <b>Dẫn đường Google Maps:</b>\n"
            f"<a href='{gmaps_link_start}'>👉 Mở dẫn đường tới điểm đứt</a>\n\n"
            f"◀️ <b>Từ điểm {end_name}:</b>\n"
            f"<code>{p_end[0]:.6f}, {p_end[1]:.6f}</code>\n"
            f"🧭 <b>Dẫn đường Google Maps:</b>\n"
            f"<a href='{gmaps_link_end}'>👉 Mở dẫn đường tới điểm đứt</a>"
        )

        await update.message.reply_text(msg, parse_mode="HTML")

    except asyncio.TimeoutError:
        await update.message.reply_text(
            "⏱️ Quá thời gian xử lý (5 phút)."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi xử lý: {e}")


async def map_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return

    chat_id = update.effective_chat.id
    session = sessions.get(chat_id)

    if not session or "route" not in session:
        await update.message.reply_text("⚠️ Chưa chọn tuyến. Dùng /tuyen → /chon trước.")
        return

    route_file = session["route"]
    kml_path = resolve_data_path(route_file)

    try:
        # Lấy điểm đầu – cuối
        p_start, p_end = calculate_points(kml_path, 0)

        center_lat, center_lon, zoom = calc_center_zoom(p_start, p_end)

        mymap_id = os.getenv("MYMAP_ID")

        map_link = (
            "https://www.google.com/maps/d/viewer"
            f"?mid={mymap_id}"
            f"&ll={center_lat},{center_lon}"
            f"&z={zoom}"
        )

        msg = (
            "🗺️ <b>Xem tuyến trên Google My Maps</b>\n\n"
            f"👉 <a href=\"{map_link}\">Mở bản đồ các tuyến quang</a>\n\n"
        )

        await update.message.reply_text(
            msg,
            parse_mode="HTML",
            disable_web_page_preview=False
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi map: {e}")


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
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Check config.env")

    if not os.path.isdir(resolve_data_path("")):
        logger.warning("Thư mục data không tồn tại hoặc không thể truy cập: %s", resolve_data_path(""))

    print("======================================")
    print("🚀 TELEGRAM KML ROUTE CHECKER BOT")
    print("✅ Bot is starting...")
    print(f"📡 Allowed chat IDs: {ALLOWED_CHAT_IDS or 'all chats'}")
    print("======================================")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tuyen", tuyen))
    app.add_handler(CommandHandler("chon", chon))
    app.add_handler(CommandHandler("khoangcach", khoangcach))
    app.add_handler(CommandHandler("map", map_cmd))


    app.post_init = notify_startup

    print("🤖 Bot started successfully. Waiting for messages...")

    app.run_polling(
        drop_pending_updates=True,
        stop_signals=None
    )

if __name__ == "__main__":
    main()
