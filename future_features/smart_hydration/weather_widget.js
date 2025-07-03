/**
 * Weather Widget JavaScript for Smart Hydration Feature
 * Handles fetching weather data and updating the UI
 */

class WeatherWidget {
    constructor(options = {}) {
        // Default options
        this.options = {
            selector: '.weather-widget',
            apiEndpoint: '/api/weather',
            recommendationEndpoint: '/api/hydration/recommendation',
            updateGoalEndpoint: '/api/user/update_goal',
            refreshInterval: 30 * 60 * 1000, // 30 minutes
            useGeolocation: true,
            defaultCity: 'New York',
            ...options
        };
        
        // Widget elements
        this.widget = document.querySelector(this.options.selector);
        if (!this.widget) {
            console.error('Weather widget element not found');
            return;
        }
        
        // Initialize widget
        this.initElements();
        this.initEventListeners();
        this.loadWeatherData();
        
        // Set up refresh interval
        if (this.options.refreshInterval > 0) {
            this.refreshTimer = setInterval(() => this.loadWeatherData(), this.options.refreshInterval);
        }
    }
    
    /**
     * Initialize widget elements
     */
    initElements() {
        // Loading and error states
        this.loadingEl = this.widget.querySelector('.weather-loading');
        this.errorEl = this.widget.querySelector('.weather-error');
        this.errorMessageEl = this.widget.querySelector('.weather-error-message');
        this.contentEl = this.widget.querySelector('.weather-content');
        
        // Weather display elements
        this.tempEl = this.widget.querySelector('.weather-temp');
        this.conditionEl = this.widget.querySelector('.weather-condition');
        this.humidityEl = this.widget.querySelector('.weather-humidity');
        this.locationEl = this.widget.querySelector('.weather-location');
        this.iconEl = this.widget.querySelector('.weather-icon');
        
        // Hydration elements
        this.hydrationTotalEl = this.widget.querySelector('.hydration-total');
        this.hydrationProgressEl = this.widget.querySelector('.hydration-progress');
        this.hydrationExplanationEl = this.widget.querySelector('.hydration-explanation');
        this.hydrationBaseEl = this.widget.querySelector('.hydration-base');
        this.hydrationWeatherEl = this.widget.querySelector('.hydration-weather');
        this.hydrationActivityEl = this.widget.querySelector('.hydration-activity');
        
        // Buttons
        this.refreshBtn = this.widget.querySelector('.refresh-weather');
        this.retryBtn = this.widget.querySelector('.retry-weather');
        this.updateGoalBtn = this.widget.querySelector('.update-goal');
    }
    
