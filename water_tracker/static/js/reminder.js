// Reminder system for HydroMate

let reminderInterval;
let reminderEnabled = false;
let intervalMinutes = 60;
let notificationPermission = false;

// Initialize reminders
document.addEventListener('DOMContentLoaded', function() {
    // Check if reminders are enabled in user settings
    reminderEnabled = document.getElementById('reminderEnabled') ? 
                     document.getElementById('reminderEnabled').value === 'True' : false;
    
    // Get interval from user settings
    intervalMinutes = document.getElementById('reminderInterval') ? 
                     parseInt(document.getElementById('reminderInterval').value) : 60;
    
    // Check notification permission
    checkNotificationPermission();
    
    // Start reminders if enabled
    if (reminderEnabled && notificationPermission) {
        startReminders();
    }
    
    // Add event listener to the reminder toggle in settings
    if (document.getElementById('reminder_enabled')) {
        document.getElementById('reminder_enabled').addEventListener('change', function() {
            if (this.checked && !notificationPermission) {
                requestNotificationPermission();
            }
        });
    }
});

// Check if notification permission is granted
function checkNotificationPermission() {
    if (!('Notification' in window)) {
        console.log('This browser does not support notifications');
        return;
    }
    
    notificationPermission = Notification.permission === 'granted';
    
    // If permission is not determined, we'll ask when user enables reminders
    if (Notification.permission !== 'denied' && Notification.permission !== 'granted') {
        document.getElementById('notificationBanner').style.display = 'block';
    }
}

// Request notification permission
function requestNotificationPermission() {
    if (!('Notification' in window)) {
        console.log('This browser does not support notifications');
        return;
    }
    
    Notification.requestPermission().then(function(permission) {
        notificationPermission = permission === 'granted';
        
        if (notificationPermission) {
            document.getElementById('notificationBanner').style.display = 'none';
            
            // If user enabled reminders in settings, start them now
            if (document.getElementById('reminder_enabled') && 
                document.getElementById('reminder_enabled').checked) {
                startReminders();
            }
        }
    });
}

// Start the reminder system
function startReminders() {
    if (!notificationPermission) {
        console.log('Notification permission not granted');
        return;
    }
    
    // Clear any existing interval
    if (reminderInterval) {
        clearInterval(reminderInterval);
    }
    
    // Convert minutes to milliseconds
    const intervalMs = intervalMinutes * 60 * 1000;
    
    // Set up the interval
    reminderInterval = setInterval(function() {
        showReminderNotification();
    }, intervalMs);
    
    console.log(`Reminders started with interval of ${intervalMinutes} minutes`);
    
    // Show a notification immediately to confirm it's working
    showReminderNotification(true);
}

// Show a reminder notification
function showReminderNotification(isTest = false) {
    if (!notificationPermission) {
        return;
    }
    
    const title = isTest ? 'Reminder Test' : 'Hydration Reminder';
    const options = {
        body: isTest ? 'Reminders are now enabled!' : 'Time to drink some water!',
        icon: '/static/images/water-icon.png',
        badge: '/static/images/water-icon.png'
    };
    
    const notification = new Notification(title, options);
    
    // Close the notification after 10 seconds
    setTimeout(function() {
        notification.close();
    }, 10000);
    
    // Handle click on notification
    notification.onclick = function() {
        window.focus();
        notification.close();
    };
}

// Stop the reminder system
function stopReminders() {
    if (reminderInterval) {
        clearInterval(reminderInterval);
        reminderInterval = null;
        console.log('Reminders stopped');
    }
}
