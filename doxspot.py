from telegram import Update
from telegram.ext import Updater, MessageHandler, CallbackContext, filters
import requests
import json
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me a picture with location data.')

def extract_gps_info(image):
    try:
        exif_data = image._getexif()
        if exif_data is not None:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == 'GPSInfo':
                    return {GPSTAGS.get(t, t): v for t, v in value.items()}
        return None
    except Exception as e:
        print(f"Error extracting GPS info: {e}")
        return None

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

    # Open the image using Pillow
    image = Image.open(image_io)

    # Extract GPS coordinates from the image using Pillow
    gps_info = extract_gps_info(image)
    
    # Check if GPSInfo is present
    if gps_info:
        latitude = gps_info.get('GPSLatitude')
        longitude = gps_info.get('GPSLongitude')

        # Create a Google Maps link
        google_maps_link = f'https://www.google.com/maps?q={latitude},{longitude}'

        # Reply with the location link
        update.message.reply_text(f'Location: {google_maps_link}')
    else:
        # If GPSInfo is not present
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
