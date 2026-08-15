import os
import aiohttp
from hydrogram import Client, filters
from hydrogram.types import Message

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
# الاتصال بسيرفر Teleyab (Go API)
TELEYAB_API = "http://localhost:" + os.getenv("PORT", "8080")

app = Client("teleyab_runner", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.text & ~filters.bot)
async def check_user(client: Client, message: Message):
    target = message.text.strip().replace("@", "")
    status = await message.reply_text("🔍 **جاري الفحص عبر محرك Teleyab...**")
    
    async with aiohttp.ClientSession() as session:
        try:
            # إرسال استعلام البحث لمحرك teleyab Go API
            async with session.post(f"{TELEYAB_API}/api/v1/lookup", json={"query": target}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    phone = data.get("phone", "غير متوفر")
                    await status.edit_text(
                        f"✅ **نتيجة Teleyab:**\n\n"
                        f"🔗 **المعرف:** @{target}\n"
                        f"📞 **رقم الهاتف:** `{phone}`"
                    )
                else:
                    await status.edit_text("❌ **لم يعثر محرك Teleyab على رقم لهذا المعرف في قاعدة بياناته.**")
        except Exception as e:
            await status.edit_text(f"⚠️ **خطأ في الاتصال بمحرك Teleyab:**\n`{str(e)}`")

if __name__ == "__main__":
    app.run()
