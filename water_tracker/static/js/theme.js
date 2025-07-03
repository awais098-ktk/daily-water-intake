// Theme management for HydroMate

// Check for saved theme preference or use default
document.addEventListener('DOMContentLoaded', function() {
    // Set theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    const savedColor = localStorage.getItem('color') || 'blue';
    
    applyTheme(savedTheme);
    applyAccentColor(savedColor);
    
    // Set the theme toggle switch to match current theme
    if (document.getElementById('themeSwitch')) {
        document.getElementById('themeSwitch').checked = (savedTheme === 'dark');
    }
    
    // Set the color selector to match current color
    if (document.getElementById('accentColor')) {
        document.getElementById('accentColor').value = savedColor;
    }
});

// Toggle between light and dark themes
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

// Apply the selected theme
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        document.body.classList.remove('light-theme');
    } else {
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
    }
}

// Change accent color
function changeAccentColor(color) {
    applyAccentColor(color);
    localStorage.setItem('color', color);
}

// Apply the selected accent color
function applyAccentColor(color) {
    document.documentElement.style.setProperty('--accent-color', getColorCode(color));
    document.documentElement.style.setProperty('--accent-color-hover', getHoverColorCode(color));
}

// Get color code based on color name
function getColorCode(color) {
    const colors = {
        'blue': '#4DA6FF',
        'green': '#4CAF50',
        'purple': '#9C27B0',
        'orange': '#FF9800',
        'red': '#F44336'
    };
    
    return colors[color] || colors['blue'];
}

// Get hover color code (slightly darker)
function getHoverColorCode(color) {
    const hoverColors = {
        'blue': '#3a8fd9',
        'green': '#3d8b40',
        'purple': '#7B1FA2',
        'orange': '#F57C00',
        'red': '#D32F2F'
    };
    
    return hoverColors[color] || hoverColors['blue'];
}
