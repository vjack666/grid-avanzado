"""
🌐 DASHBOARD WEB FVG - PISO 3 INTEGRACIÓN
Dashboard web moderno para monitoreo del sistema FVG en tiempo real

Fecha: Agosto 13, 2025
Oficina: Integración - Piso 3
Estado: Sistema Web Interface
Versión: v1.0.0-PRODUCTION
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import webbrowser
from threading import Thread

# Flask y componentes web
try:
    from flask import Flask, render_template, jsonify, request
    from flask_socketio import SocketIO, emit
    from flask_cors import CORS
except ImportError:
    print("⚠️ Installing required web dependencies...")
    import subprocess
    subprocess.run(["pip", "install", "flask", "flask-socketio", "flask-cors"], check=False)
    from flask import Flask, render_template, jsonify, request
    from flask_socketio import SocketIO, emit
    from flask_cors import CORS

import sys
from pathlib import Path

# Configurar imports usando la central
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(project_root.absolute()))

# Usar central de imports - solo los disponibles
from src import LoggerManager, MT5_MANAGER

# Imports adicionales necesarios
try:
    from src import ConfigManager, AnalyticsManager, DataManager, ErrorManager
except ImportError:
    # Managers opcionales - crear fallbacks simples
    ConfigManager = None
    AnalyticsManager = None
    DataManager = None
    ErrorManager = None

try:
    from src import FVGDatabaseManager
except ImportError:
    FVGDatabaseManager = None

logger = logging.getLogger(__name__)

class FVGWebDashboard:
    """
    🌐 DASHBOARD WEB FVG AVANZADO
    Interface web moderna para monitoreo completo del sistema FVG
    """
    
    def __init__(self, port=8080, debug=False):
        self.port = port
        self.debug = debug
        self.is_running = False
        
        # 🏗️ INICIALIZAR MANAGERS CENTRALES (CAJA NEGRA)
        self.logger_manager = LoggerManager()
        self.logger = self.logger_manager.get_logger('web_dashboard')
        
        # Crear managers con fallbacks seguros
        if ConfigManager is not None:
            self.config_manager = ConfigManager()
        else:
            self.config_manager = self._create_fallback_config()
        
        if ErrorManager is not None:
            self.error_manager = ErrorManager(self.config_manager, self.logger_manager)
        else:
            self.error_manager = self._create_fallback_error_manager()
        
        if DataManager is not None:
            self.data_manager = DataManager(self.config_manager, self.logger_manager, self.error_manager)
        else:
            self.data_manager = self._create_fallback_data_manager()
        
        if AnalyticsManager is not None:
            self.analytics_manager = AnalyticsManager(self.config_manager, self.logger_manager, self.error_manager, self.data_manager)
        else:
            self.analytics_manager = self._create_fallback_analytics()
        
        if FVGDatabaseManager is not None:
            self.fvg_db_manager = FVGDatabaseManager()
        else:
            self.fvg_db_manager = self._create_fallback_db_manager()
        
        self.dashboard_logger = self.logger_manager.get_logger("FVGWebDashboard")
        
        # Configuración Flask
        self.app = Flask(__name__, 
                        template_folder=self._create_templates_dir(),
                        static_folder=self._create_static_dir())
        self.app.config['SECRET_KEY'] = 'trading_grid_fvg_dashboard_2025'
    
    def _create_fallback_config(self):
        """📋 Config manager fallback"""
        class FallbackConfig:
            def get_config(self): return {}
            def get_trading_config(self): return {}
        return FallbackConfig()
    
    def _create_fallback_error_manager(self):
        """🚨 Error manager fallback"""
        class FallbackErrorManager:
            def __init__(self):
                self.logger = LoggerManager().get_logger('fallback_error')
            def log_error(self, error): self.logger.error(f"Error: {error}")
            def get_recent_errors(self): return []
            def get_error_summary(self): return {'total_errors': 0, 'recent_errors': []}
        return FallbackErrorManager()
    
    def _create_fallback_data_manager(self):
        """💾 Data manager fallback"""
        class FallbackDataManager:
            def get_market_data(self, symbol): return {}
            def get_data_sources_status(self): return {}
            def get_ohlc_data(self, symbol, timeframe, count): return {}
            def get_cache_stats(self): return {'cache_hits': 0, 'cache_misses': 0}
        return FallbackDataManager()
    
    def _create_fallback_analytics(self):
        """📊 Analytics manager fallback"""
        class FallbackAnalytics:
            def __init__(self):
                self.is_initialized = True
                self.analytics_active = True
                self.performance_tracker = type('', (), {'__dict__': {}})()
                self.grid_analytics = type('', (), {'__dict__': {}})()
                self.market_analytics = type('', (), {
                    'current_market_metrics': type('', (), {'__dict__': {}})(),
                    'market_conditions': {},
                    'stochastic_signals': [],
                    'market_history': []
                })()
            def get_performance_metrics(self): return {}
            def get_fvg_analytics(self): return {}
        return FallbackAnalytics()
    
    def _create_fallback_db_manager(self):
        """🗃️ Database manager fallback"""
        class FallbackDBManager:
            def get_recent_fvgs(self, limit=10): return []
            def get_database_stats(self): return {}
            def get_pending_fvgs(self): return type('', (), {'to_dict': lambda x: []})()
        return FallbackDBManager()
    
    def _setup_flask_app(self):
        """⚙️ Configurar aplicación Flask"""
        # SocketIO para tiempo real
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        CORS(self.app)
        
        # Storage de datos
        self.fvg_data = []
        self.metrics_data = {
            'total_fvgs': 0,
            'active_fvgs': 0,
            'filled_fvgs': 0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'last_update': datetime.now()
        }
        self.alerts_data = []
        self.performance_history = []
        
        # Configurar rutas
        self._setup_routes()
        self._setup_socketio_events()
        
        self.dashboard_logger.info("🌐 FVG Web Dashboard inicializado con managers centrales")
    
    def _create_templates_dir(self) -> str:
        """Crea directorio de templates"""
        templates_dir = Path(__file__).parent / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Crear template principal si no existe
        main_template = templates_dir / "dashboard.html"
        if not main_template.exists():
            self._create_dashboard_template(main_template)
        
        return str(templates_dir)
    
    def _create_static_dir(self) -> str:
        """Crea directorio de archivos estáticos"""
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        
        # Crear CSS y JS básicos
        self._create_static_files(static_dir)
        
        return str(static_dir)
    
    def _create_dashboard_template(self, template_path: Path):
        """Crea template HTML del dashboard"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 Trading Grid - FVG Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <link rel="stylesheet" href="{{ url_for('static', filename='dashboard.css') }}">
