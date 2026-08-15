import os
import aiohttp
from hydrogram import Client, filters
from hydrogram.types import Message

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
HEROKU_APP_URL = os.getenv("HEROKU_APP_URL", "https://testbot015.herokuapp.com").rstrip("/")

app = Client("teleyab_runner", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply_text(
        "👋 **أهلاً بك في بوت فحص المعرفات عبر محرك Teleyab!**\n\n"
        "أرسل المعرف (اليوزرنيم) للبحث في قاعدة البيانات."
    )

@app.on_message(filters.text & ~filters.bot)
async def check_user(client: Client, message: Message):
    target = message.text.strip().replace("@", "")
    status = await message.reply_text("🔍 **جاري الفحص عبر محرك Teleyab...**")

    # فحص الرابط ومسار البحث
    lookup_urls = [
        f"{HEROKU_APP_URL}/api/v1/lookup",
        f"{HEROKU_APP_URL}/api/lookup",
        f"{HEROKU_APP_URL}/lookup"
    ]

    found = False
    async with aiohttp.ClientSession() as session:
        for url in lookup_urls:
            try:
                async with session.post(url, json={"username": target, "query": target}, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        phone = data.get("phone") or data.get("number") or data.get("phone_number")
                        if phone:
                            await status.edit_text(
                                f"✅ **نتيجة الفحص:**\n\n"
                                f"🔗 **المعرف:** @{target}\n"
                                f"📞 **رقم الهاتف:** `{phone}`"
                            )
                            found = True
                            break
                    elif resp.status == 404:
                        await status.edit_text("❌ **لم يتم العثور على رقم لهذا المعرف داخل قاعدة بيانات Teleyab.**")
                        found = True
                        break
            except Exception:
                continue

    if not found:
        await status.edit_text(
            "⚠️ **تعذر الوصول لسيرفر Teleyab حالياً.**\n"
            "تأكد من عمل الـ Web Dyno من لوحة تحكم Heroku."
        )

if __name__ == "__main__":
    app.run()
