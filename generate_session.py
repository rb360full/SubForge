from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio

async def main():
    api_id = int(input("API ID: "))
    api_hash = input("API Hash: ")
    async with TelegramClient(StringSession(), api_id, api_hash) as client:
        print("String session:\n", client.session.save())

asyncio.run(main())