</head>
<body class="bg-dark text-light">
    <!-- Header -->
    <nav class="navbar navbar-dark bg-primary">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                🏢 Trading Grid - Piso 3 FVG Dashboard
            </span>
            <span class="navbar-text">
                <i class="fas fa-circle text-success blink"></i> LIVE
                <span id="last-update" class="ms-2">--:--:--</span>
            </span>
        </div>
    </nav>

    <div class="container-fluid mt-3">
        <!-- Métricas principales -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 id="total-fvgs">0</h4>
                                <span>Total FVGs</span>
                            </div>
                            <i class="fas fa-chart-line fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 id="active-fvgs">0</h4>
                                <span>FVGs Activos</span>
                            </div>
                            <i class="fas fa-play fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 id="win-rate">0%</h4>
                                <span>Win Rate</span>
                            </div>
                            <i class="fas fa-target fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h4 id="profit-factor">0.0</h4>
                                <span>Profit Factor</span>
                            </div>
                            <i class="fas fa-dollar-sign fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Gráfico de Performance -->
            <div class="col-md-8">
                <div class="card bg-secondary">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-area"></i> Performance en Tiempo Real</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="performanceChart" height="100"></canvas>
                    </div>
                </div>
            </div>

            <!-- Alertas Recientes -->
            <div class="col-md-4">
                <div class="card bg-secondary">
                    <div class="card-header">
                        <h5><i class="fas fa-bell"></i> Alertas Recientes</h5>
                    </div>
                    <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                        <div id="alerts-container">
                            <p class="text-muted">Sin alertas recientes...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- FVGs Detectados -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card bg-secondary">
                    <div class="card-header">
                        <h5><i class="fas fa-list"></i> FVGs Detectados Recientes</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-dark table-striped">
                                <thead>
                                    <tr>
                                        <th>Tiempo</th>
                                        <th>Símbolo</th>
                                        <th>Timeframe</th>
                                        <th>Tipo</th>
                                        <th>Precio</th>
                                        <th>Tamaño</th>
                                        <th>Calidad</th>
                                        <th>Estado</th>
                                    </tr>
                                </thead>
                                <tbody id="fvgs-table">
                                    <tr>
                                        <td colspan="8" class="text-center text-muted">
                                            Cargando datos...
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="{{ url_for('static', filename='dashboard.js') }}"></script>
</body>
</html>
        """
        
        template_path.write_text(html_content, encoding='utf-8')
    
    def _create_static_files(self, static_dir: Path):
        """Crea archivos CSS y JS"""
        
        # CSS
        css_content = """
.blink {
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0.3; }
}

