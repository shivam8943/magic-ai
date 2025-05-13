import os
import requests
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a photo and I’ll enhance it like Remini!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = "/tmp/input.jpg"
    await photo_file.download_to_drive(photo_path)

    with open(photo_path, 'rb') as img:
        response = requests.post(
            "https://api.deepai.org/api/torch-srgan",
            files={'image': img},
            headers={'api-key': DEEPAI_API_KEY}
        )

    output_url = response.json().get('output_url')
    if output_url:
        image_data = requests.get(output_url).content
        output_path = "/tmp/output.jpg"
        with open(output_path, 'wb') as f:
            f.write(image_data)

        with open(output_path, 'rb') as output_file:
            await update.message.reply_photo(photo=InputFile(output_file), caption="Enhanced!")
    else:
        await update.message.reply_text("Sorry, enhancement failed. Try again later.")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if __name__ == "__main__":
    app.run_polling()
