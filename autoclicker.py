#!/usr/bin/env python3
import pyautogui
import time
import threading
import tkinter as tk
from tkinter import ttk
from collections import deque
from queue import Queue
import sys
import platform
from pynput.keyboard import Listener, KeyCode, Key

# Platform detection
IS_MAC = sys.platform == 'darwin'
IS_WINDOWS = sys.platform == 'win32'

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

log_queue = Queue()

# Global state
is_clicking = False
click_positions = deque()
current_position_index = 0
root = None
status_var = None
positions_var = None
interval_var = None
button_var = None
log_box = None
status_label = None

GREEN = '#4ade80'
RED = '#f87171'


def log_message(msg):
    log_queue.put(msg)


def process_log_queue():
    try:
        while True:
            msg = log_queue.get_nowait()
            if log_box is not None:
                log_box.config(state='normal')
                log_box.insert('end', msg + '\n')
                log_box.see('end')
                log_box.config(state='disabled')
    except:
        pass
    if root:
        root.after(100, process_log_queue)


def update_gui():
    if status_var:
        status_var.set("CLICKING" if is_clicking else "STOPPED")
    if positions_var:
        positions_var.set(str(len(click_positions)))
    if status_label:
        status_label.config(fg=GREEN if is_clicking else RED)


def toggle_clicking():
    global is_clicking
    if len(click_positions) == 0:
        log_message("No positions recorded! Click 'Record Position' first.")
        return
    is_clicking = not is_clicking
    update_gui()
    log_message("Clicking STARTED" if is_clicking else "Clicking STOPPED")


def record_position():
    x, y = pyautogui.position()
    click_positions.append((x, y))
    update_gui()
    log_message(f"Position recorded: ({x}, {y}) — Total: {len(click_positions)}")


def clear_positions():
    global is_clicking, current_position_index
    click_positions.clear()
    current_position_index = 0
    is_clicking = False
    update_gui()
    log_message("All positions cleared!")


def on_hotkey_press(key):
    try:
        if key == Key.f7:
            record_position()
        elif key == Key.f8:
            clear_positions()
        elif key == Key.f6:
            toggle_clicking()
    except AttributeError:
        pass


def clicking_thread():
    global current_position_index
    while True:
        if is_clicking and len(click_positions) > 0:
            try:
                interval = max(0.0001, float(interval_var.get()))
            except Exception:
                interval = 0.1
            try:
                btn_name = button_var.get()
            except Exception:
                btn_name = 'left'

            positions_list = list(click_positions)
            if positions_list:
                idx = current_position_index % len(positions_list)
                x, y = positions_list[idx]
                try:
                    # Move mouse and click - works on both macOS and Windows
                    pyautogui.moveTo(x, y, duration=0.01)
                    time.sleep(0.02)  # Small delay after moving
                    pyautogui.click(button=btn_name)
                    current_position_index += 1
                except Exception as e:
                    log_message(f"Click error: {type(e).__name__}: {str(e)}")
                    print(f"ERROR: {type(e).__name__}: {str(e)}", flush=True)

            time.sleep(interval)
        else:
            time.sleep(0.01)


def make_btn(parent, text, cmd, color):
    DARK_BG = '#1e1e2e'
    outer = tk.Frame(parent, bg=DARK_BG)
    inner = tk.Frame(outer, bg=color)
    inner.pack(fill='x')
    lbl = tk.Label(inner, text=text, bg=color, fg='#ffffff',
                   font=('Helvetica', 11, 'bold'), pady=10, cursor='hand2')
    lbl.pack(fill='x')
    inner.bind('<Button-1>', lambda e: cmd())
    lbl.bind('<Button-1>', lambda e: cmd())
    return outer


