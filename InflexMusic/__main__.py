import asyncio
import importlib
import sys
import signal

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from InflexMusic import LOGGER, app, userbot
from InflexMusic.core.call import Inflex
from InflexMusic.misc import sudo
from InflexMusic.plugins import ALL_MODULES
from InflexMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


def shutdown():
    loop = asyncio.get_event_loop()
    tasks = [task for task in asyncio.all_tasks(loop) if task is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()


def signal_handler(sig, frame):
    LOGGER("InflexMusic").info("Received signal, stopping...")
    asyncio.create_task(app.stop())
    asyncio.create_task(userbot.stop())
    asyncio.create_task(Inflex.stop())
    shutdown()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        sys.exit(1)
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("InflexMusic.plugins" + all_module)
    LOGGER("InflexMusic.plugins").info("Successfully Imported Modules...")
    await userbot.start()
    await Inflex.start()
    try:
        await Inflex.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("InflexMusic").error(
            "Please turn on the videochat of your log group\channel.\n\nStopping Bot..."
        )
        sys.exit(1)
    except:
        pass
    await Inflex.decorators()
    LOGGER("InflexMusic").info(
        "Inflex Music Bot Started Successfully"
    )
    try:
        await idle()
    except KeyboardInterrupt:
        LOGGER("InflexMusic").info("KeyboardInterrupt received, stopping...")
    finally:
        await app.stop()
        await userbot.stop()
        await Inflex.stop()
        LOGGER("InflexMusic").info("Stopping Inflex Music Bot...")


if __name__ == "__main__":
    asyncio.run(init())
