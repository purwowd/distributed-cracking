// Debug helper function
function debugLog(type, message, data) {
    const styles = {
        info: 'background: #3b82f6; color: white; padding: 2px 5px; border-radius: 3px;',
        success: 'background: #10b981; color: white; padding: 2px 5px; border-radius: 3px;',
        error: 'background: #ef4444; color: white; padding: 2px 5px; border-radius: 3px;',
        warning: 'background: #f59e0b; color: white; padding: 2px 5px; border-radius: 3px;'
    };
    
    const prefix = type.toUpperCase();
    const style = styles[type] || styles.info;
    
    if (data !== undefined) {
        console.log(`%c[${prefix}] ${message}`, style, data);
    } else {
        console.log(`%c[${prefix}] ${message}`, style);
    }
}

// Check if Chart.js is loaded
function isChartJsLoaded() {
    const loaded = typeof Chart !== 'undefined';
    if (loaded) {
        debugLog('success', 'Chart.js is loaded', Chart.version);
    } else {
        debugLog('error', 'Chart.js is NOT loaded!');
    }
    return loaded;
}

// Wait for the DOM and Chart.js to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    debugLog('info', 'DOM content loaded, checking Chart.js...');
    
    if (isChartJsLoaded()) {
        debugLog('info', 'Initializing charts with small delay...');
        setTimeout(initializeAllCharts, 300);
    } else {
        debugLog('warning', 'Chart.js not loaded yet, waiting for window load event');
        
        // Fallback to window load event
        window.addEventListener('load', function() {
            debugLog('info', 'Window loaded, checking Chart.js again...');
            
            if (isChartJsLoaded()) {
                debugLog('info', 'Initializing charts after window load...');
                setTimeout(initializeAllCharts, 500);
            } else {
                debugLog('error', 'Chart.js still not loaded after window load!');
                
                // Last attempt with longer delay
                debugLog('warning', 'Making final attempt with longer delay...');
                setTimeout(function() {
                    if (isChartJsLoaded()) {
                        initializeAllCharts();
                    } else {
                        debugLog('error', 'Failed to load Chart.js after multiple attempts');
                    }
                }, 1000);
            }
        });
    }
});

// Initialize all charts
async function initializeAllCharts() {
    debugLog('info', 'Initializing all charts...');
    
    // Get chart data from data attributes
    const chartData = document.getElementById('chart-data');
    debugLog('info', 'Chart data element:', chartData);
    
    if (!chartData) {
        debugLog('error', 'Chart data element not found!');
        return;
    }
    
    // Extract task data
    const taskChartData = [
        parseInt(chartData.getAttribute('data-task-pending') || 0),
        parseInt(chartData.getAttribute('data-task-running') || 0),
        parseInt(chartData.getAttribute('data-task-completed') || 0),
        parseInt(chartData.getAttribute('data-task-failed') || 0),
        parseInt(chartData.getAttribute('data-task-cancelled') || 0)
    ];
    debugLog('info', 'Task chart data:', taskChartData);
    
    // Extract agent data
    const agentChartData = [
        parseInt(chartData.getAttribute('data-agent-online') || 0),
        parseInt(chartData.getAttribute('data-agent-busy') || 0),
        parseInt(chartData.getAttribute('data-agent-offline') || 0)
    ];
    debugLog('info', 'Agent chart data:', agentChartData);
    
    // Check if all canvas elements exist
    const taskCanvas = document.getElementById('taskChart');
    const agentCanvas = document.getElementById('agentChart');
    const performanceCanvas = document.getElementById('performanceChart');
    
    debugLog('info', 'Canvas elements:', {
        taskCanvas: taskCanvas ? 'Found' : 'Missing',
        agentCanvas: agentCanvas ? 'Found' : 'Missing',
        performanceCanvas: performanceCanvas ? 'Found' : 'Missing'
    });
    
    try {
        // Initialize Task Chart
        if (taskCanvas) {
            debugLog('info', 'Initializing task chart...');
            initTaskChart(taskChartData);
            debugLog('success', 'Task chart initialized successfully');
        } else {
            debugLog('warning', 'Skipping task chart initialization - canvas not found');
        }
        
        // Initialize Agent Chart
        if (agentCanvas) {
            debugLog('info', 'Initializing agent chart...');
            initAgentChart(agentChartData);
            debugLog('success', 'Agent chart initialized successfully');
        } else {
            debugLog('warning', 'Skipping agent chart initialization - canvas not found');
        }
        
        // Initialize Performance Chart
        if (performanceCanvas) {
            debugLog('info', 'Initializing performance chart...');
            
            try {
                // Since initPerformanceChart returns a Promise, we need to await it
                const performanceChart = await initPerformanceChart();
                
                if (performanceChart) {
                    debugLog('success', 'Performance chart initialized successfully');
                } else {
                    debugLog('warning', 'Performance chart returned null, trying again...');
                    
                    // Try again with a longer delay
                    setTimeout(async () => {
                        debugLog('info', 'Second attempt to initialize performance chart...');
                        const retryChart = await initPerformanceChart();
                        if (retryChart) {
                            debugLog('success', 'Performance chart initialized on second attempt');
                        } else {
                            debugLog('error', 'Failed to initialize performance chart after retry');
                        }
                    }, 1000);
                }
            } catch (chartError) {
                debugLog('error', 'Error initializing performance chart:', chartError);
            }
        } else {
            debugLog('error', 'Performance chart canvas not found!');
        }
    } catch (error) {
        debugLog('error', 'Error initializing charts:', error);
        console.error('Error details:', error.message);
        console.error('Stack trace:', error.stack);
    }
}

