import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os

# ======= Tere Token & API Key =======
BOT_TOKEN = "8131148603:AAFzVpTJrQeOkYU8qd74lh-ToPKLDUYYsgk"
DEEPAI_API_KEY = "quickstart-QUdJIGlzIGNvbWluZy4uLi4K"
# ====================================

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Photo Magic AI!\nSend a photo and use /enhance to improve it.")

# Handle received photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    file_path = f"{update.message.from_user.id}_photo.jpg"
    await photo.download_to_drive(file_path)
    context.user_data["photo"] = file_path
    await update.message.reply_text("Photo received! Now send /enhance to improve it.")

# Enhance photo using DeepAI
async def enhance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "photo" not in context.user_data:
        await update.message.reply_text("Please send a photo first.")
        return

    photo_path = context.user_data["photo"]
    await update.message.reply_text("Enhancing your photo...")

    response = requests.post(
        "https://api.deepai.org/api/torch-srgan",
        files={"image": open(photo_path, "rb")},
        headers={"api-key": DEEPAI_API_KEY}
    )

    if response.status_code == 200:
        output_url = response.json().get("output_url")
        await update.message.reply_photo(photo=output_url, caption="Here is your enhanced photo!")
    else:
        await update.message.reply_text("Something went wrong while enhancing the photo.")

# Placeholder commands
async def ghibli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ghibli Art feature is coming soon.")

async def bgremove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Background remover feature is under development.")

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enhance", enhance))
    app.add_handler(CommandHandler("ghibli", ghibli))
    app.add_handler(CommandHandler("bgremove", bgremove))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
