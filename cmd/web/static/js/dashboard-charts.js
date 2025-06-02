// Initialize charts when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Get chart data from data attributes
    const chartData = document.getElementById('chart-data');
    if (!chartData) return;
    
    // Extract task data
    const taskChartData = [
        parseInt(chartData.getAttribute('data-task-pending') || 0),
        parseInt(chartData.getAttribute('data-task-running') || 0),
        parseInt(chartData.getAttribute('data-task-completed') || 0),
        parseInt(chartData.getAttribute('data-task-failed') || 0),
        parseInt(chartData.getAttribute('data-task-cancelled') || 0)
    ];
    
    // Extract agent data
    const agentChartData = [
        parseInt(chartData.getAttribute('data-agent-online') || 0),
        parseInt(chartData.getAttribute('data-agent-busy') || 0),
        parseInt(chartData.getAttribute('data-agent-offline') || 0)
    ];
    
    // Task Status Chart
    initTaskChart(taskChartData);
    
    // Agent Status Chart
    initAgentChart(agentChartData);
});

/**
 * Initialize the task status distribution chart
 * @param {Array} data - Task status data array
 */
function initTaskChart(data) {
    const taskCtx = document.getElementById('taskChart');
    if (!taskCtx) return;
    
    const taskChart = new Chart(taskCtx.getContext('2d'), {
        type: 'pie',
        data: {
            labels: ['Pending', 'Running', 'Completed', 'Failed', 'Cancelled'],
            datasets: [{
                data: data,
                backgroundColor: [
                    '#6c757d', /* Secondary (Pending) */
                    '#0d6efd', /* Primary (Running) */
                    '#198754', /* Success (Completed) */
                    '#dc3545', /* Danger (Failed) */
                    '#ffc107'  /* Warning (Cancelled) */
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Initialize the agent status distribution chart
 * @param {Array} data - Agent status data array
 */
function initAgentChart(data) {
    const agentCtx = document.getElementById('agentChart');
    if (!agentCtx) return;
    
    const agentChart = new Chart(agentCtx.getContext('2d'), {
        type: 'pie',
        data: {
            labels: ['Online', 'Busy', 'Offline'],
            datasets: [{
                data: data,
                backgroundColor: [
                    '#198754', /* Success (Online) */
                    '#0d6efd', /* Primary (Busy) */
                    '#6c757d'  /* Secondary (Offline) */
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