/**
 * Initialize the task status distribution chart
 * @param {Array} data - Task status data array
 */
function initTaskChart(data) {
    const taskCtx = document.getElementById('taskChart');
    if (!taskCtx) return;
    
    // Create gradient backgrounds
    const ctx = taskCtx.getContext('2d');
    
    // Create gradients for each segment
    const pendingGradient = ctx.createLinearGradient(0, 0, 0, 150);
    pendingGradient.addColorStop(0, '#4B5563');
    pendingGradient.addColorStop(1, '#6B7280');
    
    const runningGradient = ctx.createLinearGradient(0, 0, 0, 150);
    runningGradient.addColorStop(0, '#2563EB');
    runningGradient.addColorStop(1, '#3B82F6');
    
    const completedGradient = ctx.createLinearGradient(0, 0, 0, 150);
    completedGradient.addColorStop(0, '#059669');
    completedGradient.addColorStop(1, '#10B981');
    
    const failedGradient = ctx.createLinearGradient(0, 0, 0, 150);
    failedGradient.addColorStop(0, '#DC2626');
    failedGradient.addColorStop(1, '#EF4444');
    
    const cancelledGradient = ctx.createLinearGradient(0, 0, 0, 150);
    cancelledGradient.addColorStop(0, '#D97706');
    cancelledGradient.addColorStop(1, '#F59E0B');
    
    // Calculate total for center text
    const total = data.reduce((acc, val) => acc + val, 0);
    
    const taskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Pending', 'Running', 'Completed', 'Failed', 'Cancelled'],
            datasets: [{
                data: data,
                backgroundColor: [
                    pendingGradient,
                    runningGradient,
                    completedGradient,
                    failedGradient,
                    cancelledGradient
                ],
                borderColor: '#1F2937', /* Gray-800 - dark mode background */
                borderWidth: 2,
                hoverOffset: 15,
                borderRadius: 8,
                spacing: 3,
                hoverBorderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1.5,
            cutout: '68%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#D1D5DB', /* Gray-300 - light text for dark mode */
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'rectRounded',
                        font: {
                            family: "'Inter', sans-serif",
                            size: 11
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(31, 41, 55, 0.9)', /* Gray-800 with opacity */
                    titleColor: '#F3F4F6', /* Gray-100 */
                    bodyColor: '#E5E7EB', /* Gray-200 */
                    borderColor: '#4B5563', /* Gray-600 */
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    boxWidth: 10,
                    boxHeight: 10,
                    boxPadding: 3,
                    usePointStyle: true,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 1200,
                easing: 'easeOutCirc'
            }
        },
        plugins: [{
            id: 'centerText',
            beforeDraw: function(chart) {
                const width = chart.width;
                const height = chart.height;
                const ctx = chart.ctx;
                
                ctx.restore();
                
                // Font settings for "Total"
                let fontSize = (height / 14).toFixed(2);
                ctx.font = `bold ${fontSize}px 'Inter', sans-serif`;
                ctx.textBaseline = 'middle';
                ctx.fillStyle = '#F3F4F6'; // Gray-100
                
                // Text "Total"
                const text = 'TOTAL';
                const textX = Math.round((width - ctx.measureText(text).width) / 2);
                const textY = height / 2 - fontSize;
                ctx.fillText(text, textX, textY);
                
                // Font settings for total value
                fontSize = (height / 8).toFixed(2);
                ctx.font = `bold ${fontSize}px 'Inter', sans-serif`;
                ctx.textBaseline = 'middle';
                ctx.fillStyle = '#F3F4F6'; // Gray-100
                
                // Total value
                const text2 = total.toString();
                const text2X = Math.round((width - ctx.measureText(text2).width) / 2);
                const text2Y = height / 2 + fontSize / 2;
                ctx.fillText(text2, text2X, text2Y);
                
                ctx.save();
            }
        }]
    });
}

