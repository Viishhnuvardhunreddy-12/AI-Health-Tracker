// Chart initialization and rendering
document.addEventListener('DOMContentLoaded', function() {
    // Get chart data from the hidden element
    const chartDataElement = document.getElementById('chart-data');
    if (!chartDataElement) return;
    
    try {
        const chartData = JSON.parse(chartDataElement.textContent);
        
        // Initialize charts if we have data
        if (chartData.dates && chartData.dates.length > 0) {
            initializeHeartRateChart(chartData.dates, chartData.heart_rates);
            initializeSleepChart(chartData.dates, chartData.sleep_hours);
            initializeStepsChart(chartData.dates, chartData.steps);
            initializeMoodChart(chartData.dates, chartData.moods);
        } else {
            // Display 'No data available yet' message in each chart container
            displayNoDataMessage('heartRateChart');
            displayNoDataMessage('sleepChart');
            displayNoDataMessage('stepsChart');
            displayNoDataMessage('moodChart');
        }
    } catch (error) {
        console.error('Error parsing chart data:', error);
        // Display error message in each chart container
        displayNoDataMessage('heartRateChart');
        displayNoDataMessage('sleepChart');
        displayNoDataMessage('stepsChart');
        displayNoDataMessage('moodChart');
    }
});

// Function to display 'No data available yet' message
function displayNoDataMessage(chartId) {
    const chartCanvas = document.getElementById(chartId);
    if (!chartCanvas) return;
    
    const container = chartCanvas.parentElement;
    
    // Remove the canvas
    chartCanvas.remove();
    
    // Create and add the message
    const messageDiv = document.createElement('div');
    messageDiv.className = 'text-center py-5';
    messageDiv.innerHTML = `
        <i class="fas fa-chart-line fa-3x text-muted mb-3"></i>
        <p class="text-muted">No data available yet</p>
        <button class="btn btn-sm btn-outline-primary mt-2" onclick="document.querySelector('form').scrollIntoView({behavior: 'smooth'})">
            <i class="fas fa-plus-circle me-2"></i>Add Data
        </button>
    `;
    container.appendChild(messageDiv);
}

// Common chart options
const commonChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    elements: {
        point: {
            radius: 4,
            hoverRadius: 6,
            borderWidth: 2,
            hoverBorderWidth: 3
        },
        line: {
            tension: 0.3
        }
    },
    interaction: {
        mode: 'index',
        intersect: false
    },
    plugins: {
        legend: {
            display: false
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            padding: 10,
            titleFont: {
                size: 14,
                weight: 'bold'
            },
            bodyFont: {
                size: 13
            },
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            displayColors: false,
            caretSize: 6
        }
    },
    animation: {
        duration: 1500,
        easing: 'easeOutQuart'
    }
};

// Heart Rate Chart
function initializeHeartRateChart(dates, heartRates) {
    const ctx = document.getElementById('heartRateChart');
    if (!ctx) return;
    
    // Define healthy range for heart rate
    const normalMin = 60;
    const normalMax = 100;
    
    // Create gradient background
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(76, 201, 240, 0.3)');
    gradient.addColorStop(1, 'rgba(76, 201, 240, 0.0)');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Heart Rate (BPM)',
                data: heartRates,
                borderColor: '#4CC9F0',
                backgroundColor: gradient,
                borderWidth: 2,
                fill: true,
                pointBackgroundColor: heartRates.map(hr => 
                    hr < normalMin || hr > normalMax ? '#f72585' : '#4CC9F0'
                )
            }]
        },
        options: {
            ...commonChartOptions,
            scales: {
                y: {
                    beginAtZero: false,
                    suggestedMin: Math.max(40, Math.min(...heartRates) - 10),
                    suggestedMax: Math.min(120, Math.max(...heartRates) + 10),
                    grid: {
                        color: 'rgba(200, 200, 200, 0.1)'
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            size: 10
                        }
                    }
                }
            },
            plugins: {
                ...commonChartOptions.plugins,
                tooltip: {
                    ...commonChartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            const hr = context.raw;
                            let status = '';
                            if (hr < normalMin) status = ' (Below normal)';
                            else if (hr > normalMax) status = ' (Above normal)';
                            else status = ' (Normal)';
                            return `Heart Rate: ${hr} BPM${status}`;
                        }
                    }
                }
            }
        }
    });
}

