#!/bin/bash

# Water Intake Tracker API Testing Script
# This script tests all major API endpoints using cURL

BASE_URL="http://127.0.0.1:8080"
COOKIE_FILE="cookies.txt"

echo "🚀 Water Intake Tracker API Testing"
echo "===================================="

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2 (HTTP $3)"
    fi
}

# Clean up any existing cookies
rm -f $COOKIE_FILE

echo ""
echo "🔐 Step 1: Login"
echo "----------------"
curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo123" \
  -c $COOKIE_FILE \
  -w "%{http_code}" \
  -o /dev/null > login_status.tmp

LOGIN_STATUS=$(cat login_status.tmp)
if [ "$LOGIN_STATUS" = "200" ] || [ "$LOGIN_STATUS" = "302" ]; then
    echo "✅ Login successful"
else
    echo "❌ Login failed (HTTP $LOGIN_STATUS)"
    exit 1
fi

echo ""
echo "📊 Step 2: Testing Core APIs"
echo "-----------------------------"

# Test Progress API
echo "Testing Progress API..."
curl -s -X GET "$BASE_URL/api/progress" \
  -b $COOKIE_FILE \
  -w "%{http_code}" \
  -o progress_response.json > progress_status.tmp

PROGRESS_STATUS=$(cat progress_status.tmp)
print_result $? "Progress API" $PROGRESS_STATUS

if [ "$PROGRESS_STATUS" = "200" ]; then
    echo "   Response preview:"
    head -c 200 progress_response.json
    echo ""
fi

# Test Water Data API
echo "Testing Water Data API..."
curl -s -X GET "$BASE_URL/api/water-data" \
  -b $COOKIE_FILE \
  -w "%{http_code}" \
  -o water_data_response.json > water_data_status.tmp

WATER_DATA_STATUS=$(cat water_data_status.tmp)
print_result $? "Water Data API" $WATER_DATA_STATUS

echo ""
echo "🎤 Step 3: Testing Voice Processing API"
echo "---------------------------------------"

# Test Voice Processing
echo "Testing Voice Processing API..."
curl -s -X POST "$BASE_URL/api/process_voice" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d '{"text": "I drank 500ml of water"}' \
  -w "%{http_code}" \
  -o voice_response.json > voice_status.tmp

VOICE_STATUS=$(cat voice_status.tmp)
print_result $? "Voice Processing API" $VOICE_STATUS

if [ "$VOICE_STATUS" = "200" ]; then
    echo "   Response preview:"
    head -c 200 voice_response.json
    echo ""
fi

echo ""
echo "📱 Step 4: Testing Barcode API"
echo "------------------------------"

# Test Barcode API
echo "Testing Barcode Lookup API..."
curl -s -X POST "$BASE_URL/api/lookup_barcode" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d '{"barcode": "8901030895559"}' \
  -w "%{http_code}" \
  -o barcode_response.json > barcode_status.tmp

BARCODE_STATUS=$(cat barcode_status.tmp)
print_result $? "Barcode API" $BARCODE_STATUS

echo ""
echo "📤 Step 5: Testing Export APIs"
echo "------------------------------"

# Test Export Debug
echo "Testing Export Debug API..."
curl -s -X GET "$BASE_URL/api/test-export-debug" \
  -b $COOKIE_FILE \
  -w "%{http_code}" \
  -o export_debug_response.json > export_debug_status.tmp

EXPORT_DEBUG_STATUS=$(cat export_debug_status.tmp)
print_result $? "Export Debug API" $EXPORT_DEBUG_STATUS

if [ "$EXPORT_DEBUG_STATUS" = "200" ]; then
    echo "   Response preview:"
    head -c 300 export_debug_response.json
    echo ""
fi

# Test Export Preview
echo "Testing Export Preview API..."
curl -s -X POST "$BASE_URL/api/export/preview" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -b $COOKIE_FILE \
  -d "start_date=2025-06-01&end_date=2025-06-16" \
  -w "%{http_code}" \
  -o export_preview_response.json > export_preview_status.tmp

EXPORT_PREVIEW_STATUS=$(cat export_preview_status.tmp)
print_result $? "Export Preview API" $EXPORT_PREVIEW_STATUS

