from telegram import Update
from telegram.ext import Updater, MessageHandler, CallbackContext, filters
import requests
import json
import os
import exifread
import io

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me a picture with location data.')

def handle_image(update: Update, context: CallbackContext) -> None:
    # Get the file ID of the photo
    file_id = update.message.photo[-1].file_id

    # Get the file path from the file ID
    file_path = context.bot.get_file(file_id).file_path

    # Get the file URL
    file_url = f'https://api.telegram.org/file/bot{context.bot.token}/{file_path}'

    # Download the image
    response = requests.get(file_url)

    # Convert the bytes object to a BytesIO object
    image_io = io.BytesIO(response.content)

    # Extract GPS coordinates from the image using exifread
    tags = exifread.process_file(image_io)
    
    # Check if GPSInfo tags are present
    if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
        # Extract latitude and longitude
        latitude = tags['GPS GPSLatitude'].values[0]
        longitude = tags['GPS GPSLongitude'].values[0]

        # Create a Google Maps link
        google_maps_link = f'https://www.google.com/maps?q={latitude},{longitude}'

        # Reply with the location link
        update.message.reply_text(f'Location: {google_maps_link}')
    else:
        # If GPSInfo tags are not present
        update.message.reply_text('No location data found in the image.')


def main() -> None:
    updater = Updater(token=os.getenv("YOUR_BOT_TOKEN"))

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(filters.Filters.photo & ~filters.Filters.command, handle_image))
    dp.add_handler(MessageHandler(filters.Filters.command, start))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
