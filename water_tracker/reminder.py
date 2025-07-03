import threading
import time
from tkinter import messagebox
 
def start_reminders(interval_minutes=60):
    def remind_loop():
        while True:
            time.sleep(interval_minutes * 60)
            try:
                messagebox.showinfo("Hydration Reminder", "Time to drink water!")
            except:
                break  # If the window is closed
 
    thread = threading.Thread(target=remind_loop, daemon=True)
    thread.start()