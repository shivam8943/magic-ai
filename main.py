import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Replace with your actual keys
TELEGRAM_BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
DEEPAI_API_KEY = "PASTE_YOUR_DEEPAI_API_KEY_HERE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Photo Magic AI!\nSend me a photo to enhance it.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    photo_path = "user_photo.jpg"
    await file.download_to_drive(photo_path)

    with open(photo_path, "rb") as image_file:
        response = requests.post(
            "https://api.deepai.org/api/torch-srgan",
            files={"image": image_file},
            headers={"api-key": DEEPAI_API_KEY}
        )
    os.remove(photo_path)

    result = response.json()
    if 'output_url' in result:
        await update.message.reply_photo(photo=result['output_url'], caption="Here is your enhanced photo!")
    else:
        await update.message.reply_text("Failed to enhance image. Please try again later.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
