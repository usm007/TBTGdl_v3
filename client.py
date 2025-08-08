from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from credentials import load_credentials, save_credentials
from utils import print_error, clear_screen
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
import asyncio
import os
import ctypes
import time

console = Console()
session_name = 'video_downloader'

def show_login_success():
    console.print("\n[green bold]✅ Login Successful[/green bold]")
    time.sleep(2)  # Pause for 2 seconds
    clear_screen()  # Clear terminal after showing success

async def show_progress_bar(task_description, seconds=2):
    """
    Unified rich spinner progress bar for short tasks.
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]" + task_description + "[/bold blue]"),
        transient=True,
        console=console
    )
    progress.start()
    task = progress.add_task("work", total=None)
    await asyncio.sleep(seconds)
    progress.stop()

async def get_telegram_client():
    session_file = session_name + ".session"
    api_id, api_hash = load_credentials()

    try:
        if not os.path.exists(session_file) or api_id is None or api_hash is None:
            print("🔑 First-time setup. Please enter your Telegram API credentials:")
            api_id = int(input("👉 Enter your API ID: ").strip())
            api_hash = input("👉 Enter your API Hash: ").strip()
            save_credentials(api_id, api_hash)
            phone = input("📱 Enter your phone number (with country code): ").strip()

            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()

            if not await client.is_user_authorized():
                # Send code request
                await show_progress_bar("Sending login code", seconds=2)
                await client.send_code_request(phone)

                code = input("🔐 Enter the login code sent via Telegram: ").strip()
                try:
                    await client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    password = input("🔑 Two-Step Verification enabled. Enter your password: ").strip()
                    await client.sign_in(password=password)

            show_login_success()

        else:
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()

            if not await client.is_user_authorized():
                print_error("⚠️ Session exists but not authorized.")
                return None

            show_login_success()

        hide_session_file()
        return client

    except Exception as e:
        print_error(f"Login failed: {e}")
        return None

def hide_session_file(path="video_downloader.session"):
    try:
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)
    except Exception:
        pass  # Fail silently
