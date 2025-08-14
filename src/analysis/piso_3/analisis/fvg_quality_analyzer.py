"""
🏢 PISO 3 - OFICINA ANÁLISIS
FVG Quality Analyzer - Sistema de evaluación de calidad de FVGs
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Configurar rutas
current_dir = Path(__file__).parent
project_root = current_dir.parents[3]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "core"))

# Imports centralizados
from data_manager import DataManager
from logger_manager import LoggerManager

class FVGQuality(Enum):
    """Niveles de calidad de FVG"""
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"
    DESCARTABLE = "DESCARTABLE"

@dataclass
class FVGQualityScore:
    """Score de calidad de un FVG"""
    fvg_id: str
    score_total: float
    calidad: FVGQuality
    factores: Dict[str, float]
    recomendacion: str
    confianza: float

class FVGQualityAnalyzer:
    """
    Analizador de calidad de FVGs usando múltiples factores técnicos
    
    FACTORES DE CALIDAD:
    1. Tamaño del FVG (relative size)
    2. Velocidad de formación (pips/minuto)
    3. Volumen en la zona
    4. Contexto de mercado (trending/ranging)
    5. Distancia desde precio actual
    6. Confluencias técnicas
    7. Sesión de trading
    8. Volatilidad del momento
    """
    
    def __init__(self):
        self.logger = LoggerManager().get_logger("FVGQuality")
        self.data_manager = DataManager()
        
        # Pesos para cada factor de calidad
        self.weight_factors = {
            'size_factor': 0.25,        # Tamaño relativo del FVG
            'speed_factor': 0.20,       # Velocidad de formación
            'volume_factor': 0.15,      # Volumen en la zona
            'context_factor': 0.15,     # Contexto de mercado
            'distance_factor': 0.10,    # Distancia desde precio actual
            'confluence_factor': 0.10,  # Confluencias técnicas
            'session_factor': 0.05      # Sesión de trading
        }
        
        # Umbrales de calidad
        self.quality_thresholds = {
            'ALTA': 0.75,
            'MEDIA': 0.50,
            'BAJA': 0.25
        }
        
        self.logger.info("FVGQualityAnalyzer inicializado")

    def analyze_fvg_quality(self, fvg_data: Dict, symbol: str = "EURUSD") -> FVGQualityScore:
        """
        Analiza la calidad de un FVG específico
        
        Args:
            fvg_data: Datos del FVG a analizar
            symbol: Símbolo del instrumento
            
        Returns:
            FVGQualityScore con el análisis completo
        """
        try:
            factors = {}
            
            # 1. Factor de tamaño
            factors['size_factor'] = self._calculate_size_factor(fvg_data, symbol)
            
            # 2. Factor de velocidad
            factors['speed_factor'] = self._calculate_speed_factor(fvg_data)
            
            # 3. Factor de volumen
            factors['volume_factor'] = self._calculate_volume_factor(fvg_data, symbol)
            
            # 4. Factor de contexto
            factors['context_factor'] = self._calculate_context_factor(fvg_data, symbol)
            
            # 5. Factor de distancia
            factors['distance_factor'] = self._calculate_distance_factor(fvg_data, symbol)
            
            # 6. Factor de confluencia
            factors['confluence_factor'] = self._calculate_confluence_factor(fvg_data, symbol)
            
            # 7. Factor de sesión
            factors['session_factor'] = self._calculate_session_factor(fvg_data)
            
            # Calcular score total ponderado
            score_total = sum(
                factors[factor] * self.weight_factors[factor] 
                for factor in factors
            )
            
            # Determinar calidad
            calidad = self._determine_quality(score_total)
            
            # Generar recomendación
            recomendacion = self._generate_recommendation(score_total, factors, calidad)
            
            # Calcular confianza
            confianza = self._calculate_confidence(factors)
            
            quality_score = FVGQualityScore(
                fvg_id=fvg_data.get('id', 'unknown'),
                score_total=score_total,
                calidad=calidad,
                factores=factors,
                recomendacion=recomendacion,
                confianza=confianza
            )
            
            self.logger.info(f"FVG {quality_score.fvg_id}: Score={score_total:.3f}, Calidad={calidad.value}")
            
            return quality_score
            
        except Exception as e:
            self.logger.error(f"Error analizando calidad FVG: {e}")
            # Retornar score por defecto
            return FVGQualityScore(
                fvg_id=fvg_data.get('id', 'error'),
                score_total=0.0,
                calidad=FVGQuality.DESCARTABLE,
                factores={},
                recomendacion="Error en análisis",
                confianza=0.0
            )

    def _calculate_size_factor(self, fvg_data: Dict, symbol: str) -> float:
        """Calcula factor de calidad basado en el tamaño del FVG"""
        try:
            # Obtener ATR del período para normalizar
            df_ohlc = self.data_manager.get_ohlc_data(symbol, 'H1', 24)
            if df_ohlc is None:
                return 0.5
                
            atr = self._calculate_atr(df_ohlc, period=14)
            current_atr = atr.iloc[-1] if len(atr) > 0 else 0.0001
            
            # Tamaño del FVG en pips
            fvg_size = abs(fvg_data.get('high', 0) - fvg_data.get('low', 0))
            
            # Normalizar por ATR
            size_ratio = fvg_size / current_atr if current_atr > 0 else 0
            
            # Score: mejor entre 0.3 y 1.5 ATR
            if size_ratio < 0.1:
                return 0.1  # Muy pequeño
            elif size_ratio < 0.3:
                return 0.4  # Pequeño
            elif size_ratio <= 1.5:
                return 1.0  # Tamaño óptimo
            elif size_ratio <= 3.0:
                return 0.7  # Grande pero aceptable
            else:
                return 0.3  # Muy grande
                
        except Exception as e:
            self.logger.error(f"Error calculando size_factor: {e}")
            return 0.5

    def _calculate_speed_factor(self, fvg_data: Dict) -> float:
        """Calcula factor basado en la velocidad de formación del FVG"""
        try:
            # Tiempo de formación (asumiendo que tenemos timestamps)
            start_time = fvg_data.get('start_time', datetime.now())
            end_time = fvg_data.get('end_time', datetime.now())
            
            if isinstance(start_time, str):
                start_time = pd.to_datetime(start_time)
            if isinstance(end_time, str):
                end_time = pd.to_datetime(end_time)
                
            formation_minutes = (end_time - start_time).total_seconds() / 60
            
            # FVG size
            fvg_size = abs(fvg_data.get('high', 0) - fvg_data.get('low', 0))
            
            # Velocidad en pips por minuto
            speed = fvg_size / formation_minutes if formation_minutes > 0 else 0
            
            # Score basado en velocidad (FVGs rápidos son mejores)
            if speed > 0.001:  # Muy rápido
                return 1.0
            elif speed > 0.0005:  # Rápido
                return 0.8
            elif speed > 0.0002:  # Normal
                return 0.6
            else:  # Lento
                return 0.3
                
        except Exception as e:
            self.logger.error(f"Error calculando speed_factor: {e}")
            return 0.5

    def _calculate_volume_factor(self, fvg_data: Dict, symbol: str) -> float:
        """Calcula factor basado en el volumen durante la formación"""
        try:
            # Obtener datos de volumen tick
            df_ticks = self.data_manager.get_tick_data(symbol, count=1000)
            if df_ticks is None or len(df_ticks) == 0:
                return 0.5
                
            # Filtrar ticks en el período del FVG
            start_time = fvg_data.get('start_time', datetime.now() - timedelta(hours=1))
            end_time = fvg_data.get('end_time', datetime.now())
            
            if isinstance(start_time, str):
                start_time = pd.to_datetime(start_time)
            if isinstance(end_time, str):
                end_time = pd.to_datetime(end_time)
            
            # Volumen durante la formación del FVG
            mask = (df_ticks.index >= start_time) & (df_ticks.index <= end_time)
            volume_fvg = df_ticks[mask]['volume'].sum() if mask.any() else 0
            
            # Volumen promedio de referencia
            volume_avg = df_ticks['volume'].mean()
            
            # Ratio de volumen
            volume_ratio = volume_fvg / volume_avg if volume_avg > 0 else 1
            
            # Score: más volumen = mejor calidad
            if volume_ratio > 2.0:
                return 1.0
            elif volume_ratio > 1.5:
                return 0.8
            elif volume_ratio > 1.0:
                return 0.6
            else:
                return 0.3
                
        except Exception as e:
            self.logger.error(f"Error calculando volume_factor: {e}")
            return 0.5

    def _calculate_context_factor(self, fvg_data: Dict, symbol: str) -> float:
        """Calcula factor basado en el contexto de mercado"""
        try:
            # Obtener datos para determinar tendencia
            df_ohlc = self.data_manager.get_ohlc_data(symbol, 'H1', 50)
            if df_ohlc is None:
                return 0.5
                
            # Calcular EMAs para tendencia
            ema_20 = df_ohlc['close'].ewm(span=20).mean()
            ema_50 = df_ohlc['close'].ewm(span=50).mean()
            
            current_price = df_ohlc['close'].iloc[-1]
            current_ema20 = ema_20.iloc[-1]
            current_ema50 = ema_50.iloc[-1]
            
            # Determinar contexto
            fvg_type = fvg_data.get('type', 'BULLISH')
            
            # FVG alcista en tendencia alcista = mejor
            # FVG bajista en tendencia bajista = mejor
            if fvg_type == 'BULLISH':
                if current_price > current_ema20 > current_ema50:
                    return 1.0  # Tendencia alcista fuerte
                elif current_price > current_ema20:
                    return 0.7  # Tendencia alcista débil
                else:
                    return 0.3  # Contra tendencia
            else:  # BEARISH
                if current_price < current_ema20 < current_ema50:
                    return 1.0  # Tendencia bajista fuerte
                elif current_price < current_ema20:
                    return 0.7  # Tendencia bajista débil
                else:
                    return 0.3  # Contra tendencia
                    
        except Exception as e:
            self.logger.error(f"Error calculando context_factor: {e}")
            return 0.5

    def _calculate_distance_factor(self, fvg_data: Dict, symbol: str) -> float:
        """Calcula factor basado en la distancia desde el precio actual"""
        try:
            # Precio actual
            current_price = self.data_manager.get_current_price(symbol)
            if current_price is None:
                return 0.5
                
            # Centro del FVG
            fvg_center = (fvg_data.get('high', 0) + fvg_data.get('low', 0)) / 2
            
            # Distancia en pips
            distance = abs(current_price - fvg_center)
            
            # Obtener ATR para normalizar
            df_ohlc = self.data_manager.get_ohlc_data(symbol, 'H1', 24)
            if df_ohlc is None:
                return 0.5
                
            atr = self._calculate_atr(df_ohlc, period=14)
            current_atr = atr.iloc[-1] if len(atr) > 0 else 0.0001
            
            # Ratio de distancia
            distance_ratio = distance / current_atr if current_atr > 0 else 0
            
            # Score: distancia óptima entre 0.5 y 3 ATR
            if distance_ratio < 0.2:
                return 0.3  # Muy cerca
            elif distance_ratio <= 3.0:
                return 1.0  # Distancia óptima
            elif distance_ratio <= 5.0:
                return 0.6  # Lejos pero alcanzable
            else:
                return 0.2  # Muy lejos
                
        except Exception as e:
            self.logger.error(f"Error calculando distance_factor: {e}")
            return 0.5

    def _calculate_confluence_factor(self, fvg_data: Dict, symbol: str) -> float:
        """Calcula factor basado en confluencias técnicas"""
        try:
            confluences = 0
            
            # Obtener datos para análisis técnico
            df_ohlc = self.data_manager.get_ohlc_data(symbol, 'H1', 100)
            if df_ohlc is None:
                return 0.5
                
            fvg_level = (fvg_data.get('high', 0) + fvg_data.get('low', 0)) / 2
            
            # 1. Confluencia con Fibonacci
            recent_high = df_ohlc['high'].tail(50).max()
            recent_low = df_ohlc['low'].tail(50).min()
            fib_levels = self._calculate_fibonacci_levels(recent_high, recent_low)
            
            for level in fib_levels:
                if abs(fvg_level - level) < (recent_high - recent_low) * 0.01:
                    confluences += 1
                    break
                    
            # 2. Confluencia con niveles de soporte/resistencia
            pivot_levels = self._calculate_pivot_levels(df_ohlc)
            for level in pivot_levels:
                if abs(fvg_level - level) < (recent_high - recent_low) * 0.02:
                    confluences += 1
                    break
                    
            # 3. Confluencia con EMAs importantes
            ema_20 = df_ohlc['close'].ewm(span=20).mean().iloc[-1]
            ema_50 = df_ohlc['close'].ewm(span=50).mean().iloc[-1]
            ema_200 = df_ohlc['close'].ewm(span=200).mean().iloc[-1]
            
            for ema in [ema_20, ema_50, ema_200]:
                if abs(fvg_level - ema) < (recent_high - recent_low) * 0.015:
                    confluences += 1
                    break
            
            # Score basado en confluencias
            if confluences >= 3:
                return 1.0
            elif confluences >= 2:
                return 0.8
            elif confluences >= 1:
                return 0.6
            else:
                return 0.3
                
        except Exception as e:
            self.logger.error(f"Error calculando confluence_factor: {e}")
            return 0.5

    def _calculate_session_factor(self, fvg_data: Dict) -> float:
        """Calcula factor basado en la sesión de trading"""
        try:
            fvg_time = fvg_data.get('start_time', datetime.now())
            if isinstance(fvg_time, str):
                fvg_time = pd.to_datetime(fvg_time)
                
            hour_utc = fvg_time.hour
            
            # Sesiones de trading (UTC)
            # London: 8-16, New York: 13-21, Tokyo: 0-8
            if 8 <= hour_utc <= 11:  # London open
                return 1.0
            elif 13 <= hour_utc <= 16:  # London + NY overlap
                return 1.0
            elif 0 <= hour_utc <= 3:  # Tokyo
                return 0.7
            elif 16 <= hour_utc <= 21:  # NY only
                return 0.8
            else:  # Low activity
                return 0.3
                
        except Exception as e:
            self.logger.error(f"Error calculando session_factor: {e}")
            return 0.5

    def _determine_quality(self, score: float) -> FVGQuality:
        """Determina la calidad basada en el score"""
        if score >= self.quality_thresholds['ALTA']:
            return FVGQuality.ALTA
        elif score >= self.quality_thresholds['MEDIA']:
            return FVGQuality.MEDIA
        elif score >= self.quality_thresholds['BAJA']:
            return FVGQuality.BAJA
        else:
            return FVGQuality.DESCARTABLE

    def _generate_recommendation(self, score: float, factors: Dict, quality: FVGQuality) -> str:
        """Genera recomendación basada en el análisis"""
        if quality == FVGQuality.ALTA:
            return "FVG de alta calidad - Recomendado para trading activo"
        elif quality == FVGQuality.MEDIA:
            return "FVG de calidad media - Considerar con confirmaciones adicionales"
        elif quality == FVGQuality.BAJA:
            return "FVG de baja calidad - Usar solo con gestión de riesgo estricta"
        else:
            return "FVG de calidad insuficiente - No recomendado para trading"

    def _calculate_confidence(self, factors: Dict) -> float:
        """Calcula nivel de confianza del análisis"""
        # Confianza basada en la varianza de los factores
        factor_values = list(factors.values())
        if len(factor_values) == 0:
            return 0.0
            
        mean_score = np.mean(factor_values)
        std_score = np.std(factor_values)
        
        # Menor varianza = mayor confianza
        confidence = 1.0 - min(std_score / mean_score if mean_score > 0 else 1.0, 1.0)
        
        return max(0.0, min(1.0, confidence))

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calcula Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        return true_range.rolling(window=period).mean()

    def _calculate_fibonacci_levels(self, high: float, low: float) -> List[float]:
        """Calcula niveles de Fibonacci"""
        diff = high - low
        return [
            low + diff * 0.236,
            low + diff * 0.382,
            low + diff * 0.500,
            low + diff * 0.618,
            low + diff * 0.786
        ]

    def _calculate_pivot_levels(self, df: pd.DataFrame) -> List[float]:
        """Calcula niveles pivot de soporte y resistencia"""
        recent_data = df.tail(20)
        pivot = (recent_data['high'].iloc[-1] + recent_data['low'].iloc[-1] + recent_data['close'].iloc[-1]) / 3
        
        high = recent_data['high'].max()
        low = recent_data['low'].min()
        
        s1 = 2 * pivot - high
        r1 = 2 * pivot - low
        s2 = pivot - (high - low)
        r2 = pivot + (high - low)
        
        return [s2, s1, pivot, r1, r2]

    def batch_analyze_fvgs(self, fvg_list: List[Dict], symbol: str = "EURUSD") -> List[FVGQualityScore]:
        """
        Analiza una lista de FVGs en lote
        
        Args:
            fvg_list: Lista de FVGs a analizar
            symbol: Símbolo del instrumento
            
        Returns:
            Lista de FVGQualityScore ordenada por calidad
        """
        try:
            results = []
            
            for fvg in fvg_list:
                quality_score = self.analyze_fvg_quality(fvg, symbol)
                results.append(quality_score)
            
            # Ordenar por score descendente
            results.sort(key=lambda x: x.score_total, reverse=True)
            
            self.logger.info(f"Análisis en lote completado: {len(results)} FVGs analizados")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error en análisis en lote: {e}")
            return []

    def get_quality_statistics(self, quality_scores: List[FVGQualityScore]) -> Dict:
        """Genera estadísticas de calidad para un conjunto de FVGs"""
        try:
            stats = {
                'total_fvgs': len(quality_scores),
                'score_promedio': np.mean([qs.score_total for qs in quality_scores]),
                'confianza_promedio': np.mean([qs.confianza for qs in quality_scores]),
                'distribucion_calidad': {},
                'top_factores': {}
            }
            
            # Distribución por calidad
            for quality in FVGQuality:
                count = sum(1 for qs in quality_scores if qs.calidad == quality)
                stats['distribucion_calidad'][quality.value] = count
            
            # Top factores que más influyen
            all_factors = {}
            for qs in quality_scores:
                for factor, value in qs.factores.items():
                    if factor not in all_factors:
                        all_factors[factor] = []
                    all_factors[factor].append(value)
            
            for factor, values in all_factors.items():
                stats['top_factores'][factor] = np.mean(values)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error generando estadísticas: {e}")
            return {}


if __name__ == "__main__":
    # Test básico del analizador
    analyzer = FVGQualityAnalyzer()
    
    # Datos de prueba
    test_fvg = {
        'id': 'test_001',
        'type': 'BULLISH',
        'high': 1.0950,
        'low': 1.0930,
        'start_time': datetime.now() - timedelta(hours=2),
        'end_time': datetime.now() - timedelta(hours=1, minutes=45)
    }
    
    # Analizar calidad
    result = analyzer.analyze_fvg_quality(test_fvg)
    
    print(f"🏢 PISO 3 - OFICINA ANÁLISIS")
    print(f"FVG ID: {result.fvg_id}")
    print(f"Score Total: {result.score_total:.3f}")
    print(f"Calidad: {result.calidad.value}")
    print(f"Confianza: {result.confianza:.3f}")
    print(f"Recomendación: {result.recomendacion}")
    print("\nFactores detallados:")
    for factor, value in result.factores.items():
        print(f"  {factor}: {value:.3f}")
