import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime, timedelta

# Telegram user credentials
api_id = "27864178"
api_hash = "dc0774fbe5aebc3871d5edb5069deb2c"
source_channel = "honkai_genshin_arts"
target_channel = "@oasisnewchannel"  # Replace with a chat or channel where you have posting permissions

# Set to store IDs of posted photos to avoid duplicates
posted_photo_ids = set()

async def download_and_schedule(api_id, api_hash, source_channel, target_channel):
    # Initialize and start the client (user account)
    client = TelegramClient('session', api_id, api_hash)
    await client.start()  # Authenticate using the user account
    
    # Set initial schedule to the current time
    next_scheduled_time = datetime.now()

    while True:
        # Fetch message history from the source channel
        messages = await client(GetHistoryRequest(
            peer=source_channel,
            limit=10,  # Fetch last 10 messages
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        # Filter messages for new photos not yet posted
        for message in messages.messages:
            if message.photo and message.id not in posted_photo_ids:
                # Wait until the scheduled time for the next post
                now = datetime.now()
                if now < next_scheduled_time:
                    await asyncio.sleep((next_scheduled_time - now).total_seconds())
                
                # Download and send the file immediately
                file = await client.download_media(message.photo)
                caption = message.message or ""  # Use empty string if no caption

                # Send to the target channel
                await client.send_file(target_channel, file, caption=caption)
                posted_photo_ids.add(message.id)  # Mark photo as posted
                print(f"Posted image with caption: '{caption}' at {datetime.now().strftime('%H:%M')} (scheduled for {next_scheduled_time.strftime('%H:%M')})")

                # Schedule the next post exactly 1 hour after the last scheduled post time
                next_scheduled_time += timedelta(hours=1)

# Run the async function
asyncio.run(download_and_schedule(api_id, api_hash, source_channel, target_channel))
