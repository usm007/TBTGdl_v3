
# 📥 The Best Telegram Downloader (CLI) — TBTGdl_v3

A powerful, terminal-based Telegram video downloader built using Python, Telethon, and Rich. Easily scan your chats, select videos (even in ranges), and download them with animated CLI feedback and progress tracking.

---

## 🚀 Features

- ✅ Secure Telegram login via `Telethon`
- 📜 Chat selector with easy navigation
- 📼 Video scanner with proper size and title listing
- 🎯 Smart video selection (`1,2,4-6` supported)
- 📊 CLI download progress with animation and status
- 🗂️ Auto-hides `credentials.txt` and `.session` files on Windows
- 📦 One-click `.exe` compilation via `PyInstaller`
- 🌈 Colorful and dynamic terminal interface with `rich`, `yaspin`

---

## 🛠️ Requirements

- Python 3.8 or later

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## 💻 How to Use

```bash
python main.py
```

On first run:
- Enter your **Telegram API ID**, **API Hash**, and **phone number**
- The app will log you in, list your chats, and allow video selection

---

## 📦 Build as `.exe` (Windows)

You can compile the tool into a standalone `.exe` using [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller --onefile --console main.py
```

After build, you’ll find `main.exe` in the `/dist` folder.

---

## 📂 Folder Structure

```
telegram-video-downloader/
├── main.py
├── client.py
├── chat_selector.py
├── video_selector.py
├── downloader.py
├── credentials.py
├── crash_logger.py
├── utils.py
├── requirements.txt
├── .gitignore
├── README.md
```

---

## 🔒 Security

- `credentials.txt` and `video_downloader.session` are hidden after creation on Windows
- No sensitive information is uploaded or logged externally

---

## 📃 License

This project is licensed under the **MIT License**.

---

## 🌐 Author

Made with ❤️ by [usm007](https://github.com/usm007)
