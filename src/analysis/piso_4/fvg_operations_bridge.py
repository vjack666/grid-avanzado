"""
🔗 FVG OPERATIONS BRIDGE - PISO 4 INTEGRACIÓN
============================================

Puente de integración entre Piso 3 (FVG IA) y Piso 4 (Operaciones Avanzadas)
Combina análisis FVG inteligente con gestión temporal y ciclos de 24h

FUNCIONALIDADES:
- Integración FVGTradingOffice con SessionManager
- Filtros de sesión aplicados a señales FVG
- Gestión de riesgo por horario y ciclo
- Optimización temporal de trades FVG
- Reporting unificado Piso 3+4

OBJETIVO INTEGRADO:
- 3 trades FVG de alta calidad en 24h
- +3% ganancia / -2% riesgo máximo
- Distribución inteligente por sesiones

AUTOR: Trading Grid System - Piso 4
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any, Tuple

# Configurar imports del proyecto
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "analysis" / "piso_3" / "trading").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis" / "piso_4").absolute()))

# Imports simplificados para demo
# from fvg_trading_office import FVGTradingOffice
# from session_manager import SessionManager  
# from daily_cycle_manager import DailyCycleManager

class FVGOperationsBridge:
    """
    🔗 PUENTE DE OPERACIONES FVG AVANZADAS
    
    Integra análisis FVG (Piso 3) con gestión temporal (Piso 4)
    para trading optimizado de 24 horas
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        # Configuración del bridge
        self.bridge_config = {
            'fvg_quality_by_session': {
                'ASIA': 7.5,      # Calidad mínima más alta para Asia
                'LONDON': 7.0,    # Calidad estándar para London  
                'NEW_YORK': 7.5   # Calidad alta para NY
            },
            'max_signals_per_session': {
                'ASIA': 1,        # Máximo 1 señal en Asia
                'LONDON': 3,      # Máximo 3 señales en London (2 trades)
                'NEW_YORK': 2     # Máximo 2 señales en NY (1 trade)
            },
            'session_symbols_priority': {
                'ASIA': ['USDJPY', 'AUDUSD', 'EURJPY', 'NZDUSD'],
                'LONDON': ['EURUSD', 'GBPUSD', 'EURGBP', 'EURJPY'],
                'NEW_YORK': ['EURUSD', 'GBPUSD', 'USDCAD', 'USDCHF']
            },
            'confluence_boost_by_session': {
                'ASIA': 1.1,      # 10% boost confluencia en Asia
                'LONDON': 1.0,    # Sin boost en London (alta actividad)
                'NEW_YORK': 1.2   # 20% boost confluencia en NY
            }
        }
        
        # Estado de integración
        self.integration_stats = {
            'fvg_signals_generated': 0,
            'fvg_signals_filtered_by_session': 0,
            'fvg_signals_filtered_by_cycle': 0,
            'fvg_trades_executed': 0,
            'session_performance': {
                'ASIA': {'signals': 0, 'trades': 0, 'pnl': 0.0},
                'LONDON': {'signals': 0, 'trades': 0, 'pnl': 0.0},
                'NEW_YORK': {'signals': 0, 'trades': 0, 'pnl': 0.0}
            }
        }
        
        # Simulación de componentes (en producción serían instancias reales)
        self.simulated_state = {
            'current_session': 'LONDON',
            'cycle_trades': 1,
            'cycle_pnl': 0.3,
            'session_trades': {'ASIA': 1, 'LONDON': 0, 'NEW_YORK': 0}
        }
        
        print("🔗 FVG Operations Bridge inicializado")
        print(f"   Configuración: 3 trades/24h, +3%/-2% objetivo")
    
    def evaluate_fvg_signal_for_session(self, fvg_signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 Evaluar señal FVG según contexto de sesión y ciclo
        
        Args:
            fvg_signal: Señal FVG del Piso 3
            {
                'symbol': str,
                'direction': str,
                'quality_score': float,
                'confluence_strength': float,
                'ml_confidence': float,
                'fvg_size_pips': float,
                'session_detected': str
            }
            
        Returns:
            dict: Evaluación completa con recomendaciones
        """
        try:
            evaluation = {
                'signal_approved': False,
                'session_optimal': False,
                'quality_adequate': False,
                'cycle_capacity_ok': False,
                'recommended_action': 'REJECT',
                'reason': '',
                'adjusted_risk_percent': 0.0,
                'priority_score': 0.0,
                'timing_score': 0.0
            }
            
            symbol = fvg_signal.get('symbol', '')
            quality_score = fvg_signal.get('quality_score', 0)
            session = self.simulated_state['current_session']
            
            # 1. Verificar si estamos en sesión activa
            if session == 'INACTIVE':
                evaluation['reason'] = 'Fuera de horario de trading'
                return evaluation
            
            # 2. Verificar calidad mínima para la sesión
            min_quality = self.bridge_config['fvg_quality_by_session'].get(session, 7.0)
            evaluation['quality_adequate'] = quality_score >= min_quality
            
            if not evaluation['quality_adequate']:
                evaluation['reason'] = f'Calidad insuficiente para {session}: {quality_score:.1f} < {min_quality:.1f}'
                return evaluation
            
            # 3. Verificar símbolo prioritario para la sesión
            priority_symbols = self.bridge_config['session_symbols_priority'].get(session, [])
            evaluation['session_optimal'] = symbol in priority_symbols
            
            # 4. Verificar capacidad del ciclo
            max_cycle_trades = 3
            current_cycle_trades = self.simulated_state['cycle_trades']
            evaluation['cycle_capacity_ok'] = current_cycle_trades < max_cycle_trades
            
            if not evaluation['cycle_capacity_ok']:
                evaluation['reason'] = f'Límite de ciclo alcanzado: {current_cycle_trades}/{max_cycle_trades}'
                return evaluation
            
            # 5. Verificar capacidad de la sesión
            max_session_trades = {'ASIA': 1, 'LONDON': 2, 'NEW_YORK': 1}
            current_session_trades = self.simulated_state['session_trades'].get(session, 0)
            session_capacity_ok = current_session_trades < max_session_trades.get(session, 1)
            
            if not session_capacity_ok:
                evaluation['reason'] = f'Límite de {session} alcanzado: {current_session_trades}/{max_session_trades.get(session, 1)}'
                return evaluation
            
            # 6. Calcular scores de prioridad y timing
            evaluation['priority_score'] = self._calculate_priority_score(fvg_signal, session)
            evaluation['timing_score'] = self._calculate_timing_score(fvg_signal, session)
            
            # 7. Calcular riesgo ajustado para la sesión
            base_risk = {'ASIA': 0.7, 'LONDON': 1.0, 'NEW_YORK': 0.8}
            session_risk = base_risk.get(session, 1.0)
            
            # Ajustar por calidad y confluencia
            quality_factor = min(1.2, quality_score / 7.0)  # Max 1.2x por calidad
            confluence_boost = self.bridge_config['confluence_boost_by_session'].get(session, 1.0)
            
            evaluation['adjusted_risk_percent'] = session_risk * quality_factor * confluence_boost
            evaluation['adjusted_risk_percent'] = min(1.5, evaluation['adjusted_risk_percent'])  # Cap máximo
            
            # 8. Decisión final
            min_combined_score = 7.0  # Score mínimo combinado
            combined_score = (evaluation['priority_score'] + evaluation['timing_score']) / 2
            
            if (evaluation['quality_adequate'] and 
                evaluation['cycle_capacity_ok'] and 
                combined_score >= min_combined_score):
                
                evaluation['signal_approved'] = True
                evaluation['recommended_action'] = 'EXECUTE'
                evaluation['reason'] = f'Señal FVG aprobada para {session} - Score: {combined_score:.1f}'
            else:
                evaluation['recommended_action'] = 'HOLD' if combined_score >= 6.0 else 'REJECT'
                evaluation['reason'] = f'Score insuficiente: {combined_score:.1f} < {min_combined_score:.1f}'
            
            return evaluation
            
        except Exception as e:
            print(f"❌ Error evaluando señal FVG: {e}")
            return {
                'signal_approved': False,
                'reason': f'Error: {e}',
                'recommended_action': 'REJECT'
            }
    
    def _calculate_priority_score(self, fvg_signal: Dict[str, Any], session: str) -> float:
        """📊 Calcular score de prioridad basado en calidad y contexto"""
        try:
            # Factores base
            quality_score = fvg_signal.get('quality_score', 0)
            confluence_strength = fvg_signal.get('confluence_strength', 0)
            ml_confidence = fvg_signal.get('ml_confidence', 0)
            
            # Pesos por factor
            quality_weight = 0.4
            confluence_weight = 0.3
            ml_weight = 0.3
            
            # Score base ponderado
            base_score = (quality_score * quality_weight + 
                         confluence_strength/10 * confluence_weight +  # Normalizar confluencia
                         ml_confidence * 10 * ml_weight)  # Normalizar ML confidence
            
            # Bonus por símbolo prioritario de sesión
            symbol = fvg_signal.get('symbol', '')
            priority_symbols = self.bridge_config['session_symbols_priority'].get(session, [])
            
            if symbol in priority_symbols:
                symbol_index = priority_symbols.index(symbol)
                symbol_bonus = 1.0 - (symbol_index * 0.1)  # Primer símbolo +1.0, segundo +0.9, etc.
                base_score *= (1.0 + symbol_bonus * 0.2)  # Hasta 20% bonus
            
            return min(10.0, base_score)  # Cap en 10.0
            
        except Exception as e:
            print(f"❌ Error calculando priority score: {e}")
            return 0.0
    
    def _calculate_timing_score(self, fvg_signal: Dict[str, Any], session: str) -> float:
        """⏰ Calcular score de timing basado en horario y volatilidad"""
        try:
            # Configuración de timing por sesión
            timing_config = {
                'ASIA': {
                    'optimal_hours': [1, 2, 3],      # 01:00-03:00 GMT
                    'volatility_factor': 0.8,        # Volatilidad moderada
                    'trend_factor': 1.2              # Buenos trends
                },
                'LONDON': {
                    'optimal_hours': [8, 9, 10],     # 08:00-10:00 GMT
                    'volatility_factor': 1.2,        # Alta volatilidad
                    'trend_factor': 1.0              # Volatilidad equilibrada
                },
                'NEW_YORK': {
                    'optimal_hours': [13, 14, 15],   # 13:00-15:00 GMT
                    'volatility_factor': 1.1,        # Volatilidad alta
                    'trend_factor': 1.3              # Momentum fuerte
                }
            }
            
            session_config = timing_config.get(session, timing_config['LONDON'])
            
            # Score base por sesión
            base_timing_score = 7.0
            
            # Ajustes por características de sesión
            volatility_multiplier = session_config['volatility_factor']
            trend_multiplier = session_config['trend_factor']
            
            # Simulación: score actual de timing (en producción sería cálculo real)
            current_hour = datetime.now().hour
            optimal_hours = session_config['optimal_hours']
            
            # Bonus si estamos en horas óptimas
            hour_bonus = 1.0
            if current_hour in optimal_hours:
                hour_bonus = 1.2
            elif abs(current_hour - optimal_hours[1]) <= 1:  # 1 hora de margen
                hour_bonus = 1.1
            
            final_score = base_timing_score * volatility_multiplier * trend_multiplier * hour_bonus
            
            return min(10.0, final_score)
            
        except Exception as e:
            print(f"❌ Error calculando timing score: {e}")
            return 5.0  # Score neutro por defecto
    
    def process_fvg_signal(self, fvg_signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 Procesar señal FVG completa a través del bridge
        
        Args:
            fvg_signal: Señal del Piso 3
            
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            self.integration_stats['fvg_signals_generated'] += 1
            
            # 1. Evaluar señal en contexto de sesión/ciclo
            evaluation = self.evaluate_fvg_signal_for_session(fvg_signal)
            
            # 2. Registrar estadísticas
            session = self.simulated_state['current_session']
            if session != 'INACTIVE':
                self.integration_stats['session_performance'][session]['signals'] += 1
            
            # 3. Determinar acción
            result = {
                'signal_id': f"FVG_{datetime.now().strftime('%H%M%S')}",
                'original_signal': fvg_signal.copy(),
                'evaluation': evaluation,
                'action_taken': evaluation['recommended_action'],
                'session_context': session,
                'timestamp': datetime.now(),
                'trade_executed': False,
                'trade_result': {}
            }
            
            # 4. Ejecutar si aprobado
            if evaluation['signal_approved'] and evaluation['recommended_action'] == 'EXECUTE':
                trade_result = self._execute_fvg_trade(fvg_signal, evaluation)
                result['trade_executed'] = True
                result['trade_result'] = trade_result
                
                # Actualizar estadísticas
                self.integration_stats['fvg_trades_executed'] += 1
                if session != 'INACTIVE':
                    self.integration_stats['session_performance'][session]['trades'] += 1
                    self.integration_stats['session_performance'][session]['pnl'] += trade_result.get('pnl_percent', 0)
            
            else:
                # Contar filtrados
                if evaluation['recommended_action'] == 'REJECT':
                    if 'ciclo' in evaluation['reason'].lower():
                        self.integration_stats['fvg_signals_filtered_by_cycle'] += 1
                    else:
                        self.integration_stats['fvg_signals_filtered_by_session'] += 1
            
            return result
            
        except Exception as e:
            print(f"❌ Error procesando señal FVG: {e}")
            return {
                'signal_id': 'ERROR',
                'action_taken': 'ERROR',
                'error': str(e)
            }
    
    def _execute_fvg_trade(self, fvg_signal: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """💹 Simular ejecución de trade FVG optimizado"""
        try:
            # Parámetros optimizados del trade
            symbol = fvg_signal.get('symbol', 'EURUSD')
            direction = fvg_signal.get('direction', 'BUY')
            quality_score = fvg_signal.get('quality_score', 7.0)
            risk_percent = evaluation.get('adjusted_risk_percent', 1.0)
            
            # Simular resultado basado en calidad y sesión
            session = self.simulated_state['current_session']
            
            # Win rate mejorado por sesión y calidad
            base_win_rates = {'ASIA': 0.65, 'LONDON': 0.60, 'NEW_YORK': 0.70}
            base_win_rate = base_win_rates.get(session, 0.60)
            
            # Ajuste por calidad
            quality_bonus = (quality_score - 7.0) * 0.05  # +5% por punto sobre 7.0
            final_win_rate = min(0.85, base_win_rate + quality_bonus)
            
            # Simular resultado (en producción sería trade real)
            import random
            random.seed(int(datetime.now().timestamp()) % 1000)  # Seed semi-aleatorio
            
            is_winner = random.random() < final_win_rate
            
            if is_winner:
                # Profit mejorado por calidad y sesión
                base_profits = {'ASIA': (0.8, 1.5), 'LONDON': (1.0, 2.0), 'NEW_YORK': (0.7, 1.3)}
                profit_range = base_profits.get(session, (1.0, 1.5))
                pnl_percent = random.uniform(profit_range[0], profit_range[1])
            else:
                # Loss limitado por risk management
                pnl_percent = -random.uniform(risk_percent * 0.7, risk_percent)
            
            # Actualizar estado simulado
            self.simulated_state['cycle_trades'] += 1
            self.simulated_state['cycle_pnl'] += pnl_percent
            self.simulated_state['session_trades'][session] += 1
            
            trade_result = {
                'symbol': symbol,
                'direction': direction,
                'lot_size': round(risk_percent / 100, 2),  # Simplificado
                'entry_time': datetime.now(),
                'pnl_percent': pnl_percent,
                'pnl_usd': pnl_percent * 100,  # Simplificado para $10k
                'quality_score': quality_score,
                'session': session,
                'win_rate_used': final_win_rate,
                'risk_percent_used': risk_percent
            }
            
            print(f"💹 Trade FVG ejecutado: {symbol} {direction} en {session}")
            print(f"   P&L: {pnl_percent:+.2f}% | Calidad: {quality_score:.1f} | Riesgo: {risk_percent:.1f}%")
            
            return trade_result
            
        except Exception as e:
            print(f"❌ Error ejecutando trade FVG: {e}")
            return {'error': str(e)}
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """📈 Obtener resumen de integración Piso 3-4"""
        try:
            summary = {
                'bridge_status': 'ACTIVE',
                'integration_stats': self.integration_stats.copy(),
                'current_cycle': {
                    'trades_executed': self.simulated_state['cycle_trades'],
                    'cycle_pnl': self.simulated_state['cycle_pnl'],
                    'trades_remaining': 3 - self.simulated_state['cycle_trades'],
                    'session_distribution': self.simulated_state['session_trades']
                },
                'efficiency_metrics': {},
                'performance_by_session': self.integration_stats['session_performance']
            }
            
            # Calcular métricas de eficiencia
            total_signals = self.integration_stats['fvg_signals_generated']
            if total_signals > 0:
                summary['efficiency_metrics'] = {
                    'signal_to_trade_ratio': self.integration_stats['fvg_trades_executed'] / total_signals,
                    'session_filter_rate': self.integration_stats['fvg_signals_filtered_by_session'] / total_signals,
                    'cycle_filter_rate': self.integration_stats['fvg_signals_filtered_by_cycle'] / total_signals,
                    'execution_rate': self.integration_stats['fvg_trades_executed'] / total_signals
                }
            
            return summary
            
        except Exception as e:
            print(f"❌ Error generando resumen: {e}")
            return {}


def main():
    """Función de prueba del FVG Operations Bridge"""
    print("🔗 Testing FVG Operations Bridge - Integración Piso 3+4")
    print("=" * 65)
    
    # Crear bridge
    bridge = FVGOperationsBridge()
    
    # Simular señales FVG del Piso 3
    test_signals = [
        {
            'symbol': 'EURUSD',
            'direction': 'BUY',
            'quality_score': 8.2,
            'confluence_strength': 85,
            'ml_confidence': 0.78,
            'fvg_size_pips': 12,
            'session_detected': 'LONDON'
        },
        {
            'symbol': 'USDJPY',
            'direction': 'SELL',
            'quality_score': 6.8,  # Calidad baja para London
            'confluence_strength': 65,
            'ml_confidence': 0.62,
            'fvg_size_pips': 8,
            'session_detected': 'ASIA'
        },
        {
            'symbol': 'GBPUSD',
            'direction': 'BUY',
            'quality_score': 9.1,
            'confluence_strength': 92,
            'ml_confidence': 0.85,
            'fvg_size_pips': 15,
            'session_detected': 'NEW_YORK'
        }
    ]
    
    print(f"\n💹 Procesando {len(test_signals)} señales FVG:")
    
    # Procesar cada señal
    results = []
    for i, signal in enumerate(test_signals, 1):
        print(f"\n📊 SEÑAL {i}: {signal['symbol']} {signal['direction']} (Quality: {signal['quality_score']:.1f})")
        
        result = bridge.process_fvg_signal(signal)
        results.append(result)
        
        print(f"   Acción: {result['action_taken']}")
        print(f"   Razón: {result['evaluation']['reason']}")
        
        if result['trade_executed']:
            trade = result['trade_result']
            print(f"   ✅ Trade ejecutado: {trade['pnl_percent']:+.2f}% P&L")
    
    # Mostrar resumen de integración
    print(f"\n📈 RESUMEN DE INTEGRACIÓN:")
    print("="*40)
    
    summary = bridge.get_integration_summary()
    
    print(f"📊 Señales procesadas: {summary['integration_stats']['fvg_signals_generated']}")
    print(f"💹 Trades ejecutados: {summary['integration_stats']['fvg_trades_executed']}")
    print(f"🔄 Ciclo actual: {summary['current_cycle']['trades_executed']}/3 trades")
    print(f"💰 P&L ciclo: {summary['current_cycle']['cycle_pnl']:+.2f}%")
    
    if summary['efficiency_metrics']:
        eff = summary['efficiency_metrics']
        print(f"📈 Eficiencia signal→trade: {eff['execution_rate']:.1%}")
        print(f"🔍 Filtrado por sesión: {eff['session_filter_rate']:.1%}")
        print(f"🎯 Filtrado por ciclo: {eff['cycle_filter_rate']:.1%}")
    
    print(f"\n🏆 ESTADO INTEGRACIÓN: Bridge operativo ✅")
    print(f"🚀 Próximo paso: Master Operations Controller")


if __name__ == "__main__":
    main()
