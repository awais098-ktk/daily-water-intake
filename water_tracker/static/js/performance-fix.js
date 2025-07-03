/**
 * Performance fixes for the Water Intake Tracker
 * Addresses screen glitching, buffering, and layout issues
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fix for screen glitching and buffering
    fixScreenGlitching();
    
    // Fix for layout issues
    fixLayoutIssues();
    
    // Fix for milk display
    fixMilkDisplay();
});

/**
 * Fixes screen glitching and buffering issues
 */
function fixScreenGlitching() {
    // Add hardware acceleration
    document.body.style.transform = 'translateZ(0)';
    document.body.style.backfaceVisibility = 'hidden';
    document.body.style.perspective = '1000px';
    
    // Reduce repaints
    const heavyElements = document.querySelectorAll('.card, .progress, canvas');
    heavyElements.forEach(element => {
        element.style.willChange = 'transform';
    });
    
    // Optimize images
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.decoding = 'async';
        img.loading = 'lazy';
    });
    
    // Debounce scroll events
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        if (scrollTimeout) {
            window.cancelAnimationFrame(scrollTimeout);
        }
        
        scrollTimeout = window.requestAnimationFrame(function() {
            // Scroll handling code here
        });
    });
}

/**
 * Fixes layout issues with the sidebar and content
 */
function fixLayoutIssues() {
    // Fix for sidebar extending too low
    const sidebar = document.querySelector('.col-md-4');
    const mainContent = document.querySelector('.col-md-8');
    
    if (sidebar && mainContent) {
        // Ensure the sidebar doesn't extend beyond the main content
        const resizeObserver = new ResizeObserver(entries => {
            for (let entry of entries) {
                if (entry.target === mainContent) {
                    const mainHeight = mainContent.offsetHeight;
                    sidebar.style.maxHeight = `${mainHeight}px`;
                    sidebar.style.overflowY = 'auto';
                }
            }
        });
        
        resizeObserver.observe(mainContent);
    }
    
    // Fix for graph not showing until scroll
    const chartContainer = document.getElementById('drinkTypeChart');
    if (chartContainer) {
        // Force the chart to be visible
        chartContainer.scrollIntoView({ behavior: 'auto', block: 'nearest' });
    }
}

/**
 * Fixes milk display issues
 */
function fixMilkDisplay() {
    // Find all drink type badges
    const drinkBadges = document.querySelectorAll('.drink-type-badge');
    
    drinkBadges.forEach(badge => {
        const text = badge.textContent.trim();
        
        // Check if this is a milk badge
        if (text.toLowerCase().includes('milk')) {
            // Add a border and adjust text color for better visibility
            badge.style.border = '1px solid #ccc';
            badge.style.color = '#333';
            
            // If the background is too light, add a subtle shadow
            const bgColor = window.getComputedStyle(badge).backgroundColor;
            if (isLightColor(bgColor)) {
                badge.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
            }
        }
    });
}

/**
 * Checks if a color is light
 * @param {string} color - The color to check
 * @returns {boolean} - True if the color is light
 */
function isLightColor(color) {
    // Extract RGB values
    const rgb = color.match(/\d+/g);
    if (!rgb || rgb.length < 3) return true;
    
    // Calculate luminance
    const luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255;
    
    // Return true if the color is light (luminance > 0.5)
    return luminance > 0.5;
}
