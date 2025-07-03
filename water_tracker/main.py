from chart import show_chart
from reminder import start_reminders
from database import insert_log, get_today_total
import customtkinter as ctk
from datetime import datetime
from reminder import start_reminders
 
# Set appearance
ctk.set_appearance_mode("light")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")
 
# Create main window
app = ctk.CTk()
app.title("HydroMate - Water Intake Tracker")
app.geometry("400x400")
 
# Global variables
daily_goal_ml = 2000
total_intake = get_today_total()
 
# UI Functions
def log_water():
    global total_intake
    try:
        amount = int(entry_ml.get())
        total_intake += amount
        insert_log(amount)
        progress = min(total_intake / daily_goal_ml, 1.0)
        progress_bar.set(progress)
        label_status.configure(text=f"Total: {total_intake} ml / {daily_goal_ml} ml")
        entry_ml.delete(0, ctk.END)
    except ValueError:
        label_status.configure(text="Enter a valid number.")
 
# UI Layout
label_title = ctk.CTkLabel(app, text="Water Intake Tracker", font=("Arial", 20, "bold"))
label_title.pack(pady=20)
 
entry_ml = ctk.CTkEntry(app, placeholder_text="Enter amount (ml)")
entry_ml.pack(pady=10)
 
button_log = ctk.CTkButton(app, text="Log Water", command=log_water)
button_log.pack(pady=10)
chart_button = ctk.CTkButton(
    app,
    text="View Intake Chart",
    command=show_chart,
    fg_color="#3B82F6",  # Nice blue color
    hover_color="#2563EB",  # Darker blue on hover
    text_color="white",
    corner_radius=10,
    font=ctk.CTkFont(size=14, weight="bold")
)
chart_button.pack(pady=10)

interval_var = ctk.StringVar(value="60")
 
label_reminder = ctk.CTkLabel(app, text="Reminder every (minutes):")
label_reminder.pack(pady=(10, 0))
 
dropdown = ctk.CTkComboBox(app, values=["30", "45", "60", "90"], variable=interval_var)
dropdown.pack(pady=(0, 10))
 
progress_bar = ctk.CTkProgressBar(app, width=300)
progress_bar.set(0)
progress_bar.pack(pady=20)
 
label_status = ctk.CTkLabel(app, text="Total: 0 ml / 2000 ml", font=("Arial", 14))
label_status.pack(pady=10)
start_reminders(interval_minutes=int(interval_var.get())) 
# Run app
app.mainloop()
start_reminders(interval_minutes=int(interval_var.get()))
 