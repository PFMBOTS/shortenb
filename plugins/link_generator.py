
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from config import *
from helper_func import encode, get_message_id
import logging
from pyrogram import Client, filters
import aiohttp
import asyncio
from pyshorteners import Shortener


logging.basicConfig(filename='app.log', level=logging.DEBUG, encoding='utf-8')

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(
                text="Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return
        
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote=True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://telegram.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>Here is your link</b>\n\n<blockquote>{link}</blockquote>", quote=True, reply_markup=reply_markup)

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch_plus(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(
                text="Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            return
        
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nThis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote=True)
            continue

    while True:
        try:
            num_files_message = await client.ask(
                text="Enter the number of files you want to batch process:",
                chat_id=message.from_user.id,
                filters=filters.text,
                timeout=60
            )
        except:
            return
        
        if num_files_message.text.isdigit():
            num_files = int(num_files_message.text)
            break
        else:
            await num_files_message.reply("❌ Error\n\nPlease enter a valid number.", quote=True)
            continue

    l_msg_id = f_msg_id + num_files - 1

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{l_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://telegram.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await num_files_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)


# Ensure these are set correctly in config.py
SHORTENER_API = os.environ.get("SHORTENER_API", "0aef028290a85e9346edab753a4d557a7458d6e4")
SHORTENER_WEBSITE = os.environ.get("SHORTENER_WEBSITE", "https://urlshortx.io")
SHORTENER_API2 = os.environ.get("SHORTENER_API2", "d86f57a6ae444bdc63318e7b111a02b8edb8a59a")
SHORTENER_WEBSITE2 = os.environ.get("SHORTENER_WEBSITE2", "https://linkshortx.in")

# Define delay to avoid blocking
DELAY = 2

# Function to shorten links using specified API and URL
async def shorten_link(url, api_key, api_url):
    params = {'api': api_key, 'url': url}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, params=params, raise_for_status=True) as response:
            data = await response.json()
            return data["shortenedUrl"]

@Client.on_message(filters.private & filters.command('shortlink1'))
async def shortlink1(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: <code> /shortlink1 https://linkshortx.in</code>")
    
    original_url = message.text.split(maxsplit=1)[1]
    processing_msg = await message.reply_text("♻️ Processing your link, please wait...")
    
    try:
        # Shorten link using the first shortener
        short_url1 = await shorten_link(original_url, SHORTENER_API, f"{SHORTENER_WEBSITE}/api")
        await asyncio.sleep(DELAY)
        await processing_msg.delete()
        await message.reply_text(f"Your shortened link:\n\n<code>{short_url1}</code>")
    except Exception as e:
        await processing_msg.delete()
        await message.reply_text(f"Error occurred: {e}")

@Client.on_message(filters.private & filters.command('shortlink2'))
async def shortlink2(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /shortlink2 <code> /shortlink1 https://linkshortx.in</code>")
    
    original_url = message.text.split(maxsplit=1)[1]
    processing_msg = await message.reply_text("♻️ Processing your link, please wait...")
    
    try:
        # Shorten link using the second shortener
        short_url2 = await shorten_link(original_url, SHORTENER_API2, f"{SHORTENER_WEBSITE2}/api")
        await asyncio.sleep(DELAY)
        await processing_msg.delete()
        await message.reply_text(f"Your shortened link:\n\n<code>{short_url2}</code>")
    except Exception as e:
        await processing_msg.delete()
        await message.reply_text(f"Error occurred: {e}")

