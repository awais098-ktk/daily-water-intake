// Chart.js implementation for HydroMate

// Create water intake chart
function createWaterIntakeChart(chartData) {
    const ctx = document.getElementById('waterIntakeChart').getContext('2d');
    
    // Get theme colors
    const isDarkTheme = document.body.classList.contains('dark-theme');
    const textColor = isDarkTheme ? '#f8f9fa' : '#212529';
    const gridColor = isDarkTheme ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    
    // Get accent color
    const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim();
    
    // Create chart
    const waterIntakeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.dates,
            datasets: [{
                label: 'Water Intake',
                data: chartData.amounts,
                backgroundColor: accentColor,
                borderColor: accentColor,
                borderWidth: 1,
                borderRadius: 5,
                maxBarThickness: 50
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: isDarkTheme ? '#1e1e1e' : 'white',
                    titleColor: textColor,
                    bodyColor: textColor,
                    borderColor: gridColor,
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y} ml`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor,
                        callback: function(value) {
                            if (value >= 1000) {
                                return value / 1000 + 'L';
                            }
                            return value + 'ml';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Amount (ml)',
                        color: textColor
                    }
                },
                x: {
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                }
            }
        }
    });
    
    return waterIntakeChart;
}

// Create weekly comparison chart
function createWeeklyComparisonChart(chartData) {
    if (!document.getElementById('weeklyComparisonChart')) {
        return;
    }
    
    const ctx = document.getElementById('weeklyComparisonChart').getContext('2d');
    
    // Get theme colors
    const isDarkTheme = document.body.classList.contains('dark-theme');
    const textColor = isDarkTheme ? '#f8f9fa' : '#212529';
    const gridColor = isDarkTheme ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
    
    // Get accent color
    const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim();
    
    // Create chart
    const weeklyComparisonChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [
                {
                    label: 'This Week',
                    data: chartData.thisWeek,
                    borderColor: accentColor,
                    backgroundColor: 'transparent',
                    tension: 0.4,
                    borderWidth: 3
                },
                {
                    label: 'Last Week',
                    data: chartData.lastWeek,
                    borderColor: '#6c757d',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    tension: 0.4,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: textColor
                    }
                },
                tooltip: {
                    backgroundColor: isDarkTheme ? '#1e1e1e' : 'white',
                    titleColor: textColor,
                    bodyColor: textColor,
                    borderColor: gridColor,
                    borderWidth: 1,
                    padding: 10
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    },
                    title: {
                        display: true,
                        text: 'Amount (ml)',
                        color: textColor
                    }
                },
                x: {
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                }
            }
        }
    });
    
    return weeklyComparisonChart;
}
