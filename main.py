import asyncio
import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

api_id = 20401643
api_hash = '70526befa15fb3132d3f43233955250f'

accounts_info = [
    {'session': 'accounts/account1', 'phone': '+447535871120'},
    {'session': 'accounts/account2', 'phone': '+447904491238'},
    {'session': 'accounts/account3', 'phone': '+447507568496'},
]

async def login_all_accounts():
    for acc in accounts_info:
        client = TelegramClient(acc['session'], api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            print(f"[{acc['session']}] Logging in...")
            await client.send_code_request(acc['phone'])
            code = input(f"Enter code for {acc['phone']}: ")
            try:
                await client.sign_in(acc['phone'], code)
            except SessionPasswordNeededError:
                password = input(f"2FA Password for {acc['phone']}: ")
                await client.sign_in(password=password)
            print(f"[{acc['session']}] Logged in.")
        await client.disconnect()

async def process_account(session_name):
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()
    print(f"[{session_name}] → Started sending")

    me = await client.get_me()
    saved = await client.get_input_entity('me')
    messages = await client.get_messages(saved, limit=1)

    if not messages:
        print(f"[{session_name}] ⚠️ No message in Saved Messages.")
        await client.disconnect()
        return

    message = messages[0]

    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            try:
                await message.forward_to(dialog.entity)
                print(f"[{session_name}] ✔️ Sent to: {dialog.name}")
                await asyncio.sleep(2)  # ⏱️ Delay added here
            except Exception as e:
                print(f"[{session_name}] ❌ Error in {dialog.name}: {e}")

    await client.disconnect()

async def main():
    os.makedirs("accounts", exist_ok=True)
    
    await login_all_accounts()

    cycle = 1
    while True:
        print(f"\n🔄 Cycle #{cycle} started\n")
        for acc in accounts_info:
            try:
                await process_account(acc['session'])
            except Exception as e:
                print(f"[{acc['session']}] ⚠️ Error: {e}")
        print(f"\n✅ Cycle #{cycle} complete. ⏳ Sleeping 2 hours...\n")
        cycle += 1
        await asyncio.sleep(7200)

if __name__ == '__main__':
    asyncio.run(main())