/**
 * Initialize the agent status distribution chart
 * @param {Array} data - Agent status data array
 */
function initAgentChart(data) {
    const agentCtx = document.getElementById('agentChart');
    if (!agentCtx) return;
    
    // Create shimmer effect backgrounds
    const ctx = agentCtx.getContext('2d');
    
    // Create radial gradients for each segment
    const onlineGradient = ctx.createRadialGradient(75, 75, 0, 75, 75, 100);
    onlineGradient.addColorStop(0, 'rgba(16, 185, 129, 0.9)'); // Green-500 with opacity
    onlineGradient.addColorStop(0.7, 'rgba(5, 150, 105, 0.8)'); // Green-600 with opacity
    onlineGradient.addColorStop(1, 'rgba(4, 120, 87, 0.7)'); // Green-700 with opacity
    
    const busyGradient = ctx.createRadialGradient(75, 75, 0, 75, 75, 100);
    busyGradient.addColorStop(0, 'rgba(59, 130, 246, 0.9)'); // Blue-500 with opacity
    busyGradient.addColorStop(0.7, 'rgba(37, 99, 235, 0.8)'); // Blue-600 with opacity
    busyGradient.addColorStop(1, 'rgba(29, 78, 216, 0.7)'); // Blue-700 with opacity
    
    const offlineGradient = ctx.createRadialGradient(75, 75, 0, 75, 75, 100);
    offlineGradient.addColorStop(0, 'rgba(107, 114, 128, 0.9)'); // Gray-500 with opacity
    offlineGradient.addColorStop(0.7, 'rgba(75, 85, 99, 0.8)'); // Gray-600 with opacity
    offlineGradient.addColorStop(1, 'rgba(55, 65, 81, 0.7)'); // Gray-700 with opacity
    
    const agentChart = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: ['Online', 'Busy', 'Offline'],
            datasets: [{
                data: data,
                backgroundColor: [
                    onlineGradient,
                    busyGradient,
                    offlineGradient
                ],
                borderColor: '#1F2937', // Gray-800 - dark mode background
                borderWidth: 1,
                borderAlign: 'inner',
                hoverBorderColor: '#F9FAFB', // Gray-50
                hoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1.5,
            scales: {
                r: {
                    display: true,
                    backgroundColor: 'rgba(17, 24, 39, 0.7)', // Gray-900 with opacity
                    grid: {
                        color: 'rgba(75, 85, 99, 0.3)', // Gray-600 with opacity
                        circular: true
                    },
                    ticks: {
                        display: false
                    },
                    pointLabels: {
                        display: false
                    },
                    angleLines: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#D1D5DB', // Gray-300 - light text for dark mode
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'triangle',
                        font: {
                            family: "'Inter', sans-serif",
                            size: 11
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(17, 24, 39, 0.9)', // Gray-900 with opacity
                    titleColor: '#F3F4F6', // Gray-100
                    bodyColor: '#E5E7EB', // Gray-200
                    borderColor: '#374151', // Gray-700
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    boxWidth: 10,
                    boxHeight: 10,
                    boxPadding: 3,
                    usePointStyle: true,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 1500,
                easing: 'easeOutElastic'
            }
        }
    });
}

// Global variable to store the performance chart instance
let performanceChartInstance = null;

// Performance Chart
function initPerformanceChart() {
    debugLog('info', 'Initializing performance chart...');
    
    if (typeof Chart === 'undefined') {
        debugLog('error', 'Chart.js is not loaded!');
        return null;
    }
    
    const canvas = document.getElementById('performanceChart');
    debugLog('info', 'Performance canvas:', canvas);
    
    if (!canvas) {
        debugLog('error', 'Performance chart canvas not found!');
        return null;
    }
    
    debugLog('info', 'Canvas dimensions:', {
        width: canvas.width,
        height: canvas.height,
        clientWidth: canvas.clientWidth,
        clientHeight: canvas.clientHeight,
        style: canvas.getAttribute('style')
    });
    
    return new Promise((resolve) => {
        // Fetch performance data from API
        fetchPerformanceData()
            .then(chartData => {
                setTimeout(() => {
                    try {
                        debugLog('info', 'Creating performance chart with API data...');
                        const ctx = canvas.getContext('2d');
                        
                        if (!ctx) {
                            debugLog('error', 'Could not get 2D context from canvas!');
                            resolve(null);
                            return;
                        }
                        
                        const chartConfig = {
                            type: 'line',
                            data: chartData,
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                interaction: {
                                    mode: 'index',
                                    intersect: false,
                                },
                                stacked: false,
                                plugins: {
                                    title: {
                                        display: true,
                                        text: 'System Performance (Last 24 Hours)',
                                        color: '#D1D5DB' /* Gray-300 - light text for dark mode */
                                    },
                                    legend: {
                                        labels: {
                                            color: '#D1D5DB' /* Gray-300 - light text for dark mode */
                                        }
                                    },
                                    tooltip: {
                                        mode: 'index',
                                        intersect: false,
                                        backgroundColor: 'rgba(31, 41, 55, 0.8)', /* Gray-800 with opacity */
                                        titleColor: '#F3F4F6', /* Gray-100 */
                                        bodyColor: '#E5E7EB', /* Gray-200 */
                                        borderColor: '#4B5563', /* Gray-600 */
                                        borderWidth: 1
                                    }
                                },
                                scales: {
                                    y: {
                                        type: 'linear',
                                        display: true,
                                        position: 'left',
                                        title: {
                                            display: true,
                                            text: 'Count',
                                            color: '#9CA3AF' /* Gray-400 */
                                        },
                                        grid: {
                                            color: 'rgba(75, 85, 99, 0.2)' /* Gray-600 with opacity */
                                        },
                                        ticks: {
                                            color: '#9CA3AF' /* Gray-400 */
                                        }
                                    },
                                    y1: {
                                        type: 'linear',
                                        display: true,
                                        position: 'right',
                                        title: {
                                            display: true,
                                            text: 'Speed (MH/s)',
                                            color: '#9CA3AF' /* Gray-400 */
                                        },
                                        grid: {
                                            drawOnChartArea: false,
                                            color: 'rgba(75, 85, 99, 0.2)' /* Gray-600 with opacity */
                                        },
                                        ticks: {
                                            color: '#9CA3AF' /* Gray-400 */
                                        }
                                    },
                                    x: {
                                        grid: {
                                            color: 'rgba(75, 85, 99, 0.2)' /* Gray-600 with opacity */
                                        },
                                        ticks: {
                                            color: '#9CA3AF' /* Gray-400 */
                                        }
                                    }
                                }
                            }
                        };
                        
                        // Store chart instance in global variable for updates
                        performanceChartInstance = new Chart(ctx, chartConfig);
                        debugLog('success', 'Performance chart created successfully with API data!');
                        
                        // Set up auto-refresh every 60 seconds
                        setupPerformanceChartRefresh();
                        
                        resolve(performanceChartInstance);
                    } catch (error) {
                        debugLog('error', 'Error creating performance chart:', error);
                        console.error('Error details:', error.message);
                        console.error('Stack trace:', error.stack);
                        resolve(null);
                    }
                }, 500);
            })
            .catch(error => {
                debugLog('error', 'Error fetching performance data:', error);
                // Fallback to mock data if API fails
                setTimeout(() => {
                    try {
                        debugLog('info', 'Creating performance chart with fallback data...');
                        const ctx = canvas.getContext('2d');
                        
                        if (!ctx) {
                            debugLog('error', 'Could not get 2D context from canvas!');
                            resolve(null);
                            return;
                        }
                        
                        // Fallback chart with mock data
                        const fallbackConfig = {
                            type: 'bar',
                            data: {
                                labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
                                datasets: [{
                                    label: 'Fallback Data',
                                    data: [12, 19, 3, 5, 2, 3],
                                    backgroundColor: [
                                        'rgba(239, 68, 68, 0.5)',   // Red-500
                                        'rgba(59, 130, 246, 0.5)',  // Blue-500
                                        'rgba(245, 158, 11, 0.5)',  // Amber-500
                                        'rgba(16, 185, 129, 0.5)',  // Green-500
                                        'rgba(139, 92, 246, 0.5)',  // Purple-500
                                        'rgba(249, 115, 22, 0.5)'   // Orange-500
                                    ],
                                    borderColor: [
                                        'rgba(239, 68, 68, 1)',   // Red-500
                                        'rgba(59, 130, 246, 1)',  // Blue-500
                                        'rgba(245, 158, 11, 1)',  // Amber-500
                                        'rgba(16, 185, 129, 1)',  // Green-500
                                        'rgba(139, 92, 246, 1)',  // Purple-500
                                        'rgba(249, 115, 22, 1)'   // Orange-500
                                    ],
                                    borderWidth: 1
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: {
                                        labels: {
                                            color: '#D1D5DB' // Gray-300
                                        }
                                    },
                                    tooltip: {
                                        backgroundColor: 'rgba(31, 41, 55, 0.8)', // Gray-800 with opacity
                                        titleColor: '#F3F4F6', // Gray-100
                                        bodyColor: '#E5E7EB', // Gray-200
                                        borderColor: '#4B5563', // Gray-600
                                        borderWidth: 1
                                    }
                                },
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        grid: {
                                            color: 'rgba(75, 85, 99, 0.2)' // Gray-600 with opacity
                                        },
                                        ticks: {
                                            color: '#9CA3AF' // Gray-400
                                        }
                                    },
                                    x: {
                                        grid: {
                                            color: 'rgba(75, 85, 99, 0.2)' // Gray-600 with opacity
                                        },
                                        ticks: {
                                            color: '#9CA3AF' // Gray-400
                                        }
                                    }
                                }
                            }
                        };
                        performanceChartInstance = new Chart(ctx, fallbackConfig);
                        debugLog('warning', 'Performance chart created with fallback data due to API error');
                        resolve(performanceChartInstance);
                    } catch (error) {
                        debugLog('error', 'Error creating fallback performance chart:', error);
                        console.error('Error details:', error.message);
                        console.error('Stack trace:', error.stack);
                        resolve(null);
                    }
                }, 500);
            });
    });
}