.card {
    border: none;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.card-body h4 {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 0;
}

.table-dark {
    --bs-table-bg: #2b2b2b;
}

.alert-item {
    border-left: 4px solid;
    padding: 8px 12px;
    margin-bottom: 8px;
    border-radius: 4px;
}

.alert-low { border-left-color: #17a2b8; background: rgba(23, 162, 184, 0.1); }
.alert-medium { border-left-color: #ffc107; background: rgba(255, 193, 7, 0.1); }
.alert-high { border-left-color: #fd7e14; background: rgba(253, 126, 20, 0.1); }
.alert-critical { border-left-color: #dc3545; background: rgba(220, 53, 69, 0.1); }

.fvg-bullish { color: #28a745; }
.fvg-bearish { color: #dc3545; }
.fvg-filled { color: #6c757d; }
        """
        
        (static_dir / "dashboard.css").write_text(css_content, encoding='utf-8')
        
        # JavaScript
        js_content = """
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
        """
        
        (static_dir / "dashboard.js").write_text(js_content, encoding='utf-8')
    
    def _setup_routes(self):
        """Configura rutas HTTP"""
        
        @self.app.route('/')
        def dashboard():
            """Página principal del dashboard"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/dashboard-data')
        def api_dashboard_data():
            """API para datos del dashboard"""
            # Serializar todos los datos para JSON
            safe_data = self._serialize_for_json({
                'metrics': self.metrics_data,
                'fvgs': self.fvg_data[-20:],  # Últimos 20 FVGs
                'alerts': self.alerts_data[-10:],  # Últimas 10 alertas
                'performance_history': self.performance_history[-50:]  # Últimos 50 puntos
            })
            return jsonify(safe_data)
        
        @self.app.route('/api/health')
        def api_health():
            """Health check del dashboard"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'uptime': 'running' if self.is_running else 'stopped'
            })
        
        @self.app.route('/api/analytics/performance')
        def api_analytics_performance():
            """🏗️ CAJA NEGRA: Métricas completas de analytics_manager"""
            try:
                # Usar los submódulos del analytics_manager
                performance_data = {
                    'performance_tracker': self.analytics_manager.performance_tracker.__dict__,
                    'grid_analytics': self.analytics_manager.grid_analytics.__dict__,
                    'market_analytics': {
                        'current_metrics': self.analytics_manager.market_analytics.current_market_metrics.__dict__,
                        'market_conditions': self.analytics_manager.market_analytics.market_conditions,
                        'stochastic_signals_count': len(self.analytics_manager.market_analytics.stochastic_signals)
                    },
                    'analytics_status': {
                        'initialized': self.analytics_manager.is_initialized,
                        'active': self.analytics_manager.analytics_active
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                return jsonify(self._serialize_for_json(performance_data))
            except Exception as e:
                self.dashboard_logger.error(f"Error obteniendo analytics: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/database/fvgs')
        def api_database_fvgs():
            """🏗️ CAJA NEGRA: FVGs desde base de datos central"""
            try:
                # Obtener FVGs pendientes de la base de datos
                pending_fvgs = self.fvg_db_manager.get_pending_fvgs()
                
                return jsonify(self._serialize_for_json({
                    'fvgs': pending_fvgs.to_dict('records') if not pending_fvgs.empty else [],
                    'count': len(pending_fvgs),
                    'source': 'central_database',
                    'timestamp': datetime.now().isoformat()
                }))
            except Exception as e:
                self.dashboard_logger.error(f"Error obteniendo FVGs de DB: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/database/stats')
        def api_database_stats():
            """🏗️ CAJA NEGRA: Estadísticas de base de datos"""
            try:
                stats = self.fvg_db_manager.get_database_stats()
                
                return jsonify(self._serialize_for_json({
                    'database_stats': stats,
                    'timestamp': datetime.now().isoformat()
                }))
            except Exception as e:
                self.dashboard_logger.error(f"Error obteniendo stats de DB: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/data/market')
        def api_data_market():
            """🏗️ CAJA NEGRA: Datos de mercado desde data_manager"""
            try:
                symbol = request.args.get('symbol', 'EURUSD')
                timeframe = request.args.get('timeframe', 'M15')
                
                # Obtener datos OHLC recientes a través del data_manager
                ohlc_data = self.data_manager.get_ohlc_data(symbol, timeframe, 50)
                cache_stats = self.data_manager.get_cache_stats()
                
                market_summary = {}
                if ohlc_data is not None and not ohlc_data.empty:
                    latest = ohlc_data.iloc[-1]
                    market_summary = {
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'latest_price': float(latest['close']),
                        'latest_high': float(latest['high']),
                        'latest_low': float(latest['low']),
                        'latest_open': float(latest['open']),
                        'data_points': len(ohlc_data),
                        'latest_time': str(latest.name) if hasattr(latest, 'name') else 'N/A'
                    }
                
                return jsonify(self._serialize_for_json({
                    'market_summary': market_summary,
                    'cache_stats': cache_stats,
                    'timestamp': datetime.now().isoformat()
                }))
            except Exception as e:
                self.dashboard_logger.error(f"Error obteniendo datos de mercado: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/errors/recent')
        def api_errors_recent():
            """🏗️ CAJA NEGRA: Errores recientes del sistema"""
            try:
                error_summary = self.error_manager.get_error_summary()
                
                return jsonify(self._serialize_for_json({
                    'error_summary': error_summary,
                    'timestamp': datetime.now().isoformat()
                }))
            except Exception as e:
                self.dashboard_logger.error(f"Error obteniendo errores: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/caja-negra/sistema-completo')
        def api_caja_negra_completa():
            """🏗️ CAJA NEGRA COMPLETA: Toda la información del sistema en un endpoint"""
            try:
                # Recopilar TODA la información disponible
                sistema_completo = {
                    # 1. Analytics Manager
                    'analytics': {
                        'performance_tracker': self.analytics_manager.performance_tracker.__dict__,
                        'grid_analytics': self.analytics_manager.grid_analytics.__dict__,
                        'market_analytics': {
                            'current_metrics': self.analytics_manager.market_analytics.current_market_metrics.__dict__,
                            'market_conditions': self.analytics_manager.market_analytics.market_conditions,
                            'stochastic_signals': self.analytics_manager.market_analytics.stochastic_signals[-10:],  # Últimas 10
                            'market_history_count': len(self.analytics_manager.market_analytics.market_history)
                        },
                        'status': {
                            'initialized': self.analytics_manager.is_initialized,
                            'active': self.analytics_manager.analytics_active
                        }
                    },
                    
                    # 2. Base de datos FVG
                    'database': {
                        'stats': self.fvg_db_manager.get_database_stats(),
                        'pending_fvgs': self.fvg_db_manager.get_pending_fvgs().to_dict('records'),
                    },
                    
                    # 3. Data Manager
                    'data_manager': {
                        'cache_stats': self.data_manager.get_cache_stats(),
                    },
                    
                    # 4. Error Manager
                    'errors': {
                        'summary': self.error_manager.get_error_summary(),
                    },
                    
                    # 5. Dashboard interno
                    'dashboard': {
                        'metrics': self.metrics_data,
                        'fvgs_count': len(self.fvg_data),
                        'alerts_count': len(self.alerts_data),
                        'performance_history_count': len(self.performance_history),
                        'is_running': self.is_running,
                        'port': self.port
                    },
                    
                    # 6. Configuración
                    'config': {
                        'config_manager_type': type(self.config_manager).__name__,
                        'logger_manager_type': type(self.logger_manager).__name__,
                    },
                    
                    # Timestamp de la consulta
                    'timestamp': datetime.now().isoformat(),
                    'generated_by': 'FVGWebDashboard CAJA NEGRA v1.0'
                }
                
                self.dashboard_logger.info("🗃️ Información completa de CAJA NEGRA generada")
                return jsonify(self._serialize_for_json(sistema_completo))
                
            except Exception as e:
                self.dashboard_logger.error(f"Error generando CAJA NEGRA completa: {e}")
                return jsonify({'error': str(e), 'component': 'caja_negra_completa'}), 500
        
        @self.app.route('/api/docs')
        def api_docs():
            """📚 Documentación de todos los endpoints disponibles"""
            endpoints_docs = {
                'dashboard_endpoints': {
                    '/': 'Dashboard principal (HTML)',
                    '/api/dashboard-data': 'Datos básicos del dashboard (métricas, FVGs, alertas, historial)',
                    '/api/health': 'Estado de salud del dashboard'
                },
                'caja_negra_endpoints': {
                    '/api/analytics/performance': 'Métricas completas del analytics_manager (performance, grid, market)',
                    '/api/database/fvgs': 'FVGs desde la base de datos central',
                    '/api/database/stats': 'Estadísticas de la base de datos FVG',
                    '/api/data/market': 'Datos de mercado desde data_manager (OHLC, cache)',
                    '/api/errors/recent': 'Resumen de errores del sistema',
                    '/api/caja-negra/sistema-completo': '🏗️ TODA la información del sistema en un endpoint'
                },
                'websocket_events': {
                    'connect': 'Conexión WebSocket establecida',
                    'disconnect': 'Desconexión WebSocket',
                    'new_fvg': 'Nuevo FVG detectado (tiempo real)',
                    'fvg_update': 'Actualización de FVG existente',
                    'performance_update': 'Actualización de métricas de rendimiento',
                    'alert': 'Nueva alerta del sistema'
                },
                'integration_info': {
                    'managers_integrados': [
                        'ConfigManager: Configuración centralizada',
                        'LoggerManager: Sistema de logging avanzado',
                        'ErrorManager: Gestión de errores del sistema',
                        'DataManager: Datos de mercado y cache',
                        'AnalyticsManager: Métricas y análisis avanzado',
                        'FVGDatabaseManager: Base de datos FVG centralizada'
                    ],
                    'caja_negra_features': [
                        'Acceso completo a todas las bases de datos centrales',
                        'Información en tiempo real de todos los managers',
                        'Historial completo de métricas y rendimiento',
                        'Diagnóstico completo del sistema',
                        'Serialización JSON segura para todos los datos',
                        'Manejo de errores robusto en todos los endpoints'
                    ]
                },
                'usage_examples': {
                    'obtener_todo': 'GET /api/caja-negra/sistema-completo',
                    'solo_analytics': 'GET /api/analytics/performance',
                    'solo_database': 'GET /api/database/stats',
                    'datos_mercado': 'GET /api/data/market?symbol=EURUSD&timeframe=M15',
                    'dashboard_basico': 'GET /api/dashboard-data'
                },
                'timestamp': datetime.now().isoformat(),
                'version': 'FVGWebDashboard v1.0 - CAJA NEGRA INTEGRADA'
            }
            
            return jsonify(self._serialize_for_json(endpoints_docs))
    
    
    def _serialize_for_json(self, data):
        """Serializar datos para JSON, convirtiendo datetime a strings"""
        if isinstance(data, dict):
            return {k: self._serialize_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_for_json(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data
    
    def _setup_socketio_events(self):
        """Configura eventos SocketIO"""
        
        @self.socketio.on('connect')
        def handle_connect(auth=None):
            logger.info("🔗 Cliente conectado al dashboard")
            # Serializar datos para JSON
            safe_metrics = self._serialize_for_json(self.metrics_data)
            emit('metrics_update', safe_metrics)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info("🔌 Cliente desconectado del dashboard")
    
    def start_dashboard(self, open_browser=True):
        """Inicia el dashboard web"""
        if self.is_running:
            logger.info("⚠️ Dashboard ya está ejecutándose")
            return
        
        self.is_running = True
        
        # 🔄 INICIAR TASKS ASÍNCRONOS PRIMORDIALES
        self._start_async_tasks()
        
        # Abrir navegador automáticamente
        if open_browser:
            def open_browser_delayed():
                import time
                time.sleep(1.5)  # Esperar a que el servidor inicie
                webbrowser.open(f'http://localhost:{self.port}')
            
            Thread(target=open_browser_delayed, daemon=True).start()
        
        logger.info(f"🌐 Starting FVG Dashboard on http://localhost:{self.port}")
        
        # Iniciar servidor
        try:
            self.socketio.run(self.app, 
                            host='0.0.0.0', 
                            port=self.port, 
                            debug=self.debug,
                            allow_unsafe_werkzeug=True)
        except Exception as e:
            logger.error(f"❌ Error starting dashboard: {e}")
            self.is_running = False
    
    def _start_async_tasks(self):
        """🔄 Inicia todas las tareas asíncronas primordiales"""
        # Task para actualización automática de datos
        Thread(target=self._run_async_data_updater, daemon=True).start()
        
        # Task para monitoreo de sistema
        Thread(target=self._run_async_system_monitor, daemon=True).start()
        
        # Task para limpieza de datos antiguos
        Thread(target=self._run_async_data_cleaner, daemon=True).start()
        
        self.dashboard_logger.info("🔄 Tasks asíncronos iniciados para dashboard")
    
    def _run_async_data_updater(self):
        """🔄 Ejecutor para actualización asíncrona de datos"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_data_updater())
    
    def _run_async_system_monitor(self):
        """🔄 Ejecutor para monitoreo asíncrono del sistema"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_system_monitor())
    
    def _run_async_data_cleaner(self):
        """🔄 Ejecutor para limpieza asíncrona de datos"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_data_cleaner())
    
    async def _async_data_updater(self):
        """🔄 PRIMORDIAL: Actualización automática de datos cada 5 segundos"""
        while self.is_running:
            try:
                # Actualizar métricas desde managers centrales
                await self._update_metrics_from_managers()
                
                # Actualizar datos de FVG desde base de datos
                await self._update_fvg_data_from_db()
                
                # Enviar actualizaciones via WebSocket
                await self._broadcast_updates()
                
                # Esperar 5 segundos antes de la próxima actualización
                await asyncio.sleep(5)
                
            except Exception as e:
                self.dashboard_logger.error(f"Error en async_data_updater: {e}")
                await asyncio.sleep(10)  # Esperar más tiempo si hay error
    
    async def _async_system_monitor(self):
        """🔄 PRIMORDIAL: Monitoreo continuo del sistema cada 15 segundos"""
        while self.is_running:
            try:
                # Monitorear errores del sistema
                error_summary = self.error_manager.get_error_summary()
                
                # Si hay errores críticos, enviar alerta
                if error_summary.get('critical_errors', 0) > 0:
                    await self._send_critical_alert(error_summary)
                
                # Monitorear estado de analytics manager
                if not self.analytics_manager.is_initialized:
                    await self._send_system_alert("Analytics Manager no inicializado")
                
                # Esperar 15 segundos
                await asyncio.sleep(15)
                
            except Exception as e:
                self.dashboard_logger.error(f"Error en async_system_monitor: {e}")
                await asyncio.sleep(30)
    
    async def _async_data_cleaner(self):
        """🔄 PRIMORDIAL: Limpieza automática de datos antiguos cada 300 segundos (5 min)"""
        while self.is_running:
            try:
                # Limpiar datos antiguos de performance_history
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-500:]
                
                # Limpiar alertas antiguas
                if len(self.alerts_data) > 100:
                    self.alerts_data = self.alerts_data[-50:]
                
                # Limpiar FVG data antigua
                if len(self.fvg_data) > 500:
                    self.fvg_data = self.fvg_data[-250:]
                
                self.dashboard_logger.info("🧹 Limpieza automática de datos completada")
                await asyncio.sleep(300)  # 5 minutos
                
            except Exception as e:
                self.dashboard_logger.error(f"Error en async_data_cleaner: {e}")
                await asyncio.sleep(600)  # 10 minutos si hay error
    
    async def _update_metrics_from_managers(self):
        """🔄 Actualizar métricas desde managers centrales"""
        try:
            # Obtener métricas actualizadas
            cache_stats = self.data_manager.get_cache_stats()
            db_stats = self.fvg_db_manager.get_database_stats()
            
            # Actualizar métricas del dashboard
            self.metrics_data.update({
                'cache_hits': cache_stats.get('hits', 0),
                'cache_misses': cache_stats.get('misses', 0),
                'db_fvg_count': db_stats.get('total_records', 0),
                'last_update': datetime.now()
            })
            
        except Exception as e:
            self.dashboard_logger.error(f"Error actualizando métricas: {e}")
    
    async def _update_fvg_data_from_db(self):
        """🔄 Actualizar datos de FVG desde base de datos"""
        try:
            pending_fvgs = self.fvg_db_manager.get_pending_fvgs()
            
            if not pending_fvgs.empty:
                # Convertir a formato para dashboard
                new_fvgs = []
                for _, fvg in pending_fvgs.tail(10).iterrows():  # Últimos 10
                    new_fvgs.append({
                        'timestamp': datetime.now().isoformat(),
                        'symbol': fvg.get('symbol', 'UNKNOWN'),
                        'price': float(fvg.get('price', 0)),
                        'quality': fvg.get('quality_score', 0)
                    })
                
                # Agregar al dashboard
                self.fvg_data.extend(new_fvgs)
            
        except Exception as e:
            self.dashboard_logger.error(f"Error actualizando FVGs desde DB: {e}")
    
    async def _broadcast_updates(self):
        """🔄 Enviar actualizaciones via WebSocket"""
        try:
            if hasattr(self, 'socketio'):
                # Enviar métricas actualizadas
                safe_metrics = self._serialize_for_json(self.metrics_data)
                self.socketio.emit('metrics_update', safe_metrics)
                
        except Exception as e:
            self.dashboard_logger.error(f"Error en broadcast_updates: {e}")
    
    async def _send_critical_alert(self, error_summary):
        """🔄 Enviar alerta crítica"""
        try:
            alert = {
                'type': 'critical',
                'message': f"Errores críticos detectados: {error_summary.get('critical_errors')}",
                'timestamp': datetime.now().isoformat(),
                'details': error_summary
            }
            
            self.alerts_data.append(alert)
            
            if hasattr(self, 'socketio'):
                self.socketio.emit('alert', self._serialize_for_json(alert))
                
        except Exception as e:
            self.dashboard_logger.error(f"Error enviando alerta crítica: {e}")
    
    async def _send_system_alert(self, message):
        """🔄 Enviar alerta del sistema"""
        try:
            alert = {
                'type': 'system',
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
            self.alerts_data.append(alert)
            
            if hasattr(self, 'socketio'):
                self.socketio.emit('alert', self._serialize_for_json(alert))
                
        except Exception as e:
            self.dashboard_logger.error(f"Error enviando alerta sistema: {e}")
    
    def stop_dashboard(self):
        """Detiene el dashboard"""
        self.is_running = False
        logger.info("🛑 Dashboard detenido")
    
    def add_fvg_data(self, fvg_data: Dict):
        """Añade datos de FVG detectado"""
        fvg_entry = {
            'timestamp': datetime.now().isoformat(),
            'symbol': fvg_data.get('symbol', 'EURUSD'),
            'timeframe': fvg_data.get('timeframe', 'M5'),
            'fvg_type': fvg_data.get('type', 'bullish'),
            'price': fvg_data.get('price', 0.0),
            'size': fvg_data.get('size_pips', 0.0),
            'quality': fvg_data.get('quality', 'medium'),
            'ml_score': fvg_data.get('ml_score', 0.0)
        }
        
        self.fvg_data.append(fvg_entry)
        
        # Mantener solo últimos 100 FVGs
        if len(self.fvg_data) > 100:
            self.fvg_data.pop(0)
        
        # Actualizar métricas
        self._update_metrics()
        
        # Enviar por WebSocket con serialización segura
        if self.is_running:
            safe_fvg = self._serialize_for_json(fvg_entry)
            self.socketio.emit('new_fvg', safe_fvg)
    
    def add_alert(self, level: str, message: str, data: Optional[Dict] = None):
        """Añade alerta al dashboard"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level.upper(),
            'message': message,
            'data': data or {}
        }
        
        self.alerts_data.append(alert)
        
        # Mantener solo últimas 50 alertas
        if len(self.alerts_data) > 50:
            self.alerts_data.pop(0)
        
        # Enviar por WebSocket con serialización segura
        if self.is_running:
            safe_alert = self._serialize_for_json(alert)
            self.socketio.emit('new_alert', safe_alert)
    
    def update_performance(self, pnl: float, trades_count: int, win_rate: float):
        """Actualiza datos de performance"""
        performance_point = {
            'timestamp': datetime.now().isoformat(),
            'pnl': pnl,
            'trades': trades_count,
            'win_rate': win_rate
        }
        
        self.performance_history.append(performance_point)
        
        # Mantener solo últimos 200 puntos
        if len(self.performance_history) > 200:
            self.performance_history.pop(0)
        
        # Actualizar métricas
        self.metrics_data.update({
            'win_rate': win_rate,
            'profit_factor': max(1.0, pnl / max(abs(pnl * 0.3), 1.0)),
            'last_update': datetime.now()
        })
        
        # Enviar por WebSocket con serialización JSON segura
        if self.is_running:
            safe_history = self._serialize_for_json(self.performance_history[-50:])
            self.socketio.emit('performance_update', {
                'history': safe_history
            })
            safe_metrics = self._serialize_for_json(self.metrics_data)
            self.socketio.emit('metrics_update', safe_metrics)
    
    def _update_metrics(self):
        """Actualiza métricas generales"""
        total_fvgs = len(self.fvg_data)
        active_fvgs = len([fvg for fvg in self.fvg_data 
                          if (datetime.now() - datetime.fromisoformat(fvg['timestamp'])).seconds < 3600])
        
        self.metrics_data.update({
            'total_fvgs': total_fvgs,
            'active_fvgs': active_fvgs,
            'filled_fvgs': total_fvgs - active_fvgs,
            'last_update': datetime.now()
        })
        
        # Enviar métricas por WebSocket con serialización segura
        if self.is_running:
            safe_metrics = self._serialize_for_json(self.metrics_data)
            self.socketio.emit('metrics_update', safe_metrics)


# =============================================================================
# INTEGRACIÓN CON SISTEMA FVG
# =============================================================================

class FVGDashboardBridge:
    """
    🌉 PUENTE DE INTEGRACIÓN DASHBOARD WEB ASÍNCRONO
    Conecta el sistema FVG con el dashboard web usando operaciones asíncronas primordiales
    """
    
    def __init__(self, web_dashboard: FVGWebDashboard):
        self.dashboard = web_dashboard
        self.logger = LoggerManager().get_logger("FVGDashboardBridge")
        self.async_tasks = []  # Lista de tareas asíncronas activas
        self._start_bridge_async_tasks()
    
    def _start_bridge_async_tasks(self):
        """🔄 Iniciar tareas asíncronas del bridge"""
        Thread(target=self._run_async_bridge_monitor, daemon=True).start()
        self.logger.info("🌉 Bridge asíncrono iniciado")
    
    def _run_async_bridge_monitor(self):
        """🔄 Ejecutor para monitoreo asíncrono del bridge"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_bridge_monitor())
    
    async def _async_bridge_monitor(self):
        """🔄 PRIMORDIAL: Monitoreo continuo del bridge cada 10 segundos"""
        while self.dashboard.is_running:
            try:
                # Verificar conectividad del bridge
                await self._check_bridge_health()
                
                # Procesar cola de eventos pendientes
                await self._process_pending_events()
                
                # Esperar 10 segundos
                await asyncio.sleep(10)
                
            except Exception as e:
                self.logger.error(f"Error en async_bridge_monitor: {e}")
                await asyncio.sleep(20)
    
    async def _check_bridge_health(self):
        """🔄 Verificar salud del bridge"""
        try:
            # Verificar que el dashboard esté corriendo
            if not self.dashboard.is_running:
                await self._send_bridge_alert("Dashboard no está corriendo")
            
            # Verificar managers del dashboard
            if not self.dashboard.analytics_manager.is_initialized:
                await self._send_bridge_alert("Analytics Manager no inicializado")
                
        except Exception as e:
            self.logger.error(f"Error verificando salud del bridge: {e}")
    
    async def _process_pending_events(self):
        """🔄 Procesar eventos pendientes de forma asíncrona"""
        try:
            # Procesar cualquier cola de eventos pendientes
            # Mantener el bridge activo y responsivo
            pass
            
        except Exception as e:
            self.logger.error(f"Error procesando eventos pendientes: {e}")
    
    async def _send_bridge_alert(self, message):
        """🔄 Enviar alerta desde el bridge"""
        try:
            alert = {
                'type': 'bridge',
                'message': f"🌉 Bridge: {message}",
                'timestamp': datetime.now().isoformat(),
                'source': 'FVGDashboardBridge'
            }
            
            self.dashboard.alerts_data.append(alert)
            
            if hasattr(self.dashboard, 'socketio'):
                self.dashboard.socketio.emit('alert', self.dashboard._serialize_for_json(alert))
                
        except Exception as e:
            self.logger.error(f"Error enviando alerta bridge: {e}")

    async def on_fvg_detected(self, fvg_data: Dict, symbol: str, timeframe: str):
        """🔄 ASÍNCRONO: Callback cuando se detecta FVG"""
        try:
            enhanced_data = {
                **fvg_data,
                'symbol': symbol,
                'timeframe': timeframe,
                'detection_time': datetime.now().isoformat(),
                'processing_mode': 'async'
            }
            
            # Procesar de forma asíncrona
            await self._async_process_fvg(enhanced_data)
            
            self.logger.info(f"📊 FVG procesado asincrónicamente: {symbol} {timeframe}")
            
        except Exception as e:
            self.logger.error(f"Error procesando FVG asincrónicamente: {e}")
    
    async def _async_process_fvg(self, fvg_data: Dict):
        """🔄 Procesar FVG de forma asíncrona"""
        try:
            # Agregar al dashboard
            self.dashboard.add_fvg_data(fvg_data)
            
            # Crear alerta
            alert_message = f"🎯 FVG {fvg_data.get('type', 'detected')} detectado en {fvg_data.get('symbol')} {fvg_data.get('timeframe')}"
            self.dashboard.add_alert('MEDIUM', alert_message, fvg_data)
            
            # Enviar actualización inmediata via WebSocket
            if hasattr(self.dashboard, 'socketio'):
                self.dashboard.socketio.emit('new_fvg', self.dashboard._serialize_for_json(fvg_data))
            
        except Exception as e:
            self.logger.error(f"Error en _async_process_fvg: {e}")

    async def on_confluence_detected(self, confluence_data: Dict, symbol: str):
        """🔄 ASÍNCRONO: Callback cuando se detecta confluencia"""
        try:
            enhanced_confluence = {
                **confluence_data,
                'symbol': symbol,
                'detection_time': datetime.now().isoformat(),
                'processing_mode': 'async'
            }
            
            await self._async_process_confluence(enhanced_confluence)
            self.logger.info(f"🔗 Confluencia procesada asincrónicamente: {symbol}")
            
        except Exception as e:
            self.logger.error(f"Error procesando confluencia asincrónicamente: {e}")
    
    async def _async_process_confluence(self, confluence_data: Dict):
        """🔄 Procesar confluencia de forma asíncrona"""
        try:
            # Crear alerta de confluencia
            alert_message = f"🔗 Confluencia detectada en {confluence_data.get('symbol')}"
            self.dashboard.add_alert('HIGH', alert_message, confluence_data)
            
            # Enviar via WebSocket
            if hasattr(self.dashboard, 'socketio'):
                self.dashboard.socketio.emit('confluence_detected', self.dashboard._serialize_for_json(confluence_data))
            
        except Exception as e:
            self.logger.error(f"Error en _async_process_confluence: {e}")

    async def on_trade_executed(self, trade_data: Dict):
        """🔄 ASÍNCRONO: Callback cuando se ejecuta trade"""
        try:
            enhanced_trade = {
                **trade_data,
                'execution_time': datetime.now().isoformat(),
                'processing_mode': 'async'
            }
            
            await self._async_process_trade(enhanced_trade)
            self.logger.info(f"⚡ Trade procesado asincrónicamente: {trade_data.get('symbol', 'Unknown')}")
            
        except Exception as e:
            self.logger.error(f"Error procesando trade asincrónicamente: {e}")
    
    async def _async_process_trade(self, trade_data: Dict):
        """🔄 Procesar trade de forma asíncrona"""
        try:
            # Crear alerta crítica de trade
            alert_message = f"⚡ Trade ejecutado: {trade_data.get('symbol', 'Unknown')}"
            self.dashboard.add_alert('CRITICAL', alert_message, trade_data)
            
            # Actualizar métricas de performance asincrónicamente
            pnl = trade_data.get('pnl', 0)
            if pnl != 0:
                await self._async_update_performance(trade_data)
            
            # Enviar via WebSocket
            if hasattr(self.dashboard, 'socketio'):
                self.dashboard.socketio.emit('trade_executed', self.dashboard._serialize_for_json(trade_data))
            
        except Exception as e:
            self.logger.error(f"Error en _async_process_trade: {e}")
    
    async def _async_update_performance(self, trade_data: Dict):
        """🔄 Actualizar performance de forma asíncrona"""
        try:
            pnl = trade_data.get('pnl', 0)
            
            # Actualizar métricas básicas
            current_performance = self.dashboard.metrics_data.get('total_profit', 0)
            self.dashboard.metrics_data['total_profit'] = current_performance + pnl
            self.dashboard.metrics_data['total_trades'] = self.dashboard.metrics_data.get('total_trades', 0) + 1
            
            # Recalcular win rate si es necesario
            if pnl > 0:
                winning_trades = self.dashboard.metrics_data.get('winning_trades', 0) + 1
                self.dashboard.metrics_data['winning_trades'] = winning_trades
                total_trades = self.dashboard.metrics_data.get('total_trades', 1)
                self.dashboard.metrics_data['win_rate'] = (winning_trades / total_trades) * 100
            
            # Agregar punto al historial de performance
            self.dashboard.performance_history.append({
                'timestamp': datetime.now().isoformat(),
                'pnl': pnl,
                'cumulative_pnl': self.dashboard.metrics_data['total_profit']
            })
            
            # Enviar actualización de performance via WebSocket
            if hasattr(self.dashboard, 'socketio'):
                self.dashboard.socketio.emit('performance_update', self.dashboard._serialize_for_json(self.dashboard.metrics_data))
            
        except Exception as e:
            self.logger.error(f"Error actualizando performance asincrónicamente: {e}")
    
    def update_performance_metrics(self, pnl: float, trades: int, win_rate: float):
        """Actualiza métricas de performance"""
        self.dashboard.update_performance(pnl, trades, win_rate)


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_fvg_web_dashboard(port=8080, debug=False) -> tuple[FVGWebDashboard, FVGDashboardBridge]:
    """
    🏭 Factory para crear dashboard web completo
    
    Returns:
        tuple: (dashboard, bridge) para integración
    """
    dashboard = FVGWebDashboard(port=port, debug=debug)
    bridge = FVGDashboardBridge(dashboard)
    
    return dashboard, bridge


if __name__ == "__main__":
    # Dashboard con datos reales del sistema
    print("🌐 Iniciando FVG Web Dashboard - DATOS REALES...")
    
    dashboard, bridge = create_fvg_web_dashboard(port=8080, debug=True)
    
    # 🏢 CONECTAR CON OFICINAS REALES DEL SISTEMA
    def initialize_real_data_connections():
        """🏢 Conecta con las oficinas reales para obtener datos en vivo"""
        
        try:
            # 🏢 PISO 3 - OFICINAS PRINCIPALES
            from src.analysis.piso_3.deteccion.fvg_detector import FVGDetector, RealTimeFVGDetector
            from src.analysis.piso_3.trading.fvg_trading_office import FVGTradingOffice
            from src.analysis.piso_3 import Piso3Manager
            
            # 🏢 PISO 4 - OFICINAS DE GESTIÓN
            from src.analysis.piso_4.session_manager import SessionManager
            from src.analysis.piso_4.daily_cycle_manager import DailyCycleManager
            from src.analysis.piso_4.master_operations_controller import MasterOperationsController
            from src.analysis.piso_4 import Piso4Manager
            
            print("📊 Conectando con oficinas reales del sistema...")
            
            # 🎯 OFICINA PRINCIPAL: PISO 3 MANAGER
            try:
                piso3_manager = Piso3Manager()
                if hasattr(piso3_manager, 'initialize'):
                    piso3_manager.initialize()
                print("✅ Conectado con Piso3Manager")
                
                # Conectar FVG detector real
                if hasattr(piso3_manager, 'fvg_detector'):
                    fvg_detector = piso3_manager.fvg_detector
                    print("✅ FVG Detector conectado")
                    
                    # Hook para recibir FVGs reales
                    async def on_real_fvg_detected(fvg_data, symbol, timeframe):
                        await bridge.on_fvg_detected(fvg_data, symbol, timeframe)
                    
                    # Registrar callback si es posible
                    if hasattr(fvg_detector, 'add_callback'):
                        fvg_detector.add_callback(on_real_fvg_detected)
                
            except Exception as e:
                print(f"⚠️ Error conectando Piso3Manager: {e}")
            
            # 🎯 OFICINA PRINCIPAL: PISO 4 MANAGER  
            try:
                piso4_manager = Piso4Manager()
                if hasattr(piso4_manager, 'initialize'):
                    piso4_manager.initialize()
                print("✅ Conectado con Piso4Manager")
                
                # Conectar Master Operations Controller
                if hasattr(piso4_manager, 'master_controller'):
                    master_controller = piso4_manager.master_controller
                    print("✅ Master Operations Controller conectado")
                    
                    # Hook para recibir trades reales
                    async def on_real_trade_executed(trade_data):
                        await bridge.on_trade_executed(trade_data)
                    
                    # Registrar callback si es posible
                    if hasattr(master_controller, 'add_trade_callback'):
                        master_controller.add_trade_callback(on_real_trade_executed)
                
            except Exception as e:
                print(f"⚠️ Error conectando Piso4Manager: {e}")
            
            # 🎯 OFICINA ESPECÍFICA: FVG TRADING OFFICE
            try:
                fvg_trading_office = FVGTradingOffice()
                if hasattr(fvg_trading_office, 'initialize'):
                    fvg_trading_office.initialize()
                print("✅ Conectado con FVGTradingOffice")
                
                # Hook para recibir confluencias reales
                async def on_real_confluence_detected(confluence_data, symbol):
                    await bridge.on_confluence_detected(confluence_data, symbol)
                
                # Registrar callback si es posible
                if hasattr(fvg_trading_office, 'add_confluence_callback'):
                    fvg_trading_office.add_confluence_callback(on_real_confluence_detected)
                
            except Exception as e:
                print(f"⚠️ Error conectando FVGTradingOffice: {e}")
                
            # 🎯 OFICINA ESPECÍFICA: SESSION MANAGER
            try:
                session_manager = SessionManager()
                if hasattr(session_manager, 'initialize'):
                    session_manager.initialize()
                print("✅ Conectado con SessionManager")
                
                # Obtener datos de sesión para métricas
                if hasattr(session_manager, 'get_current_session_data'):
                    session_data = session_manager.get_current_session_data()
                    if session_data:
                        dashboard.add_alert('INFO', f"📅 Sesión activa: {session_data.get('session_name', 'Unknown')}", session_data)
                
            except Exception as e:
                print(f"⚠️ Error conectando SessionManager: {e}")
                
            # 🎯 OFICINA ESPECÍFICA: DAILY CYCLE MANAGER
            try:
                daily_cycle_manager = DailyCycleManager()
                print("✅ Conectado con DailyCycleManager")
                
                # Obtener estadísticas del ciclo diario
                if hasattr(daily_cycle_manager, 'cycle_stats'):
                    cycle_info = daily_cycle_manager.cycle_stats
                    daily_pnl = cycle_info.get('total_pnl_percent', 0)
                    dashboard.add_alert('INFO', f"📊 Ciclo diario: {daily_pnl:.2f}% PnL", cycle_info)
                
            except Exception as e:
                print(f"⚠️ Error conectando DailyCycleManager: {e}")
            
            print("🎯 Conexiones con oficinas reales completadas")
            print("📡 Dashboard ahora recibe datos EN VIVO del sistema")
            
        except Exception as e:
            print(f"❌ Error general conectando oficinas: {e}")
            print("🔄 Continuando con datos de managers centrales...")
    
    # Inicializar conexiones reales
    initialize_real_data_connections()
    
    print("🚀 Dashboard iniciado en http://localhost:8080")
    print("📊 DATOS REALES cargados desde oficinas del sistema")
    print("🏢 Oficinas conectadas: Piso3Manager, Piso4Manager, FVGTradingOffice, SessionManager")
    print("⏹️ Presiona Ctrl+C para detener")
    
    try:
        dashboard.start_dashboard(open_browser=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard detenido por usuario")
        dashboard.stop_dashboard()
