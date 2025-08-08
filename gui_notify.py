import tkinter as tk
from tkinter import messagebox

def show_gui_popup(title, message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo(title, message)
    root.destroy()
