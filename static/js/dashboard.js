// Real-time dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Set up notification system
    setupNotifications();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Add animation effects
    addAnimationEffects();
    
    // Check for anomalies when page loads
    checkAnomalies();
    
    // Auto-refresh data every 5 minutes
    setInterval(refreshData, 300000);
    
    // Set up form validation
    setupFormValidation();
});

// Function to initialize Bootstrap components
function initializeBootstrapComponents() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Function to add animation effects
function addAnimationEffects() {
    // Animate cards when they come into view
    const cards = document.querySelectorAll('.card');
    
    // Create an intersection observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    // Observe each card
    cards.forEach(card => {
        observer.observe(card);
        // Add hover effect class
        card.classList.add('hover-effect');
    });
}

// Function to handle notifications
function setupNotifications() {
    // Check if browser supports notifications
    if (!("Notification" in window)) {
        console.log("This browser does not support desktop notifications");
        return;
    }
    
    // Request permission
    if (Notification.permission !== "granted" && Notification.permission !== "denied") {
        Notification.requestPermission();
    }
    
    // Add notification settings button
    const navbarNav = document.querySelector('.navbar-nav');
    if (navbarNav) {
        const settingsLi = document.createElement('li');
        settingsLi.className = 'nav-item';
        settingsLi.innerHTML = `
            <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#notificationSettingsModal">
                <i class="fas fa-bell me-1"></i> Notifications
            </a>
        `;
        navbarNav.appendChild(settingsLi);
        
        // Create modal
        const modalDiv = document.createElement('div');
        modalDiv.className = 'modal fade';
        modalDiv.id = 'notificationSettingsModal';
        modalDiv.tabIndex = '-1';
        modalDiv.setAttribute('aria-labelledby', 'notificationSettingsModalLabel');
        modalDiv.setAttribute('aria-hidden', 'true');
        
        modalDiv.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title" id="notificationSettingsModalLabel">
                            <i class="fas fa-bell me-2"></i>Notification Settings
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="enableNotifications" checked>
                            <label class="form-check-label" for="enableNotifications">Enable Notifications</label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="heartRateAlerts" checked>
                            <label class="form-check-label" for="heartRateAlerts">Heart Rate Alerts</label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="sleepAlerts" checked>
                            <label class="form-check-label" for="sleepAlerts">Sleep Alerts</label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="moodAlerts" checked>
                            <label class="form-check-label" for="moodAlerts">Mood Alerts</label>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" id="saveNotificationSettings">
                            <i class="fas fa-save me-1"></i> Save Settings
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modalDiv);
        
        // Handle save settings
        document.getElementById('saveNotificationSettings').addEventListener('click', function() {
            const settings = {
                enabled: document.getElementById('enableNotifications').checked,
                heartRate: document.getElementById('heartRateAlerts').checked,
                sleep: document.getElementById('sleepAlerts').checked,
                mood: document.getElementById('moodAlerts').checked
            };
            
            localStorage.setItem('notificationSettings', JSON.stringify(settings));
            
            // Show success message
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success alert-dismissible fade show';
            alertDiv.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>Notification settings saved successfully!
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            document.querySelector('.container').prepend(alertDiv);
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('notificationSettingsModal'));
            modal.hide();
        });
    }
}

// Function to show a notification
function showNotification(title, message, type) {
    // Check notification settings
    const settingsStr = localStorage.getItem('notificationSettings');
    const settings = settingsStr ? JSON.parse(settingsStr) : { enabled: true, heartRate: true, sleep: true, mood: true };
    
    // Check if notifications are enabled and the specific type is enabled
    if (!settings.enabled || (type === 'heart' && !settings.heartRate) || 
        (type === 'sleep' && !settings.sleep) || (type === 'mood' && !settings.mood)) {
        return;
    }
    
    // Browser notification
    if (Notification.permission === "granted") {
        const notification = new Notification(title, {
            body: message,
            icon: '/static/images/notification-icon.png'
        });
        
        notification.onclick = function() {
            window.focus();
            this.close();
        };
    }
    
    // In-app notification
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-warning alert-dismissible fade show';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i><strong>${title}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.querySelector('.container').prepend(alertDiv);
}

// Function to refresh dashboard data
function refreshData() {
    // Show loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'position-fixed top-0 start-0 w-100 bg-primary text-white text-center py-2';
    loadingDiv.style.zIndex = '9999';
    loadingDiv.innerHTML = '<i class="fas fa-sync-alt fa-spin me-2"></i>Refreshing data...';
    document.body.appendChild(loadingDiv);
    
    // Reload the page to get fresh data from the server
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

// Function to check for anomalies in the data
function checkAnomalies() {
    // Get chart data from the hidden element
    const chartDataElement = document.getElementById('chart-data');
    if (!chartDataElement) return;
    
    try {
        const chartData = JSON.parse(chartDataElement.textContent);
        
        if (chartData.heart_rates && chartData.heart_rates.length > 0) {
            // Get the latest values
            const latestIndex = chartData.heart_rates.length - 1;
            const latestHeartRate = chartData.heart_rates[latestIndex];
            const latestSleep = chartData.sleep_hours[latestIndex];
            const latestMood = chartData.moods[latestIndex];
            
            // Check for anomalies
            if (latestHeartRate > 100) {
                showNotification('Heart Rate Alert', 'Your heart rate is unusually high at ' + latestHeartRate + ' BPM!', 'heart');
            } else if (latestHeartRate < 50) {
                showNotification('Heart Rate Alert', 'Your heart rate is unusually low at ' + latestHeartRate + ' BPM!', 'heart');
            }
            
            if (latestSleep < 6) {
                showNotification('Sleep Alert', 'You are not getting enough sleep! Only ' + latestSleep + ' hours recorded.', 'sleep');
            }
            
            if (latestMood <= 2) {
                showNotification('Mood Alert', 'Your mood has been low recently. Consider activities that boost your mood.', 'mood');
            }
        }
    } catch (error) {
        console.error('Error checking anomalies:', error);
    }
}

// Function to set up form validation
function setupFormValidation() {
    const form = document.querySelector('form');
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        form.classList.add('was-validated');
    });
    
    // Add custom validation
    const heartRateInput = document.querySelector('input[name="heart_rate"]');
    if (heartRateInput) {
        heartRateInput.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (value < 40 || value > 220) {
                this.setCustomValidity('Heart rate should be between 40 and 220 BPM');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    const sleepInput = document.querySelector('input[name="sleep_hours"]');
    if (sleepInput) {
        sleepInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 0 || value > 24) {
                this.setCustomValidity('Sleep hours should be between 0 and 24');
            } else {
                this.setCustomValidity('');
            }
        });
    }
    
    const stepsInput = document.querySelector('input[name="steps"]');
    if (stepsInput) {
        stepsInput.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (value < 0 || value > 100000) {
                this.setCustomValidity('Steps should be between 0 and 100,000');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}

// Function to add new vitals via API
function addVitals(vitalsData) {
    // Show loading indicator
    const submitBtn = document.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Saving...';
    
    fetch('/api/vitals', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(vitalsData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        
        // Show success message
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>Your health data has been saved successfully!
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.querySelector('.container').prepend(alertDiv);
        
        // Refresh the page after a short delay
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Show error message
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>There was an error saving your health data. Please try again.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.querySelector('.container').prepend(alertDiv);
        
        // Reset button
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
    });
}