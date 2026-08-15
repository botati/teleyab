import os
import aiohttp
from hydrogram import Client, filters
from hydrogram.types import Message
from hydrogram.errors import UsernameNotOccupied, UsernameInvalid

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

app = Client("teleyab_master_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply_text(
        "👋 **أهلاً بك في بوت كشف معلومات الحسابات والأرقام!**\n\n"
        "أرسل المعرف (اليوزرنيم) مسبوقاً بـ `@` لجلب كامل بيانات الحساب."
    )

@app.on_message(filters.text & ~filters.bot)
async def fetch_info(client: Client, message: Message):
    raw_user = message.text.strip().replace("@", "")
    status = await message.reply_text("🔍 **جاري فحص الحساب واستخراج البيانات...**")

    try:
        # جلب البيانات الحية المباشرة من تيليجرام
        user = await client.get_users(raw_user)
        
        user_id = user.id
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip() or "غير محدد"
        is_premium = "نعم ⭐" if user.is_premium else "لا"
        phone = user.phone_number if user.phone_number else "مخفي بواسطة الخصوصية"

        # تنسيق الرد النهائي
        result_text = (
            f"✅ **تم العثور على بيانات المستخدم بنجاح:**\n\n"
            f"👤 **الاسم:** {full_name}\n"
            f"🔗 **اليوزر:** @{user.username or raw_user}\n"
            f"🆔 **معرف الحساب (ID):** `{user_id}`\n"
            f"📞 **رقم الهاتف:** `{phone}`\n"
            f"🌟 **حساب مميز (Premium):** {is_premium}\n"
            f"🛡 **نوع الحساب:** {'بوت' if user.is_bot else 'مستخدم حقيقي'}"
        )
        await status.edit_text(result_text)

    except UsernameNotOccupied:
        await status.edit_text("❌ **هذا المعرف غير مسجل أو محذوف.**")
    except UsernameInvalid:
        await status.edit_text("⚠️ **صيغة المعرف غير صحيحة.**")
    except Exception as e:
        await status.edit_text(f"⚠️ **حدث خطأ أثناء جلب البيانات:**\n`{str(e)}`")

if __name__ == "__main__":
    app.run()
