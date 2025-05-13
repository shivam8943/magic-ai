import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import os

# --- YOUR CREDENTIALS ---
TOKEN = "8131148603:AAFzVpTJrQeOkYU8qd74lh-ToPKLDUYYsgk"
DEEPAI_API_KEY = "quickstart-QUdJIGlzIGNvbWluZy4uLi4K"

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Photo Magic AI!\nSend a photo and type /enhance to improve it.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = f"{update.message.from_user.id}_photo.jpg"
    await file.download_to_drive(file_path)
    context.user_data["photo_path"] = file_path
    await update.message.reply_text("Photo saved! Now type /enhance to improve it.")

async def enhance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "photo_path" not in context.user_data:
        await update.message.reply_text("Please send a photo first.")
        return

    photo_path = context.user_data["photo_path"]
    await update.message.reply_text("Enhancing your photo...")

    with open(photo_path, "rb") as f:
        response = requests.post(
            "https://api.deepai.org/api/torch-srgan",
            files={"image": f},
            headers={"api-key": DEEPAI_API_KEY}
        )

    try:
        result = response.json()
        output_url = result["output_url"]
        await update.message.reply_photo(photo=output_url, caption="Here is your enhanced photo!")
    except Exception as e:
        await update.message.reply_text("Something went wrong. Please try again.")

# --- MAIN ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enhance", enhance))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
