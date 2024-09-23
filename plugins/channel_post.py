#(©)Codexbotz

import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from helper_func import encode
from pyshorteners import Shortener
import aiohttp


@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start','users','broadcast','batch','genlink','stats']) & ~filters.text)
async def channel_post(client: Client, message: Message):
    if not ENABLE_LINK_CREATION:
        return  # Skip link creation if the feature is disabled
    reply_text = await message.reply_text("Please Wait...!", quote = True)
    try:
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    s = Shortener()
    url = s.dagd.short(link)
    #Add Linkshortx link shortner
    api_url = "https://linkshortx.in/api"
    params={'api': LINKSHORTX_API,'url': link}
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url,params=params,raise_for_status=True) as response:
            data=await response.json()
            url2 =data["shortenedUrl"]


    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    await reply_text.edit(f"<b>Here is your link</b>\n\nNormal_Link: <code>{link}</code>\n\nModern_Link: <code>{url}</code>\n\nLinkshortX: <code>{url2}</code>", reply_markup=reply_markup)

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)

@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):

    if not ENABLE_LINK_CREATION or DISABLE_CHANNEL_BUTTON:
        return  # Skip link creation if the feature is disabled or button is disabled

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
        pass
