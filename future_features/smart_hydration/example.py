"""
Example script to demonstrate the Smart Hydration feature.
"""

import os
import json
from weather_api import WeatherAPI
from hydration_calculator import HydrationCalculator

def main():
    """Main function to demonstrate the Smart Hydration feature."""
    # Get API key from environment variable
    api_key = os.environ.get('OPENWEATHERMAP_API_KEY')
    if not api_key:
        print("Warning: No API key provided. Using mock data.")
        use_mock = True
    else:
        use_mock = False
    
    # Initialize components
    weather_api = WeatherAPI(api_key)
    hydration_calculator = HydrationCalculator(api_key)
    
    # Get city from user
    city = input("Enter city name (or press Enter for default 'London'): ") or "London"
    
    # Get weather data
    if use_mock:
        # Use mock data
        weather_data = {
            "main": {
                "temp": 28.5,
                "humidity": 65
            },
            "weather": [
                {
                    "description": "clear sky",
                    "icon": "01d"
                }
            ],
            "name": city
        }
        print(f"\nUsing mock weather data for {city}:")
    else:
        # Get real weather data
        weather_data = weather_api.get_weather(city=city)
        if not weather_data:
            print(f"Error: Could not fetch weather data for {city}")
            return
        print(f"\nFetched weather data for {city}:")
    
    # Print weather data
    print(f"Temperature: {weather_data['main']['temp']}°C")
    print(f"Humidity: {weather_data['main']['humidity']}%")
    print(f"Condition: {weather_data['weather'][0]['description']}")
    
    # Get activity level from user
    print("\nActivity levels:")
    print("1. Low (sedentary)")
    print("2. Moderate (light exercise)")
    print("3. High (intense exercise)")
    activity_choice = input("Select activity level (1-3, default: 1): ") or "1"
    
    activity_map = {
        "1": "low",
        "2": "moderate",
        "3": "high"
    }
    activity_level = activity_map.get(activity_choice, "low")
    
    # Get base hydration from user
    base_hydration = input("Enter base hydration in ml (default: 2000): ") or "2000"
    try:
        base_hydration = int(base_hydration)
    except ValueError:
        print("Invalid input. Using default 2000ml.")
        base_hydration = 2000
    
    # Calculate hydration recommendation
    recommendation = hydration_calculator.get_recommendation(
        city=city,
        activity_level=activity_level,
        base_hydration=base_hydration
    )
    
    # Print recommendation
    print("\n" + "=" * 50)
    print("HYDRATION RECOMMENDATION")
    print("=" * 50)
    print(f"Base hydration: {recommendation['base']} ml")
    print(f"Temperature adjustment: {recommendation['temp_adjustment']} ml")
    print(f"Humidity adjustment: {recommendation['humidity_adjustment']} ml")
    print(f"Activity adjustment: {recommendation['activity_adjustment']} ml")
    print("-" * 50)
    print(f"Total recommended intake: {recommendation['total']} ml")
    print("-" * 50)
    print(f"Explanation: {recommendation['explanation']}")
    print("=" * 50)
    
    # Save recommendation to file
    save_option = input("\nSave recommendation to file? (y/n, default: n): ").lower() or "n"
    if save_option == "y":
        filename = f"hydration_recommendation_{city.lower().replace(' ', '_')}.json"
        with open(filename, "w") as f:
            json.dump(recommendation, f, indent=2)
        print(f"Recommendation saved to {filename}")

if __name__ == "__main__":
    main()
