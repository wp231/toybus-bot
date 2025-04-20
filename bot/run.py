import os
import signal
import asyncio
import discord
from core.bot import Bot
from utils.utils import init_env

init_env()

BOT_TOKEN = os.getenv("BOT_TOKEN") or ""

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = Bot(intents=intents)


class GracefulExit(SystemExit):
    code = 1


async def main():

    def raise_graceful_exit(*args):
        loop.stop()
        raise GracefulExit()

    loop = asyncio.get_event_loop()

    signal.signal(signal.SIGINT, raise_graceful_exit)
    signal.signal(signal.SIGTERM, raise_graceful_exit)

    try:
        async with bot:
            await bot.start(BOT_TOKEN)
    except asyncio.CancelledError:
        pass
    except GracefulExit:
        pass
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
