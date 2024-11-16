import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

# Telegram user credentials
api_id = "27864178"
api_hash = "7725666062:AAFDvCGRAoyZW_L1-Irszm_I40-c14XKl4Y"
source_channels = [
    "@CoingraphNews",
    "https://t.me/tapswapcode6",
    "https://t.me/MajorDurovPuzzlle",
    "https://t.me/CryptoPlusAr",
    "https://t.me/CryptoWhalesYoutube",
    "https://t.me/MemefiCode",
]
target_channel = "@xeiden_news"

# Set to store IDs of processed messages to avoid duplicates
processed_message_ids = set()


async def check_and_forward_posts(api_id, api_hash, source_channels, target_channel):
    """Check for new posts in source channels and forward them to the target channel."""
    client = TelegramClient('session', api_id, api_hash)
    await client.start()

    try:
        while True:
            for source_channel in source_channels:
                print(f"Checking channel: {source_channel}")
                try:
                    # Fetch recent messages from the current source channel
                    messages = await client(GetHistoryRequest(
                        peer=source_channel,
                        limit=10,  # Fetch the last 10 messages
                        offset_date=None,
                        offset_id=0,
                        max_id=0,
                        min_id=0,
                        add_offset=0,
                        hash=0
                    ))

                    for message in messages.messages:
                        if message.id not in processed_message_ids:
                            # Determine the content of the message
                            if message.photo:
                                caption = message.message or ""  # Use caption if available
                                content_to_post = caption
                            elif message.message:
                                content_to_post = message.message
                            else:
                                content_to_post = None  # Skip messages with no content

                            # Skip messages containing "Telegram | Twitter"
                            if content_to_post and "Telegram | Twitter" in content_to_post:
                                print(f"Skipped message containing 'Telegram | Twitter': {content_to_post}")
                                continue

                            # Forward the message to the target channel
                            if message.photo:
                                await client.forward_messages(target_channel, message)
                                print(f"Forwarded image with caption: {caption}")
                            elif message.message:
                                await client.send_message(target_channel, message.message)
                                print(f"Posted text: {message.message}")

                            # Mark this message as processed
                            processed_message_ids.add(message.id)

                except Exception as e:
                    print(f"Error checking channel {source_channel}: {e}")

            # Wait for 10 seconds before checking again
            await asyncio.sleep(10)

    finally:
        await client.disconnect()


# Execute the async function
if __name__ == "__main__":
    asyncio.run(check_and_forward_posts(api_id, api_hash, source_channels, target_channel))
