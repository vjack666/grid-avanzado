"""
PUERTA-S2-REGIME: MarketRegimeDetector v1.0.0
Sistema de Detección de Regímenes de Mercado Avanzado

Este módulo implementa un detector inteligente de regímenes de mercado que identifica
automáticamente las condiciones dominantes del mercado utilizando el sistema centralizado de SÓTANO 1.

Integración con SÓTANO 1:
- ConfigManager: Configuración centralizada
- LoggerManager: Logging unificado  
- ErrorManager: Manejo de errores centralizado
- DataManager: Gestión de datos históricos
- AnalyticsManager: Motor de análisis técnico

Protocolo: Trading Grid SÓTANO 1 + SÓTANO 2
Autor: Copilot & AI Assistant  
Fecha: 2025-08-11
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Imports del sistema SÓTANO 1 (protocolo centralizado)
from config_manager import ConfigManager
from logger_manager import LoggerManager
from error_manager import ErrorManager
from data_manager import DataManager
from analytics_manager import AnalyticsManager

class MarketRegime(Enum):
    """Regímenes de mercado identificables"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    CONSOLIDATION = "consolidation"

class RegimeConfidence(Enum):
    """Nivel de confianza en la detección del régimen"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4

@dataclass
class RegimeDetection:
    """Detección de régimen de mercado"""
    symbol: str
    timeframe: str
    regime: MarketRegime
    confidence: RegimeConfidence
    probability: float  # 0.0 - 1.0
    timestamp: datetime
    duration: timedelta
    indicators: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RegimeAnalysis:
    """Análisis completo de régimen"""
    current_regime: RegimeDetection
    previous_regime: Optional[RegimeDetection]
    regime_changes: int
    stability_score: float  # 0.0 - 1.0
    forecast: Optional[MarketRegime]
    recommendations: List[str]

class MarketRegimeDetector:
    """
    PUERTA-S2-REGIME: Detector de Regímenes de Mercado
    
    Integrado con el sistema centralizado de SÓTANO 1 siguiendo protocolos establecidos.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None,
                 logger_manager: Optional[LoggerManager] = None,
                 error_manager: Optional[ErrorManager] = None,
                 data_manager: Optional[DataManager] = None,
                 analytics_manager: Optional[AnalyticsManager] = None):
        
        # Managers principales (protocolo SÓTANO 1)
        self.config_manager = config_manager or ConfigManager()
        self.logger_manager = logger_manager or LoggerManager()
        self.error_manager = error_manager or ErrorManager(
            logger_manager=self.logger_manager, 
            config_manager=self.config_manager
        )
        self.data_manager = data_manager or DataManager()
        self.analytics_manager = analytics_manager or AnalyticsManager(
            config_manager=self.config_manager,
            logger_manager=self.logger_manager,
            error_manager=self.error_manager,
            data_manager=self.data_manager
        )
        
        # Configuración del componente
        self.component_id = "PUERTA-S2-REGIME"
        self.version = "v1.0.0"
        
        # Estado del detector
        self.is_active = False
        self.detection_running = False
        self.last_update = None
        
        # Datos de regímenes
        self.current_regimes: Dict[str, RegimeDetection] = {}  # symbol_timeframe -> detection
        self.regime_history: List[RegimeDetection] = []
        self.regime_statistics: Dict[str, Any] = {}
        
        # Configuración de detección
        self.detection_config = {
            'volatility_threshold_high': 0.025,
            'volatility_threshold_low': 0.008,
            'trend_strength_threshold': 0.6,
            'ranging_threshold': 0.3,
            'breakout_threshold': 1.5,
            'reversal_threshold': 0.8,
            'min_detection_period': 5,  # mínimo 5 períodos para confirmar régimen
            'confidence_decay_rate': 0.95
        }
        
        # Métricas
        self.detector_metrics = {
            'total_detections': 0,
            'regime_changes_detected': 0,
            'avg_detection_confidence': 0.0,
            'active_regimes_count': 0,
            'detection_accuracy': 0.0,
            'most_common_regime': None
        }
        
        # Threading
        self.detection_thread = None
        self.detection_lock = threading.Lock()
        
        # Log de inicialización
        self.logger_manager.log_info(f"✅ {self.component_id} {self.version} inicializado correctamente")
    
    def detect_market_regime(self, symbol: str, timeframe: str, 
                           market_data: Optional[Dict[str, Any]] = None) -> Optional[RegimeDetection]:
        """Detectar régimen de mercado para un símbolo específico"""
        try:
            # Obtener datos del mercado del AnalyticsManager
            market_summary = self.analytics_manager.get_market_summary()
            
            # Extraer indicadores clave
            volatility = market_summary.get('volatility', 0.015)
            trend_data = market_summary.get('trend_analysis', {})
            
            # Combinar con datos adicionales si se proporcionan
            if market_data:
                volatility = market_data.get('volatility', volatility)
            
            # Análisis de volatilidad
            volatility_regime = self._analyze_volatility_regime(volatility)
            
            # Análisis de tendencia
            trend_regime = self._analyze_trend_regime(trend_data)
            
            # Análisis de momentum
            momentum_regime = self._analyze_momentum_regime(market_summary)
            
            # Combinar análisis para determinar régimen dominante
            primary_regime, confidence, probability = self._combine_regime_analysis(
                volatility_regime, trend_regime, momentum_regime
            )
            
            # Crear detección
            detection = RegimeDetection(
                symbol=symbol,
                timeframe=timeframe,
                regime=primary_regime,
                confidence=confidence,
                probability=probability,
                timestamp=datetime.now(),
                duration=timedelta(minutes=15),  # Default timeframe
                indicators={
                    'volatility': volatility,
                    'trend_strength': trend_data.get('trend_strength', 0.0) if trend_data else 0.0,
                    'momentum': market_summary.get('momentum', 0.0),
                    'volume_profile': market_summary.get('volume_profile', 1.0),
                    'support_resistance': market_summary.get('support_resistance_strength', 0.5)
                },
                metadata={
                    'volatility_regime': volatility_regime.value,
                    'trend_regime': trend_regime.value,
                    'momentum_regime': momentum_regime.value,
                    'detection_method': 'multi_factor_analysis'
                }
            )
            
            # Actualizar estado
            key = f"{symbol}_{timeframe}"
            
            with self.detection_lock:
                old_regime = self.current_regimes.get(key)
                self.current_regimes[key] = detection
                self.regime_history.append(detection)
                
                # Detectar cambio de régimen
                if old_regime and old_regime.regime != detection.regime:
                    self.detector_metrics['regime_changes_detected'] += 1
                    self.logger_manager.log_info(f"🔄 Cambio de régimen detectado en {symbol}: "
                                               f"{old_regime.regime.value} → {detection.regime.value}")
                
                self.detector_metrics['total_detections'] += 1
            
            self.logger_manager.log_info(f"🎯 Régimen detectado: {symbol} - {primary_regime.value} "
                                       f"(Confianza: {confidence.name}, {probability:.1%})")
            
            return detection
            
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, 
                                                 {"symbol": symbol, "timeframe": timeframe})
            return None
    
    def _analyze_volatility_regime(self, volatility: float) -> MarketRegime:
        """Analizar régimen basado en volatilidad"""
        try:
            if volatility > self.detection_config['volatility_threshold_high']:
                return MarketRegime.HIGH_VOLATILITY
            elif volatility < self.detection_config['volatility_threshold_low']:
                return MarketRegime.LOW_VOLATILITY
            else:
                return MarketRegime.RANGING
                
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"volatility": volatility})
            return MarketRegime.RANGING
    
    def _analyze_trend_regime(self, trend_data: Dict[str, Any]) -> MarketRegime:
        """Analizar régimen basado en tendencia"""
        try:
            if not trend_data:
                return MarketRegime.RANGING
            
            trend_strength = trend_data.get('trend_strength', 0.0)
            trend_direction = trend_data.get('trend_direction', 0)
            
            if abs(trend_strength) > self.detection_config['trend_strength_threshold']:
                if trend_direction > 0:
                    return MarketRegime.TRENDING_UP
                else:
                    return MarketRegime.TRENDING_DOWN
            elif abs(trend_strength) < self.detection_config['ranging_threshold']:
                return MarketRegime.RANGING
            else:
                return MarketRegime.CONSOLIDATION
                
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"trend_data": trend_data})
            return MarketRegime.RANGING
    
    def _analyze_momentum_regime(self, market_summary: Dict[str, Any]) -> MarketRegime:
        """Analizar régimen basado en momentum"""
        try:
            momentum = market_summary.get('momentum', 0.0)
            volume_profile = market_summary.get('volume_profile', 1.0)
            
            # Detectar breakout
            if abs(momentum) > self.detection_config['breakout_threshold'] and volume_profile > 1.2:
                return MarketRegime.BREAKOUT
            
            # Detectar reversal
            elif abs(momentum) > self.detection_config['reversal_threshold'] and volume_profile < 0.8:
                return MarketRegime.REVERSAL
            
            # Default a consolidación
            else:
                return MarketRegime.CONSOLIDATION
                
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"market_summary": market_summary})
            return MarketRegime.CONSOLIDATION
    
    def _combine_regime_analysis(self, volatility_regime: MarketRegime, 
                               trend_regime: MarketRegime, 
                               momentum_regime: MarketRegime) -> Tuple[MarketRegime, RegimeConfidence, float]:
        """Combinar análisis de diferentes factores"""
        try:
            # Matriz de pesos para diferentes regímenes
            regime_weights = {
                MarketRegime.TRENDING_UP: 0.0,
                MarketRegime.TRENDING_DOWN: 0.0,
                MarketRegime.RANGING: 0.0,
                MarketRegime.HIGH_VOLATILITY: 0.0,
                MarketRegime.LOW_VOLATILITY: 0.0,
                MarketRegime.BREAKOUT: 0.0,
                MarketRegime.REVERSAL: 0.0,
                MarketRegime.CONSOLIDATION: 0.0
            }
            
            # Asignar pesos basados en análisis
            regime_weights[volatility_regime] += 0.3
            regime_weights[trend_regime] += 0.4
            regime_weights[momentum_regime] += 0.3
            
            # Determinar régimen dominante
            primary_regime = max(regime_weights.keys(), key=lambda k: regime_weights[k])
            max_weight = regime_weights[primary_regime]
            
            # Calcular confianza
            if max_weight >= 0.8:
                confidence = RegimeConfidence.VERY_HIGH
                probability = 0.9
            elif max_weight >= 0.6:
                confidence = RegimeConfidence.HIGH
                probability = 0.8
            elif max_weight >= 0.4:
                confidence = RegimeConfidence.MEDIUM
                probability = 0.6
            else:
                confidence = RegimeConfidence.LOW
                probability = 0.4
            
            return primary_regime, confidence, probability
            
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, 
                                                 {"regimes": [volatility_regime, trend_regime, momentum_regime]})
            return MarketRegime.RANGING, RegimeConfidence.LOW, 0.5
    
    def analyze_regime_stability(self, symbol: str, timeframe: str, 
                               lookback_periods: int = 10) -> Optional[RegimeAnalysis]:
        """Analizar estabilidad del régimen"""
        try:
            key = f"{symbol}_{timeframe}"
            current_regime = self.current_regimes.get(key)
            
            if not current_regime:
                # Detectar régimen actual si no existe
                current_regime = self.detect_market_regime(symbol, timeframe)
            
            if not current_regime:
                raise ValueError(f"No se pudo detectar régimen para {symbol} {timeframe}")
            
            # Obtener historial reciente
            recent_history = [d for d in self.regime_history 
                            if d.symbol == symbol and d.timeframe == timeframe][-lookback_periods:]
            
            # Calcular estabilidad
            regime_changes = 0
            if len(recent_history) > 1:
                regime_changes = sum(1 for i in range(1, len(recent_history))
                                   if recent_history[i].regime != recent_history[i-1].regime)
                stability_score = 1.0 - (regime_changes / len(recent_history))
            else:
                stability_score = 1.0
            
            # Determinar régimen anterior
            previous_regime = recent_history[-2] if len(recent_history) >= 2 else None
            
            # Generar forecast simple
            forecast = self._forecast_regime(recent_history)
            
            # Generar recomendaciones
            recommendations = self._generate_recommendations(current_regime, stability_score)
            
            analysis = RegimeAnalysis(
                current_regime=current_regime,
                previous_regime=previous_regime,
                regime_changes=regime_changes,
                stability_score=stability_score,
                forecast=forecast,
                recommendations=recommendations
            )
            
            return analysis
            
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, 
                                                 {"symbol": symbol, "timeframe": timeframe})
            # Crear análisis básico en caso de error
            current_regime = self.current_regimes.get(f"{symbol}_{timeframe}")
            if current_regime:
                return RegimeAnalysis(
                    current_regime=current_regime,
                    previous_regime=None,
                    regime_changes=0,
                    stability_score=0.0,
                    forecast=None,
                    recommendations=["Error en análisis: usar gestión conservadora"]
                )
            return None
    
    def _forecast_regime(self, history: List[RegimeDetection]) -> Optional[MarketRegime]:
        """Forecasting simple de próximo régimen"""
        try:
            if len(history) < 3:
                return None
            
            # Análisis de patrones simples
            recent_regimes = [d.regime for d in history[-3:]]
            
            # Si hay estabilidad, mantener régimen
            if len(set(recent_regimes)) == 1:
                return recent_regimes[0]
            
            # Si hay alternancia, predecir siguiente
            if len(recent_regimes) >= 2:
                if recent_regimes[-1] == MarketRegime.TRENDING_UP and recent_regimes[-2] == MarketRegime.RANGING:
                    return MarketRegime.TRENDING_UP
                elif recent_regimes[-1] == MarketRegime.RANGING and recent_regimes[-2] == MarketRegime.TRENDING_UP:
                    return MarketRegime.TRENDING_DOWN
            
            # Default: mantener régimen actual
            return recent_regimes[-1]
            
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"history_count": len(history)})
            return None
    
    def _generate_recommendations(self, regime: RegimeDetection, stability: float) -> List[str]:
        """Generar recomendaciones basadas en régimen"""
        try:
            recommendations = []
            
            # Recomendaciones por tipo de régimen
            if regime.regime == MarketRegime.TRENDING_UP:
                recommendations.append("Considerar estrategias de trend following alcistas")
                recommendations.append("Evitar ventas en corto agresivas")
            elif regime.regime == MarketRegime.TRENDING_DOWN:
                recommendations.append("Considerar estrategias de trend following bajistas")
                recommendations.append("Evitar compras agresivas")
            elif regime.regime == MarketRegime.RANGING:
                recommendations.append("Implementar estrategias de mean reversion")
                recommendations.append("Usar niveles de soporte y resistencia")
            elif regime.regime == MarketRegime.HIGH_VOLATILITY:
                recommendations.append("Reducir tamaño de posición")
                recommendations.append("Ampliar stops y targets")
            elif regime.regime == MarketRegime.BREAKOUT:
                recommendations.append("Preparar estrategias de breakout")
                recommendations.append("Monitorear volumen de confirmación")
            
            # Recomendaciones por estabilidad
            if stability < 0.5:
                recommendations.append("Régimen inestable: usar gestión de riesgo conservadora")
                recommendations.append("Considerar reducir exposición temporal")
            elif stability > 0.8:
                recommendations.append("Régimen estable: oportunidad para posiciones más grandes")
            
            return recommendations
            
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"regime": regime.regime})
            return ["Error generando recomendaciones"]
    
    def start_detection_service(self, symbols: List[str], timeframes: List[str]) -> bool:
        """Iniciar servicio de detección automática"""
        try:
            if self.detection_running:
                self.logger_manager.log_warning("⚠️ Servicio de detección ya está ejecutándose")
                return True
            
            self.detection_running = True
            self.is_active = True
            
            # Iniciar thread de detección
            self.detection_thread = threading.Thread(
                target=self._detection_service_loop,
                args=(symbols, timeframes),
                daemon=True
            )
            self.detection_thread.start()
            
            self.logger_manager.log_info("🚀 Servicio de detección de regímenes iniciado")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, 
                                                 {"symbols": symbols, "timeframes": timeframes})
            self.detection_running = False
            return False
    
    def stop_detection_service(self) -> bool:
        """Detener servicio de detección"""
        try:
            self.detection_running = False
            self.is_active = False
            
            if self.detection_thread and self.detection_thread.is_alive():
                self.detection_thread.join(timeout=5.0)
            
            self.logger_manager.log_info("⏹️ Servicio de detección de regímenes detenido")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"operation": "stop_service"})
            return False
    
    def _detection_service_loop(self, symbols: List[str], timeframes: List[str]):
        """Loop principal del servicio de detección"""
        try:
            while self.detection_running:
                try:
                    # Detectar regímenes para todos los símbolos y timeframes
                    for symbol in symbols:
                        for timeframe in timeframes:
                            detection = self.detect_market_regime(symbol, timeframe)
                            
                            if detection:
                                # Actualizar métricas
                                self._update_detector_metrics()
                    
                    # Actualizar timestamp
                    self.last_update = datetime.now()
                    
                    # Pausa entre ciclos (30 segundos)
                    time.sleep(30.0)
                    
                except Exception as e:
                    self.error_manager.handle_system_error("MarketRegimeDetector", e, {"location": "service_loop"})
                    time.sleep(60.0)  # Pausa más larga en caso de error
                    
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"location": "service_loop_critical"})
            self.detection_running = False
    
    def _update_detector_metrics(self):
        """Actualizar métricas del detector"""
        try:
            with self.detection_lock:
                # Confianza promedio
                if self.regime_history:
                    avg_confidence = sum(d.confidence.value for d in self.regime_history) / len(self.regime_history)
                    self.detector_metrics['avg_detection_confidence'] = avg_confidence
                
                # Conteo de regímenes activos
                self.detector_metrics['active_regimes_count'] = len(self.current_regimes)
                
                # Régimen más común
                if self.regime_history:
                    regime_counts = {}
                    for detection in self.regime_history:
                        regime = detection.regime.value
                        regime_counts[regime] = regime_counts.get(regime, 0) + 1
                    
                    most_common = max(regime_counts.keys(), key=lambda k: regime_counts[k])
                    self.detector_metrics['most_common_regime'] = most_common
            
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"location": "update_metrics"})
    
    def get_detector_status(self) -> Dict[str, Any]:
        """Obtener estado completo del detector"""
        try:
            with self.detection_lock:
                status = {
                    'component_id': self.component_id,
                    'version': self.version,
                    'is_active': self.is_active,
                    'detection_running': self.detection_running,
                    'last_update': self.last_update.isoformat() if self.last_update else None,
                    'current_regimes_count': len(self.current_regimes),
                    'regime_history_count': len(self.regime_history),
                    'metrics': dict(self.detector_metrics),
                    'active_regimes': {k: v.regime.value for k, v in self.current_regimes.items()}
                }
            
            return status
            
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"location": "get_status"})
            return {'error': str(e)}
    
    def get_current_regimes(self) -> Dict[str, RegimeDetection]:
        """Obtener regímenes actuales"""
        try:
            with self.detection_lock:
                return dict(self.current_regimes)
                
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"location": "get_regimes"})
            return {}
    
    def cleanup(self):
        """Limpieza de recursos"""
        try:
            self.stop_detection_service()
            
            with self.detection_lock:
                self.current_regimes.clear()
                self.regime_history.clear()
                self.regime_statistics.clear()
            
            self.logger_manager.log_info(f"🧹 {self.component_id} limpieza completada")
            
        except Exception as e:
            self.error_manager.handle_system_error("MarketRegimeDetector", e, {"location": "cleanup"})

if __name__ == "__main__":
    # Demo básico del MarketRegimeDetector
    print("🎯 MARKET REGIME DETECTOR - PUERTA-S2-REGIME")
    print("=" * 50)
    
    try:
        # Inicializar usando el protocolo SÓTANO 1
        detector = MarketRegimeDetector()
        
        # Detectar régimen para EURUSD
        detection = detector.detect_market_regime("EURUSD", "H1")
        
        if detection:
            print(f"🎯 Régimen detectado: {detection.regime.value}")
            print(f"📊 Confianza: {detection.confidence.name} ({detection.probability:.1%})")
            print(f"🔍 Indicadores: {detection.indicators}")
        
        # Analizar estabilidad
        analysis = detector.analyze_regime_stability("EURUSD", "H1")
        
        if analysis:
            print(f"\n📈 Estabilidad: {analysis.stability_score:.1%}")
            print(f"🔄 Cambios de régimen: {analysis.regime_changes}")
            print("💡 Recomendaciones:")
            for rec in analysis.recommendations:
                print(f"   - {rec}")
        
        # Cleanup
        detector.cleanup()
        print("\n✅ Demo completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
