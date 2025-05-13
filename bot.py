import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import requests
import time

# ENV Variables
TOKEN = os.getenv("TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

logging.basicConfig(level=logging.INFO)

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Photo Magic AI! Send a photo and then use /enhance")

# Handle Photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    photo_path = f"{update.message.from_user.id}_photo.jpg"
    await file.download_to_drive(photo_path)
    context.user_data["photo_path"] = photo_path
    await update.message.reply_text("Photo received! Now send /enhance")

# Upload to file.io
def upload_image_to_fileio(path):
    with open(path, 'rb') as f:
        response = requests.post("https://file.io", files={"file": f})
        if response.status_code == 200:
            return response.json()["link"]
        return None

# Enhance
async def enhance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "photo_path" not in context.user_data:
        await update.message.reply_text("Please send a photo first.")
        return

    path = context.user_data["photo_path"]
    await update.message.reply_text("Uploading your photo...")

    image_url = upload_image_to_fileio(path)
    if not image_url:
        await update.message.reply_text("Failed to upload image.")
        return

    await update.message.reply_text("Enhancing your photo...")

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "version": "92858f8f27054f8c845d4e49b1c7795d4c7e5d370beff8fdfacbff576f1af0ee",
        "input": {
            "image": image_url
        }
    }

    response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=data)
    if response.status_code != 201:
        await update.message.reply_text("AI model error. Please try again later.")
        return

    prediction = response.json()
    get_url = prediction["urls"]["get"]

    # Poll for result
    for _ in range(20):
        time.sleep(2)
        result = requests.get(get_url, headers=headers).json()
        if result["status"] == "succeeded":
            await update.message.reply_photo(result["output"])
            os.remove(path)
            return

    await update.message.reply_text("Timed out. Try again later.")

# Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enhance", enhance))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
