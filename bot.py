import asyncio
import aiohttp
from hydrogram import Client, filters
from hydrogram.types import Message

# إعدادات البوت والـ API
API_ID = 20182797          # ضع هنا api_id من my.telegram.org
API_HASH = "cb730814928cca90368dd2df4cea4e38"  # ضع هنا api_hash
BOT_TOKEN = "8753485771:AAFzMZj4jxrNwqYLg3okt2Eeoo9ZRO8KLmY" # توكن البوت من @BotFather
HEROKU_API_URL = "https://testbot015.herokuapp.com" # رابط تطبيق هيركو الخاص بك

app = Client("teleyab_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "👋 **أهلاً بك في بوت البحث عن أرقام التيليجرام!**\n\n"
        "أرسل اسم المستخدم (اليوزرنيم) مسبوقاً بـ `@` للبحث عن الرقم المرتبط به."
    )

@app.on_message(filters.text & ~filters.bot)
async def lookup_handler(client: Client, message: Message):
    text = message.text.strip()
    
    # تنظيف اليوزرنيم
    username = text.replace("@", "").strip()
    
    status_msg = await message.reply_text("🔍 **جاري البحث في قاعدة البيانات...**")

    # إرسال طلب إلى سيرفر Teleyab على Heroku
    endpoint = f"{HEROKU_API_URL}/api/lookup" # تأكد من مسار نقطة النهاية (Endpoint)
    payload = {"username": username}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    phone = data.get("phone", "غير متوفر")
                    await status_msg.edit_text(
                        f"✅ **تم العثور على النتيجة:**\n\n"
                        f"👤 **المستخدم:** @{username}\n"
                        f"📞 **رقم الهاتف:** `{phone}`"
                    )
                elif resp.status == 404:
                    await status_msg.edit_text("❌ **لم يتم العثور على رقم مرتبط بهذا المستخدم.**")
                else:
                    await status_msg.edit_text("⚠️ **حدث خطأ أثناء معالجة الطلب من السيرفر.**")
    except Exception as e:
        await status_msg.edit_text(f"⚠️ **فشل الاتصال بسيرفر API:**\n`{str(e)}`")

if __name__ == "__main__":
    app.run()
