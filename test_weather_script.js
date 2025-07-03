/**
 * Test script for Weather Widget
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Test environment loaded');
    
    // Elements
    const widget = document.querySelector('.weather-widget');
    const loadingEl = widget.querySelector('.weather-loading');
    const errorEl = widget.querySelector('.weather-error');
    const errorMsgEl = widget.querySelector('.weather-error-message');
    const contentEl = widget.querySelector('.weather-content');
    const retryBtn = widget.querySelector('.retry-weather');
    const refreshBtn = widget.querySelector('.refresh-weather');
    const updateGoalBtn = widget.querySelector('.update-goal');
    const cityInput = widget.querySelector('#city-input');
    const locationBtn = widget.querySelector('.location-btn');
    
    // Test controls
    const testSuccessBtn = document.getElementById('test-success');
    const testErrorBtn = document.getElementById('test-error');
    const resetWidgetBtn = document.getElementById('reset-widget');
    const useMockDataCheckbox = document.getElementById('use-mock-data');
    const apiStatusEl = document.getElementById('api-status');
    
    // Weather display elements
    const tempEl = widget.querySelector('.weather-temp');
    const conditionEl = widget.querySelector('.weather-condition');
    const humidityEl = widget.querySelector('.weather-humidity');
    const locationEl = widget.querySelector('.weather-location');
    const iconEl = widget.querySelector('.weather-icon');
    
    // Hydration display elements
    const hydrationTotalEl = widget.querySelector('.hydration-total');
    const hydrationProgressEl = widget.querySelector('.hydration-progress');
    const hydrationExplanationEl = widget.querySelector('.hydration-explanation');
    const hydrationBaseEl = widget.querySelector('.hydration-base');
    const hydrationWeatherEl = widget.querySelector('.hydration-weather');
    const hydrationActivityEl = widget.querySelector('.hydration-activity');
    
    // Mock data
    const mockWeatherData = {
        "coord": {"lon": -74.01, "lat": 40.71},
        "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
        "base": "stations",
        "main": {
            "temp": 25,
            "feels_like": 25,
            "temp_min": 23,
            "temp_max": 27,
            "pressure": 1015,
            "humidity": 60
        },
        "visibility": 10000,
        "wind": {"speed": 3, "deg": 180},
        "clouds": {"all": 0},
        "dt": Math.floor(Date.now() / 1000),
        "sys": {
            "type": 1,
            "id": 123,
            "country": "US",
            "sunrise": Math.floor((Date.now() - 6 * 60 * 60 * 1000) / 1000),
            "sunset": Math.floor((Date.now() + 6 * 60 * 60 * 1000) / 1000)
        },
        "timezone": -14400,
        "id": 5128581,
        "name": "New York",
        "cod": 200
    };
    
    const mockRecommendationData = {
        "base": 2000,
        "temperature": 25,
        "humidity": 60,
        "weather_condition": "clear sky",
        "temp_adjustment": 200,
        "humidity_adjustment": 0,
        "activity_adjustment": 100,
        "total": 2300,
        "explanation": "Based on the current weather and your activity level, we recommend drinking 2300 ml of water today."
    };
    
    // Helper functions
    function showLoading() {
        loadingEl.style.display = 'block';
        errorEl.style.display = 'none';
        contentEl.style.display = 'none';
        apiStatusEl.className = 'alert alert-info';
        apiStatusEl.textContent = 'Status: Loading...';
    }
    
    function showError(message) {
        loadingEl.style.display = 'none';
        errorEl.style.display = 'block';
        contentEl.style.display = 'none';
        errorMsgEl.textContent = message || 'Could not fetch weather data';
        apiStatusEl.className = 'alert alert-danger';
        apiStatusEl.textContent = 'Status: Error - ' + message;
    }
    
    function showContent() {
        loadingEl.style.display = 'none';
        errorEl.style.display = 'none';
        contentEl.style.display = 'block';
        apiStatusEl.className = 'alert alert-success';
        apiStatusEl.textContent = 'Status: Data loaded successfully';
    }
    
    // Update weather UI
    function updateWeatherUI(data) {
        if (!data) return;
        
        // Update city input to match the data
        if (cityInput && data.name) {
            cityInput.value = data.name;
        }
        
        // Update temperature
        if (tempEl && data.main && data.main.temp != null) {
            tempEl.textContent = `${Math.round(data.main.temp)}°C`;
        }
        
        // Update condition
        if (conditionEl && data.weather && data.weather.length > 0) {
            conditionEl.textContent = data.weather[0].description;
        }
        
        // Update humidity
        if (humidityEl && data.main && data.main.humidity != null) {
            humidityEl.textContent = `${data.main.humidity}%`;
        }
        
        // Update location
        if (locationEl && data.name) {
            locationEl.textContent = data.sys && data.sys.country
                ? `${data.name}, ${data.sys.country}`
                : data.name;
        }
        
        // Update weather icon
        if (iconEl && data.weather && data.weather.length > 0) {
            const iconCode = data.weather[0].icon;
            iconEl.innerHTML = `<img src="https://openweathermap.org/img/wn/${iconCode}@2x.png" alt="${data.weather[0].description}" width="50" height="50">`;
        }
    }
    
    // Update hydration UI
    function updateHydrationUI(data) {
        if (!data) return;
        
        // Update total
        if (hydrationTotalEl && data.total != null) {
            hydrationTotalEl.textContent = `${data.total} ml`;
        }
        
        // Update progress bar
        if (hydrationProgressEl && data.total != null && data.base != null) {
            const percentage = Math.min(100, Math.round((data.total / data.base) * 100));
            hydrationProgressEl.style.width = `${percentage}%`;
            hydrationProgressEl.setAttribute('aria-valuenow', percentage);
            hydrationProgressEl.textContent = `${percentage}%`;
            
            // Change color based on percentage
            hydrationProgressEl.classList.remove('bg-primary', 'bg-success', 'bg-warning');
            if (percentage > 120) {
                hydrationProgressEl.classList.add('bg-warning');
            } else if (percentage > 100) {
                hydrationProgressEl.classList.add('bg-success');
            } else {
                hydrationProgressEl.classList.add('bg-primary');
            }
        }
        
        // Update explanation
        if (hydrationExplanationEl && data.explanation) {
            hydrationExplanationEl.textContent = data.explanation;
        }
        
        // Update base
        if (hydrationBaseEl && data.base != null) {
            hydrationBaseEl.textContent = `${data.base} ml`;
        }
        
        // Update weather adjustment
        if (hydrationWeatherEl && data.temp_adjustment != null && data.humidity_adjustment != null) {
            const weatherAdjustment = data.temp_adjustment + data.humidity_adjustment;
            const sign = weatherAdjustment >= 0 ? '+' : '';
            hydrationWeatherEl.textContent = `${sign}${weatherAdjustment} ml`;
        }
        
        // Update activity adjustment
        if (hydrationActivityEl && data.activity_adjustment != null) {
            const sign = data.activity_adjustment >= 0 ? '+' : '';
            hydrationActivityEl.textContent = `${sign}${data.activity_adjustment} ml`;
        }
    }
    
    // Simulate loading weather data
    function loadWeatherData() {
        showLoading();
        
        // Get city from input
        const city = cityInput.value.trim() || 'New York';
        
        // Update mock data with the city name
        mockWeatherData.name = city;
        
        // Simulate API delay
        setTimeout(() => {
            if (useMockDataCheckbox.checked) {
                updateWeatherUI(mockWeatherData);
                updateHydrationUI(mockRecommendationData);
                showContent();
            }
        }, 1000);
    }
    
    // Event listeners for test controls
    testSuccessBtn.addEventListener('click', () => {
        showLoading();
        setTimeout(() => {
            updateWeatherUI(mockWeatherData);
            updateHydrationUI(mockRecommendationData);
            showContent();
        }, 1000);
    });
    
    testErrorBtn.addEventListener('click', () => {
        showLoading();
        setTimeout(() => {
            showError('Weather API error: 404');
        }, 1000);
    });
    
    resetWidgetBtn.addEventListener('click', () => {
        cityInput.value = 'New York';
        showContent();
    });
    
    // Event listeners for widget controls
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadWeatherData);
    }
    
    if (retryBtn) {
        retryBtn.addEventListener('click', loadWeatherData);
    }
    
    if (locationBtn) {
        locationBtn.addEventListener('click', () => {
            if (cityInput.value.trim()) {
                loadWeatherData();
            }
        });
    }
    
    if (updateGoalBtn) {
        updateGoalBtn.addEventListener('click', () => {
            updateGoalBtn.disabled = true;
            updateGoalBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
            
            setTimeout(() => {
                updateGoalBtn.innerHTML = '<i class="bi bi-check-circle"></i> Goal Updated!';
                updateGoalBtn.classList.remove('btn-primary');
                updateGoalBtn.classList.add('btn-success');
                
                setTimeout(() => {
                    updateGoalBtn.disabled = false;
                    updateGoalBtn.innerHTML = '<i class="bi bi-check-circle"></i> Update Daily Goal';
                    updateGoalBtn.classList.remove('btn-success');
                    updateGoalBtn.classList.add('btn-primary');
                }, 2000);
            }, 1000);
        });
    }
    
    // Initialize with content showing
    showContent();
});
