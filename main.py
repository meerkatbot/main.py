import subprocess
import sys

# Install necessary libraries
required_libraries = [
    "telethon",
    "beautifulsoup4",
    "requests"
]

for lib in required_libraries:
    subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
  import os
import random
import asyncio
import requests
from telethon import TelegramClient
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# Telegram API credentials (Replace these with your actual credentials)
api_id = "27864178"  # Replace with your API ID
api_hash = "dc0774fbe5aebc3871d5edb5069deb2c"  # Replace with your API hash
target_channel = "@oasisnewchannel"

# Website details
base_url = 'https://fapello.com/random/'
ajax_url_template = 'https://fapello.com/ajax/random/page-{page}/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

# Directory to save downloaded images
images_dir = "images"
os.makedirs(images_dir, exist_ok=True)

async def download_and_post_image(client, img_url, title):
    """Downloads a single image, generates a formatted title and hashtag, and posts it to Telegram."""
    img_data = requests.get(img_url, headers=headers).content
    img_name = f"{title.replace(' ', '_')}_{img_url.split('/')[-1]}"
    img_path = os.path.join(images_dir, img_name)

    # Extract and format caption from URL
    match = re.search(r'/content/(?:[a-z]/)*([a-z-]+)/', img_url)
    if match:
        # Extract the name from URL, format to title case and create hashtag
        extracted_name = match.group(1).replace('-', ' ').title()  # Converts to "ABC DEF" format
        hashtag = f"#{match.group(1).replace('-', '_').lower()}"  # Creates "#abc_def" format
        caption = f"{extracted_name} {hashtag}"
    else:
        caption = None if title == "Unknown_Title" else title

    # Save and post the image if not already downloaded
    if not os.path.exists(img_path):
        with open(img_path, 'wb') as f:
            f.write(img_data)
        print(f"Downloaded {img_name}")

        try:
            # Send the image to the target channel with the generated caption
            await client.send_file(target_channel, img_path, caption=caption)
            print(f"Picture has been posted. URL: {img_url}")

            # Remove the image after posting
            os.remove(img_path)

            # Delay before downloading and posting the next image
            delay = random.randint(60, 420)  # Delay between 1 and 7 minutes
            print(f"Waiting for {delay // 60} minutes before next download and post...")
            await asyncio.sleep(delay)

        except Exception as e:
            print(f"Failed to post {img_path}: {e}")

async def download_images_and_post(client):
    """Downloads images from the website and posts each one immediately after downloading."""
    page = 1

    while True:
        ajax_url = ajax_url_template.format(page=page)
        response = requests.get(ajax_url, headers=headers)
        
        if not response.ok:
            print(f"Failed to retrieve page {ajax_url}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        containers = soup.select('.uk-transition-toggle img')  # Adjust selector as needed

        # Stop if no images are found
        if not containers:
            print("No more images found.")
            break

        for container in containers:
            img_url = container.get('src')
            title_div = container.find_previous_sibling('div')
            title = title_div.text.strip() if title_div and title_div.text else "Unknown_Title"
            img_url = urljoin(base_url, img_url) if img_url else None

            # Start download and post task for each image
            if img_url:
                await download_and_post_image(client, img_url, title)
                
        page += 1

async def main():
    # Initialize Telegram client
    client = TelegramClient('session', api_id, api_hash)
    
    try:
        await client.start()
        print("Telegram client started successfully.")
    except Exception as e:
        print(f"Failed to start Telegram client: {e}")
        return  # Exit if client fails to start

    # Download and post each image as it's found
    await download_images_and_post(client)

# Run the main function
asyncio.run(main())
