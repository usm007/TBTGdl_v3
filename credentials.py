import os
import ctypes

def set_hidden(filepath):
    try:
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(filepath, FILE_ATTRIBUTE_HIDDEN)
    except Exception:
        pass  # Ignore on non-Windows or failure

def save_credentials(api_id, api_hash):
    path = "credentials.txt"
    with open(path, "w") as f:
        f.write(f"{api_id}\n{api_hash}")
    set_hidden(path)

def load_credentials():
    if not os.path.exists("credentials.txt"):
        return None, None
    with open("credentials.txt", "r") as f:
        lines = f.readlines()
        return int(lines[0].strip()), lines[1].strip()
