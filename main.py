import asyncio
from utils import clear_screen, print_header, banner_login
from client import get_telegram_client
from chat_selector import select_chat
from crash_logger import log_crash
from rich.live import Live
from rich.console import Console
from time import sleep

console = Console()

async def animated_startup():
    stages = ["🚀 Starting Telegram Video Downloader", "🚀 Starting Telegram Video Downloader.", 
              "🚀 Starting Telegram Video Downloader..", "🚀 Starting Telegram Video Downloader..."]
    with Live(refresh_per_second=4) as live:
        for _ in range(2):
            for stage in stages:
                live.update(f"[bold cyan]{stage}[/bold cyan]")
                await asyncio.sleep(0.3)

async def main():
    clear_screen()
    print_header()
    await animated_startup()
    banner_login()

    try:
        client = await get_telegram_client()
        if client is None:
            return

        async with client:
            while True:
                clear_screen()
                print_header()
                await select_chat(client)

    except Exception as e:
        log_crash(e)

if __name__ == "__main__":
    asyncio.run(main())
