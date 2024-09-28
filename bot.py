import os
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram bot token
TELEGRAM_BOT_TOKEN = '7947881180:AAFbRZ-yu3_fF7WldMiTpCRxkSZJa_PWOyE'
DOWNLOAD_DIR = 'downloads'

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Send me a link to download and upload to Telegram.')

async def download_link(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    await update.message.reply_text('Downloading...')
    try:
        subprocess.run(['gallery-dl', '-d', DOWNLOAD_DIR, url], check=True)
        await update.message.reply_text('Download complete. Uploading...')
        for file_name in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            if os.path.isfile(file_path):
                await context.bot.send_video(chat_id=update.message.chat_id, video=open(file_path, 'rb'))
                os.remove(file_path)
        await update.message.reply_text('Upload complete.')
    except subprocess.CalledProcessError:
        await update.message.reply_text('Failed to download the link.')

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_link))

    application.run_polling()

if __name__ == '__main__':
    main()
