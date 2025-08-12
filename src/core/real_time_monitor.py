"""
RealTimeMonitor - PUERTA-S2-MONITOR
Real-time monitoring system for Grid Trading

Fecha: 2025-08-11
Versión: v1.0.0
Componente: SÓTANO 2 - Real-Time Optimization System
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time
from typing import Dict, List, Optional, Any

# Configurar paths igual que en test_sistema.py
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "core").absolute()))

# Imports de SÓTANO 1 (PUERTAS) - Importar solo los básicos primero
try:
    from .config_manager import ConfigManager
    from .logger_manager import LoggerManager
    from .error_manager import ErrorManager
    from .data_manager import DataManager
    
    # Importar analytics y mt5 condicionalmente
    analytics_available = True
    mt5_available = True
    
    try:
        from analytics_manager import AnalyticsManager
    except ImportError:
        analytics_available = False
        AnalyticsManager = None
    
    try:
        from mt5_manager import MT5Manager
    except ImportError:
        mt5_available = False
        MT5Manager = None
        
except ImportError as e:
    print(f"Error importando managers básicos SÓTANO 1: {e}")
    raise


class RealTimeMonitor:
    """
    Monitor en tiempo real para trades y métricas del sistema Grid.
    
    PUERTA-S2-MONITOR: Coordina con todas las puertas SÓTANO 1
    - PUERTA-S1-CONFIG: Configuración del sistema
    - PUERTA-S1-LOGGER: Logging de eventos
    - PUERTA-S1-ERROR: Manejo de errores
    - PUERTA-S1-DATA: Gestión de datos OHLC
    - PUERTA-S1-ANALYTICS: Métricas en tiempo real
    - PUERTA-S1-MT5: Datos de trading live
    """
    
    def __init__(self):
        """Inicializar RealTimeMonitor con todas las puertas SÓTANO 1"""
        # ID del componente para sistema de puertas
        self.component_id = "PUERTA-S2-MONITOR"
        self.version = "1.0.0"
        
        # 🚪 PUERTAS SÓTANO 1 (Dependencias)
        try:
            self.config = ConfigManager()
            self.logger = LoggerManager()
            self.error_manager = ErrorManager()
            self.data_manager = DataManager()
            
            # Managers que requieren dependencias - con fallback
            if analytics_available and AnalyticsManager:
                self.analytics = AnalyticsManager(
                    config_manager=self.config,
                    logger_manager=self.logger,
                    error_manager=self.error_manager,
                    data_manager=self.data_manager
                )
            else:
                self.analytics = None
                self.logger.log_warning(f"[{self.component_id}] AnalyticsManager no disponible")
            
            if mt5_available and MT5Manager:
                self.mt5 = MT5Manager(
                    config_manager=self.config,
                    logger_manager=self.logger,
                    error_manager=self.error_manager
                )
            else:
                self.mt5 = None
                self.logger.log_warning(f"[{self.component_id}] MT5Manager no disponible")
            
            self.logger.log_info(f"[{self.component_id}] Inicializando RealTimeMonitor v{self.version}")
            
        except Exception as e:
            print(f"ERROR: No se pudieron inicializar dependencias SÓTANO 1: {e}")
            raise
        
        # Estado interno del monitor
        self.monitoring_active = False
        self.monitoring_thread = None
        self.current_trades = {}
        self.metrics_buffer = []
        self.alert_thresholds = {}
        
        # Configuración del monitor
        self.update_interval = 5  # segundos entre actualizaciones
        self.max_buffer_size = 100
        
        # Cargar configuración específica
        self._load_monitor_config()
        
        self.logger.log_success(f"[{self.component_id}] RealTimeMonitor inicializado correctamente")
    
    def _load_monitor_config(self):
        """Cargar configuración específica del monitor desde ConfigManager"""
        try:
            # TEMPORAL: Usar configuración por defecto hasta que ConfigManager implemente get_optimization_config
            config_data = {
                "max_drawdown": 0.05,  # 5%
                "min_profit_factor": 1.2,
                "max_open_trades": 10,
                "max_daily_loss": 0.02,  # 2%
                "monitor_update_interval": 5
            }
            
            # Configuración de alertas por defecto
            self.alert_thresholds = {
                "max_drawdown": config_data.get("max_drawdown", 0.05),  # 5%
                "min_profit_factor": config_data.get("min_profit_factor", 1.2),
                "max_open_trades": config_data.get("max_open_trades", 10),
                "max_daily_loss": config_data.get("max_daily_loss", 0.02)  # 2%
            }
            
            # Intervalos de actualización
            self.update_interval = config_data.get("monitor_update_interval", 5)
            
            self.logger.log_info(f"[{self.component_id}] Configuración cargada: {self.alert_thresholds}")
            
        except Exception as e:
            self.error_manager.handle_system_error(self.component_id, e)
            # Usar valores por defecto en caso de error
            self.logger.log_warning(f"[{self.component_id}] Usando configuración por defecto")
    
    def start_monitoring(self) -> bool:
        """
        Iniciar monitoreo en tiempo real
        
        Returns:
            bool: True si el monitoreo se inició correctamente
        """
        try:
            if self.monitoring_active:
                self.logger.log_warning(f"[{self.component_id}] Monitoreo ya está activo")
                return False
            
            # Verificar conexión MT5 usando PUERTA-S1-MT5
            if self.mt5 and hasattr(self.mt5, 'is_connected'):
                if not self.mt5.is_connected():
                    self.logger.log_info(f"[{self.component_id}] Conectando a MT5...")
                    if not self.mt5.connect():
                        self.error_manager.handle_system_error(self.component_id, Exception("No se pudo conectar a MT5"))
                        return False
            else:
                self.logger.log_warning(f"[{self.component_id}] MT5Manager no disponible, continuando sin MT5")
            
            # Inicializar analytics usando PUERTA-S1-ANALYTICS
            if self.analytics and hasattr(self.analytics, 'initialize'):
                self.analytics.initialize()
            else:
                self.logger.log_warning(f"[{self.component_id}] AnalyticsManager no disponible, continuando sin analytics")
            
            # Iniciar thread de monitoreo
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            self.logger.log_success(f"[{self.component_id}] Monitoreo en tiempo real iniciado")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error(self.component_id, e)
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Detener monitoreo en tiempo real
        
        Returns:
            bool: True si el monitoreo se detuvo correctamente
        """
        try:
            if not self.monitoring_active:
                self.logger.log_warning(f"[{self.component_id}] Monitoreo no está activo")
                return False
            
            self.monitoring_active = False
            
            # Esperar a que termine el thread
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=10)
            
            self.logger.log_success(f"[{self.component_id}] Monitoreo detenido correctamente")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error(self.component_id, e)
            return False
    
    def _monitoring_loop(self):
        """Loop principal de monitoreo en tiempo real"""
        self.logger.log_info(f"[{self.component_id}] Iniciando loop de monitoreo")
        
        while self.monitoring_active:
            try:
                # Actualizar datos en tiempo real
                self._update_current_trades()
                self._update_live_metrics()
                self._check_alert_conditions()
                
                # Dormir hasta la siguiente actualización
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.error_manager.handle_system_error(self.component_id, e)
                # Continuar el loop a pesar del error
                time.sleep(self.update_interval)
        
        self.logger.log_info(f"[{self.component_id}] Loop de monitoreo terminado")
    
    def _update_current_trades(self):
        """Actualizar estado actual de trades usando PUERTA-S1-MT5"""
        try:
            # Obtener posiciones actuales usando MT5Manager si está disponible
            if self.mt5 and hasattr(self.mt5, 'get_positions'):
                positions = self.mt5.get_positions()
                current_price = self.mt5.get_current_price("EURUSD") if hasattr(self.mt5, 'get_current_price') else 1.0000
            else:
                # Datos mock si MT5 no está disponible
                positions = []
                current_price = 1.0000
            
            # Actualizar diccionario de trades
            trades_update = {
                "timestamp": datetime.now(),
                "active_positions": len(positions) if positions else 0,
                "current_price": current_price,
                "positions_data": positions if positions else []
            }
            
            self.current_trades = trades_update
            
            # Log cada 10 actualizaciones para no saturar
            if hasattr(self, '_update_counter'):
                self._update_counter += 1
            else:
                self._update_counter = 1
                
            if self._update_counter % 10 == 0:
                self.logger.log_info(f"[{self.component_id}] Trades actualizados: {trades_update['active_positions']} posiciones")
            
        except Exception as e:
            self.error_manager.handle_system_error(self.component_id, e)
    
    def _update_live_metrics(self):
        """Actualizar métricas en tiempo real usando PUERTA-S1-ANALYTICS"""
        try:
            # Obtener métricas actuales usando AnalyticsManager si está disponible
            if self.analytics and hasattr(self.analytics, 'get_performance_summary'):
                performance = self.analytics.get_performance_summary()
                grid_status = self.analytics.get_grid_summary() if hasattr(self.analytics, 'get_grid_summary') else {}
                market_status = self.analytics.get_market_summary() if hasattr(self.analytics, 'get_market_summary') else {}
            else:
                # Datos mock si analytics no está disponible
                performance = {"win_rate": 0.0, "profit_factor": 1.0, "current_drawdown": 0.0}
                grid_status = {"active_levels": 0}
                market_status = {"trend": "NEUTRAL"}
            
            live_metrics = {
                "timestamp": datetime.now(),
                "win_rate": performance.get("win_rate", 0),
                "profit_factor": performance.get("profit_factor", 0),
                "current_drawdown": performance.get("current_drawdown", 0),
                "active_trades": len(self.current_trades.get("positions_data", [])),
                "grid_levels_active": grid_status.get("active_levels", 0),
                "market_trend": market_status.get("trend", "NEUTRAL"),
                "component_source": self.component_id
            }
            
            # Agregar a buffer con límite de tamaño
            self.metrics_buffer.append(live_metrics)
            if len(self.metrics_buffer) > self.max_buffer_size:
                self.metrics_buffer.pop(0)  # Remover el más antiguo
            
        except Exception as e:
            self.error_manager.handle_system_error(self.component_id, e)
    
    def _check_alert_conditions(self):
        """Verificar condiciones de alerta basadas en métricas actuales"""
        try:
            if not self.metrics_buffer:
                return
            
            latest_metrics = self.metrics_buffer[-1]
            alerts = []
            
            # Verificar drawdown máximo
            current_drawdown = latest_metrics.get("current_drawdown", 0)
            if current_drawdown > self.alert_thresholds["max_drawdown"]:
                alerts.append(f"DRAWDOWN ALTO: {current_drawdown:.2%} > {self.alert_thresholds['max_drawdown']:.2%}")
            
            # Verificar profit factor mínimo
            profit_factor = latest_metrics.get("profit_factor", 0)
            if profit_factor < self.alert_thresholds["min_profit_factor"]:
                alerts.append(f"PROFIT FACTOR BAJO: {profit_factor:.2f} < {self.alert_thresholds['min_profit_factor']:.2f}")
            
            # Verificar número máximo de trades
            active_trades = latest_metrics.get("active_trades", 0)
            if active_trades > self.alert_thresholds["max_open_trades"]:
                alerts.append(f"DEMASIADOS TRADES: {active_trades} > {self.alert_thresholds['max_open_trades']}")
            
            # Log alertas si existen
            for alert in alerts:
                self.logger.log_warning(f"[{self.component_id}] ALERTA: {alert}")
            
        except Exception as e:
            self.error_manager.handle_system_error(self.component_id, e)
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Obtener estado actual completo del monitor
        
        Returns:
            Dict: Estado completo con trades, métricas y alertas
        """
        try:
            status = {
                "component_id": self.component_id,
                "version": self.version,
                "monitoring_active": self.monitoring_active,
                "last_update": datetime.now(),
                "current_trades": self.current_trades,
                "latest_metrics": self.metrics_buffer[-1] if self.metrics_buffer else None,
                "metrics_buffer_size": len(self.metrics_buffer),
                "alert_thresholds": self.alert_thresholds,
                "update_interval": self.update_interval
            }
            
            return status
            
        except Exception as e:
            self.error_manager.handle_system_error(self.component_id, e)
            return {"error": str(e)}
    
    def get_monitor_data_for_optimizer(self) -> Optional[Dict[str, Any]]:
        """
        Proporcionar datos específicos para PUERTA-S2-OPTIMIZER
        
        Returns:
            Dict: Datos formateados para el optimizador live
        """
        try:
            if not self.metrics_buffer:
                return None
            
            data_for_optimizer = {
                "current_metrics": self.metrics_buffer[-1],
                "trades_status": self.current_trades,
                "alert_conditions": self._get_current_alerts(),
                "component_id": self.component_id,
                "data_quality": "GOOD" if len(self.metrics_buffer) > 5 else "LIMITED",
                "timestamp": datetime.now()
            }
            
            return data_for_optimizer
            
        except Exception as e:
            self.error_manager.handle_system_error(self.component_id, e)
            return None
    
    def _get_current_alerts(self) -> List[str]:
        """Obtener lista de alertas actuales activas"""
        # Esta función será expandida en el futuro
        # Por ahora retorna lista vacía
        return []
    
    def cleanup(self):
        """Limpieza de recursos antes de cerrar"""
        try:
            self.logger.log_info(f"[{self.component_id}] Iniciando limpieza...")
            
            # Detener monitoreo
            self.stop_monitoring()
            
            # Limpiar buffers
            self.metrics_buffer.clear()
            self.current_trades.clear()
            
            self.logger.log_success(f"[{self.component_id}] Limpieza completada")
            
        except Exception as e:
            self.error_manager.handle_system_error(self.component_id, e)


# Función de utilidad para testing
def test_real_time_monitor():
    """Test básico del RealTimeMonitor"""
    try:
        print("🧪 Testing RealTimeMonitor...")
        
        # Inicializar monitor
        monitor = RealTimeMonitor()
        print(f"✅ Monitor inicializado: {monitor.component_id}")
        
        # Verificar estado inicial
        status = monitor.get_current_status()
        print(f"✅ Estado inicial obtenido: monitoring_active={status['monitoring_active']}")
        
        # Test cleanup
        monitor.cleanup()
        print("✅ Cleanup completado")
        
        print("🎉 RealTimeMonitor test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ RealTimeMonitor test FAILED: {e}")
        return False


if __name__ == "__main__":
    # Ejecutar test si se llama directamente
    test_real_time_monitor()
