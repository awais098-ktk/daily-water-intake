# Water Intake Tracker - API Testing Guide

This guide provides comprehensive instructions for testing all API endpoints in your Water Intake Tracker application.

## Prerequisites

1. **Start the Flask App**:
   ```bash
   cd water_tracker
   python app.py
   ```
   The app will run on `http://127.0.0.1:8080`

2. **Authentication Required**: Most APIs require login. Use these credentials:
   - Username: `demo`
   - Password: `demo123`

## Testing Tools

### Option 1: Using cURL (Command Line)
### Option 2: Using Python requests
### Option 3: Using Postman/Insomnia
### Option 4: Using Browser Developer Tools

## API Endpoints Overview

### 🔐 Authentication APIs

#### 1. Login (Required for most APIs)
```bash
# cURL
curl -X POST http://127.0.0.1:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo123" \
  -c cookies.txt

# Python
import requests
session = requests.Session()
login_data = {'username': 'demo', 'password': 'demo123'}
response = session.post('http://127.0.0.1:8080/login', data=login_data)
```

### 📊 Core Water Tracking APIs

#### 2. Get Progress Data
**Endpoint**: `GET /api/progress`
**Description**: Get current day's water intake progress

```bash
# cURL (after login)
curl -X GET http://127.0.0.1:8080/api/progress \
  -b cookies.txt

# Python
response = session.get('http://127.0.0.1:8080/api/progress')
print(response.json())
```

**Expected Response**:
```json
{
  "success": true,
  "total_intake": 1500,
  "daily_goal": 2000,
  "progress_percentage": 75,
  "date": "2025-06-16",
  "entries_count": 5,
  "external_data": {...}
}
```

#### 3. Get Water Data (7 days)
**Endpoint**: `GET /api/water-data`
**Description**: Get last 7 days of water intake data

```bash
# cURL
curl -X GET http://127.0.0.1:8080/api/water-data \
  -b cookies.txt

# Python
response = session.get('http://127.0.0.1:8080/api/water-data')
print(response.json())
```

### 🎤 Voice Processing APIs

#### 4. Process Voice Input
**Endpoint**: `POST /api/process_voice`
**Description**: Process voice text to extract drink information

```bash
# cURL
curl -X POST http://127.0.0.1:8080/api/process_voice \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"text": "I drank 500ml of water"}'

# Python
voice_data = {"text": "I drank 500ml of water"}
response = session.post('http://127.0.0.1:8080/api/process_voice', json=voice_data)
print(response.json())
```

**Expected Response**:
```json
{
  "success": true,
  "result": {
    "volume": "500ml",
    "drink_type": "Water",
    "drink_type_id": 1,
    "volume_ml": 500,
    "text": "I drank 500ml of water",
    "source": "local_processing"
  }
}
```

### 📱 Barcode Scanner APIs

#### 5. Lookup Barcode
**Endpoint**: `POST /api/lookup_barcode`
**Description**: Look up product information by barcode

```bash
# cURL
curl -X POST http://127.0.0.1:8080/api/lookup_barcode \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"barcode": "8901030895559"}'

# Python
barcode_data = {"barcode": "8901030895559"}
response = session.post('http://127.0.0.1:8080/api/lookup_barcode', json=barcode_data)
print(response.json())
```

### 📤 Data Export APIs

#### 6. Export Preview/Statistics
**Endpoint**: `POST /api/export/preview`
**Description**: Get export statistics and preview

```bash
# cURL
curl -X POST http://127.0.0.1:8080/api/export/preview \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -b cookies.txt \
  -d "start_date=2025-06-01&end_date=2025-06-16"

# Python
export_data = {
    'start_date': '2025-06-01',
    'end_date': '2025-06-16'
}
response = session.post('http://127.0.0.1:8080/api/export/preview', data=export_data)
print(response.json())
```

#### 7. Export Data
**Endpoint**: `POST /api/export`
**Description**: Export data in various formats (CSV, JSON, PDF)

```bash
# Export as CSV
curl -X POST http://127.0.0.1:8080/api/export \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -b cookies.txt \
  -d "format=csv&start_date=2025-06-01&end_date=2025-06-16" \
  -o water_data.csv

# Export as JSON
curl -X POST http://127.0.0.1:8080/api/export \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -b cookies.txt \
  -d "format=json&start_date=2025-06-01&end_date=2025-06-16" \
  -o water_data.json

# Python
export_data = {
    'format': 'csv',
    'start_date': '2025-06-01',
    'end_date': '2025-06-16'
}
response = session.post('http://127.0.0.1:8080/api/export', data=export_data)
with open('water_data.csv', 'wb') as f:
    f.write(response.content)
```

#### 8. Test Export Debug
**Endpoint**: `GET /api/test-export-debug`
**Description**: Debug endpoint for testing export functionality

```bash
# cURL
curl -X GET http://127.0.0.1:8080/api/test-export-debug \
  -b cookies.txt

# Python
response = session.get('http://127.0.0.1:8080/api/test-export-debug')
print(response.json())
```

### 🌤️ Smart Hydration APIs

#### 9. Get Weather Data
**Endpoint**: `GET /smart-hydration/api/weather`
**Description**: Get weather data for hydration recommendations

```bash
# cURL
curl -X GET "http://127.0.0.1:8080/smart-hydration/api/weather?city=Lahore" \
  -b cookies.txt

# Python
params = {'city': 'Lahore'}
response = session.get('http://127.0.0.1:8080/smart-hydration/api/weather', params=params)
print(response.json())
```

