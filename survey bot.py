"""
Telegram So'rovnoma Bot
------------------------
Foydalanuvchidan: Ism, Telefon raqami va Qiziqqan xizmatini so'raydi,
javoblarni "javoblar.csv" fayliga saqlaydi.

O'RNATISH:
    pip install python-telegram-bot --upgrade

ISHGA TUSHIRISH:
    1. @BotFather orqali Telegram'da yangi bot yarating va TOKEN oling
    2. Quyidagi BOT_TOKEN qatoriga o'z tokeningizni qo'ying
    3. python survey_bot.py buyrug'i bilan ishga tushiring
"""

import csv
import os
import logging
from datetime import datetime

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ============ SOZLAMALAR ============
# Token'ni Railway'dagi "Variables" bo'limidan BOT_TOKEN nomi bilan qo'shasiz.
# Agar kompyuteringizda sinab ko'rmoqchi bo'lsangiz, pastdagi qatorga
# tokeningizni qo'yishingiz ham mumkin (ikkinchi argument sifatida).
BOT_TOKEN = os.environ.get("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ_BU_YERGA")
CSV_FILE = "javoblar.csv"

# Suhbat bosqichlari (state'lar)
ISM, TELEFON, XIZMAT = range(3)

# Logging - xatoliklarni ko'rish uchun
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============ CSV FAYLNI TAYYORLASH ============
def init_csv():
    """Agar CSV fayl mavjud bo'lmasa, sarlavha qatori bilan yaratadi."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Sana", "Telegram ID", "Username", "Ism", "Telefon", "Xizmat"])


# ============ SUHBAT BOSQICHLARI ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Botni /start bilan boshlash - ismni so'raydi."""
    await update.message.reply_text(
        "Assalomu alaykum! 👋\n"
        "Bizning qisqa so'rovnomamizga xush kelibsiz.\n\n"
        "Iltimos, to'liq ismingizni kiriting:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ISM


async def get_ism(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ismni saqlaydi, telefon raqamini so'raydi."""
    context.user_data["ism"] = update.message.text
    await update.message.reply_text(
        f"Rahmat, {context.user_data['ism']}!\n\n"
        "Endi telefon raqamingizni kiriting (masalan: +998901234567):"
    )
    return TELEFON


async def get_telefon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Telefon raqamini saqlaydi, xizmat turini so'raydi."""
    context.user_data["telefon"] = update.message.text
    await update.message.reply_text(
        "Qaysi xizmatimiz sizni qiziqtiradi?\n"
        "(Masalan: konsultatsiya, mahsulot, hamkorlik va h.k.)"
    )
    return XIZMAT


async def get_xizmat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Xizmat javobini saqlaydi va barcha ma'lumotlarni CSV'ga yozadi."""
    context.user_data["xizmat"] = update.message.text
    user = update.effective_user

    # CSV'ga yozish
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user.id,
            user.username or "-",
            context.user_data["ism"],
            context.user_data["telefon"],
            context.user_data["xizmat"],
        ])

    await update.message.reply_text(
        "✅ Rahmat! Javoblaringiz muvaffaqiyatli qabul qilindi.\n\n"
        f"Ism: {context.user_data['ism']}\n"
        f"Telefon: {context.user_data['telefon']}\n"
        f"Xizmat: {context.user_data['xizmat']}\n\n"
        "Yaqin orada siz bilan bog'lanamiz!"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """So'rovnomani bekor qilish uchun /cancel buyrug'i."""
    await update.message.reply_text(
        "So'rovnoma bekor qilindi. Qayta boshlash uchun /start ni bosing.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# ============ ASOSIY FUNKSIYA ============
def main():
    init_csv()

    if BOT_TOKEN == "SIZNING_BOT_TOKENINGIZ_BU_YERGA":
        print("XATOLIK: Iltimos, avval BOT_TOKEN o'zgaruvchisiga haqiqiy tokeningizni kiriting!")
        print("Token olish uchun Telegram'da @BotFather ga yozing.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ism)],
            TELEFON: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_telefon)],
            XIZMAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_xizmat)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Bot ishga tushdi... To'xtatish uchun Ctrl+C bosing.")
    app.run_polling()


if __name__ == "__main__":
    main()