def build_gui():
    global root, status_var, positions_var, interval_var, button_var, log_box, status_label

    DARK_BG = '#1e1e2e'
    CARD_BG = '#2a2a3e'
    ACCENT = '#7c6af7'
    TEXT = '#e0e0f0'
    MUTED = '#9090b0'

    root = tk.Tk()
    root.title("Auto Clicker")
    root.geometry("420x600")
    root.resizable(False, False)
    root.configure(bg=DARK_BG)

    tk.Label(root, text="Auto Clicker", font=('Helvetica', 20, 'bold'),
             bg=DARK_BG, fg=TEXT).pack(pady=(20, 4))
    tk.Label(root, text="Use buttons below or hotkeys",
             font=('Helvetica', 10), bg=DARK_BG, fg=MUTED).pack(pady=(0, 14))

    # Status card
    status_card = tk.Frame(root, bg=CARD_BG)
    status_card.pack(fill='x', padx=20, pady=6)

    tk.Label(status_card, text="Status", font=('Helvetica', 10),
             bg=CARD_BG, fg=MUTED).grid(row=0, column=0, padx=16, pady=(12, 2), sticky='w')
    tk.Label(status_card, text="Positions", font=('Helvetica', 10),
             bg=CARD_BG, fg=MUTED).grid(row=0, column=1, padx=16, pady=(12, 2), sticky='w')

    status_var = tk.StringVar(value="STOPPED")
    positions_var = tk.StringVar(value="0")

    status_label = tk.Label(status_card, textvariable=status_var,
                            font=('Helvetica', 16, 'bold'), bg=CARD_BG, fg=RED)
    status_label.grid(row=1, column=0, padx=16, pady=(0, 12), sticky='w')
    tk.Label(status_card, textvariable=positions_var, font=('Helvetica', 16, 'bold'),
             bg=CARD_BG, fg=ACCENT).grid(row=1, column=1, padx=16, pady=(0, 12), sticky='w')

    status_card.columnconfigure(0, weight=1)
    status_card.columnconfigure(1, weight=1)

    # Settings
    settings_card = tk.Frame(root, bg=CARD_BG)
    settings_card.pack(fill='x', padx=20, pady=6)

    tk.Label(settings_card, text="Click interval (seconds)", font=('Helvetica', 10),
             bg=CARD_BG, fg=MUTED).grid(row=0, column=0, padx=16, pady=(12, 2), sticky='w')
    tk.Label(settings_card, text="Mouse button", font=('Helvetica', 10),
             bg=CARD_BG, fg=MUTED).grid(row=0, column=1, padx=16, pady=(12, 2), sticky='w')

    interval_var = tk.StringVar(value="0.001")
    button_var = tk.StringVar(value="left")

    tk.Entry(settings_card, textvariable=interval_var, width=10,
             font=('Helvetica', 12), bg='#3a3a5e', fg=TEXT,
             insertbackground=TEXT, relief='flat', bd=4
             ).grid(row=1, column=0, padx=16, pady=(0, 4), sticky='w')
    tk.Label(settings_card, text="Any value, e.g. 0.001 or 0.0001",
             font=('Helvetica', 8), bg=CARD_BG, fg=MUTED
             ).grid(row=2, column=0, padx=16, pady=(0, 12), sticky='w')

    ttk.Combobox(settings_card, textvariable=button_var,
                 values=["left", "right", "middle"],
                 width=8, state='readonly', font=('Helvetica', 12)
                 ).grid(row=1, column=1, padx=16, pady=(0, 12), sticky='w')

    settings_card.columnconfigure(0, weight=1)
    settings_card.columnconfigure(1, weight=1)

    # Buttons
    btn_frame = tk.Frame(root, bg=DARK_BG)
    btn_frame.pack(fill='x', padx=20, pady=8)

    make_btn(btn_frame, "Start / Stop", toggle_clicking, '#7c6af7').pack(fill='x', pady=3)
    make_btn(btn_frame, "Record Position", record_position, '#2563eb').pack(fill='x', pady=3)
    make_btn(btn_frame, "Clear Positions", clear_positions, '#dc2626').pack(fill='x', pady=3)

    # Log
    tk.Label(root, text="Log", font=('Helvetica', 10),
             bg=DARK_BG, fg=MUTED).pack(anchor='w', padx=20, pady=(8, 2))

    log_frame = tk.Frame(root, bg=CARD_BG)
    log_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    log_box = tk.Text(log_frame, state='disabled', bg=CARD_BG, fg=TEXT,
                      font=('Courier', 10), relief='flat', bd=8, wrap='word')
    log_box.pack(fill='both', expand=True)

    log_message("Autoclicker ready!")
    log_message("Hotkeys: F6=Start/Stop | F7=Record Position | F8=Clear")
    log_message(f"Platform: {platform.system()} {platform.release()}")

    return root


def main():
    build_gui()

    t = threading.Thread(target=clicking_thread, daemon=True)
    t.start()

    # Start hotkey listener
    listener = Listener(on_press=on_hotkey_press)
    listener.start()

    # Start log queue processor
    root.after(100, process_log_queue)

    root.mainloop()


if __name__ == "__main__":
    main()
