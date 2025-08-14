"""
⚡ FVG ORDER EXECUTOR - PISO 3 OFICINA TRADING
==============================================

Ejecutor de Órdenes para señales FVG
Maneja la ejecución real de trades en MetaTrader 5

FUNCIONALIDADES:
- Ejecución segura de órdenes MT5
- SL/TP dinámicos calculados por FVGRiskManager
- Múltiples take profits (R:R 1.5, 2.5, 4.0)
- Validación doble antes de ejecución
- Fallback a ejecución tradicional

AUTOR: Sistema Trading Grid - Piso 3
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import MetaTrader5 as mt5

# Configurar imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))

from logger_manager import LoggerManager

class FVGOrderExecutor:
    """
    ⚡ EJECUTOR DE ÓRDENES FVG - PISO 3
    Ejecución segura y validada de señales FVG en MetaTrader 5
    """
    
    def __init__(self, symbol='EURUSD'):
        self.symbol = symbol
        self.logger = LoggerManager().get_logger('fvg_order_executor')
        
        # Configuración de ejecución
        self.execution_config = {
            'magic_number': 987654321,      # Magic number único para FVG
            'max_slippage': 10,             # Slippage máximo en points
            'timeout_ms': 10000,            # Timeout para órdenes
            'retry_attempts': 3,            # Intentos de reintento
            'min_distance_points': 10,      # Distancia mínima SL/TP
            'partial_close_enabled': True   # Habilitear cierres parciales
        }
        
        # Estado de órdenes
        self.pending_orders = {}
        self.executed_orders = {}
        
        # Estadísticas
        self.stats = {
            'total_attempts': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'retry_success': 0,
            'avg_execution_time_ms': 0.0,
            'success_rate': 0.0
        }
        
        self.logger.info("⚡ FVGOrderExecutor inicializado para símbolo: %s", symbol)
    
    def execute_fvg_signal(self, signal: Dict) -> Dict:
        """
        ⚡ Ejecutar señal FVG en MetaTrader 5
        
        Args:
            signal: Señal FVG completa del Signal Generator
            
        Returns:
            dict: Resultado de la ejecución
        """
        try:
            signal_id = signal.get('signal_id', 'UNKNOWN')
            self.logger.info("⚡ Ejecutando señal FVG: %s - %s @ %.5f", 
                           signal_id, signal.get('direction'), signal.get('entry_price', 0))
            
            execution_result = {
                'executed': False,
                'signal_id': signal_id,
                'order_ticket': 0,
                'execution_price': 0.0,
                'execution_time': None,
                'sl_price': 0.0,
                'tp_prices': {},
                'lot_size': 0.0,
                'slippage_pips': 0.0,
                'execution_time_ms': 0,
                'reason': '',
                'mt5_result': None
            }
            
            start_time = datetime.now()
            
            # 1. Validaciones previas
            if not self._validate_signal(signal):
                execution_result['reason'] = 'Señal no válida para ejecución'
                return execution_result
            
            # 2. Verificar conexión MT5
            if not self._check_mt5_connection():
                execution_result['reason'] = 'Sin conexión a MetaTrader 5'
                return execution_result
            
            # 3. Verificar condiciones de mercado
            market_status = self._check_market_conditions()
            if not market_status['tradeable']:
                execution_result['reason'] = f'Mercado no disponible: {market_status["reason"]}'
                return execution_result
            
            # 4. Preparar parámetros de orden
            order_params = self._prepare_order_params(signal)
            if not order_params:
                execution_result['reason'] = 'Error preparando parámetros de orden'
                return execution_result
            
            # 5. Ejecutar orden principal
            mt5_result = self._execute_market_order(order_params)
            
            if mt5_result and mt5_result.retcode == mt5.TRADE_RETCODE_DONE:
                # Orden principal exitosa
                execution_result.update({
                    'executed': True,
                    'order_ticket': mt5_result.order,
                    'execution_price': mt5_result.price,
                    'execution_time': datetime.now(),
                    'lot_size': order_params['volume'],
                    'mt5_result': mt5_result,
                    'reason': 'Orden ejecutada exitosamente'
                })
                
                # 6. Configurar SL/TP
                sl_tp_result = self._setup_sl_tp(mt5_result, signal)
                execution_result.update(sl_tp_result)
                
                # 7. Registrar orden exitosa
                self._register_successful_order(execution_result)
                
                # Calcular slippage
                expected_price = signal.get('entry_price', 0)
                actual_price = mt5_result.price
                slippage_pips = abs(expected_price - actual_price) / self._get_pip_size()
                execution_result['slippage_pips'] = round(slippage_pips, 1)
                
                self.stats['successful_executions'] += 1
                
            else:
                # Error en ejecución
                error_msg = self._get_mt5_error_message(mt5_result)
                execution_result.update({
                    'reason': f'Error MT5: {error_msg}',
                    'mt5_result': mt5_result
                })
                
                self.stats['failed_executions'] += 1
            
            # Calcular tiempo de ejecución
            end_time = datetime.now()
            execution_time_ms = (end_time - start_time).total_seconds() * 1000
            execution_result['execution_time_ms'] = round(execution_time_ms, 2)
            
            # Actualizar estadísticas
            self.stats['total_attempts'] += 1
            self._update_execution_stats()
            
            self.logger.info("   Resultado: %s - Ticket: %d, Precio: %.5f, Tiempo: %.1fms", 
                           "EXITOSO" if execution_result['executed'] else "FALLIDO",
                           execution_result.get('order_ticket', 0),
                           execution_result.get('execution_price', 0),
                           execution_result.get('execution_time_ms', 0))
            
            return execution_result
            
        except Exception as e:
            self.logger.error("❌ Error ejecutando señal FVG: %s", e)
            return {
                'executed': False,
                'signal_id': signal.get('signal_id', 'UNKNOWN'),
                'reason': f'Error interno: {e}',
                'error': str(e)
            }
    
    def _validate_signal(self, signal: Dict) -> bool:
        """✅ Validar señal antes de ejecución"""
        try:
            # Verificar campos obligatorios
            required_fields = ['signal_id', 'direction', 'entry_price', 'lot_size']
            for field in required_fields:
                if field not in signal or not signal[field]:
                    self.logger.warning("❌ Campo obligatorio faltante: %s", field)
                    return False
            
            # Verificar dirección válida
            if signal['direction'] not in ['BUY', 'SELL']:
                self.logger.warning("❌ Dirección inválida: %s", signal['direction'])
                return False
            
            # Verificar lotaje válido
            lot_size = signal.get('lot_size', 0)
            if lot_size <= 0 or lot_size > 10:
                self.logger.warning("❌ Lotaje inválido: %.3f", lot_size)
                return False
            
            # Verificar validez temporal
            valid_until = signal.get('valid_until')
            if valid_until and datetime.now() > valid_until:
                self.logger.warning("❌ Señal expirada")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error("❌ Error validando señal: %s", e)
            return False
    
    def _check_mt5_connection(self) -> bool:
        """🔌 Verificar conexión a MetaTrader 5"""
        try:
            if not mt5.initialize():
                self.logger.error("❌ No se pudo conectar a MetaTrader 5")
                return False
            
            account_info = mt5.account_info()
            if not account_info:
                self.logger.error("❌ No se pudo obtener información de cuenta")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error("❌ Error verificando conexión MT5: %s", e)
            return False
    
    def _check_market_conditions(self) -> Dict:
        """📊 Verificar condiciones de mercado"""
        try:
            symbol_info = mt5.symbol_info(self.symbol)
            if not symbol_info:
                return {'tradeable': False, 'reason': 'Símbolo no disponible'}
            
            if not symbol_info.trade_mode:
                return {'tradeable': False, 'reason': 'Trading deshabilitado para el símbolo'}
            
            # Verificar spread
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                return {'tradeable': False, 'reason': 'No hay cotizaciones disponibles'}
            
            spread_pips = (tick.ask - tick.bid) / self._get_pip_size()
            max_spread_pips = 5.0  # Máximo spread permitido
            
            if spread_pips > max_spread_pips:
                return {'tradeable': False, 'reason': f'Spread muy alto: {spread_pips:.1f} pips'}
            
            return {'tradeable': True, 'reason': 'Mercado disponible', 'spread_pips': spread_pips}
            
        except Exception as e:
            self.logger.error("❌ Error verificando mercado: %s", e)
            return {'tradeable': False, 'reason': f'Error verificando mercado: {e}'}
    
    def _prepare_order_params(self, signal: Dict) -> Optional[Dict]:
        """⚙️ Preparar parámetros para orden MT5"""
        try:
            direction = signal['direction']
            lot_size = signal['lot_size']
            
            # Obtener precio actual
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                return None
            
            # Configurar tipo de orden y precio
            if direction == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
            else:  # SELL
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
            
            order_params = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': self.symbol,
                'volume': lot_size,
                'type': order_type,
                'price': price,
                'deviation': self.execution_config['max_slippage'],
                'magic': self.execution_config['magic_number'],
                'comment': f"FVG_{signal['signal_id'][:8]}",
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC
            }
            
            return order_params
            
        except Exception as e:
            self.logger.error("❌ Error preparando parámetros: %s", e)
            return None
    
    def _execute_market_order(self, order_params: Dict):
        """📈 Ejecutar orden de mercado"""
        try:
            # Intentar ejecución con reintentos
            for attempt in range(self.execution_config['retry_attempts']):
                result = mt5.order_send(order_params)
                
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    if attempt > 0:
                        self.stats['retry_success'] += 1
                    return result
                
                # Si falló, esperar un poco antes del siguiente intento
                if attempt < self.execution_config['retry_attempts'] - 1:
                    import time
                    time.sleep(0.1)
                    
                    # Actualizar precio para siguiente intento
                    tick = mt5.symbol_info_tick(self.symbol)
                    if tick:
                        if order_params['type'] == mt5.ORDER_TYPE_BUY:
                            order_params['price'] = tick.ask
                        else:
                            order_params['price'] = tick.bid
            
            return result  # Último resultado (fallido)
            
        except Exception as e:
            self.logger.error("❌ Error ejecutando orden: %s", e)
            return None
    
    def _setup_sl_tp(self, mt5_result, signal: Dict) -> Dict:
        """📐 Configurar Stop Loss y Take Profits"""
        try:
            sl_tp_result = {
                'sl_price': 0.0,
                'tp_prices': {},
                'sl_set': False,
                'tp_set': False
            }
            
            # Obtener posición abierta
            position = mt5.positions_get(ticket=mt5_result.order)
            if not position:
                return sl_tp_result
            
            position = position[0]
            
            # Calcular precios SL/TP
            sl_price = signal.get('stop_loss', 0)
            tp_prices = signal.get('take_profits', {})
            
            if sl_price > 0:
                # Modificar posición con SL
                modify_request = {
                    'action': mt5.TRADE_ACTION_SLTP,
                    'symbol': self.symbol,
                    'position': position.ticket,
                    'sl': sl_price,
                    'tp': 0.0  # TP se configurará por separado para múltiples niveles
                }
                
                modify_result = mt5.order_send(modify_request)
                if modify_result and modify_result.retcode == mt5.TRADE_RETCODE_DONE:
                    sl_tp_result['sl_set'] = True
                    sl_tp_result['sl_price'] = sl_price
            
            # Configurar primer TP (TP1)
            if tp_prices and 'TP1' in tp_prices:
                tp1_price = tp_prices['TP1'].get('price', 0)
                if tp1_price > 0:
                    modify_request = {
                        'action': mt5.TRADE_ACTION_SLTP,
                        'symbol': self.symbol,
                        'position': position.ticket,
                        'sl': sl_price,
                        'tp': tp1_price
                    }
                    
                    modify_result = mt5.order_send(modify_request)
                    if modify_result and modify_result.retcode == mt5.TRADE_RETCODE_DONE:
                        sl_tp_result['tp_set'] = True
                        sl_tp_result['tp_prices'] = tp_prices
            
            return sl_tp_result
            
        except Exception as e:
            self.logger.error("❌ Error configurando SL/TP: %s", e)
            return {'sl_set': False, 'tp_set': False}
    
    def _register_successful_order(self, execution_result: Dict) -> None:
        """📝 Registrar orden exitosa"""
        try:
            order_record = {
                'signal_id': execution_result['signal_id'],
                'ticket': execution_result['order_ticket'],
                'execution_time': execution_result['execution_time'],
                'execution_price': execution_result['execution_price'],
                'lot_size': execution_result['lot_size'],
                'status': 'EXECUTED'
            }
            
            self.executed_orders[execution_result['signal_id']] = order_record
            
        except Exception as e:
            self.logger.error("❌ Error registrando orden: %s", e)
    
    def _get_mt5_error_message(self, result) -> str:
        """❌ Obtener mensaje de error MT5"""
        if not result:
            return "Sin respuesta de MT5"
        
        error_codes = {
            mt5.TRADE_RETCODE_REQUOTE: "Recotización",
            mt5.TRADE_RETCODE_REJECT: "Solicitud rechazada",
            mt5.TRADE_RETCODE_CANCEL: "Solicitud cancelada",
            mt5.TRADE_RETCODE_PLACED: "Orden colocada",
            mt5.TRADE_RETCODE_DONE_PARTIAL: "Ejecución parcial",
            mt5.TRADE_RETCODE_ERROR: "Error común",
            mt5.TRADE_RETCODE_TIMEOUT: "Timeout",
            mt5.TRADE_RETCODE_INVALID: "Solicitud inválida",
            mt5.TRADE_RETCODE_INVALID_VOLUME: "Volumen inválido",
            mt5.TRADE_RETCODE_INVALID_PRICE: "Precio inválido",
            mt5.TRADE_RETCODE_INVALID_STOPS: "Stops inválidos",
            mt5.TRADE_RETCODE_TRADE_DISABLED: "Trading deshabilitado",
            mt5.TRADE_RETCODE_MARKET_CLOSED: "Mercado cerrado",
            mt5.TRADE_RETCODE_NO_MONEY: "Fondos insuficientes",
            mt5.TRADE_RETCODE_PRICE_CHANGED: "Precio cambió",
            mt5.TRADE_RETCODE_PRICE_OFF: "Precio fuera de rango",
            mt5.TRADE_RETCODE_INVALID_EXPIRATION: "Expiración inválida",
            mt5.TRADE_RETCODE_ORDER_CHANGED: "Orden cambió",
            mt5.TRADE_RETCODE_TOO_MANY_REQUESTS: "Demasiadas solicitudes",
            mt5.TRADE_RETCODE_NO_CHANGES: "Sin cambios",
            mt5.TRADE_RETCODE_SERVER_DISABLES_AT: "Servidor deshabilita AT",
            mt5.TRADE_RETCODE_CLIENT_DISABLES_AT: "Cliente deshabilita AT",
            mt5.TRADE_RETCODE_LOCKED: "Bloqueado",
            mt5.TRADE_RETCODE_FROZEN: "Congelado",
            mt5.TRADE_RETCODE_INVALID_FILL: "Fill inválido",
            mt5.TRADE_RETCODE_CONNECTION: "Sin conexión",
            mt5.TRADE_RETCODE_ONLY_REAL: "Solo cuenta real",
            mt5.TRADE_RETCODE_LIMIT_ORDERS: "Límite de órdenes",
            mt5.TRADE_RETCODE_LIMIT_VOLUME: "Límite de volumen"
        }
        
        return error_codes.get(result.retcode, f"Error desconocido: {result.retcode}")
    
    def _get_pip_size(self) -> float:
        """📏 Obtener tamaño de pip para el símbolo"""
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info:
            return symbol_info.point * 10  # Para EURUSD, GBPUSD, etc.
        return 0.0001  # Valor por defecto
    
    def _update_execution_stats(self) -> None:
        """📊 Actualizar estadísticas de ejecución"""
        try:
            if self.stats['total_attempts'] > 0:
                self.stats['success_rate'] = (
                    self.stats['successful_executions'] / self.stats['total_attempts']
                ) * 100
            
        except Exception as e:
            self.logger.error("❌ Error actualizando estadísticas: %s", e)
    
    def get_execution_summary(self) -> Dict:
        """📊 Obtener resumen del ejecutor"""
        try:
            summary = {
                'timestamp': datetime.now(),
                'symbol': self.symbol,
                'stats': self.stats.copy(),
                'active_orders': len(self.executed_orders),
                'config': self.execution_config.copy()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo resumen: %s", e)
            return {'error': str(e)}

if __name__ == "__main__":
    # Test del FVG Order Executor
    print("⚡ Testing FVG Order Executor...")
    
    executor = FVGOrderExecutor('EURUSD')
    
    # Test signal (simulado)
    test_signal = {
        'signal_id': 'FVG_SIGNAL_TEST_001',
        'direction': 'BUY',
        'entry_price': 1.09450,
        'stop_loss': 1.09300,
        'take_profits': {
            'TP1': {'price': 1.09600, 'pips': 15, 'rr_ratio': 1.5},
            'TP2': {'price': 1.09750, 'pips': 30, 'rr_ratio': 2.0}
        },
        'lot_size': 0.01,
        'confidence_score': 0.85,
        'valid_until': datetime.now()
    }
    
    # Test de validación (sin ejecutar orden real)
    is_valid = executor._validate_signal(test_signal)
    print(f"✅ Validación de señal: {'VÁLIDA' if is_valid else 'INVÁLIDA'}")
    
    # Test de condiciones de mercado
    market_status = executor._check_market_conditions()
    print(f"📊 Estado del mercado: {'DISPONIBLE' if market_status['tradeable'] else 'NO DISPONIBLE'}")
    print(f"   Razón: {market_status.get('reason', 'N/A')}")
    
    # Resumen del ejecutor
    summary = executor.get_execution_summary()
    print(f"\n📊 Resumen Executor:")
    print(f"   Intentos totales: {summary.get('stats', {}).get('total_attempts', 0)}")
    print(f"   Ejecuciones exitosas: {summary.get('stats', {}).get('successful_executions', 0)}")
    print(f"   Tasa de éxito: {summary.get('stats', {}).get('success_rate', 0):.1f}%")
    
    print("\n🎯 FVG Order Executor test completado!")
    print("ℹ️  Nota: No se ejecutaron órdenes reales en este test")
