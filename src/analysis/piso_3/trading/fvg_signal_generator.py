"""
🏢 PISO 3 - OFICINA TRADING
FVG Signal Generator - Sistema de generación de señales de trading basado en FVGs
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
sys.path.insert(0, str(project_root / "src" / "analysis" / "piso_3"))

# Imports centralizados
from data_manager import DataManager
from logger_manager import LoggerManager

# Imports del Piso 3
try:
    from analisis.fvg_quality_analyzer import FVGQualityAnalyzer, FVGQuality
    from ia.fvg_ml_predictor import FVGMLPredictor, FVGPrediction
except ImportError:
    FVGQualityAnalyzer = None
    FVGMLPredictor = None

class SignalType(Enum):
    """Tipos de señales de trading"""
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"
    NO_SIGNAL = "NO_SIGNAL"

class SignalStrength(Enum):
    """Fuerza de la señal"""
    VERY_STRONG = "VERY_STRONG"
    STRONG = "STRONG"
    MEDIUM = "MEDIUM"
    WEAK = "WEAK"

@dataclass
class FVGTradingSignal:
    """Señal de trading basada en FVG"""
    signal_id: str
    fvg_id: str
    signal_type: SignalType
    strength: SignalStrength
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    lot_size: float
    risk_percentage: float
    quality_score: float
    ml_probability: float
    confluence_factors: List[str]
    expiration_time: datetime
    timestamp: datetime
    symbol: str

class FVGSignalGenerator:
    """
    Generador de señales de trading basado en análisis FVG
    
    ESTRATEGIA:
    1. Detecta FVGs de alta calidad
    2. Valida con ML predictor
    3. Establece niveles de entrada y salida
    4. Gestiona riesgo por señal
    5. Considera confluencias técnicas
    """
    
    def __init__(self):
        self.logger = LoggerManager().get_logger("FVGSignalGenerator")
        self.data_manager = DataManager()
        
        # Inicializar analizadores del Piso 3
        self.quality_analyzer = FVGQualityAnalyzer() if FVGQualityAnalyzer else None
        self.ml_predictor = FVGMLPredictor() if FVGMLPredictor else None
        
        # Configuración de señales
        self.min_quality_score = 0.6  # Score mínimo para generar señal
        self.min_ml_probability = 0.55  # Probabilidad ML mínima
        self.max_risk_per_trade = 0.02  # 2% riesgo máximo por trade
        
        # Configuración de niveles
        self.stop_loss_atr_multiplier = 1.5
        self.take_profit_ratios = [1.5, 2.5, 4.0]  # R:R ratios
        
        # Cache de señales activas
        self.active_signals = {}
        
        self.logger.info("FVGSignalGenerator inicializado")

    def generate_signal_from_fvg(self, fvg_data: Dict, symbol: str = "EURUSD") -> Optional[FVGTradingSignal]:
        """
        Genera una señal de trading desde un FVG
        
        Args:
            fvg_data: Datos del FVG detectado
            symbol: Símbolo del instrumento
            
        Returns:
            FVGTradingSignal si la señal es válida, None si no
        """
        try:
            # 1. Análisis de calidad
            if self.quality_analyzer:
                quality_result = self.quality_analyzer.analyze_fvg_quality(fvg_data, symbol)
                quality_score = quality_result.score_total
                
                if quality_score < self.min_quality_score:
                    self.logger.debug(f"FVG {fvg_data.get('id')} descartado por baja calidad: {quality_score:.3f}")
                    return None
            else:
                quality_score = 0.7  # Fallback
            
            # 2. Predicción ML
            if self.ml_predictor:
                ml_result = self.ml_predictor.predict_fvg_fill(fvg_data, symbol)
                ml_probability = ml_result.probability
                
                if ml_probability < self.min_ml_probability:
                    self.logger.debug(f"FVG {fvg_data.get('id')} descartado por baja probabilidad ML: {ml_probability:.3f}")
                    return None
            else:
                ml_probability = 0.6  # Fallback
            
            # 3. Determinar tipo de señal
            signal_type = self._determine_signal_type(fvg_data, symbol)
            if signal_type == SignalType.NO_SIGNAL:
                return None
            
            # 4. Calcular niveles de entrada y salida
            levels = self._calculate_trading_levels(fvg_data, signal_type, symbol)
            if levels is None:
                return None
            
            # 5. Determinar fuerza de la señal
            strength = self._calculate_signal_strength(quality_score, ml_probability)
            
            # 6. Calcular tamaño de posición
            lot_size = self._calculate_position_size(
                levels['entry_price'], 
                levels['stop_loss'], 
                symbol
            )
            
            # 7. Identificar factores de confluencia
            confluence_factors = self._identify_confluence_factors(fvg_data, symbol)
            
            # 8. Calcular tiempo de expiración
            expiration_time = self._calculate_expiration_time(fvg_data)
            
            # Crear señal
            signal = FVGTradingSignal(
                signal_id=f"FVG_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                fvg_id=fvg_data.get('id', 'unknown'),
                signal_type=signal_type,
                strength=strength,
                entry_price=levels['entry_price'],
                stop_loss=levels['stop_loss'],
                take_profit_1=levels['take_profit_1'],
                take_profit_2=levels['take_profit_2'],
                take_profit_3=levels['take_profit_3'],
                lot_size=lot_size,
                risk_percentage=self._calculate_risk_percentage(
                    levels['entry_price'], 
                    levels['stop_loss'], 
                    lot_size
                ),
                quality_score=quality_score,
                ml_probability=ml_probability,
                confluence_factors=confluence_factors,
                expiration_time=expiration_time,
                timestamp=datetime.now(),
                symbol=symbol
            )
            
            self.logger.info(f"Señal generada: {signal.signal_id} - {signal.signal_type.value} - Fuerza: {signal.strength.value}")
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error generando señal para FVG {fvg_data.get('id', 'unknown')}: {e}")
            return None

    def _determine_signal_type(self, fvg_data: Dict, symbol: str) -> SignalType:
        """Determina el tipo de señal basado en el FVG y contexto de mercado"""
        try:
            fvg_type = fvg_data.get('type', 'BULLISH')
            current_price = self.data_manager.get_current_price(symbol)
            
            if current_price is None:
                return SignalType.NO_SIGNAL
            
            fvg_high = fvg_data.get('high', 0)
            fvg_low = fvg_data.get('low', 0)
            fvg_center = (fvg_high + fvg_low) / 2
            
            # Obtener contexto de tendencia
            df_h1 = self.data_manager.get_ohlc_data(symbol, 'H1', 50)
            if df_h1 is None:
                return SignalType.NO_SIGNAL
            
            # EMAs para tendencia
            ema_20 = df_h1['close'].ewm(span=20).mean().iloc[-1]
            ema_50 = df_h1['close'].ewm(span=50).mean().iloc[-1]
            
            # Lógica de señales
            if fvg_type == 'BULLISH':
                # FVG alcista: esperamos que el precio regrese al FVG para comprar
                if current_price > fvg_high:
                    # Precio arriba del FVG: BUY LIMIT para regresar al FVG
                    if ema_20 > ema_50:  # Tendencia alcista
                        return SignalType.BUY_LIMIT
                elif current_price < fvg_low:
                    # Precio abajo del FVG: BUY STOP para breakout
                    return SignalType.BUY_STOP
                    
            elif fvg_type == 'BEARISH':
                # FVG bajista: esperamos que el precio regrese al FVG para vender
                if current_price < fvg_low:
                    # Precio abajo del FVG: SELL LIMIT para regresar al FVG
                    if ema_20 < ema_50:  # Tendencia bajista
                        return SignalType.SELL_LIMIT
                elif current_price > fvg_high:
                    # Precio arriba del FVG: SELL STOP para breakout
                    return SignalType.SELL_STOP
            
            return SignalType.NO_SIGNAL
            
        except Exception as e:
            self.logger.error(f"Error determinando tipo de señal: {e}")
            return SignalType.NO_SIGNAL

    def _calculate_trading_levels(self, fvg_data: Dict, signal_type: SignalType, symbol: str) -> Optional[Dict]:
        """Calcula niveles de entrada, stop loss y take profits"""
        try:
            fvg_high = fvg_data.get('high', 0)
            fvg_low = fvg_data.get('low', 0)
            fvg_center = (fvg_high + fvg_low) / 2
            
            # Obtener ATR para cálculos
            df_h1 = self.data_manager.get_ohlc_data(symbol, 'H1', 24)
            if df_h1 is None:
                return None
                
            atr = self._calculate_atr(df_h1, 14).iloc[-1]
            
            levels = {}
            
            if signal_type in [SignalType.BUY_LIMIT, SignalType.BUY_STOP]:
                # Señales de compra
                if signal_type == SignalType.BUY_LIMIT:
                    levels['entry_price'] = fvg_center
                else:  # BUY_STOP
                    levels['entry_price'] = fvg_high + (atr * 0.1)
                
                # Stop loss debajo del FVG
                levels['stop_loss'] = fvg_low - (atr * self.stop_loss_atr_multiplier)
                
                # Take profits
                risk = levels['entry_price'] - levels['stop_loss']
                levels['take_profit_1'] = levels['entry_price'] + (risk * self.take_profit_ratios[0])
                levels['take_profit_2'] = levels['entry_price'] + (risk * self.take_profit_ratios[1])
                levels['take_profit_3'] = levels['entry_price'] + (risk * self.take_profit_ratios[2])
                
            elif signal_type in [SignalType.SELL_LIMIT, SignalType.SELL_STOP]:
                # Señales de venta
                if signal_type == SignalType.SELL_LIMIT:
                    levels['entry_price'] = fvg_center
                else:  # SELL_STOP
                    levels['entry_price'] = fvg_low - (atr * 0.1)
                
                # Stop loss arriba del FVG
                levels['stop_loss'] = fvg_high + (atr * self.stop_loss_atr_multiplier)
                
                # Take profits
                risk = levels['stop_loss'] - levels['entry_price']
                levels['take_profit_1'] = levels['entry_price'] - (risk * self.take_profit_ratios[0])
                levels['take_profit_2'] = levels['entry_price'] - (risk * self.take_profit_ratios[1])
                levels['take_profit_3'] = levels['entry_price'] - (risk * self.take_profit_ratios[2])
            
            return levels
            
        except Exception as e:
            self.logger.error(f"Error calculando niveles de trading: {e}")
            return None

    def _calculate_signal_strength(self, quality_score: float, ml_probability: float) -> SignalStrength:
        """Calcula la fuerza de la señal basada en múltiples factores"""
        try:
            # Promedio ponderado
            combined_score = (quality_score * 0.6) + (ml_probability * 0.4)
            
            if combined_score >= 0.85:
                return SignalStrength.VERY_STRONG
            elif combined_score >= 0.75:
                return SignalStrength.STRONG
            elif combined_score >= 0.65:
                return SignalStrength.MEDIUM
            else:
                return SignalStrength.WEAK
                
        except Exception as e:
            self.logger.error(f"Error calculando fuerza de señal: {e}")
            return SignalStrength.WEAK

    def _calculate_position_size(self, entry_price: float, stop_loss: float, symbol: str) -> float:
        """Calcula el tamaño de posición basado en el riesgo"""
        try:
            # Obtener balance de cuenta (simulado)
            account_balance = 10000  # USD - esto debería venir del broker
            
            # Riesgo en pips
            risk_pips = abs(entry_price - stop_loss)
            
            # Valor por pip para EURUSD (simplificado)
            pip_value = 1.0  # $1 por pip para lote estándar
            
            # Riesgo en dinero
            max_risk_money = account_balance * self.max_risk_per_trade
            
            # Calcular tamaño de lote
            lot_size = max_risk_money / (risk_pips * 10000 * pip_value)
            
            # Redondear y limitar
            lot_size = round(lot_size, 2)
            lot_size = max(0.01, min(lot_size, 1.0))  # Entre 0.01 y 1.0 lote
            
            return lot_size
            
        except Exception as e:
            self.logger.error(f"Error calculando tamaño de posición: {e}")
            return 0.01

    def _calculate_risk_percentage(self, entry_price: float, stop_loss: float, lot_size: float) -> float:
        """Calcula el porcentaje de riesgo real"""
        try:
            account_balance = 10000  # USD
            risk_pips = abs(entry_price - stop_loss)
            risk_money = risk_pips * 10000 * lot_size * 1.0  # $1 per pip
            
            return (risk_money / account_balance) * 100
            
        except Exception as e:
            self.logger.error(f"Error calculando porcentaje de riesgo: {e}")
            return 2.0

    def _identify_confluence_factors(self, fvg_data: Dict, symbol: str) -> List[str]:
        """Identifica factores de confluencia técnica"""
        try:
            factors = []
            
            df_h1 = self.data_manager.get_ohlc_data(symbol, 'H1', 100)
            if df_h1 is None:
                return factors
            
            fvg_center = (fvg_data.get('high', 0) + fvg_data.get('low', 0)) / 2
            
            # 1. Confluencia con EMAs
            ema_20 = df_h1['close'].ewm(span=20).mean().iloc[-1]
            ema_50 = df_h1['close'].ewm(span=50).mean().iloc[-1]
            ema_200 = df_h1['close'].ewm(span=200).mean().iloc[-1]
            
            if abs(fvg_center - ema_20) / ema_20 < 0.001:
                factors.append("EMA_20")
            if abs(fvg_center - ema_50) / ema_50 < 0.001:
                factors.append("EMA_50")
            if abs(fvg_center - ema_200) / ema_200 < 0.001:
                factors.append("EMA_200")
            
            # 2. Confluencia con niveles psicológicos
            if self._is_psychological_level(fvg_center):
                factors.append("PSYCHOLOGICAL_LEVEL")
            
            # 3. Confluencia con Fibonacci
            recent_high = df_h1['high'].tail(50).max()
            recent_low = df_h1['low'].tail(50).min()
            
            fib_levels = self._calculate_fibonacci_levels(recent_high, recent_low)
            for i, level in enumerate(fib_levels):
                if abs(fvg_center - level) / level < 0.0005:
                    factors.append(f"FIBONACCI_{i}")
                    break
            
            # 4. Confluencia con soporte/resistencia
            if self._is_support_resistance_level(fvg_center, df_h1):
                factors.append("SUPPORT_RESISTANCE")
            
            return factors
            
        except Exception as e:
            self.logger.error(f"Error identificando confluencias: {e}")
            return []

    def _calculate_expiration_time(self, fvg_data: Dict) -> datetime:
        """Calcula tiempo de expiración de la señal"""
        try:
            # Las señales FVG expiran en 24 horas por defecto
            return datetime.now() + timedelta(hours=24)
        except:
            return datetime.now() + timedelta(hours=24)

    def batch_generate_signals(self, fvg_list: List[Dict], symbol: str = "EURUSD") -> List[FVGTradingSignal]:
        """
        Genera señales para una lista de FVGs
        
        Args:
            fvg_list: Lista de FVGs detectados
            symbol: Símbolo del instrumento
            
        Returns:
            Lista de señales válidas ordenadas por fuerza
        """
        try:
            signals = []
            
            for fvg in fvg_list:
                signal = self.generate_signal_from_fvg(fvg, symbol)
                if signal:
                    signals.append(signal)
            
            # Ordenar por fuerza y calidad
            signals.sort(key=lambda s: (
                self._strength_to_numeric(s.strength),
                s.quality_score,
                s.ml_probability
            ), reverse=True)
            
            self.logger.info(f"Generadas {len(signals)} señales de {len(fvg_list)} FVGs")
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error generando señales en lote: {e}")
            return []

    def get_active_signals(self) -> List[FVGTradingSignal]:
        """Obtiene señales activas no expiradas"""
        try:
            now = datetime.now()
            active = [
                signal for signal in self.active_signals.values()
                if signal.expiration_time > now
            ]
            
            return active
            
        except Exception as e:
            self.logger.error(f"Error obteniendo señales activas: {e}")
            return []

    def update_signal_status(self, signal_id: str, status: str):
        """Actualiza el estado de una señal"""
        try:
            if signal_id in self.active_signals:
                # Aquí se podría actualizar el estado en base de datos
                self.logger.info(f"Señal {signal_id} actualizada a estado: {status}")
                
        except Exception as e:
            self.logger.error(f"Error actualizando señal {signal_id}: {e}")

    # Métodos auxiliares
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

    def _is_psychological_level(self, price: float) -> bool:
        """Verifica si es un nivel psicológico"""
        # Niveles .0000, .0050, etc.
        return (price * 10000) % 50 == 0

    def _is_support_resistance_level(self, price: float, df: pd.DataFrame) -> bool:
        """Verifica si es un nivel de soporte/resistencia"""
        try:
            # Buscar toques cercanos en datos históricos
            touches = 0
            tolerance = price * 0.0005  # 0.05%
            
            for _, row in df.tail(100).iterrows():
                if abs(row['high'] - price) < tolerance or abs(row['low'] - price) < tolerance:
                    touches += 1
            
            return touches >= 3
            
        except:
            return False

    def _strength_to_numeric(self, strength: SignalStrength) -> int:
        """Convierte fuerza de señal a valor numérico para ordenamiento"""
        mapping = {
            SignalStrength.VERY_STRONG: 4,
            SignalStrength.STRONG: 3,
            SignalStrength.MEDIUM: 2,
            SignalStrength.WEAK: 1
        }
        return mapping.get(strength, 0)

    def get_signal_statistics(self) -> Dict:
        """Obtiene estadísticas de señales generadas"""
        try:
            active = self.get_active_signals()
            
            stats = {
                'total_active_signals': len(active),
                'signals_by_type': {},
                'signals_by_strength': {},
                'average_risk': 0,
                'total_exposure': 0
            }
            
            for signal in active:
                # Por tipo
                signal_type = signal.signal_type.value
                stats['signals_by_type'][signal_type] = stats['signals_by_type'].get(signal_type, 0) + 1
                
                # Por fuerza
                strength = signal.strength.value
                stats['signals_by_strength'][strength] = stats['signals_by_strength'].get(strength, 0) + 1
                
                # Riesgo
                stats['total_exposure'] += signal.risk_percentage
            
            if len(active) > 0:
                stats['average_risk'] = stats['total_exposure'] / len(active)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error generando estadísticas: {e}")
            return {}


if __name__ == "__main__":
    # Test básico del generador de señales
    generator = FVGSignalGenerator()
    
    # Datos de prueba
    test_fvg = {
        'id': 'test_signal_001',
        'type': 'BULLISH',
        'high': 1.0950,
        'low': 1.0930,
        'detection_time': datetime.now()
    }
    
    # Generar señal
    signal = generator.generate_signal_from_fvg(test_fvg)
    
    if signal:
        print(f"🏢 PISO 3 - OFICINA TRADING")
        print(f"Señal ID: {signal.signal_id}")
        print(f"Tipo: {signal.signal_type.value}")
        print(f"Fuerza: {signal.strength.value}")
        print(f"Entrada: {signal.entry_price:.5f}")
        print(f"Stop Loss: {signal.stop_loss:.5f}")
        print(f"TP1: {signal.take_profit_1:.5f}")
        print(f"TP2: {signal.take_profit_2:.5f}")
        print(f"TP3: {signal.take_profit_3:.5f}")
        print(f"Lote: {signal.lot_size}")
        print(f"Riesgo: {signal.risk_percentage:.2f}%")
        print(f"Confluencias: {signal.confluence_factors}")
    else:
        print("❌ No se generó señal válida")
    
    # Estadísticas
    stats = generator.get_signal_statistics()
    print(f"\nEstadísticas: {stats}")