// Function to fetch performance data from API
async function fetchPerformanceData() {
    debugLog('info', 'Fetching performance data from API...');
    
    try {
        // Try the debug endpoint first to check if API is accessible
        try {
            debugLog('info', 'Testing API connectivity with debug endpoint');
            const debugResponse = await fetch('/api/debug');
            if (debugResponse.ok) {
                const debugData = await debugResponse.json();
                debugLog('success', 'Debug API test successful:', debugData);
            } else {
                debugLog('warning', `Debug API test failed: ${debugResponse.status} ${debugResponse.statusText}`);
            }
        } catch (debugError) {
            debugLog('warning', 'Debug API test error:', debugError);
        }
        
        // Now try the actual performance data endpoint
        debugLog('info', 'Requesting performance data from /api/performance-data');
        const response = await fetch('/api/performance-data');
        
        if (!response.ok) {
            const errorText = await response.text();
            debugLog('error', `API returned ${response.status}: ${response.statusText}`);
            debugLog('error', 'Response body:', errorText);
            throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        debugLog('success', 'Performance data fetched successfully');
        debugLog('info', 'Data structure:', Object.keys(data).join(', '));
        
        // Validate the data structure
        if (!data.labels || !data.datasets) {
            debugLog('error', 'Invalid data structure received from API');
            throw new Error('Invalid data structure received from API');
        }
        
        return data;
    } catch (error) {
        debugLog('error', 'Failed to fetch performance data:', error);
        // Return mock data as fallback
        debugLog('info', 'Falling back to mock data');
        return getMockPerformanceData();
    }
}

// Function to generate mock performance data for fallback
function getMockPerformanceData() {
    debugLog('info', 'Generating mock performance data');
    
    // Generate time labels for the last 24 hours
    const now = new Date();
    const labels = [];
    for (let i = 23; i >= 0; i--) {
        const date = new Date(now);
        date.setHours(date.getHours() - i);
        labels.push(date.getHours() + ':00');
    }
    
    // Generate random data for each dataset
    return {
        labels: labels,
        datasets: [
            {
                label: 'Active Agents',
                data: Array.from({length: 24}, () => Math.floor(Math.random() * 10)),
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderWidth: 2,
                tension: 0.4,
                yAxisID: 'y'
            },
            {
                label: 'Completed Tasks',
                data: Array.from({length: 24}, () => Math.floor(Math.random() * 20)),
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                tension: 0.4,
                yAxisID: 'y'
            },
            {
                label: 'Speed (MH/s)',
                data: Array.from({length: 24}, () => Math.random() * 10),
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderWidth: 2,
                tension: 0.4,
                yAxisID: 'y1'
            }
        ]
    };
}

// Function to set up auto-refresh for performance chart
function setupPerformanceChartRefresh() {
    // Add refresh button to the chart container
    addRefreshButton();
    
    // Set up auto-refresh interval
    const refreshInterval = setInterval(() => {
        refreshPerformanceChart();
    }, 60000); // Refresh every 60 seconds
    
    // Store interval ID in window object to allow clearing if needed
    window.performanceChartRefreshInterval = refreshInterval;
    
    debugLog('info', 'Performance chart auto-refresh set up (60s interval)');
}

// Function to refresh the performance chart
function refreshPerformanceChart() {
    debugLog('info', 'Refreshing performance chart...');
    
    // Show loading indicator
    const chartContainer = document.getElementById('performanceChart').parentNode;
    const loadingIndicator = chartContainer.querySelector('.chart-loading') || createLoadingIndicator(chartContainer);
    loadingIndicator.style.display = 'flex';
    
    // Fetch new performance data from API
    fetchPerformanceData()
        .then(chartData => {
            if (performanceChartInstance) {
                // Update chart with new data
                performanceChartInstance.data = chartData;
                performanceChartInstance.update();
                
                // Update last refresh time
                updateLastRefreshTime();
                
                debugLog('success', 'Performance chart refreshed successfully!');
            } else {
                debugLog('error', 'Cannot refresh chart: chart instance is null');
            }
        })
        .catch(error => {
            debugLog('error', 'Error refreshing performance chart:', error);
        })
        .finally(() => {
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.style.display = 'none';
            }
        });
}

