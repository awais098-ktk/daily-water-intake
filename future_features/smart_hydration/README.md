# Smart Hydration Suggestions

This feature suggests extra water intake based on weather conditions. When it's hotter, the app will recommend drinking more water to stay properly hydrated.

## Implementation Details

### Weather API Integration
- Uses OpenWeatherMap API to fetch current weather data
- Requires API key (free tier available)
- Fetches temperature, humidity, and weather conditions

### Hydration Calculation
- Base hydration recommendation: 2000ml per day
- Temperature adjustment:
  - +200ml for every 5°C above 25°C
  - No change for temperatures between 15-25°C
  - -100ml for every 5°C below 15°C (minimum 2000ml)
- Humidity adjustment:
  - +100ml for humidity > 70%
  - No change for humidity between 40-70%
  - +50ml for humidity < 40% (dry air)
- Activity level adjustment (when wearable integration is implemented):
  - +300ml for high activity
  - +150ml for moderate activity
  - No change for low activity

### User Interface
- Weather widget on dashboard showing current conditions
- Adjusted daily goal with explanation
- Notification when weather conditions change significantly

## Dependencies
- `requests` library for API calls
- OpenWeatherMap API key

## Files
- `weather_api.py`: Handles API calls to OpenWeatherMap
- `hydration_calculator.py`: Calculates recommended water intake based on weather
- `weather_widget.html`: Template for weather widget on dashboard
- `weather_widget.js`: JavaScript for weather widget functionality

## Integration Points
- Dashboard page
- Daily goal calculation
- Notification system

## Testing
1. Test with various weather conditions (use API mocking)
2. Verify calculations for different temperature/humidity combinations
3. Test UI elements in different screen sizes
4. Verify API error handling

## Future Enhancements
- Add forecast-based suggestions ("It will be hot tomorrow, prepare to drink more")
- Integrate with local weather stations for more accurate data
- Consider altitude and air quality in calculations
