"""
PUERTA-PE-EXECUTOR: OrderExecutor v1.0.0
========================================
Puente crítico entre TradingSignal del StrategyEngine y ejecución real en MT5

Este componente es EL CORAZÓN del PISO EJECUTOR - convierte las señales
inteligentes generadas por el StrategyEngine en órdenes reales ejecutadas
en MetaTrader 5 a través del FundedNextMT5Manager.

FLUJO CRÍTICO:
StrategyEngine → TradingSignal → OrderExecutor → MT5Manager → MT5 Real

FUNCIONALIDADES:
- Conversión TradingSignal → MT5 order request
- Validación de señales pre-ejecución
- Ejecución segura en MT5 real
- Tracking completo de órdenes
- Error handling robusto
- Integration con sistema de riesgo

PROTOCOLO: Trading Grid - Piso Ejecutor
AUTOR: Copilot & AI Assistant
FECHA: 2025-08-12
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Imports del sistema
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.mt5_manager import MT5Manager
from src.core.fundednext_mt5_manager import FundedNextMT5Manager

# Import del StrategyEngine para TradingSignal
try:
    from src.core.real_time.strategy_engine import TradingSignal, SignalStrength
except ImportError as e:
    # Fallback si hay problemas de import
    from typing import NamedTuple
    class TradingSignal(NamedTuple):
        symbol: str
        signal_type: str
        price: float
        confidence: float

import MetaTrader5 as mt5


class OrderStatus(Enum):
    """Estados de las órdenes"""
    PENDING = "pending"
    VALIDATING = "validating"
    EXECUTING = "executing"
    EXECUTED = "executed"
    FAILED = "failed"
    REJECTED = "rejected"

class OrderType(Enum):
    """Tipos de órdenes MT5"""
    BUY = mt5.ORDER_TYPE_BUY
    SELL = mt5.ORDER_TYPE_SELL
    BUY_LIMIT = mt5.ORDER_TYPE_BUY_LIMIT
    SELL_LIMIT = mt5.ORDER_TYPE_SELL_LIMIT
    BUY_STOP = mt5.ORDER_TYPE_BUY_STOP
    SELL_STOP = mt5.ORDER_TYPE_SELL_STOP

@dataclass
class OrderRequest:
    """Request de orden para MT5"""
    symbol: str
    action: int  # mt5.TRADE_ACTION_DEAL
    type: int    # OrderType value
    volume: float
    price: float
    sl: float = 0.0  # Stop Loss
    tp: float = 0.0  # Take Profit
    comment: str = "OrderExecutor"
    magic: int = 123456
    deviation: int = 20

@dataclass
class ExecutedOrder:
    """Orden ejecutada con metadatos"""
    order_id: int
    ticket: int
    symbol: str
    type: str
    volume: float
    price: float
    timestamp: datetime
    status: OrderStatus
    original_signal: Optional[TradingSignal] = None
    execution_time_ms: int = 0
    error_code: int = 0
    error_message: str = ""

class OrderExecutor:
    """
    PUERTA-PE-EXECUTOR: Ejecutor de Órdenes Inteligente
    
    EL CORAZÓN del PISO EJECUTOR - convierte señales en órdenes reales
    """
    
    def __init__(self, 
                 config_manager: Optional[ConfigManager] = None,
                 logger_manager: Optional[LoggerManager] = None,
                 error_manager: Optional[ErrorManager] = None,
                 fundednext_manager: Optional[FundedNextMT5Manager] = None):
        
        # Managers principales del sistema
        self.config_manager = config_manager or ConfigManager()
        self.logger_manager = logger_manager or LoggerManager()
        self.error_manager = error_manager or ErrorManager(
            logger_manager=self.logger_manager,
            config_manager=self.config_manager
        )
        
        # Manager MT5 exclusivo
        self.fundednext_manager = fundednext_manager or FundedNextMT5Manager(
            config_manager=self.config_manager,
            logger_manager=self.logger_manager,
            error_manager=self.error_manager
        )
        
        # Configuración del componente
        self.component_id = "PUERTA-PE-EXECUTOR"
        self.version = "v1.0.0"
        
        # Estado del ejecutor
        self.is_active = False
        self.orders_enabled = True
        self.last_execution = None
        
        # Tracking de órdenes
        self.pending_orders: Dict[str, OrderRequest] = {}
        self.executed_orders: List[ExecutedOrder] = []
        self.failed_orders: List[ExecutedOrder] = []
        
        # Configuración de ejecución
        self.execution_config = {
            'default_volume': 0.01,
            'max_volume': 1.0,
            'default_deviation': 20,
            'magic_number': 123456,
            'max_orders_per_minute': 10,
            'enable_sl_tp': True
        }
        
        # Métricas
        self.execution_metrics = {
            'total_signals_received': 0,
            'total_orders_executed': 0,
            'total_orders_failed': 0,
            'success_rate': 0.0,
            'avg_execution_time_ms': 0.0,
            'last_24h_orders': 0
        }
        
        # Log de inicialización
        self.logger_manager.log_info(f"✅ {self.component_id} {self.version} inicializado")
        self.logger_manager.log_info(f"🔗 Integrado con FundedNextMT5Manager")
    
    def initialize_executor(self) -> bool:
        """Inicializar el ejecutor de órdenes"""
        try:
            # Verificar conexión MT5
            if not self.fundednext_manager.ensure_fundednext_terminal():
                self.logger_manager.log_error("❌ FundedNext Terminal no disponible")
                return False
            
            if not self.fundednext_manager.connect_to_mt5():
                self.logger_manager.log_error("❌ Conexión MT5 falló")
                return False
            
            # Marcar como activo
            self.is_active = True
            self.logger_manager.log_info("✅ OrderExecutor inicializado y listo")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("OrderExecutor", e, {"operation": "initialize"})
            return False
    
    def process_signal(self, signal: TradingSignal) -> bool:
        """
        FUNCIÓN CRÍTICA: Procesar señal del StrategyEngine
        
        Esta es la función principal que conecta el StrategyEngine con MT5
        """
        try:
            if not self.is_active:
                self.logger_manager.log_warning("⚠️ OrderExecutor no está activo")
                return False
            
            if not self.orders_enabled:
                self.logger_manager.log_warning("⚠️ Ejecución de órdenes deshabilitada")
                return False
            
            # Incrementar métricas
            self.execution_metrics['total_signals_received'] += 1
            
            self.logger_manager.log_info(f"📡 Procesando señal: {signal.symbol} {signal.signal_type}")
            
            # 1. Validar señal
            if not self._validate_signal(signal):
                self.logger_manager.log_warning(f"❌ Señal inválida: {signal.symbol}")
                return False
            
            # 2. Convertir a orden MT5
            order_request = self._convert_signal_to_order(signal)
            if not order_request:
                self.logger_manager.log_error(f"❌ Falló conversión señal→orden: {signal.symbol}")
                return False
            
            # 3. Ejecutar orden
            executed_order = self._execute_order(order_request, signal)
            if executed_order and executed_order.status == OrderStatus.EXECUTED:
                self.logger_manager.log_info(f"✅ Orden ejecutada: {executed_order.ticket}")
                self._update_success_metrics(executed_order)
                return True
            else:
                self.logger_manager.log_error(f"❌ Ejecución falló: {signal.symbol}")
                self._update_failure_metrics()
                return False
                
        except Exception as e:
            self.error_manager.handle_system_error("OrderExecutor", e, {"signal": signal.symbol})
            self._update_failure_metrics()
            return False
    
    def _validate_signal(self, signal: TradingSignal) -> bool:
        """Validar señal antes de ejecutar"""
        try:
            # Validaciones básicas
            if not signal.symbol or not signal.signal_type:
                return False
            
            if signal.signal_type not in ['BUY', 'SELL']:
                return False
            
            if signal.price <= 0:
                return False
            
            # Validar fuerza de señal si está disponible
            if hasattr(signal, 'strength') and hasattr(signal, 'confidence'):
                if signal.confidence < 0.5:  # Confianza mínima 50%
                    self.logger_manager.log_warning(f"⚠️ Señal con baja confianza: {signal.confidence}")
                    return False
            
            # Validar symbol en MT5
            symbol_info = mt5.symbol_info(signal.symbol)
            if symbol_info is None:
                self.logger_manager.log_error(f"❌ Símbolo no disponible en MT5: {signal.symbol}")
                return False
            
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("OrderExecutor", e, {"signal": signal.symbol})
            return False
    
    def _convert_signal_to_order(self, signal: TradingSignal) -> Optional[OrderRequest]:
        """Convertir TradingSignal a OrderRequest de MT5"""
        try:
            # Determinar tipo de orden
            order_type = OrderType.BUY.value if signal.signal_type == 'BUY' else OrderType.SELL.value
            
            # Calcular volumen basado en confianza de señal
            base_volume = self.execution_config['default_volume']
            if hasattr(signal, 'confidence'):
                # Ajustar volumen por confianza (50%-100% = 0.01-0.02 lotes)
                volume_multiplier = 0.5 + signal.confidence * 0.5
                calculated_volume = base_volume * volume_multiplier
            else:
                calculated_volume = base_volume
            
            # Limitar volumen máximo
            volume = min(calculated_volume, self.execution_config['max_volume'])
            volume = round(volume, 2)  # Redondear a 2 decimales
            
            # Crear request de orden
            order_request = OrderRequest(
                symbol=signal.symbol,
                action=mt5.TRADE_ACTION_DEAL,
                type=order_type,
                volume=volume,
                price=signal.price,
                comment=f"Signal_{signal.source if hasattr(signal, 'source') else 'Strategy'}",
                magic=self.execution_config['magic_number'],
                deviation=self.execution_config['default_deviation']
            )
            
            self.logger_manager.log_info(f"🔄 Orden creada: {signal.symbol} {signal.signal_type} {volume}")
            return order_request
            
        except Exception as e:
            self.error_manager.handle_system_error("OrderExecutor", e, {"signal": signal.symbol})
            return None
    
    def _execute_order(self, order_request: OrderRequest, original_signal: TradingSignal) -> Optional[ExecutedOrder]:
        """Ejecutar orden en MT5"""
        start_time = time.time()
        
        try:
            # Crear diccionario de request para MT5
            mt5_request = {
                "action": order_request.action,
                "symbol": order_request.symbol,
                "volume": order_request.volume,
                "type": order_request.type,
                "price": order_request.price,
                "sl": order_request.sl,
                "tp": order_request.tp,
                "deviation": order_request.deviation,
                "magic": order_request.magic,
                "comment": order_request.comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            self.logger_manager.log_info(f"🚀 Ejecutando orden: {order_request.symbol}")
            
            # Ejecutar en MT5
            result = mt5.order_send(mt5_request)
            execution_time = int((time.time() - start_time) * 1000)
            
            if result is None:
                error_code = mt5.last_error()
                error_msg = f"MT5 Error: {error_code}"
                self.logger_manager.log_error(f"❌ {error_msg}")
                
                # Crear orden fallida
                failed_order = ExecutedOrder(
                    order_id=0,
                    ticket=0,
                    symbol=order_request.symbol,
                    type=order_request.type,
                    volume=order_request.volume,
                    price=order_request.price,
                    timestamp=datetime.now(),
                    status=OrderStatus.FAILED,
                    original_signal=original_signal,
                    execution_time_ms=execution_time,
                    error_code=error_code[0] if error_code else 0,
                    error_message=error_msg
                )
                
                self.failed_orders.append(failed_order)
                return failed_order
            
            # Procesar resultado exitoso
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                executed_order = ExecutedOrder(
                    order_id=result.order,
                    ticket=result.deal if hasattr(result, 'deal') else result.order,
                    symbol=order_request.symbol,
                    type="BUY" if order_request.type == OrderType.BUY.value else "SELL",
                    volume=result.volume,
                    price=result.price,
                    timestamp=datetime.now(),
                    status=OrderStatus.EXECUTED,
                    original_signal=original_signal,
                    execution_time_ms=execution_time,
                    error_code=0,
                    error_message=""
                )
                
                self.executed_orders.append(executed_order)
                self.logger_manager.log_info(f"✅ Orden ejecutada exitosamente: ticket={executed_order.ticket}")
                return executed_order
                
            else:
                # Error en ejecución
                error_msg = f"Retcode: {result.retcode}"
                failed_order = ExecutedOrder(
                    order_id=result.order if hasattr(result, 'order') else 0,
                    ticket=0,
                    symbol=order_request.symbol,
                    type=order_request.type,
                    volume=order_request.volume,
                    price=order_request.price,
                    timestamp=datetime.now(),
                    status=OrderStatus.REJECTED,
                    original_signal=original_signal,
                    execution_time_ms=execution_time,
                    error_code=result.retcode,
                    error_message=error_msg
                )
                
                self.failed_orders.append(failed_order)
                self.logger_manager.log_error(f"❌ Orden rechazada: {error_msg}")
                return failed_order
                
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.error_manager.handle_system_error("OrderExecutor", e, {"order": order_request.symbol})
            
            # Crear orden fallida por excepción
            failed_order = ExecutedOrder(
                order_id=0,
                ticket=0,
                symbol=order_request.symbol,
                type=order_request.type,
                volume=order_request.volume,
                price=order_request.price,
                timestamp=datetime.now(),
                status=OrderStatus.FAILED,
                original_signal=original_signal,
                execution_time_ms=execution_time,
                error_code=-1,
                error_message=str(e)
            )
            
            self.failed_orders.append(failed_order)
            return failed_order
    
    def _update_success_metrics(self, executed_order: ExecutedOrder):
        """Actualizar métricas de éxito"""
        self.execution_metrics['total_orders_executed'] += 1
        
        # Actualizar tiempo promedio de ejecución
        total_orders = self.execution_metrics['total_orders_executed']
        current_avg = self.execution_metrics['avg_execution_time_ms']
        new_avg = ((current_avg * (total_orders - 1)) + executed_order.execution_time_ms) / total_orders
        self.execution_metrics['avg_execution_time_ms'] = new_avg
        
        # Actualizar tasa de éxito
        total_attempts = self.execution_metrics['total_orders_executed'] + self.execution_metrics['total_orders_failed']
        self.execution_metrics['success_rate'] = self.execution_metrics['total_orders_executed'] / total_attempts if total_attempts > 0 else 0
        
        self.last_execution = datetime.now()
    
    def _update_failure_metrics(self):
        """Actualizar métricas de fallo"""
        self.execution_metrics['total_orders_failed'] += 1
        
        # Actualizar tasa de éxito
        total_attempts = self.execution_metrics['total_orders_executed'] + self.execution_metrics['total_orders_failed']
        self.execution_metrics['success_rate'] = self.execution_metrics['total_orders_executed'] / total_attempts if total_attempts > 0 else 0
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Obtener estado del ejecutor"""
        return {
            'component_id': self.component_id,
            'version': self.version,
            'is_active': self.is_active,
            'orders_enabled': self.orders_enabled,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'metrics': self.execution_metrics.copy(),
            'recent_orders': len([o for o in self.executed_orders if o.timestamp > datetime.now().replace(hour=datetime.now().hour-1)]),
            'connection_status': self.fundednext_manager.get_connection_status() if self.fundednext_manager else "unknown"
        }
    
    def enable_orders(self, enabled: bool = True):
        """Habilitar/deshabilitar ejecución de órdenes"""
        self.orders_enabled = enabled
        status = "habilitada" if enabled else "deshabilitada"
        self.logger_manager.log_info(f"🔄 Ejecución de órdenes {status}")
    
    def cleanup(self):
        """Cleanup del ejecutor"""
        try:
            self.is_active = False
            self.orders_enabled = False
            self.logger_manager.log_info(f"🧹 {self.component_id} cleanup completado")
        except Exception as e:
            self.error_manager.handle_system_error("OrderExecutor", e, {"operation": "cleanup"})


# Función de utilidad para demo
def demo_order_executor():
    """Demo básico del OrderExecutor"""
    print("🚀 DEMO ORDEREXECUTOR - PUERTA-PE-EXECUTOR")
    print("=" * 50)
    
    try:
        # Crear executor
        executor = OrderExecutor()
        
        # Inicializar
        if executor.initialize_executor():
            print("✅ OrderExecutor inicializado correctamente")
            
            # Mostrar estado
            status = executor.get_execution_status()
            print(f"📊 Estado: Activo={status['is_active']}, Órdenes={status['orders_enabled']}")
            
            # Nota: Para demo real se necesitaría una TradingSignal del StrategyEngine
            print("💡 Para prueba completa, usar con StrategyEngine")
            
        else:
            print("❌ Error inicializando OrderExecutor")
        
        # Cleanup
        executor.cleanup()
        print("✅ Demo completado")
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")


if __name__ == "__main__":
    demo_order_executor()
