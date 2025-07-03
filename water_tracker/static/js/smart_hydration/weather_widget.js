/**
 * Weather Widget JavaScript for Smart Hydration Feature
 * Handles fetching weather data and updating the UI
 */

class WeatherWidget {
    constructor(options = {}) {
        // Default options
        this.options = {
            selector: '.weather-widget',
            apiEndpoint: '/smart-hydration/api/weather',
            recommendationEndpoint: '/smart-hydration/api/hydration/recommendation',
            updateGoalEndpoint: '/smart-hydration/api/user/update_goal',
            refreshInterval: 30 * 60 * 1000, // 30 minutes
            useGeolocation: true,
            defaultCity: 'New York',
            ...options
        };

        // Load saved location settings
        this.locationSettings = this.loadLocationSettings();

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

        // Location settings button
        const locationBtn = this.widget.querySelector('.location-settings');
        if (locationBtn) {
            locationBtn.addEventListener('click', () => this.openLocationSettings());
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
     * Load location settings from localStorage
     */
    loadLocationSettings() {
        try {
            const settings = localStorage.getItem('weatherLocationSettings');
            if (settings) {
                return JSON.parse(settings);
            }
        } catch (error) {
            console.error('Error loading location settings:', error);
        }
        return {
            method: 'auto',
            city: this.options.defaultCity
        };
    }

    /**
     * Save location settings to localStorage
     */
    saveLocationSettings() {
        try {
            console.log('Saving location settings...');

            const locationMethod = document.getElementById('locationMethod');
            const cityInput = document.getElementById('cityInput');

            if (!locationMethod || !cityInput) {
                console.error('Location settings elements not found');
                return;
            }

            const method = locationMethod.value;
            const city = cityInput.value.trim();

            if (method === 'city' && !city) {
                alert('Please enter a city name');
                return;
            }

            const settings = {
                method: method,
                city: method === 'city' ? city : this.options.defaultCity
            };

            console.log('New location settings:', settings);

            // Save to localStorage
            localStorage.setItem('weatherLocationSettings', JSON.stringify(settings));
            this.locationSettings = settings;

            // Close modal
            try {
                const modalElement = document.getElementById('locationSettingsModal');
                if (modalElement && typeof bootstrap !== 'undefined') {
                    // Try to get the modal instance
                    let modal = bootstrap.Modal.getInstance(modalElement);

                    // If no instance exists, create one
                    if (!modal) {
                        modal = new bootstrap.Modal(modalElement);
                    }

                    // Hide the modal
                    modal.hide();

                    // Remove the modal from the DOM after it's hidden
                    modalElement.addEventListener('hidden.bs.modal', function () {
                        modalElement.remove();
                    });
                }
            } catch (modalError) {
                console.error('Error closing modal:', modalError);
                // If we can't close the modal properly, just remove it from the DOM
                const modalElement = document.getElementById('locationSettingsModal');
                if (modalElement) {
                    modalElement.remove();
                }
            }

            // Reload weather data with new settings
            this.loadWeatherData();
            console.log('Weather data reload requested');

        } catch (error) {
            console.error('Error saving location settings:', error);
            alert('Could not save location settings. Please try again.');

            // Try to remove the modal if there was an error
            try {
                const modalElement = document.getElementById('locationSettingsModal');
                if (modalElement) {
                    modalElement.remove();
                }
            } catch (e) {
                console.error('Error removing modal:', e);
            }
        }
    }

    /**
     * Open location settings modal
     */
    openLocationSettings() {
        try {
            console.log('Opening location settings modal...');

            // Create the modal if it doesn't exist
            if (!document.getElementById('locationSettingsModal')) {
                console.log('Modal not found, creating it...');
                this.createLocationSettingsModal();
            }

            // Set current values
            const locationMethod = document.getElementById('locationMethod');
            const cityInput = document.getElementById('cityInput');

            if (locationMethod && cityInput) {
                locationMethod.value = this.locationSettings.method || 'auto';
                cityInput.value = this.locationSettings.city || this.options.defaultCity;

                // Toggle city input visibility
                this.toggleLocationMethod();
            } else {
                console.error('Location method or city input elements not found');
            }

            // Get modal element
            const modalElement = document.getElementById('locationSettingsModal');
            if (!modalElement) {
                console.error('Location settings modal not found even after creation attempt');
                alert('Could not open location settings. Please refresh the page and try again.');
                return;
            }

            // Check if Bootstrap is available
            if (typeof bootstrap === 'undefined') {
                console.error('Bootstrap JavaScript is not loaded');
                alert('Could not open location settings. Please refresh the page and try again.');
                return;
            }

            // Create a new modal instance every time to avoid issues with stale instances
            const modal = new bootstrap.Modal(modalElement);

            // Show modal
            modal.show();
            console.log('Modal shown successfully');
        } catch (error) {
            console.error('Error opening location settings modal:', error);
            alert('Could not open location settings. Please refresh the page and try again.');
        }
    }

    /**
     * Create the location settings modal dynamically
     */
    createLocationSettingsModal() {
        // Create modal HTML
        const modalHTML = `
        <div class="modal fade" id="locationSettingsModal" tabindex="-1" aria-labelledby="locationSettingsModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="locationSettingsModalLabel">Change Location</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="locationMethod" class="form-label">Location Method</label>
                            <select class="form-select" id="locationMethod">
                                <option value="auto">Automatic (Browser Geolocation)</option>
                                <option value="city">Enter City Name</option>
                            </select>
                        </div>

                        <div id="cityInputGroup" class="mb-3" style="display: none;">
                            <label for="cityInput" class="form-label">City Name</label>
                            <div class="input-group">
                                <input type="text" class="form-control" id="cityInput" placeholder="e.g., London, New York, Tokyo">
                                <button class="btn btn-outline-secondary" type="button" id="searchCity">
                                    <i class="bi bi-search"></i>
                                </button>
                            </div>
                            <div class="form-text">Enter city name, optionally with country code (e.g., London,UK)</div>
                        </div>

                        <div id="popularCities" class="mb-3" style="display: none;">
                            <label class="form-label">Popular Cities</label>
                            <div class="d-flex flex-wrap gap-2">
                                <button type="button" class="btn btn-sm btn-outline-primary city-btn" data-city="London">London</button>
                                <button type="button" class="btn btn-sm btn-outline-primary city-btn" data-city="New York">New York</button>
                                <button type="button" class="btn btn-sm btn-outline-primary city-btn" data-city="Tokyo">Tokyo</button>
                                <button type="button" class="btn btn-sm btn-outline-primary city-btn" data-city="Paris">Paris</button>
                                <button type="button" class="btn btn-sm btn-outline-primary city-btn" data-city="Sydney">Sydney</button>
                                <button type="button" class="btn btn-sm btn-outline-primary city-btn" data-city="Mumbai">Mumbai</button>
                                <button type="button" class="btn btn-sm btn-outline-primary city-btn" data-city="Dubai">Dubai</button>
                                <button type="button" class="btn btn-sm btn-outline-primary city-btn" data-city="Rio de Janeiro">Rio</button>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="saveLocationSettings">Save Changes</button>
                    </div>
                </div>
            </div>
        </div>
        `;

        // Create a temporary container
        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = modalHTML;

        // Append the modal to the body
        document.body.appendChild(tempContainer.firstElementChild);

        // Add event listeners to the new modal elements
        this.addModalEventListeners();
    }

    /**
     * Add event listeners to modal elements
     */
    addModalEventListeners() {
        // Location method select
        const locationMethod = document.getElementById('locationMethod');
        if (locationMethod) {
            locationMethod.addEventListener('change', () => this.toggleLocationMethod());
        }

        // Search city button
        const searchCityBtn = document.getElementById('searchCity');
        if (searchCityBtn) {
            searchCityBtn.addEventListener('click', () => this.searchCity());
        }

        // City input enter key
        const cityInput = document.getElementById('cityInput');
        if (cityInput) {
            cityInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.searchCity();
                }
            });
        }

