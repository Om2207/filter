import subprocess
import logging

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def list_installed_packages():
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
    logger.info("Installed packages:\n" + result.stdout)

list_installed_packages()

# Import telegram modules after listing installed packages
try:
    from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    from telegram.error import BadRequest
except ModuleNotFoundError as e:
    logger.error(f"Error importing telegram modules: {e}")
    raise

import re
import tempfile
import os

# Function to extract credit card details
def extract_cc_details(file_content):
    logger.info("Extracting CC details from file content")
    
    # Patterns to match different CC log formats
    patterns = [
        re.compile(r'(\d{16})\|(\d{2}/\d{4})\|(\d{3,4})'),  # Pattern for format cc|MM/YYYY|CVV
        re.compile(r'(\d{15,16})\|(\d{2})\|(\d{4})\|(\d{3,4})')  # Pattern for format cc|MM|YYYY|CVV
    ]

    matches = []
    for pattern in patterns:
        matches.extend(pattern.findall(file_content))
    
    logger.info(f"Matches found: {matches}")
    return matches

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! Send me a .txt file and I will filter CC details in the format cc|expiry date|cvv.')

# File handler
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tr
