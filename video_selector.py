from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from telethon.tl.types import MessageMediaDocument, DocumentAttributeVideo
from downloader import download_with_progress
from utils import (
    clear_screen,
    print_header,
    print_error,
    print_warning,
    print_success,
    banner_videos,
    banner_downloads,
    sanitize_filename
)
import os
import time
import asyncio
import re

console = Console()
download_folder = "Downloads"
os.makedirs(download_folder, exist_ok=True)

# -------------------- PARSE SELECTION INPUT --------------------
def parse_selection_input(input_str, max_index):
    input_str = input_str.strip().lower()
    if input_str in ("0", "back", "go back"):
        return None
    if input_str == "all":
        return list(range(1, max_index + 1))

    selected_indexes = set()
    for part in input_str.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                if start > end:
                    start, end = end, start
                selected_indexes.update(range(start, end + 1))
            except ValueError:
                continue
        elif part.isdigit():
            selected_indexes.add(int(part))
    return sorted(i for i in selected_indexes if 1 <= i <= max_index)

# -------------------- SCAN VIDEOS WITH RICH PROGRESS --------------------
async def scan_videos_with_progress(client, chat_entity):
    videos = []
    total_messages_to_scan = 1000  # adjust as needed or make dynamic

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        transient=True,
        console=console,
    )

    with progress:
        task = progress.add_task("Scanning for videos...", total=total_messages_to_scan)

        async for msg in client.iter_messages(chat_entity, limit=total_messages_to_scan, reverse=True):
            progress.update(task, advance=1)

            if msg.media and isinstance(msg.media, MessageMediaDocument):
                if any(isinstance(attr, DocumentAttributeVideo) for attr in msg.media.document.attributes):
                    size_mb = msg.media.document.size / (1024 * 1024)
                    attr_name = next(
                        (attr.file_name for attr in msg.media.document.attributes if hasattr(attr, 'file_name')),
                        None
                    )
                    file_name = f"{msg.id}.mp4" if not attr_name else attr_name
                    safe_file_name = sanitize_filename(file_name)

                    videos.append({
                        "id": msg.id,
                        "name": safe_file_name,
                        "size": round(size_mb, 2),
                        "msg": msg
                    })

    return videos

# -------------------- MAIN VIDEO SELECTION --------------------
async def handle_video_selection(client, chat, go_back_callback=None):
    while True:
        clear_screen()
        print_header()
        banner_videos()

        chat_name = chat['name']
        console.print(f"\n[bold yellow]Scanning {chat_name} for videos...[/bold yellow]")

        videos = await scan_videos_with_progress(client, chat['entity'])

        if not videos:
            console.print("\n[bold red]❌ No videos found in this chat.[/bold red]")
            console.input("\n🔁 Press Enter to go back...")
            if go_back_callback:
                await go_back_callback(client)
            return

        videos.sort(key=lambda v: v["id"], reverse=True)

        console.print(f"\n[green]✅ Found {len(videos)} videos in {chat_name}[/green]\n")

        for i, video in enumerate(videos, start=1):
            title = getattr(video["msg"], "message", None) or ""

            # Remove unwanted strings and trim
            title = title.replace("Vid_id:", "").replace("Title:", "").strip()

            # Clean newlines and excess spaces
            video_name = title.replace("\n", " ").replace("\r", " ").strip()

            # If no name, show video ID with extension
            if not video_name:
                ext = "." + video["name"].split(".")[-1]
                video_name = f"{video['id']}{ext}"

            max_len = 70  # max length for name display
            if len(video_name) > max_len:
                video_name = video_name[: max_len - 1] + "…"

            size_bytes = video["size"] * 1024 * 1024
            if size_bytes >= 1024 ** 3:
                size_str = f"{size_bytes / (1024 ** 3):.2f} GB"
            else:
                size_str = f"{size_bytes / (1024 ** 2):.2f} MB"

            console.print(
                f"[green][{i}][/green] [white]{video_name}[/white] [red]✦ {size_str}[/red]"
            )

        choice = console.input(
            "\n[bold yellow]Enter Choice (a / a,b / a-b / all / 0 to go back): [/bold yellow]"
        ).strip()

        parsed = parse_selection_input(choice, len(videos))
        if parsed is None:
            if go_back_callback:
                await go_back_callback(client)
            return
        if not parsed:
            print_error("❌ Invalid selection.")
            await asyncio.sleep(1)
            continue

        to_download = [videos[i - 1] for i in parsed]

        clear_screen()
        print_header()
        banner_downloads()

        console.print("\n[bold cyan]🎯 Videos Selected for Download:[/bold cyan]")
        for vid in to_download:
            console.print(f"• {vid['name']}")
        time.sleep(1.5)

        messages = [vid["msg"] for vid in to_download]
        file_paths = [os.path.join(download_folder, vid["name"]) for vid in to_download]
        file_sizes = [vid["size"] * 1024 * 1024 for vid in to_download]

        await download_with_progress(messages, file_paths, file_sizes, len(to_download))

        print_success("\n✅ All downloads completed successfully! 🎉🎊")

        console.print("[cyan]You can select more videos or enter 0 to go back.[/cyan]")

        choice = console.input("\nPress [bold yellow]Enter[/bold yellow] to select more videos or type [bold red]0[/bold red] to go back: ").strip()
        if choice == "0":
            if go_back_callback:
                await go_back_callback(client)
            return
