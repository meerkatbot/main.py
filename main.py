import os
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime, timedelta

# Telegram user credentials
api_id = "27864178"
api_hash = "dc0774fbe5aebc3871d5edb5069deb2c"
source_channel = "honkai_genshin_arts"
target_channel = "@oasisnewchannel"

# Path to the file storing the last processed message ID
LAST_MESSAGE_FILE = 'last_message_id.txt'

# Function to load the last message ID from the file
def load_last_message_id():
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, 'r') as file:
            return int(file.read().strip())
    return 0  # Default to 0 if the file doesn't exist

# Function to save the last message ID to the file
def save_last_message_id(message_id):
    with open(LAST_MESSAGE_FILE, 'w') as file:
        file.write(str(message_id))

async def download_and_schedule(api_id, api_hash, source_channel, target_channel):
    client = TelegramClient('session', api_id, api_hash)
    await client.start()

    # Initialize schedule and last message ID
    next_scheduled_time = datetime.now()
    last_message_id = load_last_message_id()

    while True:
        # Fetch message history from the source channel
        messages = await client(GetHistoryRequest(
            peer=source_channel,
            limit=10,  # Fetch 10 messages
            offset_id=last_message_id,
            offset_date=None,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        # Process messages in order
        for message in sorted(messages.messages, key=lambda x: x.id):
            if message.photo and message.id > last_message_id:
                now = datetime.now()
                if now < next_scheduled_time:
                    await asyncio.sleep((next_scheduled_time - now).total_seconds())

                # Download the media and prepare to send
                file = await client.download_media(message.photo)
                caption = message.message or ""
                
                # Send the file to the target channel
                await client.send_file(target_channel, file, caption=caption)
                
                print(f"Posted image with caption: '{caption}' at {datetime.now().strftime('%H:%M')} (scheduled for {next_scheduled_time.strftime('%H:%M')})")

                # Update last_message_id to avoid reposting the same message
                last_message_id = message.id

                # Save updated last_message_id to the file
                save_last_message_id(last_message_id)

                # Schedule the next post exactly 1 hour after the last post
                next_scheduled_time += timedelta(hours=1)

        # Sleep for a while before fetching new messages
        await asyncio.sleep(600)  # Sleep for 10 minutes

# Run the async function
asyncio.run(download_and_schedule(api_id, api_hash, source_channel, target_channel))
