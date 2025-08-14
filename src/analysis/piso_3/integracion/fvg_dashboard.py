"""
🌐 FVG DASHBOARD WEB BÁSICO
Interface web para visualización y control del Piso 3
"""

import os
import json
import threading
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class FVGDashboard:
    """
    🌐 DASHBOARD WEB PARA SISTEMA FVG
    
    Proporciona interface web para:
    - Visualización de FVGs activos
    - Estadísticas en tiempo real
    - Control del sistema
    - Reportes de análisis
    """
    
    def __init__(self, port=8080):
        """
        Inicializa el dashboard web
        
        Args:
            port: Puerto para el servidor web
        """
        self.port = port
        self.server = None
        self.is_running = False
        self.data_cache = {}
        
        print(f"🌐 FVGDashboard inicializado en puerto {port}")
    
    def start_server(self, auto_open=True):
        """
        Inicia el servidor web del dashboard
        
        Args:
            auto_open: Abrir automáticamente en navegador
        """
        try:
            # Configurar handler con referencia al dashboard
            handler = lambda *args: DashboardHandler(self, *args)
            
            self.server = HTTPServer(('localhost', self.port), handler)
            self.is_running = True
            
            url = f"http://localhost:{self.port}"
            print(f"🚀 Dashboard iniciado en: {url}")
            
            if auto_open:
                threading.Timer(1.0, lambda: webbrowser.open(url)).start()
            
            # Iniciar en thread separado para no bloquear
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando dashboard: {e}")
            return False
    
    def stop_server(self):
        """Detiene el servidor web"""
        if self.server:
            self.server.shutdown()
            self.is_running = False
            print("🛑 Dashboard detenido")
    
    def update_data(self, data_type, data):
        """
        Actualiza datos del cache para el dashboard
        
        Args:
            data_type: Tipo de datos (fvgs, stats, signals, etc.)
            data: Datos a actualizar
        """
        self.data_cache[data_type] = {
            'data': data,
            'timestamp': datetime.now(),
            'count': len(data) if isinstance(data, list) else 1
        }
    
    def get_dashboard_data(self):
        """Obtiene todos los datos para el dashboard"""
        return {
            'system_status': self._get_system_status(),
            'fvg_summary': self._get_fvg_summary(),
            'recent_signals': self._get_recent_signals(),
            'performance_stats': self._get_performance_stats(),
            'cache_info': {k: {'count': v['count'], 'timestamp': v['timestamp'].isoformat()} 
                          for k, v in self.data_cache.items()}
        }
    
    def _get_system_status(self):
        """Obtiene estado del sistema"""
        return {
            'status': 'ONLINE' if self.is_running else 'OFFLINE',
            'uptime': datetime.now().isoformat(),
            'version': 'Piso 3 v1.0',
            'modules': {
                'analisis': 'ACTIVE',
                'ia': 'ACTIVE', 
                'trading': 'ACTIVE',
                'integracion': 'ACTIVE'
            }
        }
    
    def _get_fvg_summary(self):
        """Obtiene resumen de FVGs"""
        fvgs = self.data_cache.get('fvgs', {}).get('data', [])
        
        if not fvgs:
            return {
                'total': 0,
                'bullish': 0,
                'bearish': 0,
                'avg_quality': 0,
                'high_quality': 0
            }
        
        bullish = sum(1 for fvg in fvgs if getattr(fvg, 'type', '') == 'BULLISH')
        bearish = len(fvgs) - bullish
        
        # Calcular calidad promedio real
        quality_scores = [getattr(fvg, 'quality_score', 0) for fvg in fvgs if hasattr(fvg, 'quality_score')]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            'total': len(fvgs),
            'bullish': bullish,
            'bearish': bearish,
            'avg_quality': avg_quality,
            'high_quality': sum(1 for fvg in fvgs if getattr(fvg, 'quality_score', 0) > 7)
        }
    
    def _get_recent_signals(self):
        """Obtiene señales recientes"""
        signals = self.data_cache.get('signals', {}).get('data', [])
        
        # Retornar últimas 10 señales
        return signals[-10:] if signals else []
    
    def _get_performance_stats(self):
        """Obtiene estadísticas de rendimiento"""
        
        # Obtener estadísticas reales del sistema
        try:
            from src.analysis.piso_3 import piso3_manager
            
            if piso3_manager:
                # Obtener métricas reales del sistema
                recent_signals = self.data_cache.get('signals', {}).get('data', [])
                
                if recent_signals:
                    total_signals = len(recent_signals)
                    successful_signals = sum(1 for s in recent_signals if s.get('success', False))
                    accuracy = (successful_signals / total_signals * 100) if total_signals > 0 else 0
                    
                    return {
                        'accuracy': accuracy,
                        'profit_factor': self._calculate_profit_factor(recent_signals),
                        'total_trades': total_signals,
                        'winning_trades': successful_signals,
                        'avg_return': self._calculate_avg_return(recent_signals)
                    }
        
        except Exception:
            pass
        
        # Fallback si no hay datos
        return {
            'accuracy': 0,
            'profit_factor': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'avg_return': 0
        }
    
    def _calculate_profit_factor(self, signals):
        """Calcula factor de beneficio real"""
        profits = [s.get('profit', 0) for s in signals if s.get('profit', 0) > 0]
        losses = [abs(s.get('profit', 0)) for s in signals if s.get('profit', 0) < 0]
        
        total_profit = sum(profits)
        total_loss = sum(losses)
        
        return total_profit / total_loss if total_loss > 0 else 0
    
    def _calculate_avg_return(self, signals):
        """Calcula retorno promedio real"""
        returns = [s.get('return_pct', 0) for s in signals if 'return_pct' in s]
        return sum(returns) / len(returns) if returns else 0


