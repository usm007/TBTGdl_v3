from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
import os
import asyncio

console = Console()

async def download_with_progress(messages, file_paths, file_sizes, total):
    for i, (msg, file_path, file_size) in enumerate(zip(messages, file_paths, file_sizes), start=1):
        filename = os.path.basename(file_path)
        display_name = filename[:37] + "..." if len(filename) > 40 else filename
        total_mb = file_size / (1024 * 1024)

        console.print(f"\n[bold green]⬇️ Starting:[/bold green] {filename}")

        progress = Progress(
            TextColumn(f"[cyan]{i}/{total} {display_name}"),
            BarColumn(bar_width=30, complete_style="green", finished_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}% | {task.completed:.1f}/{task.total:.1f} MB |", justify="left"),
            TimeRemainingColumn(),
            console=console
        )

        with progress:
            task = progress.add_task("download", total=total_mb)

            def callback(current_bytes, total_bytes):
                current_mb = current_bytes / (1024 * 1024)
                progress.update(task, completed=current_mb)

            await msg.download_media(file=file_path, progress_callback=callback)

        console.print(f"[bold green]✅ Completed:[/bold green] {filename}")