// Function to add refresh button to chart container
function addRefreshButton() {
    const chartContainer = document.getElementById('performanceChart').parentNode;
    
    // Create refresh controls container
    const controlsContainer = document.createElement('div');
    controlsContainer.className = 'chart-controls';
    controlsContainer.style.position = 'absolute';
    controlsContainer.style.top = '10px';
    controlsContainer.style.right = '10px';
    controlsContainer.style.zIndex = '10';
    controlsContainer.style.display = 'flex';
    controlsContainer.style.alignItems = 'center';
    controlsContainer.style.gap = '8px';
    
    // Create refresh button
    const refreshButton = document.createElement('button');
    refreshButton.className = 'chart-refresh-btn';
    refreshButton.innerHTML = '<i class="fa-solid fa-sync-alt"></i> Refresh';
    refreshButton.style.padding = '4px 8px';
    refreshButton.style.backgroundColor = '#3b82f6';
    refreshButton.style.color = 'white';
    refreshButton.style.border = 'none';
    refreshButton.style.borderRadius = '4px';
    refreshButton.style.cursor = 'pointer';
    refreshButton.style.fontSize = '12px';
    refreshButton.style.display = 'flex';
    refreshButton.style.alignItems = 'center';
    refreshButton.style.gap = '4px';
    
    // Add click event listener
    refreshButton.addEventListener('click', function() {
        refreshPerformanceChart();
    });
    
    // Create last refresh time element
    const lastRefreshTime = document.createElement('span');
    lastRefreshTime.className = 'last-refresh-time';
    lastRefreshTime.style.fontSize = '11px';
    lastRefreshTime.style.color = '#6b7280';
    lastRefreshTime.textContent = 'Last update: Just now';
    
    // Add elements to controls container
    controlsContainer.appendChild(refreshButton);
    controlsContainer.appendChild(lastRefreshTime);
    
    // Create loading indicator
    createLoadingIndicator(chartContainer);
    
    // Add controls to chart container
    chartContainer.style.position = 'relative';
    chartContainer.appendChild(controlsContainer);
}

