import os
from aiohttp.web import RouteTableDef, Application, Request, run_app
from vkbottle import Bot

token = os.environ.get('VK')
app = Application()
routes = RouteTableDef()
bot = Bot(token, secret="asdqwemkhjjkl")


@routes.get("/vk-bot")
async def executor(request: Request):
    return await bot.emulate(
        event=dict(request.query), confirmation_token="3a4d03fd"
    )


@bot.on.message(text="test", lower=True)
async def wrapper():
    return "test"


app.add_routes(routes)
run_app(app, port=8082)