class DashboardHandler(BaseHTTPRequestHandler):
    """Handler HTTP para el dashboard"""
    
    def __init__(self, dashboard, *args):
        self.dashboard = dashboard
        super().__init__(*args)
    
    def do_GET(self):
        """Maneja requests GET"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self._serve_main_page()
        elif path == '/api/data':
            self._serve_api_data()
        elif path == '/api/status':
            self._serve_system_status()
        elif path.startswith('/static/'):
            self._serve_static_file(path)
        else:
            self._serve_404()
    
    def _serve_main_page(self):
        """Sirve la página principal del dashboard"""
        html = self._generate_main_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def _serve_api_data(self):
        """Sirve datos JSON para el dashboard"""
        data = self.dashboard.get_dashboard_data()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode('utf-8'))
    
    def _serve_system_status(self):
        """Sirve estado del sistema"""
        status = self.dashboard._get_system_status()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status, default=str).encode('utf-8'))
    
    def _serve_static_file(self, path):
        """Sirve archivos estáticos (CSS, JS, etc.)"""
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Static files not implemented')
    
    def _serve_404(self):
        """Sirve página 404"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>404 - Page Not Found</h1>')
    
    def _generate_main_html(self):
        """Genera HTML principal del dashboard"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏢 Piso 3 - FVG Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.8; font-size: 1.1em; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { 
            background: rgba(255,255,255,0.1); 
            backdrop-filter: blur(10px);
            border-radius: 15px; 
            padding: 20px; 
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h3 { margin-bottom: 15px; color: #FFD700; }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; }
        .metric-value { font-weight: bold; color: #00FF7F; }
        .status-online { color: #00FF7F; }
        .status-offline { color: #FF6347; }
        .progress-bar { 
            width: 100%; 
            height: 10px; 
            background: rgba(255,255,255,0.2); 
            border-radius: 5px; 
            overflow: hidden;
            margin: 5px 0;
        }
        .progress-fill { height: 100%; background: #00FF7F; transition: width 0.3s; }
        .refresh-btn { 
            background: #FFD700; 
            color: #1e3c72; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer;
            font-weight: bold;
            margin: 10px 5px;
        }
        .refresh-btn:hover { background: #FFA500; }
        .timestamp { font-size: 0.8em; opacity: 0.7; margin-top: 10px; }
        .signal-item { 
            background: rgba(255,255,255,0.1); 
            padding: 10px; 
            margin: 5px 0; 
            border-radius: 5px; 
            border-left: 4px solid #FFD700;
        }
        .bullish { border-left-color: #00FF7F !important; }
        .bearish { border-left-color: #FF6347 !important; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 PISO 3 - FVG DASHBOARD</h1>
            <p>Sistema Avanzado de Análisis FVG • Trading Grid System</p>
            <div style="margin-top: 15px;">
                <button class="refresh-btn" onclick="refreshData()">🔄 Actualizar</button>
                <button class="refresh-btn" onclick="toggleAutoRefresh()">⏱️ Auto-refresh</button>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>🖥️ Estado del Sistema</h3>
                <div class="metric">
                    <span>Estado:</span>
                    <span id="system-status" class="status-online">ONLINE</span>
                </div>
                <div class="metric">
                    <span>Versión:</span>
                    <span class="metric-value">Piso 3 v1.0</span>
                </div>
                <div class="metric">
                    <span>Módulos Activos:</span>
                    <span class="metric-value" id="active-modules">4/4</span>
                </div>
                <div class="metric">
                    <span>Uptime:</span>
                    <span class="metric-value" id="uptime">--:--:--</span>
                </div>
            </div>

            <div class="card">
                <h3>📊 Resumen FVGs</h3>
                <div class="metric">
                    <span>Total FVGs:</span>
                    <span class="metric-value" id="total-fvgs">0</span>
                </div>
                <div class="metric">
                    <span>📈 Bullish:</span>
                    <span class="metric-value" id="bullish-fvgs">0</span>
                </div>
                <div class="metric">
                    <span>📉 Bearish:</span>
                    <span class="metric-value" id="bearish-fvgs">0</span>
                </div>
                <div class="metric">
                    <span>Calidad Promedio:</span>
                    <span class="metric-value" id="avg-quality">0.0</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="quality-progress" style="width: 0%"></div>
                </div>
            </div>

            <div class="card">
                <h3>⚡ Rendimiento</h3>
                <div class="metric">
                    <span>Precisión:</span>
                    <span class="metric-value" id="accuracy">0%</span>
                </div>
                <div class="metric">
                    <span>Factor Profit:</span>
                    <span class="metric-value" id="profit-factor">0.00</span>
                </div>
                <div class="metric">
                    <span>Total Trades:</span>
                    <span class="metric-value" id="total-trades">0</span>
                </div>
                <div class="metric">
                    <span>Trades Ganadores:</span>
                    <span class="metric-value" id="winning-trades">0</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="accuracy-progress" style="width: 0%"></div>
                </div>
            </div>

            <div class="card">
                <h3>🔔 Señales Recientes</h3>
                <div id="recent-signals">
                    <div class="signal-item">
                        <div>📡 Sistema iniciando...</div>
                        <div style="font-size: 0.8em; opacity: 0.7;">Cargando datos...</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="timestamp" id="last-update">
            Última actualización: --:--:--
        </div>
    </div>

    <script>
        let autoRefresh = false;
        let refreshInterval = null;

        async function refreshData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                updateDashboard(data);
                
                document.getElementById('last-update').textContent = 
                    `Última actualización: ${new Date().toLocaleTimeString()}`;
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }

        function updateDashboard(data) {
            // Sistema
            const systemStatus = data.system_status || {};
            document.getElementById('system-status').textContent = systemStatus.status || 'UNKNOWN';
            document.getElementById('system-status').className = 
                systemStatus.status === 'ONLINE' ? 'status-online' : 'status-offline';

            // FVGs
            const fvgSummary = data.fvg_summary || {};
            document.getElementById('total-fvgs').textContent = fvgSummary.total || 0;
            document.getElementById('bullish-fvgs').textContent = fvgSummary.bullish || 0;
            document.getElementById('bearish-fvgs').textContent = fvgSummary.bearish || 0;
            document.getElementById('avg-quality').textContent = (fvgSummary.avg_quality || 0).toFixed(1);
            
            const qualityPercent = ((fvgSummary.avg_quality || 0) / 10) * 100;
            document.getElementById('quality-progress').style.width = qualityPercent + '%';

            // Rendimiento
            const performance = data.performance_stats || {};
            document.getElementById('accuracy').textContent = (performance.accuracy || 0).toFixed(1) + '%';
            document.getElementById('profit-factor').textContent = (performance.profit_factor || 0).toFixed(2);
            document.getElementById('total-trades').textContent = performance.total_trades || 0;
            document.getElementById('winning-trades').textContent = performance.winning_trades || 0;
            
            const accuracyPercent = performance.accuracy || 0;
            document.getElementById('accuracy-progress').style.width = accuracyPercent + '%';

            // Señales recientes
            const signals = data.recent_signals || [];
            const signalsContainer = document.getElementById('recent-signals');
            
            if (signals.length === 0) {
                signalsContainer.innerHTML = '<div class="signal-item">📡 No hay señales recientes</div>';
            } else {
                signalsContainer.innerHTML = signals.slice(0, 5).map(signal => 
                    `<div class="signal-item ${signal.type ? signal.type.toLowerCase() : ''}">
                        <div>🎯 ${signal.symbol || 'UNKNOWN'} - ${signal.type || 'SIGNAL'}</div>
                        <div style="font-size: 0.8em; opacity: 0.7;">
                            Score: ${signal.score || 'N/A'} | ${signal.timestamp || 'Ahora'}
                        </div>
                    </div>`
                ).join('');
            }
        }

        function toggleAutoRefresh() {
            autoRefresh = !autoRefresh;
            const btn = event.target;
            
            if (autoRefresh) {
                btn.textContent = '⏹️ Detener';
                refreshInterval = setInterval(refreshData, 5000); // Cada 5 segundos
            } else {
                btn.textContent = '⏱️ Auto-refresh';
                if (refreshInterval) {
                    clearInterval(refreshInterval);
                    refreshInterval = null;
                }
            }
        }

        // Actualización inicial
        refreshData();
        
        // Actualizar cada 30 segundos por defecto
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
"""

    def log_message(self, format, *args):
        """Suprimir logs HTTP para limpiar salida"""
        pass


# Funciones de utilidad
def start_dashboard(port=8080, auto_open=True):
    """
    Función de conveniencia para iniciar el dashboard
    
    Args:
        port: Puerto del servidor
        auto_open: Abrir navegador automáticamente
        
    Returns:
        Instancia del dashboard
    """
    dashboard = FVGDashboard(port)
    
    if dashboard.start_server(auto_open):
        print(f"🌐 Dashboard disponible en: http://localhost:{port}")
        return dashboard
    else:
        print("❌ Error iniciando dashboard")
        return None

if __name__ == "__main__":
    # Ejecutar dashboard en modo producción
    print("🌐 FVG Dashboard - Modo Producción")
    print("="*50)
    
    dashboard = start_dashboard(port=8080, auto_open=True)
    
    if dashboard:
        try:
            print("🌐 Dashboard ejecutándose en modo producción")
            print("📡 Conectar con datos reales del sistema FVG")
            print("⏸️ Presiona Ctrl+C para detener")
            
            # Mantener dashboard ejecutándose
            while True:
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n⏸️ Deteniendo dashboard...")
            dashboard.stop_server()
            print("✅ Dashboard detenido")
