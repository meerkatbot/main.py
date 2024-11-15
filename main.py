import os
import json
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime, timedelta

# Telegram user credentials
api_id = "27864178"
api_hash = "dc0774fbe5aebc3871d5edb5069deb2c"
source_channel = "honkai_genshin_arts"
target_channel = "@oasisnewchannel"  # Replace with a chat or channel where you have posting permissions

# File to store posted photo IDs
POSTED_PHOTOS_FILE = "posted_photo_ids.json"

# Load posted photo IDs from a file
def load_posted_photo_ids():
    if os.path.exists(POSTED_PHOTOS_FILE):
        with open(POSTED_PHOTOS_FILE, "r") as file:
            return set(json.load(file))
    return set()

# Save posted photo IDs to a file
def save_posted_photo_ids(ids):
    with open(POSTED_PHOTOS_FILE, "w") as file:
        json.dump(list(ids), file)

# Initialize posted_photo_ids
posted_photo_ids = load_posted_photo_ids()

async def download_and_schedule(api_id, api_hash, source_channel, target_channel):
    # Initialize and start the client
    client = TelegramClient('session', api_id, api_hash)
    await client.start()

    # Initialize schedule and last message ID
    next_scheduled_time = datetime.now()
    last_message_id = 0  # Track the last processed message ID

    while True:
        # Fetch message history from the source channel
        messages = await client(GetHistoryRequest(
            peer=source_channel,
            limit=10,  # Fetch 10 messages at a time
            offset_id=last_message_id,
            offset_date=None,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        # Sort messages in ascending order for sequential processing
        for message in sorted(messages.messages, key=lambda x: x.id):
            if message.photo and message.id not in posted_photo_ids:
                now = datetime.now()
                if now < next_scheduled_time:
                    await asyncio.sleep((next_scheduled_time - now).total_seconds())

                # Download the media and prepare to send
                file = await client.download_media(message.photo)
                caption = message.message or ""  # Use empty string if no caption
                
                # Send the file to the target channel
                await client.send_file(target_channel, file, caption=caption)
                posted_photo_ids.add(message.id)  # Mark the photo as posted
                save_posted_photo_ids(posted_photo_ids)  # Save updated IDs to file
                
                print(f"Posted image with caption: '{caption}' at {datetime.now().strftime('%H:%M')} (scheduled for {next_scheduled_time.strftime('%H:%M')})")
                
                # Schedule the next post exactly 1 hour later
                next_scheduled_time += timedelta(hours=1)

        # Update last_message_id to fetch newer messages in the next iteration
        if messages.messages:
            last_message_id = messages.messages[0].id
        
        # Sleep for 1 minute before checking for new messages
        await asyncio.sleep(60)

# Run the async function
asyncio.run(download_and_schedule(api_id, api_hash, source_channel, target_channel))
