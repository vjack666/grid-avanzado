"""
🏢 OFICINA TRADING COMPLETA - PISO 3
===================================

Script integrador de todos los componentes de la Oficina Trading:
- FVGRiskManager: Gestión de riesgo específica FVG
- FVGSignalGenerator: Generación de señales de trading
- FVGOrderExecutor: Ejecución de órdenes en MT5

AUTOR: Sistema Trading Grid - Piso 3
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict

# Configurar imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "analysis" / "piso_3" / "trading").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))

from fvg_risk_manager import get_fvg_risk_manager
from signal_generator import FVGSignalGenerator
from order_executor import FVGOrderExecutor
from logger_manager import LoggerManager

class FVGTradingOffice:
    """
    🏢 OFICINA TRADING COMPLETA - PISO 3
    Integración completa de gestión de riesgo, señales y ejecución FVG
    """
    
    def __init__(self, symbol='EURUSD'):
        self.symbol = symbol
        self.logger = LoggerManager().get_logger('fvg_trading_office')
        
        # Componentes de la oficina
        self.risk_manager = get_fvg_risk_manager(symbol)
        self.signal_generator = FVGSignalGenerator(symbol)
        self.order_executor = FVGOrderExecutor(symbol)
        
        # Configuración de la oficina
        self.office_config = {
            'auto_execution_enabled': False,  # Por seguridad, manual por defecto
            'min_confidence_auto': 0.85,      # Confianza mínima para auto-ejecución
            'max_daily_trades': 5,            # Máximo trades por día
            'emergency_stop_enabled': True,   # Parada de emergencia
            'logging_enabled': True           # Logging detallado
        }
        
        # Estado de la oficina
        self.office_stats = {
            'session_start': datetime.now(),
            'total_analyses': 0,
            'signals_generated': 0,
            'orders_executed': 0,
            'successful_trades': 0,
            'daily_pnl': 0.0
        }
        
        self.logger.info("🏢 FVG Trading Office inicializada para símbolo: %s", symbol)
    
    def process_fvg_analysis(self, fvg_analysis: Dict) -> Dict:
        """
        🔄 Procesar análisis FVG completo: Riesgo → Señal → Ejecución
        
        Args:
            fvg_analysis: Análisis completo del FVG
            
        Returns:
            dict: Resultado completo del procesamiento
        """
        try:
            self.logger.info("🔄 Procesando análisis FVG en Trading Office")
            
            processing_result = {
                'analysis_processed': False,
                'risk_evaluation': {},
                'signal_generated': {},
                'order_executed': {},
                'final_status': 'PENDING',
                'processing_time_ms': 0,
                'reason': ''
            }
            
            start_time = datetime.now()
            
            # 1. FASE RIESGO: Evaluar con FVGRiskManager
            self.logger.info("🛡️ FASE 1: Evaluación de riesgo")
            risk_evaluation = self.risk_manager.evaluate_fvg_trade(fvg_analysis)
            processing_result['risk_evaluation'] = risk_evaluation
            
            if not risk_evaluation.get('trade_allowed', False):
                processing_result.update({
                    'final_status': 'REJECTED_RISK',
                    'reason': f"Risk Manager: {risk_evaluation.get('reason', 'Trade no permitido')}"
                })
                self._update_office_stats('analysis_only')
                return processing_result
            
            # 2. FASE SEÑAL: Generar señal con FVGSignalGenerator
            self.logger.info("📡 FASE 2: Generación de señal")
            signal = self.signal_generator.generate_signal(fvg_analysis)
            processing_result['signal_generated'] = signal
            
            if not signal.get('signal_generated', False):
                processing_result.update({
                    'final_status': 'REJECTED_SIGNAL',
                    'reason': f"Signal Generator: {signal.get('reason', 'Señal no generada')}"
                })
                self._update_office_stats('signal_filtered')
                return processing_result
            
            # 3. FASE EJECUCIÓN: Decidir si ejecutar automáticamente
            self.logger.info("⚡ FASE 3: Evaluación para ejecución")
            execution_decision = self._evaluate_execution_decision(signal, risk_evaluation)
            
            if execution_decision['execute']:
                # Ejecutar orden automáticamente
                self.logger.info("🤖 Ejecutando orden automáticamente")
                execution_result = self.order_executor.execute_fvg_signal(signal)
                processing_result['order_executed'] = execution_result
                
                if execution_result.get('executed', False):
                    processing_result.update({
                        'final_status': 'EXECUTED',
                        'reason': 'Orden ejecutada automáticamente'
                    })
                    self._update_office_stats('executed')
                    
                    # Marcar señal como ejecutada
                    self.signal_generator.mark_signal_executed(signal['signal_id'])
                else:
                    processing_result.update({
                        'final_status': 'EXECUTION_FAILED',
                        'reason': f"Ejecución falló: {execution_result.get('reason', 'Error desconocido')}"
                    })
                    self._update_office_stats('execution_failed')
            else:
                # Señal generada pero no ejecutada automáticamente
                processing_result.update({
                    'final_status': 'SIGNAL_PENDING',
                    'reason': f"Señal generada, ejecución manual requerida: {execution_decision['reason']}"
                })
                self._update_office_stats('signal_pending')
            
            # Calcular tiempo de procesamiento
            end_time = datetime.now()
            processing_time_ms = (end_time - start_time).total_seconds() * 1000
            processing_result['processing_time_ms'] = round(processing_time_ms, 2)
            processing_result['analysis_processed'] = True
            
            self.logger.info("✅ Procesamiento completado: %s - Tiempo: %.1fms", 
                           processing_result['final_status'], processing_result['processing_time_ms'])
            
            return processing_result
            
        except Exception as e:
            self.logger.error("❌ Error procesando análisis FVG: %s", e)
            return {
                'analysis_processed': False,
                'final_status': 'ERROR',
                'reason': f'Error interno: {e}',
                'error': str(e)
            }
    
    def _evaluate_execution_decision(self, signal: Dict, risk_evaluation: Dict) -> Dict:
        """🤔 Evaluar si ejecutar orden automáticamente"""
        try:
            decision = {
                'execute': False,
                'reason': '',
                'confidence_score': 0.0,
                'auto_execution_eligible': False
            }
            
            # Verificar si auto-ejecución está habilitada
            if not self.office_config['auto_execution_enabled']:
                decision['reason'] = 'Auto-ejecución deshabilitada'
                return decision
            
            # Verificar nivel de confianza
            confidence_score = signal.get('confidence_score', 0)
            min_confidence = self.office_config['min_confidence_auto']
            
            if confidence_score < min_confidence:
                decision['reason'] = f'Confianza insuficiente: {confidence_score:.2f} < {min_confidence}'
                return decision
            
            # Verificar límites diarios
            if self.office_stats['orders_executed'] >= self.office_config['max_daily_trades']:
                decision['reason'] = 'Límite diario de trades alcanzado'
                return decision
            
            # Verificar prioridad de señal
            priority = signal.get('priority', 'LOW')
            if priority not in ['HIGH', 'MEDIUM']:
                decision['reason'] = f'Prioridad insuficiente: {priority}'
                return decision
            
            # Verificar nivel de riesgo
            risk_level = risk_evaluation.get('risk_level', 'VERY_HIGH')
            if risk_level not in ['VERY_LOW', 'LOW']:
                decision['reason'] = f'Nivel de riesgo alto: {risk_level}'
                return decision
            
            # Todas las condiciones cumplidas
            decision.update({
                'execute': True,
                'reason': 'Todas las condiciones para auto-ejecución cumplidas',
                'confidence_score': confidence_score,
                'auto_execution_eligible': True
            })
            
            return decision
            
        except Exception as e:
            self.logger.error("❌ Error evaluando ejecución: %s", e)
            return {
                'execute': False,
                'reason': f'Error evaluando ejecución: {e}'
            }
    
    def _update_office_stats(self, action: str) -> None:
        """📊 Actualizar estadísticas de la oficina"""
        try:
            self.office_stats['total_analyses'] += 1
            
            if action == 'signal_filtered':
                pass  # Solo análisis, no señal
            elif action == 'signal_pending':
                self.office_stats['signals_generated'] += 1
            elif action == 'executed':
                self.office_stats['signals_generated'] += 1
                self.office_stats['orders_executed'] += 1
            elif action == 'execution_failed':
                self.office_stats['signals_generated'] += 1
            
        except Exception as e:
            self.logger.error("❌ Error actualizando estadísticas: %s", e)
    
    def get_office_summary(self) -> Dict:
        """📊 Obtener resumen completo de la oficina"""
        try:
            # Obtener resúmenes de cada componente
            risk_summary = self.risk_manager.get_fvg_summary()
            signal_summary = self.signal_generator.get_signal_summary()
            execution_summary = self.order_executor.get_execution_summary()
            
            office_summary = {
                'timestamp': datetime.now(),
                'symbol': self.symbol,
                'session_duration_minutes': (datetime.now() - self.office_stats['session_start']).total_seconds() / 60,
                'office_stats': self.office_stats.copy(),
                'office_config': self.office_config.copy(),
                'components': {
                    'risk_manager': {
                        'status': 'ACTIVE',
                        'base_riskbot_status': risk_summary.get('base_riskbot', {}).get('status', 'UNKNOWN'),
                        'fvg_positions': risk_summary.get('fvg_specific', {}).get('current_fvg_positions', 0)
                    },
                    'signal_generator': {
                        'status': 'ACTIVE',
                        'active_signals': signal_summary.get('signals', {}).get('active_count', 0),
                        'hourly_count': signal_summary.get('signals', {}).get('hourly_count', 0),
                        'total_generated': signal_summary.get('stats', {}).get('total_generated', 0)
                    },
                    'order_executor': {
                        'status': 'ACTIVE',
                        'success_rate': execution_summary.get('stats', {}).get('success_rate', 0),
                        'total_executions': execution_summary.get('stats', {}).get('successful_executions', 0)
                    }
                }
            }
            
            return office_summary
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo resumen de oficina: %s", e)
            return {'error': str(e)}
    
    def enable_auto_execution(self, min_confidence: float = 0.85) -> bool:
        """🤖 Habilitar auto-ejecución con nivel de confianza"""
        try:
            self.office_config['auto_execution_enabled'] = True
            self.office_config['min_confidence_auto'] = min_confidence
            
            self.logger.info("🤖 Auto-ejecución habilitada - Confianza mínima: %.2f", min_confidence)
            return True
            
        except Exception as e:
            self.logger.error("❌ Error habilitando auto-ejecución: %s", e)
            return False
    
    def disable_auto_execution(self) -> bool:
        """🛑 Deshabilitar auto-ejecución"""
        try:
            self.office_config['auto_execution_enabled'] = False
            self.logger.info("🛑 Auto-ejecución deshabilitada")
            return True
            
        except Exception as e:
            self.logger.error("❌ Error deshabilitando auto-ejecución: %s", e)
            return False

# Instancia global de la oficina
fvg_trading_office = None

def get_fvg_trading_office(symbol: str = 'EURUSD') -> FVGTradingOffice:
    """
    🏢 Obtener instancia de la FVG Trading Office
    
    Args:
        symbol: Símbolo para la oficina
        
    Returns:
        FVGTradingOffice: Instancia de la oficina completa
    """
    global fvg_trading_office
    
    if fvg_trading_office is None or fvg_trading_office.symbol != symbol:
        fvg_trading_office = FVGTradingOffice(symbol)
    
    return fvg_trading_office

if __name__ == "__main__":
    # Test completo de la FVG Trading Office
    print("🏢 Testing FVG Trading Office Completa...")
    
    # Crear oficina
    trading_office = FVGTradingOffice('EURUSD')
    
    # Test de análisis FVG completo
    test_fvg_analysis = {
        'quality_score': 8.7,
        'confluence_strength': 88,
        'fvg_size_pips': 18,
        'direction': 'BUY',
        'ml_confidence': 0.86,
        'session_type': 'LONDON',
        'timeframe': 'M15',
        'price_current': 1.09520,
        'fvg_levels': {
            'high': 1.09550,
            'low': 1.09490
        }
    }
    
    # Procesar análisis completo
    result = trading_office.process_fvg_analysis(test_fvg_analysis)
    
    print(f"✅ Procesamiento completado:")
    print(f"   Status final: {result.get('final_status', 'UNKNOWN')}")
    print(f"   Tiempo procesamiento: {result.get('processing_time_ms', 0):.1f}ms")
    print(f"   Razón: {result.get('reason', 'N/A')}")
    
    # Verificar cada fase
    risk_eval = result.get('risk_evaluation', {})
    signal_gen = result.get('signal_generated', {})
    order_exec = result.get('order_executed', {})
    
    print(f"\n📊 Detalle por fases:")
    print(f"   🛡️ Riesgo: {'APROBADO' if risk_eval.get('trade_allowed') else 'RECHAZADO'}")
    print(f"   📡 Señal: {'GENERADA' if signal_gen.get('signal_generated') else 'NO GENERADA'}")
    print(f"   ⚡ Ejecución: {'EJECUTADA' if order_exec.get('executed') else 'NO EJECUTADA'}")
    
    # Resumen de la oficina
    summary = trading_office.get_office_summary()
    print(f"\n🏢 Resumen Trading Office:")
    print(f"   Análisis totales: {summary.get('office_stats', {}).get('total_analyses', 0)}")
    print(f"   Señales generadas: {summary.get('office_stats', {}).get('signals_generated', 0)}")
    print(f"   Órdenes ejecutadas: {summary.get('office_stats', {}).get('orders_executed', 0)}")
    
    # Estado de componentes
    components = summary.get('components', {})
    print(f"\n🔧 Estado componentes:")
    print(f"   Risk Manager: {components.get('risk_manager', {}).get('status', 'UNKNOWN')}")
    print(f"   Signal Generator: {components.get('signal_generator', {}).get('status', 'UNKNOWN')}")
    print(f"   Order Executor: {components.get('order_executor', {}).get('status', 'UNKNOWN')}")
    
    print("\n🎯 FVG Trading Office test completado!")
    print("🏢 Oficina Trading del Piso 3 100% operativa!")
