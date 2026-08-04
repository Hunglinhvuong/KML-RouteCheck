import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv

from core.route_manager import list_routes
from core.geo_calc import calculate_points
from utils.pathing import resolve_config_path, resolve_data_path


load_dotenv(resolve_config_path())

BOT_TOKEN = os.getenv("DISCORD_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing in config.env")


# =========================
# DISCORD BOT SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
user_sessions = {}


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")


# =========================
# !tuyen <keyword>
# =========================
@bot.command()
async def tuyen(ctx, *, keyword: str):
    routes = list_routes(keyword)

    if not routes:
        await ctx.send("❌ Không tìm thấy tuyến phù hợp")
        return

    msg = "**📍 Các tuyến tìm được:**\n"
    for i, r in enumerate(routes, 1):
        msg += f"{i}. {r}\n"

    msg += "\n👉 Gõ `!chon <số>` để chọn tuyến"
    await ctx.send(msg)

    user_sessions[ctx.author.id] = {"routes": routes}


# =========================
# !chon <index>
# =========================
@bot.command()
async def chon(ctx, index: int):
    session = user_sessions.get(ctx.author.id)

    if not session:
        await ctx.send("⚠️ Gõ `!tuyen <từ khóa>` trước.")
        return

    try:
        route_file = session["routes"][index - 1]
    except IndexError:
        await ctx.send("❌ Số không hợp lệ")
        return

    session["route_file"] = route_file
    await ctx.send(
        f"✅ Đã chọn tuyến **{route_file}**\n👉 Gõ `!khoangcach <mét>`"
    )


# =========================
# !khoangcach <D>
# =========================
@bot.command()
async def khoangcach(ctx, D: float):
    session = user_sessions.get(ctx.author.id)

    if not session or "route_file" not in session:
        await ctx.send("⚠️ Chưa chọn tuyến.")
        return

    kml_path = resolve_data_path(session["route_file"])


    try:
        p_start, p_end = calculate_points(kml_path, D)
    except Exception as e:
        await ctx.send(f"❌ Lỗi xử lý: {e}")
        return

    msg = (
        f"📍 **KẾT QUẢ TRA CỨU**\n"
        f"🛣️ Tuyến: **{session['route_file']}**\n"
        f"📏 Khoảng cách: **{D} m**\n\n"
        f"▶️ **Từ đầu tuyến:**\n"
        f"`{p_start[0]:.6f}, {p_start[1]:.6f}`\n\n"
        f"◀️ **Từ cuối tuyến:**\n"
        f"`{p_end[0]:.6f}, {p_end[1]:.6f}`"
    )

    await ctx.send(msg)


bot.run(BOT_TOKEN)
