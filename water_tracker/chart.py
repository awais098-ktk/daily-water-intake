import matplotlib.pyplot as plt
from database import get_last_7_days
 
def show_chart():
    data = get_last_7_days()
 
    if not data:
        print("No data available.")
        return
 
    # Separate the data into two lists: dates and amounts
    dates = []
    amounts = []
 
    for row in data:
        dates.append(row[0])
        amounts.append(row[1])
 
    # Plotting the bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(dates, amounts, color="#4DA6FF")
    plt.title("Water Intake - Last 7 Days")
    plt.xlabel("Date")
    plt.ylabel("Total ml")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()