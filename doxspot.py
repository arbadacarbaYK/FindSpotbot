from telegram import Update
from telegram.ext import Updater, MessageHandler, CallbackContext, filters
import requests
import os
import magic
import io
import exifread

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me a picture with location data.')

def extract_gps_info(image):
    try:
        tags = exifread.process_file(image)
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            latitude = tags['GPS GPSLatitude'].values[0]
            longitude = tags['GPS GPSLongitude'].values[0]
            return latitude, longitude
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

    try:
        # Use python-magic to identify the file type
        file_type = magic.Magic(mime=True).from_buffer(response.content)

        # Check if the file is a supported image format
        supported_formats = {'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/tiff', 'image/heic'}
        if file_type in supported_formats:
            # Convert the bytes object to a BytesIO object
            image_io = io.BytesIO(response.content)

            # Extract GPS coordinates from the image using exifread
            gps_info = extract_gps_info(image_io)

            # Check if GPSInfo is present
            if gps_info:
                latitude, longitude = gps_info

                # Create a Google Maps link
                google_maps_link = f'https://www.google.com/maps?q={latitude},{longitude}'

                # Reply with the location link
                update.message.reply_text(f'Location: {google_maps_link}')
            else:
                # If GPSInfo is not present
                update.message.reply_text('No location data found in the image.')
        else:
            # If the file is not a supported image format
            update.message.reply_text(f"Please send a valid image. Detected file type: {file_type}")
    except Exception as e:
        # Handle other exceptions
        update.message.reply_text(f'Error processing the image: {e}')

def main() -> None:
    updater = Updater(token=os.getenv("YOUR_BOT_TOKEN"))

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(filters.Filters.photo & ~filters.Filters.command, handle_image))
    dp.add_handler(MessageHandler(filters.Filters.command, start))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