// Sleep Chart
function initializeSleepChart(dates, sleepHours) {
    const ctx = document.getElementById('sleepChart');
    if (!ctx) return;
    
    // Define healthy range for sleep
    const normalMin = 7;
    const normalMax = 9;
    
    // Create gradient background
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(72, 149, 239, 0.3)');
    gradient.addColorStop(1, 'rgba(72, 149, 239, 0.0)');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Sleep Hours',
                data: sleepHours,
                borderColor: '#4895EF',
                backgroundColor: gradient,
                borderWidth: 2,
                fill: true,
                pointBackgroundColor: sleepHours.map(hrs => 
                    hrs < normalMin || hrs > normalMax ? '#f72585' : '#4895EF'
                )
            }]
        },
        options: {
            ...commonChartOptions,
            scales: {
                y: {
                    beginAtZero: false,
                    suggestedMin: Math.max(0, Math.min(...sleepHours) - 1),
                    suggestedMax: Math.min(12, Math.max(...sleepHours) + 1),
                    grid: {
                        color: 'rgba(200, 200, 200, 0.1)'
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            size: 10
                        }
                    }
                }
            },
            plugins: {
                ...commonChartOptions.plugins,
                tooltip: {
                    ...commonChartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            const hrs = context.raw;
                            let status = '';
                            if (hrs < normalMin) status = ' (Below recommended)';
                            else if (hrs > normalMax) status = ' (Above recommended)';
                            else status = ' (Optimal)';
                            return `Sleep: ${hrs} hours${status}`;
                        }
                    }
                }
            }
        }
    });
}

// Steps Chart
function initializeStepsChart(dates, steps) {
    const ctx = document.getElementById('stepsChart');
    if (!ctx) return;
    
    // Define target steps
    const targetSteps = 10000;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Steps',
                data: steps,
                backgroundColor: steps.map(step => 
                    step >= targetSteps ? 'rgba(247, 37, 133, 0.7)' : 'rgba(247, 37, 133, 0.4)'
                ),
                borderWidth: 0,
                borderRadius: 4,
                barPercentage: 0.7,
                categoryPercentage: 0.7
            }]
        },
        options: {
            ...commonChartOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(200, 200, 200, 0.1)'
                    },
                    ticks: {
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            if (value >= 1000) {
                                return value / 1000 + 'k';
                            }
                            return value;
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            size: 10
                        }
                    }
                }
            },
            plugins: {
                ...commonChartOptions.plugins,
                tooltip: {
                    ...commonChartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            const step = context.raw;
                            const percentage = Math.round((step / targetSteps) * 100);
                            return [
                                `Steps: ${step.toLocaleString()}`,
                                `${percentage}% of daily goal`
                            ];
                        }
                    }
                }
            }
        }
    });
}

// Mood Chart
function initializeMoodChart(dates, moods) {
    const ctx = document.getElementById('moodChart');
    if (!ctx) return;
    
    // Convert numeric moods to labels
    const moodLabels = {
        1: 'Very Poor',
        2: 'Poor',
        3: 'Neutral',
        4: 'Good',
        5: 'Excellent'
    };
    
    // Define colors for different moods
    const moodColors = {
        1: '#e63946', // Very Poor - Red
        2: '#f4a261', // Poor - Orange
        3: '#a8dadc', // Neutral - Light Blue
        4: '#90be6d', // Good - Light Green
        5: '#43aa8b'  // Excellent - Green
    };
    
    // Create dataset with colored points
    const moodDataset = {
        label: 'Mood',
        data: moods,
        borderColor: '#6c757d',
        backgroundColor: 'rgba(108, 117, 125, 0.1)',
        borderWidth: 2,
        fill: false,
        stepped: 'middle',
        pointBackgroundColor: moods.map(mood => moodColors[mood] || '#6c757d')
    };
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [moodDataset]
        },
        options: {
            ...commonChartOptions,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 0.5,
                    max: 5.5,
                    grid: {
                        color: 'rgba(200, 200, 200, 0.1)'
                    },
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return moodLabels[value] || '';
                        },
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: {
                            size: 10
                        }
                    }
                }
            },
            plugins: {
                ...commonChartOptions.plugins,
                tooltip: {
                    ...commonChartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            return `Mood: ${moodLabels[value] || value}`;
                        }
                    }
                }
            }
        }
    });
}