// Function to create loading indicator
function createLoadingIndicator(container) {
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'chart-loading';
    loadingIndicator.style.position = 'absolute';
    loadingIndicator.style.top = '0';
    loadingIndicator.style.left = '0';
    loadingIndicator.style.width = '100%';
    loadingIndicator.style.height = '100%';
    loadingIndicator.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
    loadingIndicator.style.display = 'none';
    loadingIndicator.style.justifyContent = 'center';
    loadingIndicator.style.alignItems = 'center';
    loadingIndicator.style.zIndex = '5';
    
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.style.border = '4px solid #f3f3f3';
    spinner.style.borderTop = '4px solid #3b82f6';
    spinner.style.borderRadius = '50%';
    spinner.style.width = '30px';
    spinner.style.height = '30px';
    spinner.style.animation = 'spin 1s linear infinite';
    
    // Add keyframes for spinner animation
    if (!document.getElementById('spinner-keyframes')) {
        const style = document.createElement('style');
        style.id = 'spinner-keyframes';
        style.textContent = '@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }';
        document.head.appendChild(style);
    }
    
    loadingIndicator.appendChild(spinner);
    container.appendChild(loadingIndicator);
    
    return loadingIndicator;
}

// Function to update last refresh time
function updateLastRefreshTime() {
    const lastRefreshElement = document.querySelector('.last-refresh-time');
    if (lastRefreshElement) {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        lastRefreshElement.textContent = `Last update: ${timeString}`;
    }
}
