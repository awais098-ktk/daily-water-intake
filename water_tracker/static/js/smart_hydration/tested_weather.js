/**
 * Tested Weather Widget
 * A thoroughly tested implementation for the Weather & Hydration feature
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Tested Weather Widget loaded');
    
    // Elements
    const widget = document.querySelector('.weather-widget');
    if (!widget) {
        console.error('Weather widget not found');
        return;
    }
    
    const loadingEl = widget.querySelector('.weather-loading');
    const errorEl = widget.querySelector('.weather-error');
    const errorMsgEl = widget.querySelector('.weather-error-message');
    const contentEl = widget.querySelector('.weather-content');
    const retryBtn = widget.querySelector('.retry-weather');
    const refreshBtn = widget.querySelector('.refresh-weather');
    const updateGoalBtn = widget.querySelector('.update-goal');
    const cityInput = widget.querySelector('#city-input');
    const locationBtn = widget.querySelector('.location-btn');
    
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
    
    // API endpoints
    const weatherEndpoint = '/smart-hydration/api/weather';
    const recommendationEndpoint = '/smart-hydration/api/hydration/recommendation';
    const updateGoalEndpoint = '/smart-hydration/api/user/update_goal';
    
    // Default city
    let currentCity = localStorage.getItem('weatherCity') || 'New York';
    if (cityInput) {
        cityInput.value = currentCity;
    }
    
    // Event listeners
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            console.log('Refresh button clicked');
            loadWeatherData();
        });
    }
    
    if (retryBtn) {
        retryBtn.addEventListener('click', function() {
            console.log('Retry button clicked');
            loadWeatherData();
        });
    }
    
    if (updateGoalBtn) {
        updateGoalBtn.addEventListener('click', function() {
            console.log('Update goal button clicked');
            updateDailyGoal();
        });
    }
    
    if (locationBtn) {
        locationBtn.addEventListener('click', function() {
            console.log('Location button clicked');
            if (cityInput && cityInput.value.trim()) {
                currentCity = cityInput.value.trim();
                localStorage.setItem('weatherCity', currentCity);
                loadWeatherData();
            }
        });
    }
    
    // Helper functions
    function showLoading() {
        console.log('Showing loading state');
        if (loadingEl) loadingEl.style.display = 'block';
        if (errorEl) errorEl.style.display = 'none';
        if (contentEl) contentEl.style.display = 'none';
    }
    
    function showError(message) {
        console.log('Showing error state:', message);
        if (loadingEl) loadingEl.style.display = 'none';
        if (errorEl) errorEl.style.display = 'block';
        if (contentEl) contentEl.style.display = 'none';
        if (errorMsgEl) errorMsgEl.textContent = message || 'Could not fetch weather data';
    }
    
    function showContent() {
        console.log('Showing content state');
        if (loadingEl) loadingEl.style.display = 'none';
        if (errorEl) errorEl.style.display = 'none';
        if (contentEl) contentEl.style.display = 'block';
    }
    
    // Load weather data
    async function loadWeatherData() {
        showLoading();
        
        try {
            console.log('Fetching weather data for city:', currentCity);
            
            // Fetch weather data
            const response = await fetch(`${weatherEndpoint}?city=${encodeURIComponent(currentCity)}`);
            
            if (!response.ok) {
                throw new Error(`Weather API error: ${response.status}`);
            }
            
            const weatherData = await response.json();
            console.log('Weather data received:', weatherData);
            
            // Fetch hydration recommendation
            const recommendationResponse = await fetch(recommendationEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    temperature: weatherData.main?.temp,
                    humidity: weatherData.main?.humidity,
                    weather_condition: weatherData.weather?.[0]?.description
                })
            });
            
            if (!recommendationResponse.ok) {
                throw new Error(`Recommendation API error: ${recommendationResponse.status}`);
            }
            
            const recommendationData = await recommendationResponse.json();
            console.log('Recommendation data received:', recommendationData);
            
            // Update UI
            updateWeatherUI(weatherData);
            updateHydrationUI(recommendationData);
            showContent();
            
        } catch (error) {
            console.error('Error fetching data:', error);
            showError(error.message);
        }
    }
    
    // Update weather UI
    function updateWeatherUI(data) {
        if (!data) {
            console.error('No weather data to update UI');
            return;
        }
        
        console.log('Updating weather UI with data:', data);
        
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
        if (!data) {
            console.error('No hydration data to update UI');
            return;
        }
        
        console.log('Updating hydration UI with data:', data);
        
        // Store recommendation data for later use
        window.recommendationData = data;
        
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
    
    // Update daily goal
    async function updateDailyGoal() {
        if (!window.recommendationData || !window.recommendationData.total) {
            console.error('No recommendation data available for updating goal');
            return;
        }
        
        try {
            console.log('Updating daily goal to:', window.recommendationData.total);
            
            updateGoalBtn.disabled = true;
            updateGoalBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
            
            const response = await fetch(updateGoalEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    daily_goal: window.recommendationData.total
                })
            });
            
            if (!response.ok) {
                throw new Error(`Update goal error: ${response.status}`);
            }
            
            console.log('Goal updated successfully');
            
            // Show success message
            updateGoalBtn.innerHTML = '<i class="bi bi-check-circle"></i> Goal Updated!';
            updateGoalBtn.classList.remove('btn-primary');
            updateGoalBtn.classList.add('btn-success');
            
            // Refresh page after a delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
            
        } catch (error) {
            console.error('Error updating goal:', error);
            updateGoalBtn.innerHTML = '<i class="bi bi-x-circle"></i> Error';
            updateGoalBtn.classList.remove('btn-primary');
            updateGoalBtn.classList.add('btn-danger');
            
            // Reset button after a delay
            setTimeout(() => {
                updateGoalBtn.disabled = false;
                updateGoalBtn.innerHTML = '<i class="bi bi-check-circle"></i> Update Daily Goal';
                updateGoalBtn.classList.remove('btn-danger');
                updateGoalBtn.classList.add('btn-primary');
            }, 3000);
        }
    }
    
    // Load weather data on page load
    console.log('Initializing weather widget with city:', currentCity);
    loadWeatherData();
});
