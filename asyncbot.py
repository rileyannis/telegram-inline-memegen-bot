import logging
from aiogram import Bot, Dispatcher, executor, types
import aiohttp, asyncio
import ujson
import requests

with open("config.json", "r") as file_pointer:
    config = ujson.load(file_pointer)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config["api_token"])
dp = Dispatcher(bot)

global image_dict
image_dict = {}

@dp.message_handler(commands=["reload"])
def fetch():
    with requests.get("https://api.imgflip.com/get_memes") as response:
            global image_dict
            image_dict = response.json()

@dp.inline_handler()
async def inline_call(inline_query: types.InlineQuery):
    split_query = inline_query.query.split('"')
    title = split_query[0].strip()
    text = '"'.join(split_query[1::2])
    memes = []
    for meme in image_dict["data"]["memes"]:
        if title in meme["name"].lower():
            memes.append(meme)
    items = [types.InlineQueryResultPhoto(
            id=meme["id"],
            photo_url=meme["url"],
            thumb_url=meme["url"],
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=
                [[types.InlineKeyboardButton("Generate Meme!",callback_data=str(meme["id"])+'"'+text)]]),
            input_message_content=types.InputTextMessageContent(message_text=meme["name"]))
        for meme in memes][:50]
    await bot.answer_inline_query(inline_query.id, results=items, cache_time=1)
    
@dp.callback_query_handler()
async def generate_meme(callback_query: types.CallbackQuery):
    data = callback_query.data.split('"')
    query_data = {
        "template_id":data[0],
        "username":config["username"],
        "password":config["password"]}
    for i in range(1,len(data)):
        query_data[f"boxes[{i-1}][text]"] = data[i]
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post("https://api.imgflip.com/caption_image",data=query_data) as response:
            json_resp = ujson.decode(await response.text())
            if json_resp["success"]:
                image_url = json_resp["data"]["url"]
            else:
                image_url = "ERROR: " + json_resp["error_message"]
            await bot.edit_message_text(inline_message_id=callback_query.inline_message_id, text=image_url)

if __name__ == "__main__":
    fetch()
    executor.start_polling(dp, skip_updates=True)