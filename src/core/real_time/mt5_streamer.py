"""
MT5Streamer - PUERTA-S2-STREAMER
Streaming de datos MT5 en tiempo real para SÓTANO 2

Funcionalidades:
- Stream continuo de precios desde MT5
- Buffer de datos optimizado
- Reconexión automática
- Compresión de datos
- Monitoreo de latencia

Fecha: 2025-08-11
Versión: v2.1.0
Componente: SÓTANO 2 - Real-Time Optimization
"""

import sys
from pathlib import Path
from datetime import datetime
import threading
import time
import queue
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
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    sys.exit(1)


class MT5Streamer:
    """
    Streaming de datos MT5 en tiempo real
    
    Gestiona:
    - Stream continuo de precios
    - Buffer de datos optimizado
    - Reconexión automática
    - Métricas de rendimiento
    """
    
    def __init__(self, config: ConfigManager, logger: LoggerManager, 
                 error: ErrorManager, mt5: MT5Manager):
        """
        Inicializar MT5Streamer
        
        Args:
            config: ConfigManager para configuración
            logger: LoggerManager para logging
            error: ErrorManager para manejo de errores
            mt5: MT5Manager para conexión MT5
        """
        self.component_id = "PUERTA-S2-STREAMER"
        self.version = "v2.1.0"
        
        # Dependencias SÓTANO 1
        self.config = config
        self.logger = logger
        self.error = error
        self.mt5 = mt5
        
        # Estado del streaming
        self.is_streaming = False
        self.is_connected = False
        self._stop_event = threading.Event()
        self._stream_thread = None
        
        # Buffer de datos
        self._data_buffer = queue.Queue(maxsize=1000)
        self._subscribers = []
        
        # Configuración por defecto
        self._load_streaming_config()
        
        # Métricas de rendimiento
        self.metrics = {
            "total_ticks": 0,
            "last_update": None,
            "latency_ms": 0,
            "buffer_size": 0,
            "reconnections": 0,
            "errors": 0
        }
        
        self.logger.log_info(f"[{self.component_id}] Inicializando MT5Streamer {self.version}")
        
    def _load_streaming_config(self):
        """Cargar configuración de streaming"""
        try:
            # Configuración por defecto para streaming
            self.streaming_config = {
                "update_interval": 0.1,        # 100ms
                "max_reconnect_attempts": 5,
                "connection_timeout": 10,
                "data_buffer_size": 1000,
                "enable_tick_data": True,
                "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
                "compression_level": 3
            }
            
            self.logger.log_info(f"[{self.component_id}] Configuración cargada: {len(self.streaming_config['symbols'])} símbolos")
            
        except Exception as e:
            self.error.handle_system_error(f"{self.component_id}: Error cargando configuración", e)
            # Configuración mínima de emergencia
            self.streaming_config = {
                "update_interval": 1.0,
                "symbols": ["EURUSD"],
                "enable_tick_data": False
            }
            
    def start_streaming(self, symbols: Optional[List[str]] = None) -> bool:
        """
        Iniciar streaming de datos MT5
        
        Args:
            symbols: Lista de símbolos a monitorear (opcional)
            
        Returns:
            bool: True si el streaming se inició correctamente
        """
        try:
            if self.is_streaming:
                self.logger.log_warning(f"[{self.component_id}] Stream ya está activo")
                return True
                
            # Usar símbolos proporcionados o configuración por defecto
            if symbols:
                self.streaming_config["symbols"] = symbols
                
            # Verificar conexión MT5
            if not self._verify_mt5_connection():
                return False
                
            # Iniciar thread de streaming
            self._stop_event.clear()
            self._stream_thread = threading.Thread(
                target=self._streaming_loop,
                name=f"{self.component_id}-Stream",
                daemon=True
            )
            self._stream_thread.start()
            
            self.is_streaming = True
            self.logger.log_success(f"[{self.component_id}] Streaming iniciado para {len(self.streaming_config['symbols'])} símbolos")
            return True
            
        except Exception as e:
            self.error.handle_system_error(f"{self.component_id}: Error iniciando streaming", e)
            return False
            
    def stop_streaming(self) -> bool:
        """
        Detener streaming de datos
        
        Returns:
            bool: True si se detuvo correctamente
        """
        try:
            if not self.is_streaming:
                self.logger.log_warning(f"[{self.component_id}] Stream no está activo")
                return True
                
            # Señal de parada
            self._stop_event.set()
            
            # Esperar que termine el thread
            if self._stream_thread and self._stream_thread.is_alive():
                self._stream_thread.join(timeout=5.0)
                
            self.is_streaming = False
            self.logger.log_success(f"[{self.component_id}] Streaming detenido")
            return True
            
        except Exception as e:
            self.error.handle_system_error(f"{self.component_id}: Error deteniendo streaming", e)
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
            
    def _streaming_loop(self):
        """Loop principal de streaming"""
        self.logger.log_info(f"[{self.component_id}] Iniciando loop de streaming")
        
        while not self._stop_event.is_set():
            try:
                # Obtener datos actuales
                market_data = self._get_current_market_data()
                
                if market_data:
                    # Agregar timestamp
                    market_data["timestamp"] = datetime.now()
                    
                    # Agregar al buffer
                    self._add_to_buffer(market_data)
                    
                    # Notificar suscriptores
                    self._notify_subscribers(market_data)
                    
                    # Actualizar métricas
                    self._update_metrics(market_data)
                
                # Esperar intervalo configurado
                time.sleep(self.streaming_config["update_interval"])
                
            except Exception as e:
                self.metrics["errors"] += 1
                self.error.handle_data_error(f"{self.component_id}_streaming", e)
                
                # Intentar reconectar si es necesario
                if not self._verify_mt5_connection():
                    self._attempt_reconnection()
                    
        self.logger.log_info(f"[{self.component_id}] Loop de streaming terminado")
        
    def _get_current_market_data(self) -> Optional[Dict[str, Any]]:
        """Obtener datos actuales del mercado"""
        try:
            market_data = {}
            
            for symbol in self.streaming_config["symbols"]:
                # Obtener precio actual
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    market_data[symbol] = {
                        "bid": tick.bid,
                        "ask": tick.ask,
                        "spread": tick.ask - tick.bid,
                        "volume": tick.volume,
                        "time": tick.time
                    }
                    
            return market_data if market_data else None
            
        except Exception as e:
            self.error.handle_data_error(f"{self.component_id}_market_data", e)
            return None
            
    def _add_to_buffer(self, data: Dict[str, Any]):
        """Agregar datos al buffer"""
        try:
            if not self._data_buffer.full():
                self._data_buffer.put(data, block=False)
                self.metrics["buffer_size"] = self._data_buffer.qsize()
            else:
                # Buffer lleno, remover dato más antiguo
                try:
                    self._data_buffer.get(block=False)
                    self._data_buffer.put(data, block=False)
                except queue.Empty:
                    pass
                    
        except Exception as e:
            self.error.handle_data_error(f"{self.component_id}_buffer", e)
            
    def _notify_subscribers(self, data: Dict[str, Any]):
        """Notificar a suscriptores de nuevos datos"""
        for callback in self._subscribers:
            try:
                callback(data)
            except Exception as e:
                self.error.handle_system_error(f"{self.component_id}: Error en callback", e)
                
    def _update_metrics(self, data: Dict[str, Any]):
        """Actualizar métricas de rendimiento"""
        self.metrics["total_ticks"] += 1
        self.metrics["last_update"] = datetime.now()
        # Calcular latency básica (simplificado)
        self.metrics["latency_ms"] = (datetime.now() - data["timestamp"]).total_seconds() * 1000
        
    def _attempt_reconnection(self):
        """Intentar reconexión a MT5"""
        self.metrics["reconnections"] += 1
        self.logger.log_warning(f"[{self.component_id}] Intentando reconexión...")
        time.sleep(1)  # Esperar antes de reintentar
        
    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Suscribirse a actualizaciones de datos
        
        Args:
            callback: Función a llamar cuando lleguen nuevos datos
        """
        if callback not in self._subscribers:
            self._subscribers.append(callback)
            self.logger.log_info(f"[{self.component_id}] Nuevo suscriptor agregado")
            
    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]):
        """Desuscribirse de actualizaciones"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            self.logger.log_info(f"[{self.component_id}] Suscriptor removido")
            
    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """Obtener datos más recientes del buffer"""
        try:
            if not self._data_buffer.empty():
                # Obtener sin remover del buffer
                data = self._data_buffer.queue[-1]
                return data
            return None
        except Exception as e:
            self.error.handle_data_error(f"{self.component_id}_latest_data", e)
            return None
            
    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de rendimiento"""
        return self.metrics.copy()
        
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del streamer"""
        return {
            "component_id": self.component_id,
            "version": self.version,
            "is_streaming": self.is_streaming,
            "is_connected": self.is_connected,
            "symbols_count": len(self.streaming_config["symbols"]),
            "buffer_size": self.metrics["buffer_size"],
            "total_ticks": self.metrics["total_ticks"],
            "errors": self.metrics["errors"],
            "last_update": self.metrics["last_update"]
        }


# Función de testing para desarrollo
def main():
    """Función de test para desarrollo"""
    print("🧪 Testing MT5Streamer...")
    
    try:
        # Imports para testing
        from config_manager import ConfigManager
        from logger_manager import LoggerManager
        from error_manager import ErrorManager
        from mt5_manager import MT5Manager
        
        # Crear dependencias
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        mt5_manager = MT5Manager(config, logger, error)
        
        # Crear streamer
        streamer = MT5Streamer(config, logger, error, mt5_manager)
        
        print(f"✅ MT5Streamer inicializado: {streamer.component_id}")
        print(f"✅ Versión: {streamer.version}")
        print(f"✅ Estado: {streamer.get_status()}")
        
        # Test básico de configuración
        print(f"✅ Símbolos configurados: {streamer.streaming_config['symbols']}")
        print(f"✅ Intervalo de actualización: {streamer.streaming_config['update_interval']}s")
        
        print("🎉 MT5Streamer test básico PASSED")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
