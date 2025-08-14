"""
🎯 DAILY CYCLE MANAGER - PISO 4 OPERACIONES AVANZADAS
====================================================

Gestor del ciclo completo de 24 horas con objetivos específicos
Objetivo: +3% ganancia / -2% riesgo máximo en 3 trades distribuidos

FUNCIONALIDADES:
- Tracking objetivo diario +3% / -2% riesgo máximo
- Control de trades por sesión (Asia: 1, London: 2, NY: 1)
- Gestión de capital progresiva
- Reset automático cada 24h
- Estadísticas y reporting

AUTOR: Trading Grid System - Piso 4
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from enum import Enum

# Configurar imports del proyecto
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "core").absolute()))

from logger_manager import LoggerManager

class CycleStatus(Enum):
    """Estados del ciclo diario"""
    ACTIVE = "ACTIVE"               # Ciclo en progreso
    OBJECTIVE_ACHIEVED = "OBJECTIVE_ACHIEVED"  # +3% alcanzado
    RISK_LIMIT_HIT = "RISK_LIMIT_HIT"         # -2% alcanzado
    COMPLETED = "COMPLETED"         # 24h completadas
    RESET_PENDING = "RESET_PENDING" # Esperando reset

class DailyCycleManager:
    """
    🎯 GESTOR DE CICLO DIARIO 24H
    
    Funcionalidades:
    - Tracking objetivo +3% / riesgo -2%
    - Control total de trades (máximo 3 por día)
    - Gestión de capital por sesión
    - Reinversión inteligente de ganancias
    - Protección contra over-trading
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        self.logger = LoggerManager().get_logger('daily_cycle_manager')
        
        # Configuración del ciclo
        self.cycle_config = {
            'daily_target_percent': 3.0,      # +3% objetivo diario
            'daily_risk_limit_percent': -2.0, # -2% riesgo máximo
            'max_daily_trades': 3,             # Máximo 3 trades por día
            'compound_enabled': True,          # Reinversión de ganancias
            'auto_reset_enabled': True,        # Reset automático 24h
            'emergency_stop_enabled': True     # Stop de emergencia
        }
        
        # Estado del ciclo actual
        self.cycle_start_time = datetime.now()
        self.cycle_status = CycleStatus.ACTIVE
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        
        # Tracking de performance
        self.cycle_stats = {
            'start_balance': initial_balance,
            'current_balance': initial_balance,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl_usd': 0.0,
            'total_pnl_percent': 0.0,
            'max_profit_reached': 0.0,
            'max_drawdown': 0.0,
            'trades_by_session': {
                'ASIA': [],
                'LONDON': [],
                'NEW_YORK': []
            },
            'daily_objective_achieved': False,
            'risk_limit_breached': False
        }
        
        # Control de sesiones
        self.session_allocation = {
            'ASIA': {
                'max_trades': 1,
                'risk_allocation_percent': 0.7,  # 0.7% de cuenta
                'target_allocation_percent': 1.0  # 1.0% objetivo
            },
            'LONDON': {
                'max_trades': 2,                  # Sesión principal
                'risk_allocation_percent': 1.0,  # 1.0% de cuenta
                'target_allocation_percent': 1.5 # 1.5% objetivo
            },
            'NEW_YORK': {
                'max_trades': 1,
                'risk_allocation_percent': 0.8,  # 0.8% de cuenta
                'target_allocation_percent': 0.8 # 0.8% objetivo
            }
        }
        
        # Historial de ciclos
        self.cycle_history = []
        
        self.logger.info("🎯 DailyCycleManager inicializado - Balance: $%.2f", initial_balance)
        self.logger.info("   Objetivo diario: +%.1f%% / Riesgo límite: %.1f%%", 
                        self.cycle_config['daily_target_percent'],
                        self.cycle_config['daily_risk_limit_percent'])
    
    def can_execute_trade(self, session: str, trade_risk_percent: float) -> Dict[str, Any]:
        """
        🎯 Verificar si se puede ejecutar trade según límites del ciclo
        
        Args:
            session: Sesión de trading ('ASIA', 'LONDON', 'NEW_YORK')
            trade_risk_percent: Riesgo del trade como % de cuenta
            
        Returns:
            dict: Resultado de la evaluación
        """
        try:
            result = {
                'can_execute': False,
                'reason': '',
                'remaining_risk_budget': 0.0,
                'remaining_trades': 0,
                'session_trades_remaining': 0,
                'recommended_risk_percent': 0.0
            }
            
            # Verificar estado del ciclo
            if self.cycle_status != CycleStatus.ACTIVE:
                result['reason'] = f'Ciclo en estado: {self.cycle_status.value}'
                return result
            
            # Verificar límite total de trades diarios
            remaining_trades = self.cycle_config['max_daily_trades'] - self.cycle_stats['total_trades']
            if remaining_trades <= 0:
                result['reason'] = f'Límite diario de trades alcanzado ({self.cycle_stats["total_trades"]}/{self.cycle_config["max_daily_trades"]})'
                self.cycle_status = CycleStatus.COMPLETED
                return result
            
            result['remaining_trades'] = remaining_trades
            
            # Verificar límite de trades por sesión
            session_trades = len(self.cycle_stats['trades_by_session'].get(session, []))
            session_max = self.session_allocation.get(session, {}).get('max_trades', 0)
            
            if session_trades >= session_max:
                result['reason'] = f'Límite de trades de {session} alcanzado ({session_trades}/{session_max})'
                return result
            
            result['session_trades_remaining'] = session_max - session_trades
            
            # Verificar riesgo acumulado vs límite diario
            current_loss = min(0, self.cycle_stats['total_pnl_percent'])  # Solo pérdidas
            risk_used = abs(current_loss)
            risk_limit = abs(self.cycle_config['daily_risk_limit_percent'])
            remaining_risk = risk_limit - risk_used
            
            if remaining_risk <= 0.1:  # Margen de seguridad 0.1%
                result['reason'] = f'Límite de riesgo diario alcanzado ({risk_used:.1f}%/{risk_limit:.1f}%)'
                self.cycle_status = CycleStatus.RISK_LIMIT_HIT
                return result
            
            result['remaining_risk_budget'] = remaining_risk
            
            # Verificar si el trade propuesto excede el riesgo restante
            if trade_risk_percent > remaining_risk:
                result['reason'] = f'Trade excede riesgo disponible ({trade_risk_percent:.1f}% > {remaining_risk:.1f}%)'
                result['recommended_risk_percent'] = max(0.1, remaining_risk * 0.8)  # 80% del disponible
                return result
            
            # Verificar asignación de riesgo por sesión
            session_risk_limit = self.session_allocation.get(session, {}).get('risk_allocation_percent', 1.0)
            if trade_risk_percent > session_risk_limit:
                result['reason'] = f'Trade excede límite de {session} ({trade_risk_percent:.1f}% > {session_risk_limit:.1f}%)'
                result['recommended_risk_percent'] = session_risk_limit
                return result
            
            # Verificar si ya se alcanzó el objetivo diario
            if self.cycle_stats['total_pnl_percent'] >= self.cycle_config['daily_target_percent']:
                result['reason'] = f'Objetivo diario ya alcanzado ({self.cycle_stats["total_pnl_percent"]:.1f}% >= {self.cycle_config["daily_target_percent"]:.1f}%)'
                self.cycle_status = CycleStatus.OBJECTIVE_ACHIEVED
                return result
            
            # Todo OK - trade permitido
            result['can_execute'] = True
            result['reason'] = f'Trade autorizado en {session} - Riesgo: {trade_risk_percent:.1f}%'
            result['recommended_risk_percent'] = trade_risk_percent
            
            return result
            
        except Exception as e:
            self.logger.error("❌ Error evaluando trade: %s", e)
            return {
                'can_execute': False,
                'reason': f'Error: {e}'
            }
    
    def record_trade_result(self, session: str, trade_data: Dict[str, Any]) -> bool:
        """
        📊 Registrar resultado de trade ejecutado
        
        Args:
            session: Sesión donde se ejecutó
            trade_data: Datos del trade
            
        Returns:
            bool: True si se registró correctamente
        """
        try:
            # Extraer datos del trade
            pnl_percent = trade_data.get('pnl_percent', 0.0)
            pnl_usd = trade_data.get('pnl_usd', 0.0)
            
            # Si no se proporciona PnL en USD, calcularlo
            if pnl_usd == 0.0 and pnl_percent != 0.0:
                pnl_usd = (pnl_percent / 100) * self.current_balance
            
            # Actualizar balance actual
            self.current_balance += pnl_usd
            
            # Actualizar estadísticas
            self.cycle_stats['current_balance'] = self.current_balance
            self.cycle_stats['total_trades'] += 1
            self.cycle_stats['total_pnl_usd'] += pnl_usd
            self.cycle_stats['total_pnl_percent'] += pnl_percent
            
            # Clasificar trade
            if pnl_percent > 0:
                self.cycle_stats['winning_trades'] += 1
            else:
                self.cycle_stats['losing_trades'] += 1
            
            # Actualizar máximos
            if self.cycle_stats['total_pnl_percent'] > self.cycle_stats['max_profit_reached']:
                self.cycle_stats['max_profit_reached'] = self.cycle_stats['total_pnl_percent']
            
            # Calcular drawdown desde máximo
            drawdown = self.cycle_stats['max_profit_reached'] - self.cycle_stats['total_pnl_percent']
            if drawdown > self.cycle_stats['max_drawdown']:
                self.cycle_stats['max_drawdown'] = drawdown
            
            # Registrar en sesión específica
            trade_record = {
                'timestamp': datetime.now(),
                'symbol': trade_data.get('symbol', ''),
                'direction': trade_data.get('direction', ''),
                'lot_size': trade_data.get('lot_size', 0),
                'pnl_percent': pnl_percent,
                'pnl_usd': pnl_usd,
                'quality_score': trade_data.get('quality_score', 0),
                'balance_after': self.current_balance
            }
            
            self.cycle_stats['trades_by_session'][session].append(trade_record)
            
            self.logger.info("📊 Trade registrado en %s: %.2f%% (%.2f USD)", 
                           session, pnl_percent, pnl_usd)
            self.logger.info("   Balance actualizado: $%.2f", self.current_balance)
            self.logger.info("   P&L ciclo: %.2f%% ($%.2f)", 
                           self.cycle_stats['total_pnl_percent'], 
                           self.cycle_stats['total_pnl_usd'])
            
            # Verificar objetivos del ciclo
            self._check_cycle_objectives()
            
            return True
            
        except Exception as e:
            self.logger.error("❌ Error registrando trade: %s", e)
            return False
    
    def _check_cycle_objectives(self):
        """🎯 Verificar objetivos y límites del ciclo"""
        try:
            current_pnl = self.cycle_stats['total_pnl_percent']
            
            # Verificar objetivo alcanzado
            if current_pnl >= self.cycle_config['daily_target_percent']:
                if not self.cycle_stats['daily_objective_achieved']:
                    self.cycle_stats['daily_objective_achieved'] = True
                    self.cycle_status = CycleStatus.OBJECTIVE_ACHIEVED
                    self.logger.info("🎯 OBJETIVO DIARIO ALCANZADO: %.2f%% >= %.1f%%", 
                                   current_pnl, self.cycle_config['daily_target_percent'])
            
            # Verificar límite de riesgo
            if current_pnl <= self.cycle_config['daily_risk_limit_percent']:
                if not self.cycle_stats['risk_limit_breached']:
                    self.cycle_stats['risk_limit_breached'] = True
                    self.cycle_status = CycleStatus.RISK_LIMIT_HIT
                    self.logger.warning("🚨 LÍMITE DE RIESGO ALCANZADO: %.2f%% <= %.1f%%", 
                                      current_pnl, self.cycle_config['daily_risk_limit_percent'])
            
        except Exception as e:
            self.logger.error("❌ Error verificando objetivos: %s", e)
    
    def get_cycle_summary(self) -> Dict[str, Any]:
        """
        📈 Obtener resumen completo del ciclo actual
        
        Returns:
            dict: Estadísticas completas del ciclo
        """
        try:
            cycle_duration = datetime.now() - self.cycle_start_time
            
            summary = {
                'cycle_start': self.cycle_start_time,
                'cycle_duration': str(cycle_duration).split('.')[0],
                'cycle_status': self.cycle_status.value,
                'initial_balance': self.cycle_stats['start_balance'],
                'current_balance': self.cycle_stats['current_balance'],
                'total_pnl_usd': self.cycle_stats['total_pnl_usd'],
                'total_pnl_percent': self.cycle_stats['total_pnl_percent'],
                'daily_target': self.cycle_config['daily_target_percent'],
                'daily_risk_limit': self.cycle_config['daily_risk_limit_percent'],
                'objective_achieved': self.cycle_stats['daily_objective_achieved'],
                'risk_limit_breached': self.cycle_stats['risk_limit_breached'],
                'total_trades': self.cycle_stats['total_trades'],
                'winning_trades': self.cycle_stats['winning_trades'],
                'losing_trades': self.cycle_stats['losing_trades'],
                'win_rate': 0.0,
                'max_profit': self.cycle_stats['max_profit_reached'],
                'max_drawdown': self.cycle_stats['max_drawdown'],
                'trades_remaining': self.cycle_config['max_daily_trades'] - self.cycle_stats['total_trades'],
                'sessions': {}
            }
            
            # Calcular win rate
            if self.cycle_stats['total_trades'] > 0:
                summary['win_rate'] = (self.cycle_stats['winning_trades'] / self.cycle_stats['total_trades']) * 100
            
            # Estadísticas por sesión
            for session, trades in self.cycle_stats['trades_by_session'].items():
                session_pnl = sum(trade['pnl_percent'] for trade in trades)
                session_wins = sum(1 for trade in trades if trade['pnl_percent'] > 0)
                
                summary['sessions'][session] = {
                    'trades_executed': len(trades),
                    'max_trades': self.session_allocation[session]['max_trades'],
                    'trades_remaining': self.session_allocation[session]['max_trades'] - len(trades),
                    'session_pnl_percent': session_pnl,
                    'session_wins': session_wins,
                    'session_losses': len(trades) - session_wins,
                    'risk_allocation': self.session_allocation[session]['risk_allocation_percent'],
                    'target_allocation': self.session_allocation[session]['target_allocation_percent']
                }
            
            return summary
            
        except Exception as e:
            self.logger.error("❌ Error generando resumen: %s", e)
            return {}
    
    def reset_cycle(self, new_balance: Optional[float] = None) -> bool:
        """
        🔄 Reiniciar ciclo de 24 horas
        
        Args:
            new_balance: Nuevo balance inicial (si no se proporciona, usa balance actual)
            
        Returns:
            bool: True si se reinició correctamente
        """
        try:
            # Guardar ciclo anterior en historial
            cycle_summary = self.get_cycle_summary()
            cycle_summary['end_time'] = datetime.now()
            self.cycle_history.append(cycle_summary)
            
            self.logger.info("🔄 Reiniciando ciclo diario - Balance anterior: $%.2f", 
                           self.current_balance)
            
            # Determinar nuevo balance inicial
            if new_balance is not None:
                self.initial_balance = new_balance
                self.current_balance = new_balance
            else:
                # Usar balance actual como nuevo inicial (compound effect)
                if self.cycle_config['compound_enabled']:
                    self.initial_balance = self.current_balance
                else:
                    # Reset a balance original
                    self.current_balance = self.initial_balance
            
            # Reiniciar estadísticas
            self.cycle_start_time = datetime.now()
            self.cycle_status = CycleStatus.ACTIVE
            
            self.cycle_stats = {
                'start_balance': self.initial_balance,
                'current_balance': self.current_balance,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl_usd': 0.0,
                'total_pnl_percent': 0.0,
                'max_profit_reached': 0.0,
                'max_drawdown': 0.0,
                'trades_by_session': {
                    'ASIA': [],
                    'LONDON': [],
                    'NEW_YORK': []
                },
                'daily_objective_achieved': False,
                'risk_limit_breached': False
            }
            
            self.logger.info("✅ Nuevo ciclo iniciado - Balance inicial: $%.2f", 
                           self.initial_balance)
            self.logger.info("   Objetivo: +%.1f%% / Límite riesgo: %.1f%%", 
                           self.cycle_config['daily_target_percent'],
                           self.cycle_config['daily_risk_limit_percent'])
            
            return True
            
        except Exception as e:
            self.logger.error("❌ Error reiniciando ciclo: %s", e)
            return False
    
    def should_auto_reset(self) -> bool:
        """
        ⏰ Verificar si el ciclo debe reiniciarse automáticamente
        
        Returns:
            bool: True si debe reiniciarse
        """
        try:
            if not self.cycle_config['auto_reset_enabled']:
                return False
            
            cycle_duration = datetime.now() - self.cycle_start_time
            
            # Reset después de 24 horas
            if cycle_duration >= timedelta(hours=24):
                return True
            
            # Reset si se alcanzó objetivo y han pasado al menos 12 horas
            if (self.cycle_status == CycleStatus.OBJECTIVE_ACHIEVED and 
                cycle_duration >= timedelta(hours=12)):
                return True
            
            # Reset inmediato si se alcanzó límite de riesgo
            if self.cycle_status == CycleStatus.RISK_LIMIT_HIT:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error("❌ Error verificando auto-reset: %s", e)
            return False
    
    def get_risk_allocation_for_session(self, session: str) -> float:
        """
        🛡️ Obtener asignación de riesgo para sesión específica
        
        Args:
            session: Sesión de trading
            
        Returns:
            float: Porcentaje de riesgo asignado
        """
        return self.session_allocation.get(session, {}).get('risk_allocation_percent', 1.0)
    
    def get_target_allocation_for_session(self, session: str) -> float:
        """
        🎯 Obtener objetivo de ganancia para sesión específica
        
        Args:
            session: Sesión de trading
            
        Returns:
            float: Porcentaje objetivo de ganancia
        """
        return self.session_allocation.get(session, {}).get('target_allocation_percent', 1.0)


def main():
    """Función de prueba del DailyCycleManager"""
    print("🎯 Testing DailyCycleManager - Piso 4")
    print("=" * 50)
    
    # Crear manager con balance inicial
    cycle_manager = DailyCycleManager(initial_balance=10000.0)
    
    # Simular algunos trades
    print("\n📊 Simulando trades del ciclo:")
    
    # Trade 1 - Asia (ganador)
    trade_check = cycle_manager.can_execute_trade('ASIA', 0.7)
    print(f"✅ Trade Asia permitido: {trade_check['can_execute']}")
    
    if trade_check['can_execute']:
        cycle_manager.record_trade_result('ASIA', {
            'pnl_percent': 1.2,
            'symbol': 'USDJPY',
            'direction': 'BUY',
            'lot_size': 0.1,
            'quality_score': 8.1
        })
    
    # Trade 2 - London (perdedor)
    trade_check = cycle_manager.can_execute_trade('LONDON', 1.0)
    print(f"✅ Trade London permitido: {trade_check['can_execute']}")
    
    if trade_check['can_execute']:
        cycle_manager.record_trade_result('LONDON', {
            'pnl_percent': -0.8,
            'symbol': 'EURUSD',
            'direction': 'SELL',
            'lot_size': 0.15,
            'quality_score': 7.3
        })
    
    # Trade 3 - New York (ganador grande)
    trade_check = cycle_manager.can_execute_trade('NEW_YORK', 0.8)
    print(f"✅ Trade NY permitido: {trade_check['can_execute']}")
    
    if trade_check['can_execute']:
        cycle_manager.record_trade_result('NEW_YORK', {
            'pnl_percent': 2.1,
            'symbol': 'GBPUSD',
            'direction': 'BUY',
            'lot_size': 0.12,
            'quality_score': 8.7
        })
    
    # Mostrar resumen del ciclo
    print("\n📈 RESUMEN DEL CICLO:")
    summary = cycle_manager.get_cycle_summary()
    
    print(f"💰 Balance inicial: ${summary['initial_balance']:,.2f}")
    print(f"💰 Balance actual: ${summary['current_balance']:,.2f}")
    print(f"📊 P&L total: {summary['total_pnl_percent']:.2f}% (${summary['total_pnl_usd']:,.2f})")
    print(f"🎯 Objetivo diario: {summary['daily_target']:.1f}%")
    print(f"🏆 ¿Objetivo alcanzado?: {summary['objective_achieved']}")
    print(f"📈 Win Rate: {summary['win_rate']:.1f}%")
    print(f"📊 Trades: {summary['total_trades']} (W:{summary['winning_trades']} L:{summary['losing_trades']})")
    
    # Detalles por sesión
    print("\n📋 DETALLES POR SESIÓN:")
    for session, data in summary['sessions'].items():
        print(f"{session}: {data['trades_executed']}/{data['max_trades']} trades, "
              f"P&L: {data['session_pnl_percent']:.2f}%")


if __name__ == "__main__":
    main()
