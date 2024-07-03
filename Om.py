import re
import logging
import tempfile
import os
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram bot token
TOKEN = '7335162364:AAGiFnx4Y4Gon3jDRHlBIYti7NJ06eB3ufM'

# Function to extract credit card details
def extract_cc_details(file_content):
    logger.info("Extracting CC details from file content")
    
    # Patterns to match different CC log formats
    patterns = [
        re.compile(r'(\d{16})\|(\d{2}/\d{4})\|(\d{3,4})'),  # Pattern for format cc|MM/YYYY|CVV
        re.compile(r'(\d{15,16})\|(\d{2})\|(\d{4})\|(\d{3,4})'),  # Pattern for format cc|MM|YYYY|CVV
        re.compile(r'(\d{13,16})\|(\d{2}/\d{2})\|(\d{3,4})'),  # Pattern for format cc|MM/YY|CVV
        re.compile(r'(\d{15,16})\|(\d{2})\|(\d{2})\|(\d{3,4})'),  # Pattern for format cc|MM|YY|CVV
        re.compile(r'(\d{16})\|(\d{2})/(\d{4})\|(\d{3,4})'),  # Pattern for format cc|MM/YYYY|CVV with /
        re.compile(r'(\d{16})\|(\d{4})\|(\d{3,4})'),  # Pattern for format cc|YYYY|CVV
        re.compile(r'(\d{16}) (\d{2}/\d{4}) (\d{3,4})'),  # Pattern for format cc MM/YYYY CVV with spaces
        re.compile(r'(\d{16}) (\d{2})/(\d{4}) (\d{3,4})'),  # Pattern for format cc MM/YYYY CVV with spaces
        re.compile(r'(\d{16}) (\d{2}) (\d{2}) (\d{3,4})'),  # Pattern for format cc MM YY CVV with spaces
        re.compile(r'(\d{16}) (\d{4}) (\d{3,4})'),  # Pattern for format cc YYYY CVV with spaces
        re.compile(r'(\d{13,16}) (\d{2})/(\d{2}) (\d{3,4})'),  # Pattern for format cc MM/YY CVV with spaces
        re.compile(r'(\d{13,16}) (\d{2}/\d{2}) (\d{3,4})'),  # Pattern for format cc MM/YY CVV with spaces
        re.compile(r'(\d{16}) (\d{2}/\d{2}) (\d{3,4})'),  # Pattern for format cc MM/YY CVV with spaces
        re.compile(r'(\d{16}) (\d{2}) (\d{2}) (\d{3,4})'),  # Pattern for format cc MM YY CVV with spaces
        re.compile(r'(\d{13,16}) (\d{2}) (\d{4}) (\d{3,4})'),  # Pattern for format cc MM YYYY CVV with spaces
        re.compile(r'(\d{16}) (\d{2}) (\d{2}) (\d{3,4})'),  # Pattern for format cc MM YY CVV with spaces
        re.compile(r'(\d{16}) (\d{4}) (\d{3,4})'),  # Pattern for format cc YYYY CVV with spaces
        re.compile(r'(\d{13,16}) (\d{2})/(\d{2}) (\d{3,4})'),  # Pattern for format cc MM/YY CVV with spaces
        re.compile(r'(\d{13,16}) (\d{2}/\d{2}) (\d{3,4})'),  # Pattern for format cc MM/YY CVV with spaces
        re.compile(r'(\d{16}) (\d{2}/\d{2}) (\d{3,4})'),  # Pattern for format cc MM/YY CVV with spaces
        re.compile(r'(\d{16}) (\d{2}) (\d{2}) (\d{3,4})'),  # Pattern for format cc MM YY CVV with spaces
    ]

    matches = []
    for pattern in patterns:
        matches.extend(pattern.findall(file_content))
    
    logger.info(f"Matches found: {matches}")
    return matches

# Welcome command handler
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I'm your bot, here are the available commands:\n"
        "/logs - Extract credit card details from a text file\n"
        "\nDeveloper: OM"
    )

# Logs command handler
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Send me a .txt file and I will filter CC details in the format cc|expiry date|cvv.')

# File handler for extracting CC details
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        logger.info("Received a file from the user")
        file = await context.bot.get_file(update.message.document.file_id)
        file_content = await file.download_as_bytearray()
        file_content = file_content.decode('utf-8')
        logger.info("File content received")

        cc_details = extract_cc_details(file_content)
        if cc_details:
            # Create a temporary file to store the extracted credit card details
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                for detail in cc_details:
                    temp_file.write("|".join(detail) + "\n")

            # Read the temporary file and send its content as a document to the user
            with open(temp_file.name, 'rb') as f:
                await update.message.reply_document(InputFile(f, filename='extracted_ccs.txt'), caption="Here are the extracted CC details")

            # Clean up the temporary file
            os.unlink(temp_file.name)

            # Create an inline button for donation
            keyboard = [[InlineKeyboardButton("Donate", url="https://t.me/rundilundlegamera")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send the button
            await update.message.reply_text("If you found this bot useful, consider donating!", reply_markup=reply_markup)
        else:
            await update.message.reply_text("No valid CC details found in the file.")
    except BadRequest as e:
        if "File is too big" in str(e):
            await update.message.reply_text("FILE IS TOO BIG. TRY SENDING SOME SMALLER FILES.")
        else:
            logger.error(f"Error processing file: {e}")
            await update.message.reply_text("There was an error processing the file.")

# Main function to set up the bot
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", welcome))
    application.add_handler(CommandHandler("logs", logs))
    application.add_handler(MessageHandler(filters.Document.MimeType("text/plain"), handle_file))

    application.run_polling()

if __name__ == '__main__':
    main()
            
