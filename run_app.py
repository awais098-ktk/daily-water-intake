import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set OpenWeatherMap API key
os.environ['OPENWEATHERMAP_API_KEY'] = '6c5688794c42581bb9715872c8d98449'

try:
    # Import and run the app
    from water_tracker.app import app

    if __name__ == '__main__':
        print("Starting the Water Intake Tracker app...")
        print("Application will be available at: http://127.0.0.1:5001")
        app.run(debug=True, host='127.0.0.1', port=5001)
except Exception as e:
    print(f"Error starting the app: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
