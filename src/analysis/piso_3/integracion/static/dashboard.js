
// Socket.IO connection
const socket = io();

// Chart.js configuration
let performanceChart;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeChart();
    
    // Socket events
    socket.on('connect', function() {
        console.log('🔗 Conectado al dashboard');
    });
    
    socket.on('metrics_update', function(data) {
        updateMetrics(data);
    });
    
    socket.on('new_fvg', function(data) {
        addFVGToTable(data);
        updateChart();
    });
    
    socket.on('new_alert', function(data) {
        addAlert(data);
    });
    
    socket.on('performance_update', function(data) {
        updatePerformanceChart(data);
    });
    
    // Request initial data
    requestData();
});

function initializeChart() {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'PnL Acumulado',
                data: [],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#ffffff' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#ffffff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    ticks: { color: '#ffffff' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                }
            }
        }
    });
}

function updateMetrics(data) {
    document.getElementById('total-fvgs').textContent = data.total_fvgs || 0;
    document.getElementById('active-fvgs').textContent = data.active_fvgs || 0;
    document.getElementById('win-rate').textContent = (data.win_rate || 0).toFixed(1) + '%';
    document.getElementById('profit-factor').textContent = (data.profit_factor || 0).toFixed(2);
    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
}

function addFVGToTable(fvg) {
    const tbody = document.getElementById('fvgs-table');
    
    // Clear loading message
    if (tbody.children.length === 1 && tbody.children[0].cells.length === 1) {
        tbody.innerHTML = '';
    }
    
    const row = tbody.insertRow(0);
    const typeClass = fvg.fvg_type === 'bullish' ? 'fvg-bullish' : 'fvg-bearish';
    
    row.innerHTML = `
        <td>${new Date(fvg.timestamp).toLocaleTimeString()}</td>
        <td><strong>${fvg.symbol}</strong></td>
        <td><span class="badge bg-info">${fvg.timeframe}</span></td>
        <td><span class="badge ${typeClass}">${fvg.fvg_type.toUpperCase()}</span></td>
        <td>${fvg.price?.toFixed(5) || '--'}</td>
        <td>${fvg.size?.toFixed(1) || '--'} pips</td>
        <td><span class="badge bg-${getQualityColor(fvg.quality)}">${fvg.quality}</span></td>
        <td><span class="badge bg-warning">ACTIVO</span></td>
    `;
    
    // Keep only last 20 rows
    while (tbody.children.length > 20) {
        tbody.removeChild(tbody.lastChild);
    }
}

function addAlert(alert) {
    const container = document.getElementById('alerts-container');
    
    // Clear "no alerts" message
    if (container.children.length === 1 && container.children[0].tagName === 'P') {
        container.innerHTML = '';
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert-item alert-${alert.level.toLowerCase()}`;
    alertDiv.innerHTML = `
        <div class="d-flex justify-content-between">
            <strong>${alert.level.toUpperCase()}</strong>
            <small>${new Date(alert.timestamp).toLocaleTimeString()}</small>
        </div>
        <div>${alert.message}</div>
    `;
    
    container.insertBefore(alertDiv, container.firstChild);
    
    // Keep only last 10 alerts
    while (container.children.length > 10) {
        container.removeChild(container.lastChild);
    }
}

function updatePerformanceChart(data) {
    if (performanceChart && data.history) {
        performanceChart.data.labels = data.history.map(point => 
            new Date(point.timestamp).toLocaleTimeString()
        );
        performanceChart.data.datasets[0].data = data.history.map(point => point.pnl);
        performanceChart.update('none');
    }
}

function getQualityColor(quality) {
    const q = quality?.toLowerCase() || '';
    if (q.includes('high') || q.includes('excellent')) return 'success';
    if (q.includes('medium') || q.includes('good')) return 'warning';
    return 'secondary';
}

function requestData() {
    fetch('/api/dashboard-data')
        .then(response => response.json())
        .then(data => {
            updateMetrics(data.metrics);
            
            // Load recent FVGs
            data.fvgs.forEach(fvg => addFVGToTable(fvg));
            
            // Load recent alerts
            data.alerts.forEach(alert => addAlert(alert));
            
            // Update chart
            updatePerformanceChart({ history: data.performance_history });
        })
        .catch(error => console.error('Error loading data:', error));
}
        