import os
import asyncio
import ctypes
import time
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from credentials import load_credentials, save_credentials
from utils import print_error, clear_screen
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console

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


async def show_api_manual():
    manual = """
[bold cyan]=== Telegram API ID & API Hash Setup Guide ===[/bold cyan]

[bold yellow]Step 1:[/bold yellow] Register a Telegram Account
- Download the Telegram app on your device and sign up at [cyan]https://telegram.org[/cyan] if you don’t have an account.

[bold yellow]Step 2:[/bold yellow] Visit Telegram’s API Development Page
- Open your browser and go to [cyan]https://my.telegram.org[/cyan]

[bold yellow]Step 3:[/bold yellow] Log In
- Enter your phone number linked to your Telegram account.
- You will receive a login code in your Telegram app.
- Enter this code on the website to continue.

[bold yellow]Step 4:[/bold yellow] Open API Development Tools
- Click on the ‘API Development Tools’ link.

[bold yellow]Step 5:[/bold yellow] Create a New Application
- Fill out the form:
    • App title (e.g., Telegram Video Downloader)
    • Short name (e.g., tgvd)
    • URL (can be your website or http://localhost)
    • Platform (Desktop, Mobile, etc.)
    • Description (optional)
- Click ‘Create application’.

[bold yellow]Step 6:[/bold yellow] Copy Your API ID and API Hash
- Note the API ID (a number) and API Hash (a secret string).
- Keep your API Hash [red]private[/red] and never share it publicly!

[bold yellow]Step 7:[/bold yellow] Use These Credentials
- Return to this program and enter your API ID and API Hash when prompted.

[green]Press [Enter] to continue...[/green]
"""
    console.print(manual)
    await asyncio.to_thread(input)  # Wait for user to press Enter


async def get_telegram_client():
    session_file = session_name + ".session"
    api_id, api_hash = load_credentials()

    try:
        if not os.path.exists(session_file) or api_id is None or api_hash is None:
            await show_api_manual()

            console.print("🔑 First-time setup. Please enter your Telegram API credentials:")

            api_id_str = await asyncio.to_thread(input, "👉 Enter your API ID: ")
            api_hash_input = await asyncio.to_thread(input, "👉 Enter your API Hash: ")
            phone = await asyncio.to_thread(input, "📱 Enter your phone number (with country code): ")

            try:
                api_id = int(api_id_str.strip())
                api_hash = api_hash_input.strip()
                phone = phone.strip()
            except Exception as e:
                console.print(f"[red]❌ Invalid input: {e}[/red]")
                return None

            save_credentials(api_id, api_hash)

            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()

            if not await client.is_user_authorized():
                await show_progress_bar("Sending login code", seconds=2)
                await client.send_code_request(phone)

                code = await asyncio.to_thread(input, "🔐 Enter the login code sent via Telegram: ")
                try:
                    await client.sign_in(phone, code.strip())
                except SessionPasswordNeededError:
                    password = await asyncio.to_thread(input, "🔑 Two-Step Verification enabled. Enter your password: ")
                    await client.sign_in(password=password.strip())

            show_login_success()

        else:
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()

            if not await client.is_user_authorized():
                print_error("⚠️ Session exists but not authorized.")
                return None

            show_login_success()

        hide_session_file(session_file)
        return client

    except Exception as e:
        print_error(f"Login failed: {e}")
        return None


def hide_session_file(path):
    """
    Hide the main session file and its SQLite journal file (Windows only).
    """
    try:
        FILE_ATTRIBUTE_HIDDEN = 0x02

        # Hide main session file
        if os.path.exists(path):
            ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)

        # Hide SQLite journal file
        journal_path = path + "-journal"
        if os.path.exists(journal_path):
            ctypes.windll.kernel32.SetFileAttributesW(journal_path, FILE_ATTRIBUTE_HIDDEN)

    except Exception:
        pass  # Fail silently
