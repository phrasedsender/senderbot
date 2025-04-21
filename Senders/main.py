import asyncio
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import PeerUser

api_id = 20902196  # Replace with your actual API ID
api_hash = '668beb13cf07a998cd1237641ff3c4f3'  # Replace with your actual API hash

accounts_info = [
    {'session': 'accounts/account1', 'phone': '+447424829548'},
    {'session': 'accounts/account2', 'phone': '+447349869901'},
    {'session': 'accounts/account3', 'phone': '+447405283730'},
]

async def login_account(session_name, phone):
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        print(f"[{session_name}] Logging in...")
        await client.send_code_request(phone)
        code = input(f"Enter the code for {phone}: ")
        try:
            await client.sign_in(phone, code)
        except SessionPasswordNeededError:
            password = input(f"2FA Password for {phone}: ")
            await client.sign_in(password=password)
        print(f"[{session_name}] Logged in successfully.")
    await client.disconnect()

async def process_account(session_name):
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()
    print(f"[{session_name}] Running...")

    me = await client.get_me()
    saved = await client.get_input_entity('me')
    messages = await client.get_messages(saved, limit=1)

    if not messages:
        print(f"[{session_name}] No message found in Saved Messages.")
        await client.disconnect()
        return

    message = messages[0]

    async for dialog in client.iter_dialogs():
        if dialog.is_group and dialog.entity.id != me.id:
            try:
                await message.forward_to(dialog.entity)
                print(f"[{session_name}] → Sent to: {dialog.name}")
            except Exception as e:
                print(f"[{session_name}] ❌ Error in {dialog.name}: {e}")

    await client.disconnect()

async def main():
    os.makedirs("accounts", exist_ok=True)
    for acc in accounts_info:
        await login_account(acc['session'], acc['phone'])

    while True:
        for acc in accounts_info:
            try:
                await process_account(acc['session'])
            except Exception as e:
                print(f"[{acc['session']}] ⚠️ Error: {e}")
        print("⏳ Sleeping 1 hour and 1 minute...")
        await asyncio.sleep(3660)

if __name__ == '__main__':
    asyncio.run(main())
