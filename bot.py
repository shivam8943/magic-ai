import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ.get("TOKEN")
DEEPAI_API_KEY = os.environ.get("DEEPAI_API_KEY")

FREE_EDIT_LIMIT = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["used"] = 0
    await update.message.reply_text("Welcome to Photo Magic AI!\nSend me a photo and I'll enhance it for you!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    used = context.user_data.get("used", 0)

    if used >= FREE_EDIT_LIMIT:
        await update.message.reply_text("Free limit reached. Upgrade to Premium (₹249/month).\nPay via UPI: 8264327023@ybl and send screenshot on support.")
        return

    file = await update.message.photo[-1].get_file()
    file_path = f"temp_{update.effective_user.id}.jpg"
    await file.download_to_drive(file_path)

    with open(file_path, 'rb') as img:
        res = requests.post(
            "https://api.deepai.org/api/torch-srgan",
            files={'image': img},
            headers={'api-key': DEEPAI_API_KEY}
        )

    data = res.json()
    if "output_url" in data:
        await update.message.reply_photo(photo=data["output_url"], caption="Enhanced!")
        context.user_data["used"] = used + 1
    else:
        await update.message.reply_text("Enhancement failed. Try later.")

def main():
    if not TOKEN:
        raise ValueError("Bot TOKEN is missing. Set it in Railway environment.")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
