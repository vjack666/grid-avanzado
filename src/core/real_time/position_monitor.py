"""
PositionMonitor - PUERTA-S2-POSITIONS
Monitoreo de posiciones y órdenes MT5 en tiempo real para SÓTANO 2

Funcionalidades:
- Monitoreo continuo de posiciones abiertas
- Detección de cambios en tiempo real
- Cálculo de P&L dinámico
- Detectar niveles críticos
- Alertas de riesgo automáticas

Fecha: 2025-08-11
Versión: v2.1.0
Componente: SÓTANO 2 - Real-Time Optimization
"""

import sys
from pathlib import Path
from datetime import datetime
import threading
import time
from typing import Dict, List, Optional, Any, Callable
import MetaTrader5 as mt5

# Configurar paths para imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "core").absolute()))

try:
    from config_manager import ConfigManager
    from logger_manager import LoggerManager
    from error_manager import ErrorManager
    from mt5_manager import MT5Manager
    from data_manager import DataManager
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    sys.exit(1)


class PositionMonitor:
    """
    Monitor de posiciones MT5 en tiempo real
    
    Gestiona:
    - Monitoreo continuo de posiciones
    - Detección de cambios en tiempo real
    - Cálculo de P&L dinámico
    - Alertas de niveles críticos
    """
    
    def __init__(self, config: ConfigManager, logger: LoggerManager, 
                 error: ErrorManager, mt5: MT5Manager, data: DataManager):
        """
        Inicializar PositionMonitor
        
        Args:
            config: ConfigManager para configuración
            logger: LoggerManager para logging
            error: ErrorManager para manejo de errores
            mt5: MT5Manager para conexión MT5
            data: DataManager para datos de mercado
        """
        self.component_id = "PUERTA-S2-POSITIONS"
        self.version = "v2.1.0"
        
        # Dependencias SÓTANO 1
        self.config = config
        self.logger = logger
        self.error = error
        self.mt5 = mt5
        self.data = data
        
        # Estado del monitoreo
        self.is_monitoring = False
        self.is_connected = False
        self._stop_event = threading.Event()
        self._monitor_thread = None
        
        # Estado de posiciones
        self.current_positions = {}
        self.position_history = []
        self.last_pnl = 0.0
        self.last_update = None
        
        # Configuración de monitoreo
        self._load_monitor_config()
        
        # Alertas y thresholds
        self.alert_callbacks = []
        self.risk_thresholds = {
            "max_drawdown": 0.05,      # 5%
            "max_daily_loss": 0.02,    # 2%
            "max_position_size": 100,   # 100 lotes
            "margin_level_min": 200    # 200%
        }
        
        # Métricas de rendimiento
        self.metrics = {
            "total_positions_tracked": 0,
            "position_changes_detected": 0,
            "alerts_triggered": 0,
            "max_pnl_today": 0.0,
            "min_pnl_today": 0.0,
            "last_update": None,
            "monitoring_uptime": 0.0
        }
        
        self.logger.log_info(f"[{self.component_id}] Inicializando PositionMonitor {self.version}")
        
    def _load_monitor_config(self):
        """Cargar configuración del monitor de posiciones"""
        try:
            # Configuración por defecto para monitoreo de posiciones
            self.monitor_config = {
                "update_interval": 1.0,        # 1 segundo
                "track_history": True,         # Guardar histórico
                "calculate_pnl": True,         # Calcular P&L
                "enable_alerts": True,         # Habilitar alertas
                "max_history_items": 1000,     # Máximo histórico
                "symbols_to_track": ["EURUSD", "GBPUSD", "USDJPY"],
                "alert_on_change": True        # Alertar en cambios
            }
            
            self.logger.log_info(f"[{self.component_id}] Configuración cargada: {len(self.monitor_config['symbols_to_track'])} símbolos")
            
        except Exception as e:
            self.error.handle_system_error(f"{self.component_id}: Error cargando configuración", e)
            # Configuración mínima de emergencia
            self.monitor_config = {
                "update_interval": 5.0,
                "track_history": False,
                "symbols_to_track": ["EURUSD"]
            }
            
    def start_monitoring(self, symbols: Optional[List[str]] = None) -> bool:
        """
        Iniciar monitoreo de posiciones
        
        Args:
            symbols: Lista de símbolos a monitorear (opcional)
            
        Returns:
            bool: True si el monitoreo se inició correctamente
        """
        try:
            if self.is_monitoring:
                self.logger.log_warning(f"[{self.component_id}] Monitoreo ya está activo")
                return True
                
            # Usar símbolos proporcionados o configuración por defecto
            if symbols:
                self.monitor_config["symbols_to_track"] = symbols
                
            # Verificar conexión MT5
            if not self._verify_mt5_connection():
                return False
                
            # Obtener estado inicial de posiciones
            self._snapshot_current_positions()
            
            # Iniciar thread de monitoreo
            self._stop_event.clear()
            self._monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                name=f"{self.component_id}-Monitor",
                daemon=True
            )
            self._monitor_thread.start()
            
            self.is_monitoring = True
            self.logger.log_success(f"[{self.component_id}] Monitoreo iniciado para {len(self.monitor_config['symbols_to_track'])} símbolos")
            return True
            
        except Exception as e:
            self.error.handle_system_error(f"{self.component_id}: Error iniciando monitoreo", e)
            return False
            
    def stop_monitoring(self) -> bool:
        """
        Detener monitoreo de posiciones
        
        Returns:
            bool: True si se detuvo correctamente
        """
        try:
            if not self.is_monitoring:
                self.logger.log_warning(f"[{self.component_id}] Monitoreo no está activo")
                return True
                
            # Señal de parada
            self._stop_event.set()
            
            # Esperar que termine el thread
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=5.0)
                
            self.is_monitoring = False
            self.logger.log_success(f"[{self.component_id}] Monitoreo detenido")
            return True
            
        except Exception as e:
            self.error.handle_system_error(f"{self.component_id}: Error deteniendo monitoreo", e)
            return False
            
    def _verify_mt5_connection(self) -> bool:
        """Verificar conexión con MT5"""
        try:
            # Usar MT5Manager para verificar conexión
            if hasattr(self.mt5, 'is_connected') and callable(self.mt5.is_connected):
                self.is_connected = self.mt5.is_connected()
            else:
                # Fallback: verificar directamente con MT5
                self.is_connected = mt5.terminal_info() is not None
                
            if not self.is_connected:
                self.logger.log_error(f"[{self.component_id}] MT5 no está conectado")
                
            return self.is_connected
            
        except Exception as e:
            self.error.handle_system_error(f"{self.component_id}: Error verificando conexión MT5", e)
            return False
            
    def _snapshot_current_positions(self):
        """Tomar snapshot del estado actual de posiciones"""
        try:
            positions = mt5.positions_get()
            
            if positions is None:
                self.current_positions = {}
                return
                
            # Convertir a diccionario para fácil comparación
            position_dict = {}
            total_pnl = 0.0
            
            for pos in positions:
                position_dict[pos.ticket] = {
                    "symbol": pos.symbol,
                    "type": pos.type,
                    "volume": pos.volume,
                    "price_open": pos.price_open,
                    "price_current": pos.price_current,
                    "profit": pos.profit,
                    "commission": pos.commission,
                    "swap": pos.swap,
                    "time_create": pos.time,
                    "comment": pos.comment
                }
                total_pnl += pos.profit
                
            self.current_positions = position_dict
            self.last_pnl = total_pnl
            self.last_update = datetime.now()
            
            self.logger.log_info(f"[{self.component_id}] Snapshot: {len(position_dict)} posiciones, P&L: {total_pnl:.2f}")
            
        except Exception as e:
            self.error.handle_data_error(f"{self.component_id}_snapshot", e)
            
    def _monitoring_loop(self):
        """Loop principal de monitoreo"""
        self.logger.log_info(f"[{self.component_id}] Iniciando loop de monitoreo")
        start_time = datetime.now()
        
        while not self._stop_event.is_set():
            try:
                # Obtener estado actual
                previous_positions = self.current_positions.copy()
                self._snapshot_current_positions()
                
                # Detectar cambios
                changes = self._detect_position_changes(previous_positions, self.current_positions)
                
                if changes:
                    self._process_position_changes(changes)
                    
                # Verificar niveles de riesgo
                self._check_risk_levels()
                
                # Actualizar métricas
                self._update_metrics()
                
                # Esperar intervalo configurado
                time.sleep(self.monitor_config["update_interval"])
                
            except Exception as e:
                self.metrics["alerts_triggered"] += 1
                self.error.handle_data_error(f"{self.component_id}_monitoring", e)
                
                # Intentar reconectar si es necesario
                if not self._verify_mt5_connection():
                    self._attempt_reconnection()
                    
        # Calcular uptime
        self.metrics["monitoring_uptime"] = (datetime.now() - start_time).total_seconds()
        self.logger.log_info(f"[{self.component_id}] Loop de monitoreo terminado. Uptime: {self.metrics['monitoring_uptime']:.1f}s")
        
    def _detect_position_changes(self, previous: Dict, current: Dict) -> List[Dict]:
        """Detectar cambios en posiciones"""
        changes = []
        
        # Posiciones nuevas
        for ticket, position in current.items():
            if ticket not in previous:
                changes.append({
                    "type": "NEW_POSITION",
                    "ticket": ticket,
                    "position": position,
                    "timestamp": datetime.now()
                })
                
        # Posiciones cerradas
        for ticket, position in previous.items():
            if ticket not in current:
                changes.append({
                    "type": "CLOSED_POSITION",
                    "ticket": ticket,
                    "position": position,
                    "timestamp": datetime.now()
                })
                
        # Posiciones modificadas
        for ticket, position in current.items():
            if ticket in previous:
                prev_pos = previous[ticket]
                if (position["profit"] != prev_pos["profit"] or 
                    position["price_current"] != prev_pos["price_current"]):
                    changes.append({
                        "type": "POSITION_UPDATE",
                        "ticket": ticket,
                        "position": position,
                        "previous": prev_pos,
                        "timestamp": datetime.now()
                    })
                    
        return changes
        
    def _process_position_changes(self, changes: List[Dict]):
        """Procesar cambios detectados en posiciones"""
        self.metrics["position_changes_detected"] += len(changes)
        
        for change in changes:
            # Log del cambio
            if change["type"] == "NEW_POSITION":
                self.logger.log_info(f"[{self.component_id}] Nueva posición: {change['ticket']} {change['position']['symbol']}")
            elif change["type"] == "CLOSED_POSITION":
                self.logger.log_info(f"[{self.component_id}] Posición cerrada: {change['ticket']} {change['position']['symbol']}")
            elif change["type"] == "POSITION_UPDATE":
                profit_change = change['position']['profit'] - change['previous']['profit']
                self.logger.log_info(f"[{self.component_id}] Posición actualizada: {change['ticket']} P&L change: {profit_change:.2f}")
                
            # Guardar en histórico si está habilitado
            if self.monitor_config.get("track_history", False):
                self.position_history.append(change)
                
                # Limpiar histórico si excede máximo
                max_items = self.monitor_config.get("max_history_items", 1000)
                if len(self.position_history) > max_items:
                    self.position_history = self.position_history[-max_items:]
                    
            # Notificar callbacks de alertas
            if self.monitor_config.get("alert_on_change", True):
                self._notify_alert_callbacks("POSITION_CHANGE", change)
                
    def _check_risk_levels(self):
        """Verificar niveles de riesgo"""
        try:
            # Calcular P&L total actual
            total_pnl = sum(pos.get("profit", 0) for pos in self.current_positions.values())
            
            # Actualizar métricas min/max
            if total_pnl > self.metrics["max_pnl_today"]:
                self.metrics["max_pnl_today"] = total_pnl
            if total_pnl < self.metrics["min_pnl_today"]:
                self.metrics["min_pnl_today"] = total_pnl
                
            # Verificar umbral de pérdida diaria
            if total_pnl < 0 and abs(total_pnl) > (self.risk_thresholds["max_daily_loss"] * 10000):  # Asumiendo balance 10k
                self._trigger_risk_alert("MAX_DAILY_LOSS_EXCEEDED", {
                    "current_pnl": total_pnl,
                    "threshold": self.risk_thresholds["max_daily_loss"]
                })
                
            # Verificar drawdown
            if self.metrics["max_pnl_today"] > 0:
                drawdown = (self.metrics["max_pnl_today"] - total_pnl) / self.metrics["max_pnl_today"]
                if drawdown > self.risk_thresholds["max_drawdown"]:
                    self._trigger_risk_alert("MAX_DRAWDOWN_EXCEEDED", {
                        "current_drawdown": drawdown,
                        "threshold": self.risk_thresholds["max_drawdown"]
                    })
                    
        except Exception as e:
            self.error.handle_data_error(f"{self.component_id}_risk_check", e)
            
    def _trigger_risk_alert(self, alert_type: str, data: Dict):
        """Disparar alerta de riesgo"""
        self.metrics["alerts_triggered"] += 1
        alert = {
            "type": alert_type,
            "data": data,
            "timestamp": datetime.now(),
            "component": self.component_id
        }
        
        self.logger.log_warning(f"[{self.component_id}] ALERTA DE RIESGO: {alert_type}")
        self._notify_alert_callbacks("RISK_ALERT", alert)
        
    def _notify_alert_callbacks(self, alert_type: str, data: Any):
        """Notificar a callbacks de alertas"""
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, data)
            except Exception as e:
                self.error.handle_system_error(f"{self.component_id}: Error en callback de alerta", e)
                
    def _update_metrics(self):
        """Actualizar métricas de rendimiento"""
        self.metrics["total_positions_tracked"] = len(self.current_positions)
        self.metrics["last_update"] = datetime.now()
        
    def _attempt_reconnection(self):
        """Intentar reconexión a MT5"""
        self.logger.log_warning(f"[{self.component_id}] Intentando reconexión...")
        time.sleep(2)  # Esperar antes de reintentar
        
    def subscribe_alerts(self, callback: Callable[[str, Any], None]):
        """
        Suscribirse a alertas de posiciones
        
        Args:
            callback: Función a llamar cuando se generen alertas
        """
        if callback not in self.alert_callbacks:
            self.alert_callbacks.append(callback)
            self.logger.log_info(f"[{self.component_id}] Callback de alerta agregado")
            
    def unsubscribe_alerts(self, callback: Callable[[str, Any], None]):
        """Desuscribirse de alertas"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
            self.logger.log_info(f"[{self.component_id}] Callback de alerta removido")
            
    def get_current_positions(self) -> Dict[str, Any]:
        """Obtener posiciones actuales"""
        return self.current_positions.copy()
        
    def get_position_history(self) -> List[Dict]:
        """Obtener histórico de cambios de posiciones"""
        return self.position_history.copy()
        
    def get_current_pnl(self) -> float:
        """Obtener P&L actual"""
        return sum(pos.get("profit", 0) for pos in self.current_positions.values())
        
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento"""
        return self.metrics.copy()
        
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del monitor"""
        return {
            "component_id": self.component_id,
            "version": self.version,
            "is_monitoring": self.is_monitoring,
            "is_connected": self.is_connected,
            "positions_count": len(self.current_positions),
            "current_pnl": self.get_current_pnl(),
            "symbols_tracked": len(self.monitor_config["symbols_to_track"]),
            "alerts_triggered": self.metrics["alerts_triggered"],
            "last_update": self.last_update
        }


# Función de testing para desarrollo
def main():
    """Función de test para desarrollo"""
    print("🧪 Testing PositionMonitor...")
    
    try:
        # Imports para testing
        from config_manager import ConfigManager
        from logger_manager import LoggerManager
        from error_manager import ErrorManager
        from mt5_manager import MT5Manager
        from data_manager import DataManager
        
        # Crear dependencias
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        mt5_manager = MT5Manager(config, logger, error)
        data_manager = DataManager(config, logger, error)
        
        # Crear monitor
        monitor = PositionMonitor(config, logger, error, mt5_manager, data_manager)
        
        print(f"✅ PositionMonitor inicializado: {monitor.component_id}")
        print(f"✅ Versión: {monitor.version}")
        print(f"✅ Estado: {monitor.get_status()}")
        
        # Test básico de configuración
        print(f"✅ Símbolos configurados: {monitor.monitor_config['symbols_to_track']}")
        print(f"✅ Intervalo de actualización: {monitor.monitor_config['update_interval']}s")
        
        # Test de callbacks
        def test_alert_callback(alert_type, data):
            print(f"🚨 Alerta recibida: {alert_type}")
            
        monitor.subscribe_alerts(test_alert_callback)
        print("✅ Sistema de alertas configurado")
        
        print("🎉 PositionMonitor test básico PASSED")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
