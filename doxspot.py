from telegram.ext import Update, Filters, MessageHandler, CallbackContext
from PIL import Image
import requests
import json

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me a picture with location data.')

def handle_image(update: Update, context: CallbackContext) -> None:
    file_id = update.message.photo[-1].file_id
    file_path = context.bot.get_file(file_id).file_path
    file_url = f'https://api.telegram.org/file/bot{context.bot.token}/{file_path}'

    # Download the image
    response = requests.get(file_url)
    with open('image.jpg', 'wb') as f:
        f.write(response.content)

    # Extract GPS coordinates from the image
    image = Image.open('image.jpg')
    exif_data = image._getexif()
    gps_info = exif_data.get(34853, None)

    if gps_info:
        latitude = gps_info[2][0] + gps_info[2][1] / 60 + gps_info[2][2] / 3600
        longitude = gps_info[4][0] + gps_info[4][1] / 60 + gps_info[4][2] / 3600

        # Use the Google Maps API to generate a map link
        google_maps_link = f'https://www.google.com/maps?q={latitude},{longitude}'
        update.message.reply_text('Location: ' + google_maps_link)
    else:
        update.message.reply_text('No location data found in the image.')

def main() -> None:
    updater = Updater("YOUR_BOT_TOKEN")

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.photo & ~Filters.command, handle_image))
    dp.add_handler(MessageHandler(Filters.command, start))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
