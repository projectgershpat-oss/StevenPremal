import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

import config
from database import init_db
from handlers import commands, messages, documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

dp.include_router(commands.router)
dp.include_router(documents.router)
dp.include_router(messages.router)

async def on_startup(bot: Bot):
    init_db()
    logger.info("Database initialized")
    
    if config.WEBHOOK_HOST:
        await bot.set_webhook(config.WEBHOOK_URL)
        logger.info(f"Webhook set to {config.WEBHOOK_URL}")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    logger.info("Webhook removed")

def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    if config.WEBHOOK_HOST:
        app = web.Application()
        webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_handler.register(app, path=config.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        logger.info("Starting webhook server on port 10000")
        web.run_app(app, host="0.0.0.0", port=10000)
    else:
        asyncio.run(dp.start_polling(bot))

if __name__ == "__main__":
    main()