echo ""
echo "🌤️ Step 6: Testing Smart Hydration APIs"
echo "----------------------------------------"

# Test Weather API
echo "Testing Weather API..."
curl -s -X GET "$BASE_URL/smart-hydration/api/weather?city=Lahore" \
  -b $COOKIE_FILE \
  -w "%{http_code}" \
  -o weather_response.json > weather_status.tmp

WEATHER_STATUS=$(cat weather_status.tmp)
print_result $? "Weather API" $WEATHER_STATUS

# Test Hydration Recommendation
echo "Testing Hydration Recommendation API..."
curl -s -X POST "$BASE_URL/smart-hydration/api/hydration/recommendation" \
  -H "Content-Type: application/json" \
  -b $COOKIE_FILE \
  -d '{"temperature": 30, "humidity": 70, "weather_condition": "sunny"}' \
  -w "%{http_code}" \
  -o hydration_rec_response.json > hydration_rec_status.tmp

HYDRATION_REC_STATUS=$(cat hydration_rec_status.tmp)
print_result $? "Hydration Recommendation API" $HYDRATION_REC_STATUS

echo ""
echo "🏃‍♂️ Step 7: Testing Wearable APIs"
echo "----------------------------------"

# Test Activity Data API
echo "Testing Activity Data API..."
curl -s -X GET "$BASE_URL/wearable/api/activity-data?days=7" \
  -b $COOKIE_FILE \
  -w "%{http_code}" \
  -o activity_data_response.json > activity_data_status.tmp

ACTIVITY_DATA_STATUS=$(cat activity_data_status.tmp)
print_result $? "Activity Data API" $ACTIVITY_DATA_STATUS

# Test Wearable Hydration Recommendation
echo "Testing Wearable Hydration Recommendation API..."
curl -s -X GET "$BASE_URL/wearable/api/hydration-recommendation?date=2025-06-16" \
  -b $COOKIE_FILE \
  -w "%{http_code}" \
  -o wearable_hydration_response.json > wearable_hydration_status.tmp

WEARABLE_HYDRATION_STATUS=$(cat wearable_hydration_status.tmp)
print_result $? "Wearable Hydration Recommendation API" $WEARABLE_HYDRATION_STATUS

echo ""
echo "🧹 Cleanup"
echo "----------"
# Clean up temporary files
rm -f *.tmp *.json $COOKIE_FILE

echo ""
echo "🎉 API Testing Complete!"
echo "========================"
echo ""
echo "📋 Summary:"
echo "- Login: $([ "$LOGIN_STATUS" = "200" ] || [ "$LOGIN_STATUS" = "302" ] && echo "✅" || echo "❌")"
echo "- Progress API: $([ "$PROGRESS_STATUS" = "200" ] && echo "✅" || echo "❌")"
echo "- Water Data API: $([ "$WATER_DATA_STATUS" = "200" ] && echo "✅" || echo "❌")"
echo "- Voice Processing API: $([ "$VOICE_STATUS" = "200" ] && echo "✅" || echo "❌")"
echo "- Barcode API: $([ "$BARCODE_STATUS" = "200" ] && echo "✅" || echo "❌")"
echo "- Export Debug API: $([ "$EXPORT_DEBUG_STATUS" = "200" ] && echo "✅" || echo "❌")"
echo "- Export Preview API: $([ "$EXPORT_PREVIEW_STATUS" = "200" ] && echo "✅" || echo "❌")"
echo "- Weather API: $([ "$WEATHER_STATUS" = "200" ] && echo "✅" || echo "❌")"
echo "- Hydration Rec API: $([ "$HYDRATION_REC_STATUS" = "200" ] && echo "✅" || echo "❌")"
echo "- Activity Data API: $([ "$ACTIVITY_DATA_STATUS" = "200" ] && echo "✅" || echo "❌")"
echo "- Wearable Hydration API: $([ "$WEARABLE_HYDRATION_STATUS" = "200" ] && echo "✅" || echo "❌")"
echo ""
echo "💡 Tip: Check the Flask app terminal for detailed logs"
