"""
📡 FVG SIGNAL GENERATOR - PISO 3 OFICINA TRADING
================================================

Generador de Señales de Trading basado en análisis FVG
Convierte análisis de calidad y ML en señales ejecutables

FUNCIONALIDADES:
- Conversión de análisis FVG en señales de trading
- Rate limiting inteligente (máx 5 señales/hora)
- Filtros de calidad y confluencia avanzados
- Integración con FVGRiskManager y ML Predictor
- Gestión de múltiples timeframes

AUTOR: Sistema Trading Grid - Piso 3
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict

# Configurar imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "analysis" / "piso_3" / "trading").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis" / "piso_3" / "analisis").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis" / "piso_3" / "ia").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))

from fvg_risk_manager import get_fvg_risk_manager
from logger_manager import LoggerManager

class FVGSignalGenerator:
    """
    📡 GENERADOR DE SEÑALES FVG - PISO 3
    Convierte análisis FVG en señales ejecutables de trading
    """
    
    def __init__(self, symbol='EURUSD'):
        self.symbol = symbol
        self.logger = LoggerManager().get_logger('fvg_signal_generator')
        
        # Configuración de señales
        self.signal_config = {
            'max_signals_per_hour': 5,      # Límite de señales por hora
            'min_quality_threshold': 7.0,   # Calidad mínima para señal
            'min_ml_confidence': 0.75,      # Confianza ML mínima
            'min_confluence_strength': 75,   # Fuerza confluencia mínima
            'cooldown_minutes': 15,         # Tiempo entre señales del mismo tipo
            'signal_timeout_minutes': 30    # Tiempo de validez de señal
        }
        
        # Gestores integrados
        self.risk_manager = get_fvg_risk_manager(symbol)
        
        # Estado de señales
        self.signal_history = []
        self.active_signals = {}
        self.hourly_count = 0
        self.last_hour_reset = datetime.now().hour
        
        # Estadísticas
        self.stats = {
            'total_signals_generated': 0,
            'signals_executed': 0,
            'signals_filtered': 0,
            'best_signal_quality': 0.0,
            'avg_signal_confidence': 0.0
        }
        
        self.logger.info("📡 FVGSignalGenerator inicializado para símbolo: %s", symbol)
    
    def generate_signal(self, fvg_analysis: Dict) -> Dict:
        """
        📡 Generar señal de trading basada en análisis FVG
        
        Args:
            fvg_analysis: Análisis completo del FVG
            
        Returns:
            dict: Señal de trading generada
        """
        try:
            self.logger.info("📡 Generando señal FVG - Quality: %.1f, ML: %.2f, Direction: %s", 
                           fvg_analysis.get('quality_score', 0),
                           fvg_analysis.get('ml_confidence', 0),
                           fvg_analysis.get('direction', 'UNKNOWN'))
            
            signal = {
                'signal_generated': False,
                'signal_id': '',
                'signal_type': 'FVG_TRADE',
                'direction': fvg_analysis.get('direction', 'WAIT'),
                'entry_price': 0.0,
                'stop_loss': 0.0,
                'take_profits': {},
                'lot_size': 0.0,
                'confidence_score': 0.0,
                'priority': 'LOW',
                'valid_until': None,
                'reason': '',
                'fvg_details': fvg_analysis.copy()
            }
            
            # 1. Verificar rate limiting
            if not self._check_rate_limits():
                signal['reason'] = 'Rate limit alcanzado'
                self.stats['signals_filtered'] += 1
                return signal
            
            # 2. Filtros básicos de calidad
            if not self._passes_quality_filters(fvg_analysis):
                signal['reason'] = 'No pasa filtros de calidad'
                self.stats['signals_filtered'] += 1
                return signal
            
            # 3. Verificar cooldown period
            if not self._check_cooldown_period(fvg_analysis.get('direction', '')):
                signal['reason'] = 'Período de cooldown activo'
                self.stats['signals_filtered'] += 1
                return signal
            
            # 4. Evaluar riesgo con FVGRiskManager
            risk_evaluation = self.risk_manager.evaluate_fvg_trade(fvg_analysis)
            
            if not risk_evaluation.get('trade_allowed', False):
                signal['reason'] = f"Risk Manager: {risk_evaluation.get('reason', 'Trade no permitido')}"
                self.stats['signals_filtered'] += 1
                return signal
            
            # 5. Construir señal válida
            signal_id = self._generate_signal_id()
            
            signal.update({
                'signal_generated': True,
                'signal_id': signal_id,
                'entry_price': fvg_analysis.get('price_current', 0),
                'stop_loss': self._calculate_sl_price(fvg_analysis, risk_evaluation),
                'take_profits': self._calculate_tp_prices(fvg_analysis, risk_evaluation),
                'lot_size': risk_evaluation.get('recommended_lots', 0.01),
                'confidence_score': risk_evaluation.get('confidence_score', 0.0),
                'priority': self._determine_signal_priority(fvg_analysis, risk_evaluation),
                'valid_until': datetime.now() + timedelta(minutes=self.signal_config['signal_timeout_minutes']),
                'reason': 'Señal FVG válida generada'
            })
            
            # 6. Registrar señal
            self._register_signal(signal)
            
            # 7. Actualizar estadísticas
            self.stats['total_signals_generated'] += 1
            self.stats['best_signal_quality'] = max(
                self.stats['best_signal_quality'], 
                fvg_analysis.get('quality_score', 0)
            )
            
            self.logger.info("✅ Señal FVG generada: %s - %s @ %.5f, Lots: %.3f", 
                           signal_id, signal['direction'], signal['entry_price'], signal['lot_size'])
            
            return signal
            
        except Exception as e:
            self.logger.error("❌ Error generando señal FVG: %s", e)
            return {
                'signal_generated': False,
                'reason': f'Error interno: {e}',
                'error': str(e)
            }
    
    def _check_rate_limits(self) -> bool:
        """⏱️ Verificar límites de rate limiting"""
        try:
            current_hour = datetime.now().hour
            
            # Reset contador si cambió la hora
            if current_hour != self.last_hour_reset:
                self.hourly_count = 0
                self.last_hour_reset = current_hour
            
            if self.hourly_count >= self.signal_config['max_signals_per_hour']:
                self.logger.warning("⚠️ Rate limit alcanzado: %d/%d señales esta hora", 
                                  self.hourly_count, self.signal_config['max_signals_per_hour'])
                return False
            
            return True
            
        except Exception as e:
            self.logger.error("❌ Error verificando rate limits: %s", e)
            return False
    
    def _passes_quality_filters(self, fvg_analysis: Dict) -> bool:
        """🔍 Verificar filtros de calidad"""
        quality_score = fvg_analysis.get('quality_score', 0)
        ml_confidence = fvg_analysis.get('ml_confidence', 0)
        confluence_strength = fvg_analysis.get('confluence_strength', 0)
        
        # Filtro de calidad mínima
        if quality_score < self.signal_config['min_quality_threshold']:
            return False
        
        # Filtro de confianza ML
        if ml_confidence < self.signal_config['min_ml_confidence']:
            return False
        
        # Filtro de confluencia
        if confluence_strength < self.signal_config['min_confluence_strength']:
            return False
        
        return True
    
    def _check_cooldown_period(self, direction: str) -> bool:
        """⏳ Verificar período de cooldown entre señales"""
        try:
            now = datetime.now()
            cooldown_limit = now - timedelta(minutes=self.signal_config['cooldown_minutes'])
            
            # Buscar señales recientes del mismo tipo
            recent_signals = [
                s for s in self.signal_history 
                if (s.get('direction') == direction and 
                    s.get('timestamp', datetime.min) > cooldown_limit)
            ]
            
            return len(recent_signals) == 0
            
        except Exception as e:
            self.logger.error("❌ Error verificando cooldown: %s", e)
            return True
    
    def _generate_signal_id(self) -> str:
        """🆔 Generar ID único para la señal"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"FVG_SIGNAL_{self.symbol}_{timestamp}"
    
    def _calculate_sl_price(self, fvg_analysis: Dict, risk_evaluation: Dict) -> float:
        """📉 Calcular precio de Stop Loss"""
        try:
            entry_price = fvg_analysis.get('price_current', 0)
            direction = fvg_analysis.get('direction', 'BUY')
            sl_pips = risk_evaluation.get('stop_loss_pips', 15)
            
            # Convertir pips a precio
            pip_size = 0.0001  # Para EURUSD
            sl_distance = sl_pips * pip_size
            
            if direction == 'BUY':
                sl_price = entry_price - sl_distance
            else:  # SELL
                sl_price = entry_price + sl_distance
            
            return round(sl_price, 5)
            
        except Exception as e:
            self.logger.error("❌ Error calculando SL: %s", e)
            return 0.0
    
    def _calculate_tp_prices(self, fvg_analysis: Dict, risk_evaluation: Dict) -> Dict:
        """📈 Calcular precios de Take Profit múltiples"""
        try:
            entry_price = fvg_analysis.get('price_current', 0)
            direction = fvg_analysis.get('direction', 'BUY')
            tp_levels = risk_evaluation.get('take_profits', {})
            
            tp_prices = {}
            pip_size = 0.0001  # Para EURUSD
            
            for tp_name, tp_info in tp_levels.items():
                tp_pips = tp_info.get('pips', 0)
                tp_distance = tp_pips * pip_size
                
                if direction == 'BUY':
                    tp_price = entry_price + tp_distance
                else:  # SELL
                    tp_price = entry_price - tp_distance
                
                tp_prices[tp_name] = {
                    'price': round(tp_price, 5),
                    'pips': tp_pips,
                    'rr_ratio': tp_info.get('rr_ratio', 1.0)
                }
            
            return tp_prices
            
        except Exception as e:
            self.logger.error("❌ Error calculando TPs: %s", e)
            return {}
    
    def _determine_signal_priority(self, fvg_analysis: Dict, risk_evaluation: Dict) -> str:
        """🎯 Determinar prioridad de la señal"""
        quality_score = fvg_analysis.get('quality_score', 0)
        confidence_score = risk_evaluation.get('confidence_score', 0)
        risk_level = risk_evaluation.get('risk_level', 'HIGH')
        
        # Señal de alta prioridad
        if (quality_score >= 8.5 and 
            confidence_score >= 0.8 and 
            risk_level in ['VERY_LOW', 'LOW']):
            return 'HIGH'
        
        # Señal de prioridad media
        elif (quality_score >= 7.0 and 
              confidence_score >= 0.7 and 
              risk_level in ['LOW', 'MEDIUM']):
            return 'MEDIUM'
        
        # Señal de baja prioridad
        else:
            return 'LOW'
    
    def _register_signal(self, signal: Dict) -> None:
        """📝 Registrar señal en historial"""
        try:
            signal_record = {
                'signal_id': signal['signal_id'],
                'timestamp': datetime.now(),
                'direction': signal['direction'],
                'confidence_score': signal['confidence_score'],
                'priority': signal['priority'],
                'status': 'GENERATED'
            }
            
            self.signal_history.append(signal_record)
            self.active_signals[signal['signal_id']] = signal
            self.hourly_count += 1
            
        except Exception as e:
            self.logger.error("❌ Error registrando señal: %s", e)
    
    def mark_signal_executed(self, signal_id: str) -> bool:
        """✅ Marcar señal como ejecutada"""
        try:
            if signal_id in self.active_signals:
                self.active_signals[signal_id]['status'] = 'EXECUTED'
                self.stats['signals_executed'] += 1
                self.logger.info("✅ Señal marcada como ejecutada: %s", signal_id)
                return True
            return False
        except Exception as e:
            self.logger.error("❌ Error marcando señal ejecutada: %s", e)
            return False
    
    def get_signal_summary(self) -> Dict:
        """📊 Obtener resumen del generador de señales"""
        try:
            execution_rate = 0.0
            if self.stats['total_signals_generated'] > 0:
                execution_rate = (self.stats['signals_executed'] / 
                                self.stats['total_signals_generated']) * 100
            
            summary = {
                'timestamp': datetime.now(),
                'symbol': self.symbol,
                'signals': {
                    'active_count': len(self.active_signals),
                    'hourly_count': self.hourly_count,
                    'hourly_limit': self.signal_config['max_signals_per_hour']
                },
                'stats': {
                    'total_generated': self.stats['total_signals_generated'],
                    'total_executed': self.stats['signals_executed'],
                    'total_filtered': self.stats['signals_filtered'],
                    'execution_rate': execution_rate,
                    'best_quality': self.stats['best_signal_quality'],
                    'avg_confidence': self.stats['avg_signal_confidence']
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo resumen: %s", e)
            return {'error': str(e)}

if __name__ == "__main__":
    # Test del FVG Signal Generator
    print("📡 Testing FVG Signal Generator...")
    
    signal_gen = FVGSignalGenerator('EURUSD')
    
    test_fvg_analysis = {
        'quality_score': 8.5,
        'confluence_strength': 85,
        'fvg_size_pips': 15,
        'direction': 'BUY',
        'ml_confidence': 0.82,
        'session_type': 'LONDON',
        'timeframe': 'M15',
        'price_current': 1.09450
    }
    
    signal = signal_gen.generate_signal(test_fvg_analysis)
    
    print(f"✅ Señal generada:")
    print(f"   Señal válida: {signal.get('signal_generated', False)}")
    print(f"   ID: {signal.get('signal_id', 'N/A')}")
    print(f"   Dirección: {signal.get('direction', 'N/A')}")
    print(f"   Entry: {signal.get('entry_price', 0):.5f}")
    print(f"   SL: {signal.get('stop_loss', 0):.5f}")
    print(f"   Lots: {signal.get('lot_size', 0):.3f}")
    print(f"   Razón: {signal.get('reason', 'N/A')}")
    
    summary = signal_gen.get_signal_summary()
    print(f"\n📊 Resumen:")
    print(f"   Total generadas: {summary.get('stats', {}).get('total_generated', 0)}")
    print(f"   Total filtradas: {summary.get('stats', {}).get('total_filtered', 0)}")
    
    print("\n🎯 FVG Signal Generator test completado!")
