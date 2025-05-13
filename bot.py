import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
import requests
import base64

# Telegram Bot Token
TOKEN = "8131148603:AAFzVpTJrQeOkYU8qd74lh-ToPKLDUYYsgk"

# Replicate API Token
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Photo Magic AI! Send a photo and use /enhance to improve it.")

# Handle received photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"{update.message.from_user.id}_photo.jpg"
    await photo_file.download_to_drive(file_path)
    context.user_data["photo"] = file_path
    await update.message.reply_text("Photo received! Now send /enhance to improve it.")

# Enhance command
async def enhance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "photo" not in context.user_data:
        await update.message.reply_text("Please send a photo first.")
        return

    photo_path = context.user_data["photo"]
    await update.message.reply_text("Enhancing your photo...")

    # Convert image to base64
    with open(photo_path, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read()).decode("utf-8")

    # Replicate API call
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "92858f8f27054f8c845d4e49b1c7795d4c7e5d370beff8fdfacbff576f1af0ee",
        "input": {
            "image": f"data:image/jpeg;base64,{base64_image}"
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        await update.message.reply_text("Failed to enhance image. Please try again later.")
        return

    output_url = response.json().get("urls", {}).get("get")
    await update.message.reply_text(f"Photo sent for processing! Check status here:\n{output_url}")

# Placeholder commands
async def ghibli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ghibli Art generation coming soon!")

async def bgremove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Background remover coming soon!")

# Main function
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
