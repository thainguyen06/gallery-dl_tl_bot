import os
import asyncio
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
import ffmpeg

# Replace with your actual Telegram bot token, app_id, and api_hash
TELEGRAM_BOT_TOKEN = 'TOKEN'
API_ID = ID
API_HASH = 'HASH'
DOWNLOAD_DIR = 'downloads'

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Create a new client instance
app = Client("my_bot", bot_token=TELEGRAM_BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text('Send me a link to download and upload to Telegram.')

def get_video_info(file_path):
    probe = ffmpeg.probe(file_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream:
        duration = float(probe['format']['duration'])
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        return duration, width, height
    return None, None, None

def extract_thumbnail(video_path, thumbnail_path):
    (
        ffmpeg
        .input(video_path, ss="00:00:01")
        .filter('scale', 320, -1)
        .output(thumbnail_path, vframes=1)
        .overwrite_output()
        .run(capture_stdout=True, capture_stderr=True)
    )

async def upload_file(client: Client, message: Message, file_path: str):
    file_extension = os.path.splitext(file_path)[1].lower()
    try:
        if file_extension in ['.mp4', '.mov']:
            duration, width, height = get_video_info(file_path)
            thumbnail_path = f"{file_path}_thumb.jpg"
            extract_thumbnail(file_path, thumbnail_path)
            
            await client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                duration=int(duration) if duration else None,
                width=width,
                height=height,
                thumb=thumbnail_path
            )
            os.remove(thumbnail_path)
        elif file_extension in ['.jpg', '.jpeg', '.png']:
            await client.send_photo(chat_id=message.chat.id, photo=file_path)
        elif file_extension in ['.mp3', '.wav']:
            await client.send_audio(chat_id=message.chat.id, audio=file_path)
        else:
            await client.send_document(chat_id=message.chat.id, document=file_path)
        await asyncio.sleep(1)  # Add a small delay between uploads
    except Exception as e:
        await message.reply_text(f'Failed to upload {os.path.basename(file_path)}: {e}')

@app.on_message(filters.text & ~filters.command(["start"]))
async def download_link(client: Client, message: Message):
    url = message.text
    await message.reply_text('Downloading...')
    try:
        subprocess.run(['gallery-dl', '-d', DOWNLOAD_DIR, url], check=True)
        await message.reply_text('Download complete. Uploading...')
        
        for root, dirs, files in os.walk(DOWNLOAD_DIR):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                await upload_file(client, message, file_path)
                os.remove(file_path)
        
        # Clean up empty directories
        for root, dirs, files in os.walk(DOWNLOAD_DIR, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
        
        await message.reply_text('Upload complete.')
    except subprocess.CalledProcessError:
        await message.reply_text('Failed to download the link.')
    except Exception as e:
        await message.reply_text(f'An error occurred: {e}')

def main():
    app.run()

if __name__ == '__main__':
    main()
