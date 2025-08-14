"""
📊 OFICINA DE ANÁLISIS - PISO 3
Módulos especializados en análisis avanzado de calidad FVG

Componentes:
- FVGQualityAnalyzer: Análisis de calidad y scoring
- FVGPredictor: Predicción de llenado y comportamiento
- SessionAnalyzer: Análisis por sesiones de trading
- MarketRegimeDetector: Detección de regímenes de mercado
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FVGQualityAnalyzer:
    """
    🎯 ANALIZADOR DE CALIDAD FVG
    
    Evalúa la calidad de FVGs basado en múltiples criterios:
    - Tamaño relativo del gap
    - Contexto de mercado
    - Volumen asociado
    - Estructura de velas
    """
    
    def __init__(self, config=None):
        """
        Inicializa el analizador de calidad
        
        Args:
            config: Configuración personalizada
        """
        self.config = config or {
            "min_quality_score": 6.0,
            "volume_weight": 0.2,
            "structure_weight": 0.3,
            "context_weight": 0.3,
            "size_weight": 0.2
        }
        
        print("🎯 FVGQualityAnalyzer inicializado")
    
    def analyze_fvg_quality(self, fvg, market_context=None, volume_data=None):
        """
        Analiza la calidad de un FVG específico
        
        Args:
            fvg: FVG a analizar
            market_context: Contexto de mercado
            volume_data: Datos de volumen
            
        Returns:
            Dict con score y detalles del análisis
        """
        scores = {}
        
        # 1. Análisis de tamaño
        scores['size'] = self._analyze_size_quality(fvg)
        
        # 2. Análisis de estructura
        scores['structure'] = self._analyze_structure_quality(fvg)
        
        # 3. Análisis de contexto
        scores['context'] = self._analyze_context_quality(fvg, market_context)
        
        # 4. Análisis de volumen
        scores['volume'] = self._analyze_volume_quality(fvg, volume_data)
        
        # Cálculo de score final ponderado
        final_score = (
            scores['size'] * self.config['size_weight'] +
            scores['structure'] * self.config['structure_weight'] +
            scores['context'] * self.config['context_weight'] +
            scores['volume'] * self.config['volume_weight']
        )
        
        return {
            'final_score': final_score,
            'scores': scores,
            'quality_level': self._get_quality_level(final_score),
            'analysis_time': datetime.now()
        }
    
    def _analyze_size_quality(self, fvg):
        """Analiza la calidad basada en el tamaño del gap"""
        if hasattr(fvg, 'gap_size_pips'):
            pips = fvg.gap_size_pips
            if pips >= 10:
                return 10.0
            elif pips >= 5:
                return 8.0
            elif pips >= 2:
                return 6.0
            elif pips >= 1:
                return 4.0
            else:
                return 2.0
        return 5.0
    
    def _analyze_structure_quality(self, fvg):
        """Analiza la calidad basada en la estructura de velas"""
        # Análisis de la fuerza de las velas de formación
        if hasattr(fvg, 'formation_candles') and len(fvg.formation_candles) >= 3:
            candles = fvg.formation_candles
            
            # Vela central (impulso)
            middle_candle = candles[1]
            body_size = abs(middle_candle['close'] - middle_candle['open'])
            total_range = middle_candle['high'] - middle_candle['low']
            
            if total_range > 0:
                body_ratio = body_size / total_range
                if body_ratio >= 0.8:
                    return 9.0
                elif body_ratio >= 0.6:
                    return 7.0
                elif body_ratio >= 0.4:
                    return 5.0
                else:
                    return 3.0
        
        return 5.0
    
    def _analyze_context_quality(self, fvg, market_context):
        """Analiza la calidad basada en el contexto de mercado"""
        if not market_context:
            return 5.0
        
        # Análisis de tendencia
        trend_alignment = market_context.get('trend_alignment', 0.5)
        
        # Análisis de soporte/resistencia
        sr_proximity = market_context.get('sr_proximity', 0.5)
        
        # Análisis de momento
        momentum = market_context.get('momentum', 0.5)
        
        context_score = (trend_alignment + sr_proximity + momentum) / 3 * 10
        return min(10.0, max(0.0, context_score))
    
    def _analyze_volume_quality(self, fvg, volume_data):
        """Analiza la calidad basada en el volumen"""
        if not volume_data or not hasattr(fvg, 'formation_candles'):
            return 5.0
        
        # Obtener volumen de vela de impulso
        if len(fvg.formation_candles) >= 2:
            impulse_volume = fvg.formation_candles[1].get('volume', 0)
            avg_volume = volume_data.get('avg_volume', 1)
            
            if avg_volume > 0:
                volume_ratio = impulse_volume / avg_volume
                if volume_ratio >= 2.0:
                    return 9.0
                elif volume_ratio >= 1.5:
                    return 7.0
                elif volume_ratio >= 1.0:
                    return 5.0
                else:
                    return 3.0
        
        return 5.0
    
    def _get_quality_level(self, score):
        """Convierte score numérico a nivel cualitativo"""
        if score >= 8.5:
            return "EXCELENTE"
        elif score >= 7.0:
            return "BUENA"
        elif score >= 5.5:
            return "REGULAR"
        elif score >= 4.0:
            return "BAJA"
        else:
            return "MUY_BAJA"


class FVGPredictor:
    """
    🔮 PREDICTOR DE COMPORTAMIENTO FVG
    
    Predice probabilidades de llenado y comportamiento futuro
    """
    
    def __init__(self):
        """Inicializa el predictor"""
        self.historical_data = []
        print("🔮 FVGPredictor inicializado")
    
    def predict_fill_probability(self, fvg, market_conditions=None):
        """
        Predice la probabilidad de llenado de un FVG
        
        Args:
            fvg: FVG a analizar
            market_conditions: Condiciones actuales del mercado
            
        Returns:
            Dict con probabilidades y factores
        """
        factors = {}
        
        # Factor de distancia al precio actual
        factors['distance'] = self._calculate_distance_factor(fvg, market_conditions)
        
        # Factor de tendencia
        factors['trend'] = self._calculate_trend_factor(fvg, market_conditions)
        
        # Factor de tiempo
        factors['time'] = self._calculate_time_factor(fvg)
        
        # Factor de tamaño
        factors['size'] = self._calculate_size_factor(fvg)
        
        # Probabilidad combinada
        probability = (
            factors['distance'] * 0.3 +
            factors['trend'] * 0.25 +
            factors['time'] * 0.25 +
            factors['size'] * 0.2
        )
        
        return {
            'fill_probability': min(0.95, max(0.05, probability)),
            'factors': factors,
            'confidence': self._calculate_confidence(factors),
            'estimated_time_to_fill': self._estimate_time_to_fill(fvg, probability)
        }
    
    def _calculate_distance_factor(self, fvg, market_conditions):
        """Calcula factor basado en distancia al precio actual"""
        if not market_conditions or not hasattr(fvg, 'gap_low'):
            return 0.5
        
        current_price = market_conditions.get('current_price', 0)
        if current_price == 0:
            return 0.5
        
        if fvg.type == 'BULLISH':
            distance = abs(current_price - fvg.gap_low) / current_price
        else:
            distance = abs(current_price - fvg.gap_high) / current_price
        
        # Probabilidad inversamente proporcional a distancia
        if distance <= 0.001:  # Muy cerca
            return 0.9
        elif distance <= 0.005:  # Cerca
            return 0.7
        elif distance <= 0.01:  # Moderado
            return 0.5
        else:  # Lejos
            return 0.2
    
    def _calculate_trend_factor(self, fvg, market_conditions):
        """Calcula factor basado en alineación con tendencia"""
        if not market_conditions:
            return 0.5
        
        trend = market_conditions.get('trend', 'NEUTRAL')
        
        if (fvg.type == 'BULLISH' and trend == 'BULLISH') or \
           (fvg.type == 'BEARISH' and trend == 'BEARISH'):
            return 0.8
        elif trend == 'NEUTRAL':
            return 0.5
        else:
            return 0.3
    
    def _calculate_time_factor(self, fvg):
        """Calcula factor basado en tiempo transcurrido"""
        if hasattr(fvg, 'formation_time'):
            # Los FVGs más recientes tienen mayor probabilidad
            hours_elapsed = (datetime.now() - pd.to_datetime(fvg.formation_time)).total_seconds() / 3600
            
            if hours_elapsed <= 4:
                return 0.8
            elif hours_elapsed <= 24:
                return 0.6
            elif hours_elapsed <= 72:
                return 0.4
            else:
                return 0.2
        
        return 0.5
    
    def _calculate_size_factor(self, fvg):
        """Calcula factor basado en tamaño del gap"""
        if hasattr(fvg, 'gap_size_pips'):
            pips = fvg.gap_size_pips
            if pips >= 15:
                return 0.3  # Gaps muy grandes son difíciles de llenar
            elif pips >= 8:
                return 0.6
            elif pips >= 3:
                return 0.8
            else:
                return 0.9  # Gaps pequeños se llenan fácilmente
        
        return 0.5
    
    def _calculate_confidence(self, factors):
        """Calcula nivel de confianza de la predicción"""
        variance = np.var(list(factors.values()))
        confidence = 1.0 - min(0.5, variance)
        return confidence
    
    def _estimate_time_to_fill(self, fvg, probability):
        """Estima tiempo para llenado basado en probabilidad"""
        if probability >= 0.8:
            return "1-4 horas"
        elif probability >= 0.6:
            return "4-12 horas"
        elif probability >= 0.4:
            return "12-48 horas"
        else:
            return "48+ horas o nunca"


class SessionAnalyzer:
    """
    🕒 ANALIZADOR DE SESIONES
    
    Analiza patrones FVG por sesiones de trading
    """
    
    def __init__(self):
        """Inicializa el analizador de sesiones"""
        self.session_configs = {
            'ASIA': {'start': 21, 'end': 6},     # 21:00-06:00 UTC
            'LONDON': {'start': 7, 'end': 16},   # 07:00-16:00 UTC  
            'NY': {'start': 13, 'end': 22},      # 13:00-22:00 UTC
            'OVERLAP': {'start': 13, 'end': 16}  # London-NY overlap
        }
        print("🕒 SessionAnalyzer inicializado")
    
    def analyze_session_patterns(self, fvgs_data):
        """
        Analiza patrones de FVGs por sesión
        
        Args:
            fvgs_data: Lista de FVGs con timestamps
            
        Returns:
            Dict con análisis por sesión
        """
        session_stats = {}
        
        for session_name, config in self.session_configs.items():
            session_fvgs = self._filter_fvgs_by_session(fvgs_data, config)
            
            if session_fvgs:
                session_stats[session_name] = {
                    'total_fvgs': len(session_fvgs),
                    'bullish_count': sum(1 for fvg in session_fvgs if fvg.type == 'BULLISH'),
                    'bearish_count': sum(1 for fvg in session_fvgs if fvg.type == 'BEARISH'),
                    'avg_size_pips': np.mean([fvg.gap_size_pips for fvg in session_fvgs if hasattr(fvg, 'gap_size_pips')]),
                    'largest_fvg_pips': max([fvg.gap_size_pips for fvg in session_fvgs if hasattr(fvg, 'gap_size_pips')], default=0),
                    'session_bias': self._calculate_session_bias(session_fvgs)
                }
        
        return session_stats
    
    def _filter_fvgs_by_session(self, fvgs_data, session_config):
        """Filtra FVGs por sesión específica"""
        session_fvgs = []
        
        for fvg in fvgs_data:
            if hasattr(fvg, 'formation_time'):
                fvg_time = pd.to_datetime(fvg.formation_time)
                hour = fvg_time.hour
                
                start_hour = session_config['start']
                end_hour = session_config['end']
                
                # Manejar sesiones que cruzan medianoche
                if start_hour > end_hour:
                    if hour >= start_hour or hour <= end_hour:
                        session_fvgs.append(fvg)
                else:
                    if start_hour <= hour <= end_hour:
                        session_fvgs.append(fvg)
        
        return session_fvgs
    
    def _calculate_session_bias(self, session_fvgs):
        """Calcula el bias direccional de la sesión"""
        if not session_fvgs:
            return "NEUTRAL"
        
        bullish_count = sum(1 for fvg in session_fvgs if fvg.type == 'BULLISH')
        bearish_count = len(session_fvgs) - bullish_count
        
        if bullish_count > bearish_count * 1.5:
            return "BULLISH"
        elif bearish_count > bullish_count * 1.5:
            return "BEARISH"
        else:
            return "NEUTRAL"


class MarketRegimeDetector:
    """
    📈 DETECTOR DE REGÍMENES DE MERCADO
    
    Identifica regímenes de mercado para contexto FVG
    """
    
    def __init__(self):
        """Inicializa el detector de regímenes"""
        print("📈 MarketRegimeDetector inicializado")
    
    def detect_current_regime(self, price_data, fvg_data=None):
        """
        Detecta el régimen actual de mercado
        
        Args:
            price_data: Datos de precios
            fvg_data: Datos de FVGs para contexto
            
        Returns:
            Dict con información del régimen
        """
        # Análisis de volatilidad
        volatility = self._calculate_volatility(price_data)
        
        # Análisis de tendencia
        trend = self._calculate_trend(price_data)
        
        # Análisis de FVG density
        fvg_density = self._calculate_fvg_density(fvg_data) if fvg_data else 0.5
        
        # Determinar régimen
        regime = self._determine_regime(volatility, trend, fvg_density)
        
        return {
            'regime': regime,
            'volatility_level': volatility,
            'trend_strength': trend,
            'fvg_density': fvg_density,
            'confidence': self._calculate_regime_confidence(volatility, trend, fvg_density)
        }
    
    def _calculate_volatility(self, price_data):
        """Calcula nivel de volatilidad"""
        if len(price_data) < 20:
            return 0.5
        
        returns = price_data['close'].pct_change().dropna()
        volatility = returns.std()
        
        # Normalizar a escala 0-1
        if volatility < 0.001:
            return 0.2  # Baja volatilidad
        elif volatility < 0.005:
            return 0.5  # Volatilidad media
        else:
            return 0.8  # Alta volatilidad
    
    def _calculate_trend(self, price_data):
        """Calcula fuerza de tendencia"""
        if len(price_data) < 50:
            return 0.5
        
        # Simple moving averages
        sma_20 = price_data['close'].rolling(20).mean()
        sma_50 = price_data['close'].rolling(50).mean()
        
        current_price = price_data['close'].iloc[-1]
        sma_20_current = sma_20.iloc[-1]
        sma_50_current = sma_50.iloc[-1]
        
        if current_price > sma_20_current > sma_50_current:
            return 0.8  # Tendencia alcista fuerte
        elif current_price < sma_20_current < sma_50_current:
            return 0.2  # Tendencia bajista fuerte
        else:
            return 0.5  # Sin tendencia clara
    
    def _calculate_fvg_density(self, fvg_data):
        """Calcula densidad de FVGs"""
        if not fvg_data:
            return 0.5
        
        # Contar FVGs recientes (últimas 24 horas)
        recent_fvgs = [fvg for fvg in fvg_data if hasattr(fvg, 'formation_time')]
        
        if len(recent_fvgs) > 10:
            return 0.8  # Alta densidad
        elif len(recent_fvgs) > 5:
            return 0.6  # Media densidad
        else:
            return 0.3  # Baja densidad
    
    def _determine_regime(self, volatility, trend, fvg_density):
        """Determina el régimen de mercado"""
        if volatility > 0.7 and fvg_density > 0.7:
            return "HIGH_VOLATILITY_BREAKOUT"
        elif volatility < 0.3 and fvg_density < 0.4:
            return "LOW_VOLATILITY_RANGE"
        elif trend > 0.7 or trend < 0.3:
            return "TRENDING"
        else:
            return "RANGING"
    
    def _calculate_regime_confidence(self, volatility, trend, fvg_density):
        """Calcula confianza en la detección del régimen"""
        # Confianza basada en claridad de las señales
        signals = [volatility, abs(trend - 0.5) * 2, abs(fvg_density - 0.5) * 2]
        confidence = np.mean(signals)
        return min(0.95, max(0.5, confidence))


# Configuración de la oficina
ANALISIS_CONFIG = {
    "quality_analyzer": {
        "min_quality_score": 6.0,
        "weights": {
            "volume": 0.2,
            "structure": 0.3,
            "context": 0.3,
            "size": 0.2
        }
    },
    "predictor": {
        "max_prediction_horizon": "72h",
        "confidence_threshold": 0.7
    },
    "session_analyzer": {
        "timezone": "UTC",
        "min_fvgs_for_analysis": 5
    },
    "regime_detector": {
        "volatility_periods": [20, 50],
        "trend_periods": [20, 50, 100]
    }
}

__all__ = [
    "FVGQualityAnalyzer",
    "FVGPredictor", 
    "SessionAnalyzer",
    "MarketRegimeDetector",
    "ANALISIS_CONFIG"
]
