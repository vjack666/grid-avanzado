"""
🏢 PISO 4 - GESTOR DE EJECUCIÓN DE ENTRADAS
===========================================

Módulo para gestionar la ejecución de entradas basadas en confluencias FVG-Estocástico.
Integra gestión de riesgo con ejecución de órdenes MT5.

FUNCIONALIDADES:
- Ejecución de entradas por confluencias
- Gestión de stop loss y take profit
- Monitoreo de posiciones activas
- Cierre automático por condiciones
- Logging completo de operaciones

AUTOR: Sistema Trading Grid - Piso 4
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import MetaTrader5 as mt5

# Configurar imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "core").absolute()))

from logger_manager import LoggerManager
from .risk_position_manager import RiskPositionManager

class EntryExecutionManager:
    """
    🎯 GESTOR DE EJECUCIÓN DE ENTRADAS
    Ejecuta entradas basadas en confluencias FVG-Estocástico con gestión de riesgo
    """
    
    def __init__(self, symbol='EURUSD'):
        self.symbol = symbol
        self.logger = LoggerManager().get_logger('entry_execution_manager')
        
        # Gestor de riesgo
        self.risk_manager = RiskPositionManager(symbol)
        
        # Configuración de ejecución
        self.execution_config = {
            'auto_execute': False,      # Ejecución manual por seguridad
            'stop_loss_pips': 20,       # Stop loss en pips
            'take_profit_pips': 40,     # Take profit en pips
            'slippage': 3,              # Slippage permitido
            'magic_number': 888888,     # Número mágico para identificar órdenes
            'max_retry_attempts': 3,    # Intentos máximos de ejecución
            'confirmation_required': True  # Requiere confirmación manual
        }
        
        # Estado de ejecuciones
        self.execution_history = []
        self.pending_executions = []
        
        # Estadísticas
        self.execution_stats = {
            'total_attempts': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'manual_confirmations': 0,
            'auto_executions': 0
        }
    
    def process_confluence_signal(self, confluence_result: Dict) -> Dict:
        """
        🎯 Procesar señal de confluencia para posible ejecución
        
        Args:
            confluence_result: Resultado de confluencia FVG-Estocástico
            
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            self.logger.info("🎯 Procesando señal de confluencia para ejecución")
            
            processing_result = {
                'status': 'processed',
                'confluence_result': confluence_result,
                'risk_evaluation': None,
                'execution_result': None,
                'recommendation': 'WAIT',
                'timestamp': datetime.now()
            }
            
            # 1. Verificar si hay confluencia
            if not confluence_result.get('confluence_detected', False):
                processing_result['recommendation'] = 'NO_CONFLUENCE'
                self.logger.info("   ❌ Sin confluencia detectada")
                return processing_result
            
            # 2. Verificar fuerza de confluencia
            confluence_strength = confluence_result.get('confluence_strength', 0)
            if confluence_strength < 70:
                processing_result['recommendation'] = 'WEAK_CONFLUENCE'
                self.logger.info(f"   ⚠️ Confluencia débil: {confluence_strength}%")
                return processing_result
            
            # 3. Evaluar riesgo
            risk_evaluation = self.risk_manager.evaluate_position_risk(confluence_result)
            processing_result['risk_evaluation'] = risk_evaluation
            
            if not risk_evaluation.get('position_allowed', False):
                processing_result['recommendation'] = 'RISK_TOO_HIGH'
                reason = risk_evaluation.get('reason', 'Riesgo no evaluado')
                self.logger.info(f"   ❌ Riesgo alto: {reason}")
                return processing_result
            
            # 4. Determinar recomendación
            entry_type = confluence_result.get('entry_recommendation', 'WAIT')
            if entry_type in ['BUY', 'SELL']:
                processing_result['recommendation'] = 'EXECUTE_ENTRY'
                
                # 5. Ejecutar o preparar ejecución
                if self.execution_config['auto_execute']:
                    execution_result = self._execute_entry(confluence_result, risk_evaluation)
                    processing_result['execution_result'] = execution_result
                else:
                    # Agregar a pendientes para confirmación manual
                    self._add_to_pending_executions(confluence_result, risk_evaluation)
                    processing_result['recommendation'] = 'PENDING_CONFIRMATION'
                    self.logger.info("   ⏳ Ejecución pendiente de confirmación manual")
            
            return processing_result
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando señal de confluencia: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'recommendation': 'ERROR'
            }
    
    def _execute_entry(self, confluence_result: Dict, risk_evaluation: Dict) -> Dict:
        """
        🚀 Ejecutar entrada en MT5
        
        Args:
            confluence_result: Resultado de confluencia
            risk_evaluation: Evaluación de riesgo
            
        Returns:
            dict: Resultado de la ejecución
        """
        try:
            self.logger.info("🚀 Ejecutando entrada en MT5")
            
            # Incrementar estadísticas
            self.execution_stats['total_attempts'] += 1
            
            # Preparar parámetros de orden
            entry_type = confluence_result.get('entry_recommendation', 'WAIT')
            lot_size = risk_evaluation.get('recommended_lots', 0.01)
            
            # Obtener precio actual
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                raise Exception(f"No se pudo obtener tick para {self.symbol}")
            
            # Determinar tipo de orden y precios
            if entry_type == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
                sl = price - (self.execution_config['stop_loss_pips'] * self._get_pip_value())
                tp = price + (self.execution_config['take_profit_pips'] * self._get_pip_value())
            elif entry_type == 'SELL':
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
                sl = price + (self.execution_config['stop_loss_pips'] * self._get_pip_value())
                tp = price - (self.execution_config['take_profit_pips'] * self._get_pip_value())
            else:
                raise Exception(f"Tipo de entrada inválido: {entry_type}")
            
            # Crear request de orden
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": self.execution_config['slippage'],
                "magic": self.execution_config['magic_number'],
                "comment": f"FVG_Stoch_{confluence_result.get('confluence_strength', 0):.0f}%",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Ejecutar orden
            result = mt5.order_send(request)
            
            execution_result = {
                'success': False,
                'retcode': result.retcode if result else None,
                'deal': result.deal if result else None,
                'order': result.order if result else None,
                'volume': result.volume if result else None,
                'price': result.price if result else None,
                'request': request,
                'result': result._asdict() if result else None,
                'timestamp': datetime.now()
            }
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                execution_result['success'] = True
                self.execution_stats['successful_executions'] += 1
                
                # Registrar posición en risk manager
                position_info = {
                    'deal': result.deal,
                    'order': result.order,
                    'volume': result.volume,
                    'price': result.price
                }
                
                position_id = self.risk_manager.register_fvg_position(
                    confluence_result, 
                    position_info
                )
                
                execution_result['position_id'] = position_id
                
                self.logger.info(f"✅ Entrada ejecutada exitosamente: {entry_type} {lot_size} lotes")
                self.logger.info(f"   Deal: {result.deal}, Precio: {result.price}")
                
            else:
                self.execution_stats['failed_executions'] += 1
                error_msg = f"Retcode: {result.retcode if result else 'None'}"
                self.logger.error(f"❌ Error ejecutando entrada: {error_msg}")
                execution_result['error'] = error_msg
            
            # Guardar en historial
            self.execution_history.append(execution_result)
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"❌ Error en ejecución: {e}")
            self.execution_stats['failed_executions'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def _get_pip_value(self) -> float:
        """📏 Obtener valor de pip para el símbolo"""
        # Valores de pip comunes
        pip_values = {
            'EURUSD': 0.0001,
            'GBPUSD': 0.0001,
            'USDJPY': 0.01,
            'AUDUSD': 0.0001,
            'USDCAD': 0.0001,
            'USDCHF': 0.0001
        }
        
        return pip_values.get(self.symbol, 0.0001)  # Default a 0.0001
    
    def _add_to_pending_executions(self, confluence_result: Dict, risk_evaluation: Dict):
        """⏳ Agregar ejecución a pendientes para confirmación manual"""
        pending_execution = {
            'id': f"PENDING_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'confluence_result': confluence_result,
            'risk_evaluation': risk_evaluation,
            'created_time': datetime.now(),
            'status': 'PENDING',
            'expires_in_minutes': 15  # Expira en 15 minutos
        }
        
        self.pending_executions.append(pending_execution)
        self.logger.info(f"⏳ Ejecución agregada a pendientes: {pending_execution['id']}")
    
    def get_pending_executions(self) -> List[Dict]:
        """📋 Obtener ejecuciones pendientes (no expiradas)"""
        current_time = datetime.now()
        
        # Filtrar solo las no expiradas
        valid_executions = []
        for execution in self.pending_executions:
            created_time = execution.get('created_time', current_time)
            expires_in = execution.get('expires_in_minutes', 15)
            
            if (current_time - created_time).total_seconds() < (expires_in * 60):
                valid_executions.append(execution)
        
        # Actualizar lista con solo las válidas
        self.pending_executions = valid_executions
        
        return valid_executions
    
    def confirm_manual_execution(self, execution_id: str) -> Dict:
        """
        ✅ Confirmar ejecución manual
        
        Args:
            execution_id: ID de la ejecución pendiente
            
        Returns:
            dict: Resultado de la confirmación
        """
        try:
            # Buscar ejecución pendiente
            pending_execution = None
            for execution in self.pending_executions:
                if execution.get('id') == execution_id:
                    pending_execution = execution
                    break
            
            if not pending_execution:
                return {
                    'success': False,
                    'error': f'Ejecución pendiente no encontrada: {execution_id}'
                }
            
            # Verificar que no haya expirado
            current_time = datetime.now()
            created_time = pending_execution.get('created_time', current_time)
            expires_in = pending_execution.get('expires_in_minutes', 15)
            
            if (current_time - created_time).total_seconds() >= (expires_in * 60):
                # Remover de pendientes
                self.pending_executions.remove(pending_execution)
                return {
                    'success': False,
                    'error': 'Ejecución expirada'
                }
            
            # Ejecutar entrada
            confluence_result = pending_execution.get('confluence_result')
            risk_evaluation = pending_execution.get('risk_evaluation')
            
            execution_result = self._execute_entry(confluence_result, risk_evaluation)
            
            # Actualizar estadísticas
            self.execution_stats['manual_confirmations'] += 1
            
            # Remover de pendientes
            self.pending_executions.remove(pending_execution)
            
            self.logger.info(f"✅ Ejecución manual confirmada: {execution_id}")
            
            return {
                'success': True,
                'execution_result': execution_result,
                'confirmed_at': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error confirmando ejecución manual: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_execution_status(self) -> Dict:
        """
        📊 Obtener estado del gestor de ejecución
        
        Returns:
            dict: Estado completo del gestor
        """
        return {
            'symbol': self.symbol,
            'config': self.execution_config.copy(),
            'stats': self.execution_stats.copy(),
            'pending_executions': len(self.get_pending_executions()),
            'recent_executions': len([e for e in self.execution_history if 
                                    (datetime.now() - e.get('timestamp', datetime.now())).total_seconds() < 3600]),
            'risk_summary': self.risk_manager.get_risk_summary(),
            'timestamp': datetime.now()
        }

# Instancia global del gestor de ejecución
entry_execution_manager = None

def get_entry_execution_manager(symbol: str = 'EURUSD'):
    """
    🎯 Obtener gestor de ejecución de entradas
    
    Args:
        symbol: Símbolo para el gestor
        
    Returns:
        EntryExecutionManager: Instancia del gestor
    """
    global entry_execution_manager
    
    if entry_execution_manager is None or entry_execution_manager.symbol != symbol:
        entry_execution_manager = EntryExecutionManager(symbol)
    
    return entry_execution_manager
