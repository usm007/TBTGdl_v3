from rich.console import Console
from rich.prompt import Prompt
from telethon.tl.types import Channel, Chat, User
from utils import clear_screen, print_header, banner_chats
from crash_logger import log_crash
from gui_notify import show_gui_popup
from video_selector import handle_video_selection
import asyncio

console = Console()


# -------------------- PRINT CHAT LIST --------------------
def print_section(title, items):
    from rich.table import Table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column()
    table.add_column()

    col = []
    for pos, item in enumerate(items):
        display = item["name"]
        col.append(f"[{pos}] {display}")  # Use list position as index display
        if len(col) == 2:
            table.add_row(*col)
            col = []

    if col:
        table.add_row(*col, "")

    if title.lower() == "channels":
        header = "[bold cyan]\n📡 CHANNELS[/bold cyan]\n[cyan]" + "*" * 100 + "[/cyan]"
    elif title.lower() == "groups":
        header = "[bold green]\n👥 GROUPS[/bold green]\n[green]" + "*" * 100 + "[/green]"
    elif title.lower() == "bots":
        header = "[bold yellow]\n🤖 BOTS[/bold yellow]\n[yellow]" + "*" * 100 + "[/yellow]"
    elif title.lower() == "dms":
        header = "[bold magenta]\n💬 DIRECT MESSAGES[/bold magenta]\n[magenta]" + "*" * 100 + "[/magenta]"
    else:
        header = f"\n[bold white]{title.upper()}[/bold white]"

    console.print(header)
    console.print(table)


# -------------------- ANIMATED CHAT LOADER --------------------
async def animated_chat_loader():
    frames = ["📡 Fetching chats", "📡 Fetching chats.", "📡 Fetching chats..", "📡 Fetching chats..."]
    for _ in range(2):
        for f in frames:
            console.print(f"[bold yellow]{f}[/bold yellow]", end="\r")
            await asyncio.sleep(0.3)


# -------------------- MAIN CHAT SELECTION --------------------
async def select_chat(client):
    try:
        while True:  # main category menu
            clear_screen()
            print_header()
            banner_chats()

            console.print("\n[bold yellow]Select chat category:[/bold yellow]")
            console.print("[cyan]1.[/cyan] Channels")
            console.print("[cyan]2.[/cyan] Groups")
            console.print("[cyan]3.[/cyan] Bots")
            console.print("[cyan]4.[/cyan] DMs (Direct Messages)")

            category_choice = Prompt.ask("\nEnter choice")
            if not category_choice.isdigit() or int(category_choice) not in [0, 1, 2, 3, 4]:
                console.print("[red]❌ Invalid choice.[/red]")
                continue

            category_choice = int(category_choice)
            if category_choice == 0:
                return

            await animated_chat_loader()
            chats = await client.get_dialogs()

            filtered_chats = []
            index = 1
            for dialog in chats:
                entity = dialog.entity
                raw_name = (
                    getattr(dialog, "name", None)
                    or getattr(entity, "title", None)
                    or getattr(entity, "first_name", None)
                    or "Unnamed"
                )
                raw_name = raw_name.strip()
                name = raw_name[:37] + "…" if len(raw_name) > 40 else raw_name

                if category_choice == 1 and isinstance(entity, Channel) and not entity.megagroup:
                    filtered_chats.append({"index": index, "entity": entity, "name": name})
                elif category_choice == 2 and (
                    (isinstance(entity, Channel) and entity.megagroup) or isinstance(entity, Chat)
                ):
                    filtered_chats.append({"index": index, "entity": entity, "name": name})
                elif category_choice == 3 and isinstance(entity, User) and getattr(entity, "bot", False):
                    filtered_chats.append({"index": index, "entity": entity, "name": name})
                elif category_choice == 4 and isinstance(entity, User) and not getattr(entity, "bot", False):
                    filtered_chats.append({"index": index, "entity": entity, "name": name})
                else:
                    continue
                index += 1

            if not filtered_chats:
                console.print("[red]❌ No chats found in this category.[/red]")
                continue

            def filter_chats_by_search(chats_list, query):
                if not query:
                    return chats_list
                q = query.lower()
                return [chat for chat in chats_list if q in chat['name'].lower()]

            async def go_back(client_ref):
                # Local callback for going back to same subcategory
                await select_chat(client_ref)

            # --- SEARCH & SELECTION LOOP ---
            search_query = ""
            while True:
                clear_screen()
                print_header()
                banner_chats()

                console.print(f"\n[bold yellow]Search chats (leave empty to show all):[/bold yellow] [dim]{search_query}[/dim]")

                searched_chats = filter_chats_by_search(filtered_chats, search_query)
                if not searched_chats:
                    console.print("[red]❌ No chats found matching your search.[/red]")

                display_chats = [{"index": 0, "entity": None, "name": "🔙 Back"}] + searched_chats
                print_section(
                    "Channels" if category_choice == 1 else
                    "Groups" if category_choice == 2 else
                    "Bots" if category_choice == 3 else
                    "DMs",
                    display_chats
                )

                choice = Prompt.ask("\n🔍 Enter chat index or type search query (or 0 to go back)").strip()

                if choice == "0":
                    break  # go back to category menu

                if choice.isdigit():
                    idx = int(choice)
                    if 0 < idx < len(display_chats):
                        selected_chat = display_chats[idx]
                        await handle_video_selection(client, selected_chat, go_back_callback=lambda c=client: go_back(c))
                    else:
                        console.print("[red]❌ Choice out of range.[/red]")
                        await asyncio.sleep(1)  # small pause before re-prompt
                else:
                    # treat input as new search query string
                    search_query = choice

    except Exception as e:
        log_crash(e)
        try:
            show_gui_popup("Script Error", f"A crash occurred:\n{str(e)}")
        except:
            pass
        console.print(f"[red]❌ Error: {e}[/red]")
