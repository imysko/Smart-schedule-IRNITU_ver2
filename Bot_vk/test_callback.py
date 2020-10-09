import os

from vkbottle import Bot, Message
from aiohttp import web

token = os.environ.get('VK')

bot = Bot(token=token)
app = web.Application()


async def executor(request: web.Request):
    event = await request.json()
    print(event)
    print(bot)
    emulation = await bot.emulate(event, confirmation_token="3a4d03fd")
    print(emulation)
    return web.Response(text=emulation)


@bot.on.message(text="test", lower=True)
async def wrapper(ans: Message):
    return "Got it."


app.router.add_route("POST", "/vk-bot", executor)
web.run_app(app=app, port=8082)