#### 10. Get Hydration Recommendation
**Endpoint**: `POST /smart-hydration/api/hydration/recommendation`
**Description**: Get personalized hydration recommendation

```bash
# cURL
curl -X POST http://127.0.0.1:8080/smart-hydration/api/hydration/recommendation \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"temperature": 30, "humidity": 70, "weather_condition": "sunny"}'

# Python
hydration_data = {
    "temperature": 30,
    "humidity": 70,
    "weather_condition": "sunny"
}
response = session.post('http://127.0.0.1:8080/smart-hydration/api/hydration/recommendation', json=hydration_data)
print(response.json())
```

### 🏃‍♂️ Wearable Integration APIs

#### 11. Get Activity Data
**Endpoint**: `GET /wearable/api/activity-data`
**Description**: Get activity data from connected wearables

```bash
# cURL
curl -X GET "http://127.0.0.1:8080/wearable/api/activity-data?days=7" \
  -b cookies.txt

# Python
params = {'days': 7}
response = session.get('http://127.0.0.1:8080/wearable/api/activity-data', params=params)
print(response.json())
```

#### 12. Get Hydration Recommendation (Wearable)
**Endpoint**: `GET /wearable/api/hydration-recommendation`
**Description**: Get hydration recommendation based on activity data

```bash
# cURL
curl -X GET "http://127.0.0.1:8080/wearable/api/hydration-recommendation?date=2025-06-16" \
  -b cookies.txt

# Python
params = {'date': '2025-06-16'}
response = session.get('http://127.0.0.1:8080/wearable/api/hydration-recommendation', params=params)
print(response.json())
```

#### 13. Sync Wearable Connection
**Endpoint**: `GET /wearable/api/sync/<connection_id>`
**Description**: Sync data from a specific wearable connection

```bash
# cURL (replace 1 with actual connection ID)
curl -X GET http://127.0.0.1:8080/wearable/api/sync/1 \
  -b cookies.txt

# Python
connection_id = 1
response = session.get(f'http://127.0.0.1:8080/wearable/api/sync/{connection_id}')
print(response.json())
```

## Quick Start Testing

### Method 1: Run the Complete Test Script
```bash
# Make sure your Flask app is running first
python water_tracker/app.py

# In another terminal, run the test script
python api_test_script.py
```

### Method 2: Manual Testing with Browser
1. Open browser and go to `http://127.0.0.1:8080`
2. Login with `demo` / `demo123`
3. Open Developer Tools (F12)
4. Go to Console tab
5. Run JavaScript API calls:

```javascript
// Test Progress API
fetch('/api/progress')
  .then(response => response.json())
  .then(data => console.log('Progress:', data));

// Test Voice Processing
fetch('/api/process_voice', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: 'I drank 500ml of water'})
})
.then(response => response.json())
.then(data => console.log('Voice:', data));

// Test Export Debug
fetch('/api/test-export-debug')
  .then(response => response.json())
  .then(data => console.log('Export:', data));
```

## Error Handling

### Common Issues and Solutions

1. **401 Unauthorized**: You need to login first
2. **404 Not Found**: Check if the endpoint URL is correct
3. **500 Internal Server Error**: Check Flask app logs for details
4. **Connection Refused**: Make sure Flask app is running

### Debug Tips

1. **Check Flask Logs**: Look at the terminal where you started the Flask app
2. **Use Debug Mode**: The app runs with `debug=True` by default
3. **Test Individual Endpoints**: Start with simple GET requests
4. **Verify Authentication**: Make sure you're logged in

## API Response Formats

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "details": "Additional error details"
}
```

## Testing Checklist

- [ ] Flask app is running on port 8080
- [ ] Can login with demo/demo123 credentials
- [ ] Progress API returns current day's data
- [ ] Voice processing recognizes drink commands
- [ ] Barcode lookup connects to external API
- [ ] Export functionality works without errors
- [ ] Weather API returns temperature data
- [ ] Wearable APIs handle missing data gracefully

## Advanced Testing

### Load Testing
```python
import concurrent.futures
import requests

def test_api_load():
    session = requests.Session()
    # Login first
    session.post('http://127.0.0.1:8080/login',
                data={'username': 'demo', 'password': 'demo123'})

    # Test multiple concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(session.get, 'http://127.0.0.1:8080/api/progress')
                  for _ in range(50)]

        for future in concurrent.futures.as_completed(futures):
            response = future.result()
            print(f"Status: {response.status_code}")
```

### Integration Testing
```python
def test_full_workflow():
    """Test complete user workflow"""
    session = requests.Session()

    # 1. Login
    session.post('http://127.0.0.1:8080/login',
                data={'username': 'demo', 'password': 'demo123'})

    # 2. Get current progress
    progress = session.get('http://127.0.0.1:8080/api/progress').json()

    # 3. Process voice input
    voice_result = session.post('http://127.0.0.1:8080/api/process_voice',
                               json={'text': 'I drank 300ml of water'}).json()

    # 4. Check updated progress
    new_progress = session.get('http://127.0.0.1:8080/api/progress').json()

    # 5. Export data
    export_data = session.get('http://127.0.0.1:8080/api/test-export-debug').json()

    print("Workflow test completed successfully!")
```

## Complete Python Testing Script

The `api_test_script.py` file contains a comprehensive test suite that:
