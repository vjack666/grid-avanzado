"""
🏢 PISO 4 - GESTIÓN DE RIESGO Y POSICIONES
==========================================

Módulo de gestión de riesgo y posiciones basado en RiskBotMT5 existente,
adaptado para integración con el sistema FVG-Estocástico.

FUNCIONALIDADES:
- Gestión de riesgo basada en RiskBotMT5
- Control de posiciones por confluencias FVG-Estocástico
- Cálculo de lotaje según calidad de señal
- Límites de riesgo dinámicos
- Gestión de múltiples posiciones

AUTOR: Sistema Trading Grid - Piso 4
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import MetaTrader5 as mt5

# Configurar imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "core").absolute()))

from riskbot_mt5 import RiskBotMT5
from logger_manager import LoggerManager

class RiskPositionManager:
    """
    🎯 GESTOR DE RIESGO Y POSICIONES - PISO 4
    Gestión avanzada de riesgo integrada con confluencias FVG-Estocástico
    """
    
    def __init__(self, symbol='EURUSD'):
        self.symbol = symbol
        self.logger = LoggerManager().get_logger('risk_position_manager')
        
        # Configuración base de riesgo (heredada de RiskBotMT5)
        self.risk_config = {
            'risk_target_profit': 100,      # Profit objetivo base
            'max_profit_target': 300,       # Profit máximo antes de cerrar
            'risk_percent': 2.0,            # Porcentaje de riesgo máximo
            'comision_por_lote': 7.0,       # Comisión por lote
            'max_positions': 3,             # Máximo posiciones simultáneas
            'min_lot_size': 0.01,           # Tamaño mínimo de lote
            'max_lot_size': 1.0             # Tamaño máximo de lote
        }
        
        # RiskBot base
        self.risk_bot = RiskBotMT5(
            risk_target_profit=self.risk_config['risk_target_profit'],
            max_profit_target=self.risk_config['max_profit_target'],
            risk_percent=self.risk_config['risk_percent'],
            comision_por_lote=self.risk_config['comision_por_lote']
        )
        
        # Estado de posiciones FVG
        self.fvg_positions = {}  # Posiciones abiertas por confluencias FVG
        self.position_history = []
        
        # Estadísticas
        self.stats = {
            'total_positions': 0,
            'successful_positions': 0,
            'failed_positions': 0,
            'total_profit': 0.0,
            'max_drawdown': 0.0,
            'success_rate': 0.0
        }
    
    def evaluate_position_risk(self, confluence_result: Dict) -> Dict:
        """
        🎯 Evaluar riesgo para nueva posición basada en confluencia
        
        Args:
            confluence_result: Resultado de confluencia FVG-Estocástico
            
        Returns:
            dict: Evaluación de riesgo y recomendación
        """
        try:
            self.logger.info("🎯 Evaluando riesgo para nueva posición")
            
            risk_evaluation = {
                'position_allowed': False,
                'recommended_lots': 0.0,
                'risk_level': 'HIGH',
                'max_loss': 0.0,
                'confluence_factor': 0.0,
                'reason': ''
            }
            
            # 1. Verificar estado actual del account
            account_status = self._check_account_status()
            if not account_status['can_trade']:
                risk_evaluation['reason'] = account_status['reason']
                return risk_evaluation
            
            # 2. Verificar límite de posiciones
            if not self._check_position_limits():
                risk_evaluation['reason'] = 'Límite máximo de posiciones alcanzado'
                return risk_evaluation
            
            # 3. Calcular factor de confluencia
            confluence_strength = confluence_result.get('confluence_strength', 0)
            confluence_factor = self._calculate_confluence_factor(confluence_strength)
            risk_evaluation['confluence_factor'] = confluence_factor
            
            # 4. Calcular lotaje recomendado
            recommended_lots = self._calculate_lot_size(confluence_result, confluence_factor)
            risk_evaluation['recommended_lots'] = recommended_lots
            
            # 5. Calcular pérdida máxima
            account_balance = self.risk_bot.get_account_balance()
            max_loss = account_balance * (self.risk_config['risk_percent'] / 100)
            risk_evaluation['max_loss'] = max_loss
            
            # 6. Determinar nivel de riesgo
            risk_level = self._determine_risk_level(confluence_strength, account_status)
            risk_evaluation['risk_level'] = risk_level
            
            # 7. Decisión final
            if (confluence_strength >= 70 and 
                recommended_lots >= self.risk_config['min_lot_size'] and
                risk_level in ['LOW', 'MEDIUM']):
                
                risk_evaluation['position_allowed'] = True
                risk_evaluation['reason'] = f'Confluencia fuerte ({confluence_strength}%) - Riesgo {risk_level}'
            else:
                risk_evaluation['reason'] = f'Confluencia débil ({confluence_strength}%) o riesgo alto'
            
            self.logger.info(f"   Posición permitida: {risk_evaluation['position_allowed']}")
            self.logger.info(f"   Lotaje recomendado: {risk_evaluation['recommended_lots']}")
            self.logger.info(f"   Nivel de riesgo: {risk_evaluation['risk_level']}")
            
            return risk_evaluation
            
        except Exception as e:
            self.logger.error(f"❌ Error evaluando riesgo: {e}")
            return {
                'position_allowed': False,
                'recommended_lots': 0.0,
                'risk_level': 'VERY_HIGH',
                'reason': f'Error en evaluación: {e}'
            }
    
    def _check_account_status(self) -> Dict:
        """🏦 Verificar estado de la cuenta"""
        try:
            # Usar RiskBot para verificar estado
            risk_status = self.risk_bot.check_and_act()
            
            account_info = {
                'can_trade': True,
                'balance': self.risk_bot.get_account_balance(),
                'risk_status': risk_status,
                'reason': ''
            }
            
            # Verificar condiciones de riesgo
            if risk_status == 'riesgo':
                account_info['can_trade'] = False
                account_info['reason'] = 'Límite de riesgo alcanzado'
            elif risk_status == 'objetivo_maximo':
                account_info['can_trade'] = False
                account_info['reason'] = 'Objetivo máximo de profit alcanzado'
            elif account_info['balance'] <= 0:
                account_info['can_trade'] = False
                account_info['reason'] = 'Balance insuficiente'
            
            return account_info
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando cuenta: {e}")
            return {
                'can_trade': False,
                'balance': 0.0,
                'risk_status': 'error',
                'reason': f'Error verificando cuenta: {e}'
            }
    
    def _check_position_limits(self) -> bool:
        """📊 Verificar límites de posiciones"""
        try:
            current_positions = self.risk_bot.get_open_positions()
            position_count = len(current_positions) if current_positions else 0
            
            # Filtrar posiciones del símbolo actual
            symbol_positions = [pos for pos in current_positions if pos.symbol == self.symbol]
            symbol_position_count = len(symbol_positions)
            
            # Verificar límites
            if position_count >= self.risk_config['max_positions']:
                self.logger.warning(f"⚠️ Límite total de posiciones alcanzado: {position_count}")
                return False
            
            if symbol_position_count >= 2:  # Máximo 2 posiciones por símbolo
                self.logger.warning(f"⚠️ Límite de posiciones para {self.symbol}: {symbol_position_count}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando límites: {e}")
            return False
    
    def _calculate_confluence_factor(self, confluence_strength: float) -> float:
        """🔢 Calcular factor de confluencia para ajustar riesgo"""
        if confluence_strength >= 90:
            return 1.0  # Máximo factor
        elif confluence_strength >= 80:
            return 0.8
        elif confluence_strength >= 70:
            return 0.6
        elif confluence_strength >= 60:
            return 0.4
        else:
            return 0.2  # Mínimo factor
    
    def _calculate_lot_size(self, confluence_result: Dict, confluence_factor: float) -> float:
        """📏 Calcular tamaño de lote basado en confluencia y riesgo"""
        try:
            # Balance actual
            balance = self.risk_bot.get_account_balance()
            if balance <= 0:
                return 0.0
            
            # Riesgo base (2% del balance)
            base_risk = balance * (self.risk_config['risk_percent'] / 100)
            
            # Ajustar por factor de confluencia
            adjusted_risk = base_risk * confluence_factor
            
            # Calcular lotaje base (simplificado)
            # Asumiendo que 1 lote = ~$10 por pip para EURUSD
            pip_value = 10.0  # Valor aproximado por pip para 1 lote
            stop_loss_pips = 20  # Stop loss promedio en pips
            
            calculated_lots = adjusted_risk / (pip_value * stop_loss_pips)
            
            # Aplicar límites
            calculated_lots = max(self.risk_config['min_lot_size'], calculated_lots)
            calculated_lots = min(self.risk_config['max_lot_size'], calculated_lots)
            
            # Redondear a 2 decimales
            return round(calculated_lots, 2)
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando lotaje: {e}")
            return self.risk_config['min_lot_size']
    
    def _determine_risk_level(self, confluence_strength: float, account_status: Dict) -> str:
        """🎯 Determinar nivel de riesgo"""
        # Factor de confluencia
        if confluence_strength >= 90:
            confluence_risk = 'VERY_LOW'
        elif confluence_strength >= 80:
            confluence_risk = 'LOW'
        elif confluence_strength >= 70:
            confluence_risk = 'MEDIUM'
        elif confluence_strength >= 60:
            confluence_risk = 'HIGH'
        else:
            confluence_risk = 'VERY_HIGH'
        
        # Factor de cuenta
        risk_status = account_status.get('risk_status', 'ok')
        if risk_status == 'objetivo_parcial':
            account_risk = 'MEDIUM'
        elif risk_status == 'riesgo':
            account_risk = 'VERY_HIGH'
        else:
            account_risk = 'LOW'
        
        # Combinar factores (usar el más restrictivo)
        risk_levels = ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']
        
        confluence_index = risk_levels.index(confluence_risk)
        account_index = risk_levels.index(account_risk)
        
        final_index = max(confluence_index, account_index)
        
        return risk_levels[final_index]
    
    def register_fvg_position(self, confluence_result: Dict, position_info: Dict) -> str:
        """
        📝 Registrar posición abierta por confluencia FVG
        
        Args:
            confluence_result: Resultado de confluencia
            position_info: Información de la posición MT5
            
        Returns:
            str: ID de registro de la posición
        """
        try:
            position_id = f"FVG_{self.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            fvg_position = {
                'id': position_id,
                'symbol': self.symbol,
                'confluence_result': confluence_result,
                'position_info': position_info,
                'open_time': datetime.now(),
                'status': 'OPEN',
                'fvg_quality': confluence_result.get('fvg_signal', {}).get('quality_score', 0),
                'confluence_strength': confluence_result.get('confluence_strength', 0),
                'entry_recommendation': confluence_result.get('entry_recommendation', 'WAIT')
            }
            
            self.fvg_positions[position_id] = fvg_position
            self.stats['total_positions'] += 1
            
            self.logger.info(f"📝 Posición FVG registrada: {position_id}")
            
            return position_id
            
        except Exception as e:
            self.logger.error(f"❌ Error registrando posición FVG: {e}")
            return ""
    
    def get_risk_summary(self) -> Dict:
        """
        📊 Obtener resumen de gestión de riesgo
        
        Returns:
            dict: Resumen completo de riesgo
        """
        try:
            # Estado del RiskBot
            risk_status = self.risk_bot.check_and_act()
            total_profit, total_commission, profit_neto, total_lots = self.risk_bot.get_total_profit_and_lots()
            balance = self.risk_bot.get_account_balance()
            
            # Posiciones actuales
            current_positions = self.risk_bot.get_open_positions()
            position_count = len(current_positions) if current_positions else 0
            
            # Calcular tasa de éxito
            if self.stats['total_positions'] > 0:
                self.stats['success_rate'] = (self.stats['successful_positions'] / self.stats['total_positions']) * 100
            
            summary = {
                'account': {
                    'balance': balance,
                    'profit_neto': profit_neto,
                    'total_lots': total_lots,
                    'risk_status': risk_status
                },
                'positions': {
                    'current_count': position_count,
                    'max_allowed': self.risk_config['max_positions'],
                    'fvg_positions': len(self.fvg_positions)
                },
                'risk_config': self.risk_config.copy(),
                'stats': self.stats.copy(),
                'timestamp': datetime.now()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo resumen: {e}")
            return {'error': str(e)}

# Instancia global del gestor de riesgo
risk_position_manager = None

def get_risk_position_manager(symbol: str = 'EURUSD'):
    """
    🎯 Obtener gestor de riesgo y posiciones
    
    Args:
        symbol: Símbolo para el gestor
        
    Returns:
        RiskPositionManager: Instancia del gestor
    """
    global risk_position_manager
    
    if risk_position_manager is None or risk_position_manager.symbol != symbol:
        risk_position_manager = RiskPositionManager(symbol)
    
    return risk_position_manager
