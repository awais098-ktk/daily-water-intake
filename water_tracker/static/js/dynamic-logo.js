/**
 * Dynamic Logo for Water Intake Tracker
 * Updates the logo's water level based on the user's progress
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the progress value from the dashboard
    const progressElement = document.getElementById('progress-value');
    if (!progressElement) return;
    
    const progress = parseFloat(progressElement.value) || 0;
    
    // Update all logo SVGs on the page
    updateLogoProgress(progress);
});

/**
 * Updates the water level in the logo based on progress
 * @param {number} progress - Progress percentage (0-100)
 */
function updateLogoProgress(progress) {
    // Find all logo SVGs
    const logoImages = document.querySelectorAll('img[src*="logo.svg"]');
    
    logoImages.forEach(img => {
        // When the SVG is loaded
        img.addEventListener('load', function() {
            // Get the SVG document
            const svgDoc = img.contentDocument;
            if (!svgDoc) return;
            
            // Find the water progress element
            const waterProgress = svgDoc.getElementById('water-progress');
            if (!waterProgress) return;
            
            // Calculate the new height and y position based on progress
            // The water container is 120px tall, positioned at y=40
            const maxHeight = 120;
            const minY = 40;
            
            // Clamp progress between 0 and 100
            const clampedProgress = Math.max(0, Math.min(100, progress));
            
            // Calculate height (progress % of max height)
            const height = (clampedProgress / 100) * maxHeight;
            
            // Calculate y position (starts from bottom)
            const y = minY + (maxHeight - height);
            
            // Update the water progress element
            waterProgress.setAttribute('height', height);
            waterProgress.setAttribute('y', y);
        });
    });
}
