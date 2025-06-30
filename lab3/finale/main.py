import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime

from app import MainApp

if __name__ == "__main__":
    root = tk.Tk()
    root.title("教师管理系统")
    root.geometry("800x600+200+50")
    root.resizable(True, True)
    root.option_add("*Font", "方正清刻本悦宋简体 10")
    app = MainApp(root)
    root.mainloop()
