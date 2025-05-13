import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import base64
import time

# Environment variables
TOKEN = os.getenv("TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Logging
logging.basicConfig(level=logging.INFO)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Photo Magic AI! Send a photo and then /enhance")

# Photo handler
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    photo_path = f"{update.message.from_user.id}_photo.jpg"
    await file.download_to_drive(photo_path)
    context.user_data["photo_path"] = photo_path
    await update.message.reply_text("Photo received! Now send /enhance")

# /enhance command
async def enhance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "photo_path" not in context.user_data:
        await update.message.reply_text("Please send a photo first.")
        return

    photo_path = context.user_data["photo_path"]
    await update.message.reply_text("Enhancing your photo...")

    with open(photo_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    response = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "version": "92858f8f27054f8c845d4e49b1c7795d4c7e5d370beff8fdfacbff576f1af0ee",
            "input": {
                "image": f"data:image/jpeg;base64,{base64_image}"
            }
        }
    )

    if response.status_code != 201:
        await update.message.reply_text("Failed to send image to AI. Please try again later.")
        return

    prediction = response.json()
    prediction_url = prediction["urls"]["get"]

    # Poll until done
    for _ in range(20):
        result = requests.get(prediction_url, headers={"Authorization": f"Token {REPLICATE_API_TOKEN}"}).json()
        if result["status"] == "succeeded":
            output_url = result["output"]
            await update.message.reply_photo(photo=output_url)
            os.remove(photo_path)
            return
        time.sleep(1)

    await update.message.reply_text("Image enhancement timed out. Please try again later.")

# Main app
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enhance", enhance))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
