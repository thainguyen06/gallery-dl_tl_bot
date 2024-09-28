import os
import subprocess
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram bot token
TELEGRAM_BOT_TOKEN = '7947881180:AAFbRZ-yu3_fF7WldMiTpCRxkSZJa_PWOyE'
DOWNLOAD_DIR = 'downloads'

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def start(update, context):
    update.message.reply_text('Send me a link to download and upload to Telegram.')

def download_link(update, context):
    url = update.message.text
    update.message.reply_text('Downloading...')
    try:
        subprocess.run(['gallery-dl', '-d', DOWNLOAD_DIR, url], check=True)
        update.message.reply_text('Download complete. Uploading...')
        for file_name in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            context.bot.send_video(chat_id=update.message.chat_id, video=open(file_path, 'rb'))
            os.remove(file_path)
        update.message.reply_text('Upload complete.')
    except subprocess.CalledProcessError:
        update.message.reply_text('Failed to download the link.')

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_link))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