    /**
     * Initialize event listeners
     */
    initEventListeners() {
        // Refresh button
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => this.loadWeatherData());
        }
        
        // Retry button
        if (this.retryBtn) {
            this.retryBtn.addEventListener('click', () => this.loadWeatherData());
        }
        
        // Update goal button
        if (this.updateGoalBtn) {
            this.updateGoalBtn.addEventListener('click', () => this.updateDailyGoal());
        }
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        if (this.loadingEl) this.loadingEl.style.display = 'block';
        if (this.errorEl) this.errorEl.style.display = 'none';
        if (this.contentEl) this.contentEl.style.display = 'none';
    }
    
    /**
     * Show error state
     * @param {string} message - Error message to display
     */
    showError(message) {
        if (this.loadingEl) this.loadingEl.style.display = 'none';
        if (this.errorEl) this.errorEl.style.display = 'block';
        if (this.contentEl) this.contentEl.style.display = 'none';
        
        if (this.errorMessageEl) {
            this.errorMessageEl.textContent = message || 'Could not fetch weather data.';
        }
    }
    
    /**
     * Show content state
     */
    showContent() {
        if (this.loadingEl) this.loadingEl.style.display = 'none';
        if (this.errorEl) this.errorEl.style.display = 'none';
        if (this.contentEl) this.contentEl.style.display = 'block';
    }
    
    /**
     * Load weather data from API
     */
    async loadWeatherData() {
        this.showLoading();
        
        try {
            let url = this.options.apiEndpoint;
            
            // Use geolocation if enabled
            if (this.options.useGeolocation && navigator.geolocation) {
                try {
                    const position = await this.getCurrentPosition();
                    url += `?lat=${position.coords.latitude}&lon=${position.coords.longitude}`;
                } catch (geoError) {
                    console.warn('Geolocation error:', geoError);
                    url += `?city=${encodeURIComponent(this.options.defaultCity)}`;
                }
            } else {
                url += `?city=${encodeURIComponent(this.options.defaultCity)}`;
            }
            
            // Fetch weather data
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Weather API error: ${response.status}`);
            }
            
            const weatherData = await response.json();
            
            // Fetch hydration recommendation
            const recommendationResponse = await fetch(this.options.recommendationEndpoint, {
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
            
            // Update UI with data
            this.updateWeatherUI(weatherData);
            this.updateHydrationUI(recommendationData);
            this.showContent();
            
        } catch (error) {
            console.error('Error fetching data:', error);
            this.showError(error.message);
        }
    }
    
    /**
     * Get current position using geolocation
     * @returns {Promise} - Resolves with position object
     */
    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: false,
                timeout: 5000,
                maximumAge: 10 * 60 * 1000 // 10 minutes
            });
        });
    }
    
    /**
     * Update weather UI with data
     * @param {Object} data - Weather data from API
     */
    updateWeatherUI(data) {
        if (!data) return;
        
        // Update temperature
        if (this.tempEl && data.main && data.main.temp != null) {
            this.tempEl.textContent = `${Math.round(data.main.temp)}°C`;
        }
        
        // Update condition
        if (this.conditionEl && data.weather && data.weather.length > 0) {
            this.conditionEl.textContent = data.weather[0].description;
        }
        
        // Update humidity
        if (this.humidityEl && data.main && data.main.humidity != null) {
            this.humidityEl.textContent = `${data.main.humidity}%`;
        }
        
        // Update location
        if (this.locationEl && data.name) {
            this.locationEl.textContent = data.sys && data.sys.country 
                ? `${data.name}, ${data.sys.country}` 
                : data.name;
        }
        
        // Update weather icon
        if (this.iconEl && data.weather && data.weather.length > 0) {
            const iconCode = data.weather[0].icon;
            this.iconEl.innerHTML = `<img src="https://openweathermap.org/img/wn/${iconCode}@2x.png" alt="${data.weather[0].description}" width="50" height="50">`;
        }
    }
    
    /**
     * Update hydration UI with recommendation data
     * @param {Object} data - Hydration recommendation data
     */
    updateHydrationUI(data) {
        if (!data) return;
        
        // Update total
        if (this.hydrationTotalEl && data.total != null) {
            this.hydrationTotalEl.textContent = `${data.total} ml`;
        }
        
        // Update progress bar
        if (this.hydrationProgressEl && data.total != null && data.base != null) {
            const percentage = Math.min(100, Math.round((data.total / data.base) * 100));
            this.hydrationProgressEl.style.width = `${percentage}%`;
            this.hydrationProgressEl.setAttribute('aria-valuenow', percentage);
            this.hydrationProgressEl.textContent = `${percentage}%`;
            
            // Change color based on percentage
            this.hydrationProgressEl.classList.remove('bg-primary', 'bg-success', 'bg-warning');
            if (percentage > 120) {
                this.hydrationProgressEl.classList.add('bg-warning');
            } else if (percentage > 100) {
                this.hydrationProgressEl.classList.add('bg-success');
            } else {
                this.hydrationProgressEl.classList.add('bg-primary');
            }
        }
        
        // Update explanation
        if (this.hydrationExplanationEl && data.explanation) {
            this.hydrationExplanationEl.textContent = data.explanation;
        }
        
        // Update base
        if (this.hydrationBaseEl && data.base != null) {
            this.hydrationBaseEl.textContent = `${data.base} ml`;
        }
        
        // Update weather adjustment
        if (this.hydrationWeatherEl && data.temp_adjustment != null && data.humidity_adjustment != null) {
            const weatherAdjustment = data.temp_adjustment + data.humidity_adjustment;
            const sign = weatherAdjustment >= 0 ? '+' : '';
            this.hydrationWeatherEl.textContent = `${sign}${weatherAdjustment} ml`;
        }
        
        // Update activity adjustment
        if (this.hydrationActivityEl && data.activity_adjustment != null) {
            const sign = data.activity_adjustment >= 0 ? '+' : '';
            this.hydrationActivityEl.textContent = `${sign}${data.activity_adjustment} ml`;
        }
        
        // Store recommendation data for later use
        this.recommendationData = data;
    }
    
    /**
     * Update user's daily goal with the recommended amount
     */
    async updateDailyGoal() {
        if (!this.recommendationData || !this.recommendationData.total) {
            console.error('No recommendation data available');
            return;
        }
        
        try {
            this.updateGoalBtn.disabled = true;
            this.updateGoalBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
            
            const response = await fetch(this.options.updateGoalEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    daily_goal: this.recommendationData.total
                })
            });
            
            if (!response.ok) {
                throw new Error(`Update goal error: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Show success message
            this.updateGoalBtn.innerHTML = '<i class="bi bi-check-circle"></i> Goal Updated!';
            this.updateGoalBtn.classList.remove('btn-primary');
            this.updateGoalBtn.classList.add('btn-success');
            
            // Refresh page after a delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
            
        } catch (error) {
            console.error('Error updating goal:', error);
            this.updateGoalBtn.innerHTML = '<i class="bi bi-x-circle"></i> Error';
            this.updateGoalBtn.classList.remove('btn-primary');
            this.updateGoalBtn.classList.add('btn-danger');
            
            // Reset button after a delay
            setTimeout(() => {
                this.updateGoalBtn.disabled = false;
                this.updateGoalBtn.innerHTML = '<i class="bi bi-check-circle"></i> Update Daily Goal';
                this.updateGoalBtn.classList.remove('btn-danger');
                this.updateGoalBtn.classList.add('btn-primary');
            }, 3000);
        }
    }
}

// Initialize widget when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WeatherWidget();
});
