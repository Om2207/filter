import re
import logging
import time
import requests
from telethon import TelegramClient, events, functions, types
from telethon.tl.custom import Button

# Replace these with your own values
api_id = '26404724'
api_hash = 'c173ec37cd2a6190394a0ec7915e7d50'
bot_token = '6972425077:AAG1-KTOtuR-qVO6siEP1sOnyilWbds8Sy4'
owner_id = 6008343239  # Owner's Telegram ID

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TelegramClient('session_ame', api_id, api_hash)
acc = TelegramClient('acc_ame', api_id, api_hash)

# In-memory set to track seen credit card entries
seen_ccs = set()

# Set to track forbidden words/patterns
forbidden_words = {"badword1", "badword2"}  # Replace with actual words

# Universal function to clean and normalize credit card details
def clean_card_data(cc_number, month, year, cvv):
    formatted_month = month.zfill(2)
    formatted_year = '20' + year if len(year) == 2 else year
    cc_entry = f"{cc_number}|{formatted_month}|{formatted_year}|{cvv}"
    return cc_entry

# Function to extract credit card details in any format
def extract_cc(text):
    formatted_cc = []

    # Enhanced regex for any CC format
    regex_cc = r'\b(\d{13,19})\D+(\d{1,2})\D+(\d{2,4})\D+(\d{3,4})\b'
    matches = re.findall(regex_cc, text)

    for match in matches:
        cc_number, month, year, cvv = match
        cc_entry = clean_card_data(cc_number, month, year, cvv)
        if cc_entry not in seen_ccs:
            formatted_cc.append(cc_entry)
            seen_ccs.add(cc_entry)

    return formatted_cc

@client.on(events.NewMessage(pattern='/start'))
async def welcome(event):
    welcome_message = (
        "Welcome to the Free CC Logs Extractor Bot! 🎉\n"
        "Here are the commands you can use:\n\n"
        "/scrape <chat_name> <amount> - Scrape CC details from a chat\n"
        "/flt - Extract CC details from a text file (reply to the file with this command)\n"
        "/id - Show your user ID and chat ID\n"
        "Developer: [OM](https://t.me/rundilundlegamera)"
    )
    await event.reply(welcome_message)

@client.on(events.NewMessage(pattern='/scrape (.*) (\d+)'))
async def handler(event):
    start_time = time.time()
    found_ccs = 0
    msgg = await event.reply("Please wait...")
    chat_name = event.pattern_match.group(1)
    amount = int(event.pattern_match.group(2))

    try:
        chat = await acc.get_input_entity(chat_name)
        async for message in acc.iter_messages(chat):
            text = message.text
            if text and not any(word in text for word in forbidden_words):
                extracted_ccs = extract_cc(text)
                if extracted_ccs:
                    with open("combos/scrapped.txt", "a") as file:
                        for cc in extracted_ccs:
                            file.write(f"{cc}\n")
                    found_ccs += len(extracted_ccs)
                    if found_ccs >= amount:
                        break

        with open("combos/scrapped.txt", "r") as file:
            lines = file.readlines()
            count = len(lines)

        end_time = time.time()
        time_taken = end_time - start_time

        await client.send_file(
            event.chat_id,
            "combos/scrapped.txt",
            caption=f'CCs Found: `{count}`\nTime Taken: `{time_taken:.2f}s`',
            buttons=[[
                Button.url("Owner", "https://t.me/rundilundlegamera")
            ]]
        )
        await msgg.delete()
        with open("combos/scrapped.txt", "w") as file:
            file.write("")
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        await event.reply("An error occurred during scraping. Please try again later.")

@client.on(events.NewMessage(pattern='/flt'))
async def extract_cc_command(event):
    user_id = event.sender_id
    if event.is_reply and event.message.reply_to_msg_id:
        message = await event.get_reply_message()
        if message.file:
            try:
                start_time = time.time()
                msgg = await event.reply("Please wait...")
                file_path = await message.download_media(f'combos/fil_{user_id}.txt')
                
                with open(file_path, "r") as fie:
                    lines = fie.readlines()
                    with open(f"combos/results_{user_id}.txt", "w") as res:
                        found_ccs = 0
                        for line in lines:
                            credit_cards = extract_cc(line)
                            if credit_cards:
                                formatted_cc = credit_cards[0]
                                res.write(f"{formatted_cc}\n")
                                found_ccs += 1

                end_time = time.time()
                time_taken = end_time - start_time

                await msgg.delete()
                await client.send_file(
                    event.chat_id,
                    f"combos/results_{user_id}.txt",
                    caption=f'CCs Found: `{found_ccs}`\nTime Taken: `{time_taken:.2f}s`',
                    buttons=[[
                        Button.url("Owner", "https://t.me/rundilundlegamera")
                    ]]
                )
            except Exception as e:
                logger.error(f"Error processing file: {e}")
                await event.reply("There was an error processing the file.")
        else:
            await event.reply('No file found. Please reply to a text file.')
    else:
        await event.reply('Please reply to a file.')

@client.on(events.NewMessage(pattern='/id'))
async def id_command(event):
    user_id = event.sender_id
    chat_id = event.chat_id
    await event.reply(f'Your User ID: `{user_id}`\nYour Chat ID: `{chat_id}`')

async def main():
    await acc.start()
    await client.start(bot_token=bot_token)
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
