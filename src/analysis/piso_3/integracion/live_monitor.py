"""
📡 LIVE MONITOR FVG
Monitor en tiempo real para sistema FVG del Piso 3
"""

import time
import threading
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

class LiveMonitor:
    """
    📡 MONITOR EN TIEMPO REAL FVG
    
    Monitorea continuamente:
    - Detección de nuevos FVGs
    - Estado del sistema
    - Rendimiento en tiempo real
    - Alertas y notificaciones
    """
    
    def __init__(self, config=None):
        """
        Inicializa el monitor en tiempo real
        
        Args:
            config: Configuración del monitor
        """
        self.config = config or {
            "monitor_interval": 5,  # segundos
            "alert_threshold": 7.0,  # score mínimo para alerta
            "max_alerts_per_hour": 10,
            "log_performance": True,
            "auto_restart": True
        }
        
        self.is_running = False
        self.monitor_thread = None
        self.stats = {
            'start_time': None,
            'fvgs_detected': 0,
            'alerts_sent': 0,
            'uptime': 0,
            'last_detection': None,
            'system_errors': 0
        }
        
        self.alerts_history = []
        self.performance_metrics = []
        self.callbacks = {
            'on_fvg_detected': [],
            'on_alert': [],
            'on_error': [],
            'on_status_change': []
        }
        
        self.logger = logging.getLogger(__name__)
        print("📡 LiveMonitor inicializado")
    
    def start_monitoring(self):
        """Inicia el monitoreo en tiempo real"""
        
        if self.is_running:
            print("⚠️ Monitor ya está ejecutándose")
            return False
        
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        
        # Iniciar thread de monitoreo
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("🚀 Monitor en tiempo real iniciado")
        self._trigger_callback('on_status_change', {'status': 'STARTED'})
        
        return True
    
    def stop_monitoring(self):
        """Detiene el monitoreo en tiempo real"""
        
        if not self.is_running:
            print("⚠️ Monitor no está ejecutándose")
            return False
        
        self.is_running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        print("🛑 Monitor en tiempo real detenido")
        self._trigger_callback('on_status_change', {'status': 'STOPPED'})
        
        return True
    
    def register_callback(self, event_type, callback_func):
        """
        Registra callback para eventos del monitor
        
        Args:
            event_type: Tipo de evento (on_fvg_detected, on_alert, etc.)
            callback_func: Función a ejecutar
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback_func)
            print(f"✅ Callback registrado para: {event_type}")
        else:
            print(f"❌ Tipo de evento no válido: {event_type}")
    
    def get_live_status(self):
        """Obtiene estado actual del monitor"""
        
        current_time = datetime.now()
        uptime = 0
        
        if self.stats['start_time']:
            uptime = (current_time - self.stats['start_time']).total_seconds()
        
        return {
            'is_running': self.is_running,
            'uptime_seconds': uptime,
            'uptime_formatted': self._format_uptime(uptime),
            'stats': self.stats.copy(),
            'recent_alerts': self.alerts_history[-5:],
            'performance': self._get_performance_summary(),
            'system_health': self._assess_system_health(),
            'timestamp': current_time.isoformat()
        }
    
    def get_performance_report(self):
        """Genera reporte de rendimiento"""
        
        if not self.performance_metrics:
            return {'message': 'No hay datos de rendimiento disponibles'}
        
        recent_metrics = self.performance_metrics[-100:]  # Últimas 100 mediciones
        
        detection_times = [m['detection_time'] for m in recent_metrics if 'detection_time' in m]
        cpu_usage = [m['cpu_usage'] for m in recent_metrics if 'cpu_usage' in m]
        memory_usage = [m['memory_usage'] for m in recent_metrics if 'memory_usage' in m]
        
        return {
            'avg_detection_time': sum(detection_times) / len(detection_times) if detection_times else 0,
            'max_detection_time': max(detection_times) if detection_times else 0,
            'avg_cpu_usage': sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
            'avg_memory_usage': sum(memory_usage) / len(memory_usage) if memory_usage else 0,
            'total_samples': len(recent_metrics),
            'report_time': datetime.now().isoformat()
        }
    
    def _monitor_loop(self):
        """Loop principal del monitor"""
        
        print("🔄 Loop de monitoreo iniciado")
        
        while self.is_running:
            try:
                start_time = time.time()
                
                # Verificar nuevos FVGs
                self._check_for_new_fvgs()
                
                # Verificar estado del sistema
                self._check_system_health()
                
                # Registrar métricas de rendimiento
                if self.config['log_performance']:
                    self._log_performance_metrics(time.time() - start_time)
                
                # Actualizar estadísticas
                self._update_stats()
                
                # Esperar intervalo configurado
                time.sleep(self.config['monitor_interval'])
                
            except Exception as e:
                self.stats['system_errors'] += 1
                self.logger.error(f"Error en monitor loop: {e}")
                self._trigger_callback('on_error', {'error': str(e), 'timestamp': datetime.now()})
                
                if not self.config['auto_restart']:
                    break
                
                # Esperar antes de reintentar
                time.sleep(5)
        
        print("🔄 Loop de monitoreo finalizado")
    
    def _check_for_new_fvgs(self):
        """Verifica si hay nuevos FVGs detectados"""
        
        try:
            # Integración real con detector FVG
            from src.analysis.fvg_detector import FVGDetector
            from src.core.data_manager import DataManager
            
            # Obtener datos recientes del mercado
            data_manager = DataManager()
            recent_data = data_manager.get_recent_market_data(
                symbol='EURUSD',  # Configurar según necesidades
                timeframe='M15',
                bars=100
            )
            
            if recent_data is not None and len(recent_data) > 0:
                # Ejecutar detección FVG
                detector = FVGDetector()
                new_fvgs = detector.detect_fvgs(recent_data)
                
                # Procesar FVGs detectados
                for fvg in new_fvgs:
                    if self._is_new_fvg(fvg):
                        self._process_new_fvg(fvg)
                        
        except Exception as e:
            self.logger.error(f"Error verificando FVGs: {e}")
    
    def _is_new_fvg(self, fvg):
        """Verifica si es un FVG nuevo (no procesado antes)"""
        
        # Verificar si este FVG ya fue procesado
        fvg_id = getattr(fvg, 'id', None) or f"FVG_{fvg.get('timestamp', time.time())}"
        
        # Mantener lista de FVGs procesados (último 1000)
        if not hasattr(self, '_processed_fvgs'):
            self._processed_fvgs = set()
        
        if fvg_id in self._processed_fvgs:
            return False
        
        self._processed_fvgs.add(fvg_id)
        
        # Limpiar lista si es muy grande
        if len(self._processed_fvgs) > 1000:
            old_fvgs = list(self._processed_fvgs)[:500]
            self._processed_fvgs = set(old_fvgs)
        
        return True
    
    def _process_new_fvg(self, fvg):
        """Procesa un nuevo FVG detectado"""
        
        self.stats['fvgs_detected'] += 1
        self.stats['last_detection'] = datetime.now()
        
        print(f"🎯 Nuevo FVG detectado: {fvg['type']} {fvg['symbol']} (Score: {fvg['quality_score']:.1f})")
        
        # Trigger callback
        self._trigger_callback('on_fvg_detected', fvg)
        
        # Verificar si requiere alerta
        if fvg['quality_score'] >= self.config['alert_threshold']:
            self._send_alert(fvg)
    
    def _send_alert(self, fvg):
        """Envía alerta por FVG de alta calidad"""
        
        # Verificar límite de alertas por hora
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_alerts = [a for a in self.alerts_history if a['timestamp'] > hour_ago]
        
        if len(recent_alerts) >= self.config['max_alerts_per_hour']:
            print(f"⚠️ Límite de alertas por hora alcanzado ({self.config['max_alerts_per_hour']})")
            return
        
        alert = {
            'id': f"ALERT_{int(time.time())}",
            'fvg': fvg,
            'timestamp': datetime.now(),
            'priority': 'HIGH' if fvg['quality_score'] >= 8.0 else 'MEDIUM',
            'message': f"🚨 FVG {fvg['type']} de alta calidad detectado en {fvg['symbol']}"
        }
        
        self.alerts_history.append(alert)
        self.stats['alerts_sent'] += 1
        
        print(f"🚨 ALERTA: {alert['message']} (Score: {fvg['quality_score']:.1f})")
        
        # Trigger callback
        self._trigger_callback('on_alert', alert)
    
    def _check_system_health(self):
        """Verifica salud del sistema"""
        
        try:
            # Verificar uso de CPU y memoria (simulado)
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            # Alertas de salud del sistema
            if cpu_percent > 90:
                print(f"⚠️ Alto uso de CPU: {cpu_percent}%")
            
            if memory_percent > 85:
                print(f"⚠️ Alto uso de memoria: {memory_percent}%")
                
        except ImportError:
            # psutil no disponible, usar métricas básicas
            pass
        except Exception as e:
            self.logger.error(f"Error verificando salud del sistema: {e}")
    
    def _log_performance_metrics(self, cycle_time):
        """Registra métricas de rendimiento"""
        
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
        except:
            cpu_percent = 0
            memory_percent = 0
        
        metric = {
            'timestamp': datetime.now(),
            'cycle_time': cycle_time,
            'detection_time': cycle_time,  # Tiempo del ciclo de detección
            'cpu_usage': cpu_percent,
            'memory_usage': memory_percent,
            'fvgs_count': self.stats['fvgs_detected'],
            'alerts_count': self.stats['alerts_sent']
        }
        
        self.performance_metrics.append(metric)
        
        # Mantener solo últimas 1000 métricas para evitar uso excesivo de memoria
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-1000:]
    
    def _update_stats(self):
        """Actualiza estadísticas generales"""
        
        if self.stats['start_time']:
            self.stats['uptime'] = (datetime.now() - self.stats['start_time']).total_seconds()
    
    def _trigger_callback(self, event_type, data):
        """Ejecuta callbacks registrados para un evento"""
        
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Error en callback {event_type}: {e}")
    
    def _format_uptime(self, seconds):
        """Formatea tiempo de funcionamiento"""
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _get_performance_summary(self):
        """Obtiene resumen de rendimiento"""
        
        if not self.performance_metrics:
            return {'avg_cycle_time': 0, 'total_cycles': 0}
        
        recent = self.performance_metrics[-20:]  # Últimos 20 ciclos
        avg_cycle_time = sum(m['cycle_time'] for m in recent) / len(recent)
        
        return {
            'avg_cycle_time': avg_cycle_time,
            'total_cycles': len(self.performance_metrics),
            'last_cycle_time': recent[-1]['cycle_time'] if recent else 0
        }
    
    def _assess_system_health(self):
        """Evalúa salud general del sistema"""
        
        health_score = 100
        issues = []
        
        # Verificar errores recientes
        if self.stats['system_errors'] > 5:
            health_score -= 20
            issues.append(f"Múltiples errores del sistema ({self.stats['system_errors']})")
        
        # Verificar tiempo desde última detección
        if self.stats['last_detection']:
            time_since_detection = (datetime.now() - self.stats['last_detection']).total_seconds()
            if time_since_detection > 300:  # 5 minutos
                health_score -= 15
                issues.append("No hay detecciones recientes")
        
        # Verificar rendimiento
        if self.performance_metrics:
            recent_avg = sum(m['cycle_time'] for m in self.performance_metrics[-10:]) / min(10, len(self.performance_metrics))
            if recent_avg > 2.0:  # Ciclos muy lentos
                health_score -= 10
                issues.append("Rendimiento degradado")
        
        if health_score >= 90:
            status = "EXCELENTE"
        elif health_score >= 70:
            status = "BUENO"
        elif health_score >= 50:
            status = "REGULAR"
        else:
            status = "CRÍTICO"
        
        return {
            'score': health_score,
            'status': status,
            'issues': issues
        }


if __name__ == "__main__":
    # Ejecutar monitor en producción
    print("📡 LIVE MONITOR - MODO PRODUCCIÓN")
    print("="*50)
    
    monitor = LiveMonitor({
        "monitor_interval": 30,  # 30 segundos en producción
        "alert_threshold": 7.0,
        "max_alerts_per_hour": 20,
        "log_performance": True,
        "auto_restart": True
    })
    
    monitor.start_monitoring()
    
    try:
        print("🔄 Monitor ejecutándose en modo producción...")
        print("⏸️ Presiona Ctrl+C para detener")
        
        while True:
            time.sleep(60)  # Status cada minuto
            status = monitor.get_live_status()
            if status['stats']['fvgs_detected'] > 0:
                print(f"📊 FVGs detectados: {status['stats']['fvgs_detected']}, "
                      f"Alertas: {status['stats']['alerts_sent']}")
                
    except KeyboardInterrupt:
        print("\n⏸️ Deteniendo monitor...")
        monitor.stop_monitoring()
        print("✅ Monitor detenido correctamente")