        // Popular city buttons
        const cityBtns = document.querySelectorAll('.city-btn');
        cityBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const city = btn.dataset.city;
                const cityInput = document.getElementById('cityInput');
                if (cityInput) {
                    cityInput.value = city;
                }
            });
        });

        // Save location settings button
        const saveLocationBtn = document.getElementById('saveLocationSettings');
        if (saveLocationBtn) {
            saveLocationBtn.addEventListener('click', () => this.saveLocationSettings());
        }
    }

    /**
     * Toggle location method inputs
     */
    toggleLocationMethod() {
        try {
            const locationMethod = document.getElementById('locationMethod');
            const cityInputGroup = document.getElementById('cityInputGroup');
            const popularCities = document.getElementById('popularCities');

            if (!locationMethod || !cityInputGroup || !popularCities) {
                console.error('Location method elements not found');
                return;
            }

            const method = locationMethod.value;

            if (method === 'city') {
                cityInputGroup.style.display = 'block';
                popularCities.style.display = 'block';
            } else {
                cityInputGroup.style.display = 'none';
                popularCities.style.display = 'none';
            }
        } catch (error) {
            console.error('Error toggling location method:', error);
        }
    }

    /**
     * Search for city
     */
    searchCity() {
        try {
            console.log('Searching for city...');

            const cityInput = document.getElementById('cityInput');
            if (!cityInput) {
                console.error('City input element not found');
                return;
            }

            const city = cityInput.value.trim();

            if (!city) {
                alert('Please enter a city name');
                return;
            }

            console.log('Searching for city:', city);

            // Update location settings
            this.locationSettings.method = 'city';
            this.locationSettings.city = city;

            // Save settings
            localStorage.setItem('weatherLocationSettings', JSON.stringify(this.locationSettings));

            // Close modal
            try {
                const modalElement = document.getElementById('locationSettingsModal');
                if (modalElement && typeof bootstrap !== 'undefined') {
                    // Try to get the modal instance
                    let modal = bootstrap.Modal.getInstance(modalElement);

                    // If no instance exists, create one
                    if (!modal) {
                        modal = new bootstrap.Modal(modalElement);
                    }

                    // Hide the modal
                    modal.hide();

                    // Remove the modal from the DOM after it's hidden
                    modalElement.addEventListener('hidden.bs.modal', function () {
                        modalElement.remove();
                    });
                }
            } catch (modalError) {
                console.error('Error closing modal:', modalError);
                // If we can't close the modal properly, just remove it from the DOM
                const modalElement = document.getElementById('locationSettingsModal');
                if (modalElement) {
                    modalElement.remove();
                }
            }

            // Reload weather data
            this.loadWeatherData();
            console.log('Weather data reload requested for city:', city);

        } catch (error) {
            console.error('Error searching city:', error);

            // Try to remove the modal if there was an error
            try {
                const modalElement = document.getElementById('locationSettingsModal');
                if (modalElement) {
                    modalElement.remove();
                }
            } catch (e) {
                console.error('Error removing modal:', e);
            }
        }
    }

    /**
     * Load weather data from API
     */
    async loadWeatherData() {
        this.showLoading();

        try {
            let url = this.options.apiEndpoint;

            // Use location settings
            if (this.locationSettings.method === 'auto' && this.options.useGeolocation && navigator.geolocation) {
                try {
                    const position = await this.getCurrentPosition();
                    url += `?lat=${position.coords.latitude}&lon=${position.coords.longitude}`;
                } catch (geoError) {
                    console.warn('Geolocation error:', geoError);
                    url += `?city=${encodeURIComponent(this.locationSettings.city || this.options.defaultCity)}`;
                }
            } else {
                url += `?city=${encodeURIComponent(this.locationSettings.city || this.options.defaultCity)}`;
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
    console.log('Weather widget script loaded and DOM is ready');
    console.log('Looking for weather widget element with selector: .weather-widget');
    const widgetElement = document.querySelector('.weather-widget');
    console.log('Weather widget element found:', widgetElement);

    try {
        new WeatherWidget();
        console.log('Weather widget initialized successfully');
    } catch (error) {
        console.error('Error initializing weather widget:', error);
    }
});
