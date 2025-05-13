import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get bot token and API key from Railway environment
TOKEN = os.environ.get("TOKEN")
DEEPAI_API_KEY = os.environ.get("DEEPAI_API_KEY")

# Free users limit
FREE_EDIT_LIMIT = 1

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data["used"] = 0
    await update.message.reply_text("Welcome to Photo Magic AI!\nSend me a photo and I'll enhance it for you!")

# Handle photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    used = context.user_data.get("used", 0)

    if used >= FREE_EDIT_LIMIT:
        await update.message.reply_text("Free limit reached. To use unlimited photo enhancement, upgrade to Premium (₹249/month).\nPay via UPI: 8264327023@ybl and send screenshot on support.")
        return

    file = await update.message.photo[-1].get_file()
    file_path = f"{user_id}_photo.jpg"
    await file.download_to_drive(file_path)

    # Upload to DeepAI
    with open(file_path, 'rb') as image_file:
        response = requests.post(
            "https://api.deepai.org/api/torch-srgan",
            files={'image': image_file},
            headers={'api-key': DEEPAI_API_KEY}
        )

    data = response.json()
    if "output_url" in data:
        await update.message.reply_photo(photo=data["output_url"], caption="Here’s your enhanced photo!")
        context.user_data["used"] = used + 1
    else:
        await update.message.reply_text("Failed to enhance image. Please try again later.")

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
