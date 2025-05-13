import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import time

TOKEN = "8131148603:AAFzVpTJrQeOkYU8qd74lh-ToPKLDUYYsgk"
REPLICATE_API_TOKEN = "r8_PikmNXylQqvGVcLKh1dcIYbnzCEH1KMGykeD"

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Photo Magic AI! Send a photo and use /enhance, /ghibli or /bgremove.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"{update.message.from_user.id}_photo.jpg"
    await photo_file.download_to_drive(file_path)
    context.user_data["photo"] = file_path
    await update.message.reply_text("Photo received! Now send /enhance or /ghibli or /bgremove")

async def enhance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "photo" not in context.user_data:
        await update.message.reply_text("Please send a photo first.")
        return

    photo_path = context.user_data["photo"]
    await update.message.reply_text("Enhancing your photo... Please wait 15-30 seconds.")

    with open(photo_path, "rb") as file:
        image_data = file.read()

    # Upload image to imgur or temp hosting (Replicate needs a public URL)
    img_url = upload_image(image_data)
    if not img_url:
        await update.message.reply_text("Failed to upload image.")
        return

    # Call Replicate API
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "92858f8f27054f8c845d4e49b1c7795d4c7e5d370beff8fdfacbff576f1af0ee",
        "input": {
            "image": img_url
        }
    }

    response = requests.post(url, headers=headers, json=data).json()
    prediction_url = response.get("urls", {}).get("get")
    
    # Wait for processing
    for _ in range(20):
        result = requests.get(prediction_url, headers=headers).json()
        status = result.get("status")
        if status == "succeeded":
            output_url = result.get("output")[0]
            await update.message.reply_photo(photo=output_url)
            return
        elif status == "failed":
            await update.message.reply_text("Enhancement failed.")
            return
        time.sleep(2)

    await update.message.reply_text("Enhancement timed out. Try again.")

def upload_image(image_data):
    try:
        response = requests.post(
            "https://freeimage.host/api/1/upload",
            files={"source": image_data},
            data={"action": "upload", "type": "file"},
        )
        return response.json()["image"]["url"]
    except:
        return None

async def ghibli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ghibli Art generation is under development.")

async def bgremove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Background remover feature coming soon.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enhance", enhance))
    app.add_handler(CommandHandler("ghibli", ghibli))
    app.add_handler(CommandHandler("bgremove", bgremove))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
