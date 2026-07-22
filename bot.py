import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-railway-app-url.up.railway.app/app")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name if user else "Trader"
    keyboard = [
        [InlineKeyboardButton("🚀 Launch P2P Market", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("💰 My Wallet & Balance", callback_data="wallet")],
        [InlineKeyboardButton("📖 Help & Support", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 Welcome *{name}* to the Ethiopian P2P Crypto Market!\n\n"
        "Securely buy and sell USDT using Telebirr, CBE, Dashen, and more.\n"
        "Tap the button below to open your Mini App trading dashboard."
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.warning("Please set TELEGRAM_BOT_TOKEN environment variable.")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    logger.info("Starting Telegram Bot for P2P Mini App...")
    app.run_polling()
