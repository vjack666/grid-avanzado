"""
🔍 MULTI-TIMEFRAME FVG DETECTOR
Detección expandida con análisis multi-timeframe y alertas

Fecha: Agosto 12, 2025
Oficina: Detección Expandida - Piso 3
Estado: Implementación Multi-TF
"""

import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import logging

# Imports del sistema base
from .fvg_detector import FVGDetector, FVGData, RealTimeFVGDetector

logger = logging.getLogger(__name__)

@dataclass
class SessionStats:
    """Estadísticas por sesión de trading"""
    session_name: str
    total_fvgs: int = 0
    bullish_count: int = 0
    bearish_count: int = 0
    total_pips: float = 0.0
    avg_size_pips: float = 0.0
    largest_gap_pips: float = 0.0
    smallest_gap_pips: float = float('inf')
    time_range: str = ""
    
    def update_stats(self, fvg: FVGData):
        """Actualiza estadísticas con nuevo FVG"""
        gap_pips = fvg.gap_size * 10000
        
        self.total_fvgs += 1
        self.total_pips += gap_pips
        
        if fvg.type == 'BULLISH':
            self.bullish_count += 1
        else:
            self.bearish_count += 1
        
        self.largest_gap_pips = max(self.largest_gap_pips, gap_pips)
        if self.smallest_gap_pips == float('inf'):
            self.smallest_gap_pips = gap_pips
        else:
            self.smallest_gap_pips = min(self.smallest_gap_pips, gap_pips)
        
        self.avg_size_pips = self.total_pips / self.total_fvgs if self.total_fvgs > 0 else 0

@dataclass
class MultiTimeframeAnalysis:
    """Análisis completo multi-timeframe"""
    symbol: str
    timestamp: datetime
    timeframe_data: Dict[str, List[FVGData]] = field(default_factory=dict)
    session_stats: Dict[str, SessionStats] = field(default_factory=dict)
    confluence_fvgs: List[Dict] = field(default_factory=list)
    market_bias: str = "NEUTRAL"
    total_fvgs_detected: int = 0
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'timeframe_summary': {
                tf: len(fvgs) for tf, fvgs in self.timeframe_data.items()
            },
            'session_summary': {
                name: {
                    'total_fvgs': stats.total_fvgs,
                    'bullish_count': stats.bullish_count,
                    'bearish_count': stats.bearish_count,
                    'avg_size_pips': round(stats.avg_size_pips, 1),
                    'largest_gap_pips': round(stats.largest_gap_pips, 1)
                } for name, stats in self.session_stats.items()
            },
            'confluence_count': len(self.confluence_fvgs),
            'market_bias': self.market_bias,
            'total_fvgs': self.total_fvgs_detected
        }

class MultiTimeframeFVGDetector:
    """
    🔍 DETECTOR FVG MULTI-TIMEFRAME EXPANDIDO
    
    Características:
    - Análisis simultáneo M5, M15, H1, H4
    - Detección de confluencias entre timeframes
    - Estadísticas por sesión de trading
    - Sistema de alertas inteligente
    - Análisis de bias de mercado
    """
    
    def __init__(self, symbol: str = "EURUSD", config: Dict = None):
        """
        Inicializa detector multi-timeframe
        
        Args:
            symbol: Símbolo a analizar
            config: Configuración personalizada
        """
        self.symbol = symbol
        self.timeframes = ['M5', 'M15', 'H1', 'H4']
        
        # Configuración por defecto
        default_config = {
            'min_gap_size': 0.00005,     # 0.5 pips
            'min_body_ratio': 0.65,      # 65%
            'max_gap_size': 0.005,       # 50 pips
            'confluence_threshold': 10,   # Pips para considerar confluencia
            'alert_min_quality': 6.0,    # Score mínimo para alertas
            'session_analysis': True,     # Activar análisis por sesión
            'real_time_alerts': True     # Activar alertas en tiempo real
        }
        
        self.config = {**default_config, **(config or {})}
        
        # Detectores por timeframe
        self.detectors = {}
        for tf in self.timeframes:
            self.detectors[tf] = FVGDetector(self.config)
        
        # Almacenamiento de FVGs por timeframe
        self.active_fvgs = {tf: {} for tf in self.timeframes}
        
        # Estadísticas por sesión
        self.session_stats = {
            'ASIA': SessionStats('ASIA', time_range="21:00-06:00 UTC"),
            'LONDON': SessionStats('LONDON', time_range="07:00-16:00 UTC"),
            'NY': SessionStats('NY', time_range="13:00-22:00 UTC"),
            'OVERLAP': SessionStats('OVERLAP', time_range="13:00-16:00 UTC")
        }
        
        # Callbacks para alertas
        self.alert_callbacks = []
        
        # Métricas globales
        self.global_metrics = {
            'total_detections': 0,
            'confluence_detections': 0,
            'session_distribution': defaultdict(int),
            'timeframe_distribution': defaultdict(int)
        }
        
        logger.info(f"MultiTimeframeFVGDetector inicializado para {symbol}")
    
    def analyze_multi_timeframe_data(self, data_by_timeframe: Dict[str, pd.DataFrame]) -> MultiTimeframeAnalysis:
        """
        Analiza datos multi-timeframe y detecta FVGs
        
        Args:
            data_by_timeframe: Dict con DataFrames por timeframe
            
        Returns:
            MultiTimeframeAnalysis con resultados completos
        """
        analysis = MultiTimeframeAnalysis(
            symbol=self.symbol,
            timestamp=datetime.now()
        )
        
        print(f"🔍 ANÁLISIS MULTI-TIMEFRAME: {self.symbol}")
        print("=" * 60)
        
        # Detectar FVGs en cada timeframe
        for timeframe in self.timeframes:
            if timeframe not in data_by_timeframe:
                continue
            
            df = data_by_timeframe[timeframe]
            print(f"\n📊 Analizando {timeframe}: {len(df)} velas")
            
            # Convertir DataFrame a lista de velas
            candles = self._dataframe_to_candles(df, timeframe)
            
            # Detectar FVGs
            detected_fvgs = self.detectors[timeframe].detect_all_fvgs(candles)
            analysis.timeframe_data[timeframe] = detected_fvgs
            analysis.total_fvgs_detected += len(detected_fvgs)
            
            # Actualizar métricas
            self.global_metrics['timeframe_distribution'][timeframe] += len(detected_fvgs)
            
            print(f"   ✅ {len(detected_fvgs)} FVGs detectados")
            
            # Analizar por sesiones
            self._analyze_session_distribution(detected_fvgs, analysis)
        
        # Detectar confluencias entre timeframes
        analysis.confluence_fvgs = self._detect_timeframe_confluences(analysis.timeframe_data)
        self.global_metrics['confluence_detections'] += len(analysis.confluence_fvgs)
        
        # Determinar bias de mercado
        analysis.market_bias = self._calculate_market_bias(analysis.timeframe_data)
        
        # Mostrar resumen
        self._print_analysis_summary(analysis)
        
        return analysis
    
    def _dataframe_to_candles(self, df: pd.DataFrame, timeframe: str) -> List[Dict]:
        """Convierte DataFrame a lista de velas"""
        candles = []
        for _, row in df.iterrows():
            candle = {
                'time': pd.to_datetime(row['datetime']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume']),
                'symbol': self.symbol,
                'timeframe': timeframe
            }
            candles.append(candle)
        return candles
    
    def _analyze_session_distribution(self, fvgs: List[FVGData], analysis: MultiTimeframeAnalysis):
        """Analiza distribución de FVGs por sesión"""
        for fvg in fvgs:
            session = self._get_trading_session(fvg.formation_time)
            
            # Actualizar estadísticas de sesión
            if session not in analysis.session_stats:
                analysis.session_stats[session] = SessionStats(session)
            
            analysis.session_stats[session].update_stats(fvg)
            self.session_stats[session].update_stats(fvg)
            self.global_metrics['session_distribution'][session] += 1
    
    def _get_trading_session(self, timestamp: datetime) -> str:
        """Determina la sesión de trading"""
        hour = timestamp.hour
        
        if 21 <= hour or hour <= 6:
            return 'ASIA'
        elif 7 <= hour <= 16:
            if 13 <= hour <= 16:
                return 'OVERLAP'  # También contará para London y NY
            return 'LONDON'
        elif 13 <= hour <= 22:
            return 'NY'
        else:
            return 'ASIA'  # Fallback
    
    def _detect_timeframe_confluences(self, timeframe_data: Dict[str, List[FVGData]]) -> List[Dict]:
        """
        Detecta confluencias de FVGs entre timeframes
        
        Una confluencia ocurre cuando FVGs de diferentes timeframes
        se superponen en precio dentro del threshold configurado.
        """
        confluences = []
        confluence_threshold = self.config['confluence_threshold'] / 10000  # Convert to price
        
        # Comparar cada par de timeframes
        timeframes = list(timeframe_data.keys())
        
        for i in range(len(timeframes)):
            for j in range(i + 1, len(timeframes)):
                tf1, tf2 = timeframes[i], timeframes[j]
                fvgs1, fvgs2 = timeframe_data[tf1], timeframe_data[tf2]
                
                # Buscar FVGs que se superpongan
                for fvg1 in fvgs1:
                    for fvg2 in fvgs2:
                        # Verificar si hay superposición de precio
                        if self._fvgs_overlap(fvg1, fvg2, confluence_threshold):
                            confluence = {
                                'timeframes': [tf1, tf2],
                                'fvg1': fvg1.to_dict(),
                                'fvg2': fvg2.to_dict(),
                                'confluence_strength': self._calculate_confluence_strength(fvg1, fvg2),
                                'price_overlap': self._calculate_price_overlap(fvg1, fvg2),
                                'type_match': fvg1.type == fvg2.type,
                                'timestamp': datetime.now().isoformat()
                            }
                            confluences.append(confluence)
        
        return confluences
    
    def _fvgs_overlap(self, fvg1: FVGData, fvg2: FVGData, threshold: float) -> bool:
        """Verifica si dos FVGs se superponen en precio"""
        # Expandir rangos con threshold
        fvg1_low = fvg1.gap_low - threshold
        fvg1_high = fvg1.gap_high + threshold
        fvg2_low = fvg2.gap_low - threshold
        fvg2_high = fvg2.gap_high + threshold
        
        # Verificar superposición
        return not (fvg1_high < fvg2_low or fvg2_high < fvg1_low)
    
    def _calculate_confluence_strength(self, fvg1: FVGData, fvg2: FVGData) -> float:
        """Calcula la fuerza de confluencia entre dos FVGs"""
        # Factores que aumentan la fuerza:
        # 1. Tamaños similares
        # 2. Mismo tipo (bullish/bearish)
        # 3. Proximidad en tiempo de formación
        # 4. Superposición de precio
        
        strength = 0.0
        
        # Factor de tamaño (0-3 puntos)
        size_ratio = min(fvg1.gap_size, fvg2.gap_size) / max(fvg1.gap_size, fvg2.gap_size)
        strength += size_ratio * 3
        
        # Factor de tipo (0-2 puntos)
        if fvg1.type == fvg2.type:
            strength += 2
        
        # Factor de proximidad temporal (0-2 puntos)
        time_diff = abs((fvg1.formation_time - fvg2.formation_time).total_seconds())
        if time_diff < 3600:  # Menos de 1 hora
            strength += 2
        elif time_diff < 14400:  # Menos de 4 horas
            strength += 1
        
        # Factor de superposición de precio (0-3 puntos)
        overlap_ratio = self._calculate_price_overlap(fvg1, fvg2)
        strength += overlap_ratio * 3
        
        return round(strength, 2)
    
    def _calculate_price_overlap(self, fvg1: FVGData, fvg2: FVGData) -> float:
        """Calcula el porcentaje de superposición de precio"""
        overlap_low = max(fvg1.gap_low, fvg2.gap_low)
        overlap_high = min(fvg1.gap_high, fvg2.gap_high)
        
        if overlap_high <= overlap_low:
            return 0.0
        
        overlap_size = overlap_high - overlap_low
        total_range = max(fvg1.gap_high, fvg2.gap_high) - min(fvg1.gap_low, fvg2.gap_low)
        
        return overlap_size / total_range if total_range > 0 else 0.0
    
    def _calculate_market_bias(self, timeframe_data: Dict[str, List[FVGData]]) -> str:
        """Calcula el bias general del mercado basado en FVGs"""
        total_bullish = 0
        total_bearish = 0
        weighted_bullish = 0.0
        weighted_bearish = 0.0
        
        # Pesos por timeframe (timeframes más altos tienen más peso)
        tf_weights = {'M5': 1.0, 'M15': 1.5, 'H1': 2.0, 'H4': 3.0}
        
        for tf, fvgs in timeframe_data.items():
            weight = tf_weights.get(tf, 1.0)
            
            for fvg in fvgs:
                gap_size = fvg.gap_size * 10000  # En pips
                weighted_gap = gap_size * weight
                
                if fvg.type == 'BULLISH':
                    total_bullish += 1
                    weighted_bullish += weighted_gap
                else:
                    total_bearish += 1
                    weighted_bearish += weighted_gap
        
        # Determinar bias
        if total_bullish == 0 and total_bearish == 0:
            return "NEUTRAL"
        
        bullish_strength = weighted_bullish / max(1, total_bullish)
        bearish_strength = weighted_bearish / max(1, total_bearish)
        
        strength_diff = abs(bullish_strength - bearish_strength)
        count_diff = abs(total_bullish - total_bearish)
        
        if strength_diff < 0.5 and count_diff <= 2:
            return "NEUTRAL"
        elif weighted_bullish > weighted_bearish:
            return "BULLISH" if strength_diff > 1.0 else "SLIGHTLY_BULLISH"
        else:
            return "BEARISH" if strength_diff > 1.0 else "SLIGHTLY_BEARISH"
    
    def _print_analysis_summary(self, analysis: MultiTimeframeAnalysis):
        """Imprime resumen del análisis"""
        print(f"\n📊 RESUMEN MULTI-TIMEFRAME")
        print("=" * 50)
        
        # Resumen por timeframe
        print(f"📈 FVGs por Timeframe:")
        for tf in self.timeframes:
            count = len(analysis.timeframe_data.get(tf, []))
            print(f"   {tf:3s}: {count:3d} FVGs")
        
        print(f"\n📊 Total FVGs detectados: {analysis.total_fvgs_detected}")
        print(f"🔗 Confluencias encontradas: {len(analysis.confluence_fvgs)}")
        print(f"📈 Bias de mercado: {analysis.market_bias}")
        
        # Resumen por sesiones
        print(f"\n🕒 Distribución por Sesiones:")
        for session_name, stats in analysis.session_stats.items():
            if stats.total_fvgs > 0:
                bullish_pct = (stats.bullish_count / stats.total_fvgs * 100) if stats.total_fvgs > 0 else 0
                print(f"   {session_name:7s}: {stats.total_fvgs:2d} FVGs | "
                      f"🟢{stats.bullish_count:2d} 🔴{stats.bearish_count:2d} | "
                      f"Avg: {stats.avg_size_pips:.1f} pips")
        
        # Confluencias destacadas
        if analysis.confluence_fvgs:
            print(f"\n🔗 CONFLUENCIAS DESTACADAS:")
            strong_confluences = [c for c in analysis.confluence_fvgs if c['confluence_strength'] >= 7.0]
            
            for i, conf in enumerate(strong_confluences[:5], 1):
                tf1, tf2 = conf['timeframes']
                strength = conf['confluence_strength']
                type_match = "✅" if conf['type_match'] else "❌"
                print(f"   {i}. {tf1}-{tf2} | Fuerza: {strength:.1f} | Tipo: {type_match}")
    
    def generate_alerts(self, analysis: MultiTimeframeAnalysis) -> List[Dict]:
        """
        Genera alertas basadas en el análisis
        
        Criterios para alertas:
        1. Confluencias fuertes (>7.0)
        2. FVGs grandes en timeframes altos
        3. Bias de mercado fuerte
        4. Concentración en sesiones importantes
        """
        alerts = []
        
        # Alertas por confluencias fuertes
        strong_confluences = [c for c in analysis.confluence_fvgs if c['confluence_strength'] >= 7.0]
        for conf in strong_confluences:
            alert = {
                'type': 'CONFLUENCE',
                'priority': 'HIGH',
                'message': f"Confluencia fuerte {conf['timeframes'][0]}-{conf['timeframes'][1]}",
                'strength': conf['confluence_strength'],
                'timeframes': conf['timeframes'],
                'timestamp': datetime.now().isoformat(),
                'data': conf
            }
            alerts.append(alert)
        
        # Alertas por FVGs grandes en H4
        h4_fvgs = analysis.timeframe_data.get('H4', [])
        large_h4_fvgs = [fvg for fvg in h4_fvgs if fvg.gap_size * 10000 >= 10.0]  # >10 pips
        
        for fvg in large_h4_fvgs:
            alert = {
                'type': 'LARGE_FVG',
                'priority': 'MEDIUM',
                'message': f"FVG grande H4: {fvg.gap_size * 10000:.1f} pips",
                'timeframe': 'H4',
                'gap_size_pips': fvg.gap_size * 10000,
                'fvg_type': fvg.type,
                'timestamp': datetime.now().isoformat(),
                'data': fvg.to_dict()
            }
            alerts.append(alert)
        
        # Alertas por bias fuerte
        if analysis.market_bias in ['BULLISH', 'BEARISH']:
            alert = {
                'type': 'MARKET_BIAS',
                'priority': 'MEDIUM',
                'message': f"Bias de mercado fuerte: {analysis.market_bias}",
                'bias': analysis.market_bias,
                'total_fvgs': analysis.total_fvgs_detected,
                'timestamp': datetime.now().isoformat()
            }
            alerts.append(alert)
        
        # Alertas por concentración en overlap
        overlap_stats = analysis.session_stats.get('OVERLAP')
        if overlap_stats and overlap_stats.total_fvgs >= 5:
            alert = {
                'type': 'SESSION_CONCENTRATION',
                'priority': 'LOW',
                'message': f"Alta actividad FVG en overlap: {overlap_stats.total_fvgs} FVGs",
                'session': 'OVERLAP',
                'fvg_count': overlap_stats.total_fvgs,
                'timestamp': datetime.now().isoformat()
            }
            alerts.append(alert)
        
        return alerts
    
    def get_global_metrics(self) -> Dict:
        """Retorna métricas globales del detector"""
        return {
            'total_detections': self.global_metrics['total_detections'],
            'confluence_detections': self.global_metrics['confluence_detections'],
            'session_distribution': dict(self.global_metrics['session_distribution']),
            'timeframe_distribution': dict(self.global_metrics['timeframe_distribution']),
            'session_stats': {
                name: {
                    'total_fvgs': stats.total_fvgs,
                    'avg_size_pips': round(stats.avg_size_pips, 1),
                    'largest_gap_pips': round(stats.largest_gap_pips, 1)
                } for name, stats in self.session_stats.items() if stats.total_fvgs > 0
            }
        }

# Función de utilidad para testing
def quick_test_multi_timeframe():
    """🧪 Test rápido del detector multi-timeframe"""
    print("🔍 Testing Multi-Timeframe FVG Detector...")
    
    detector = MultiTimeframeFVGDetector("EURUSD")
    
    # Simular datos para diferentes timeframes
    mock_data = {}
    
    for tf in ['M5', 'M15', 'H1']:
        # Crear datos mock con patrones FVG
        dates = pd.date_range('2025-08-12 08:00', periods=100, freq='5T' if tf == 'M5' else '15T' if tf == 'M15' else '1H')
        prices = np.random.normal(1.1000, 0.001, 100)
        
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            data.append({
                'datetime': date,
                'open': price,
                'high': price + np.random.uniform(0, 0.0005),
                'low': price - np.random.uniform(0, 0.0005),
                'close': price + np.random.uniform(-0.0003, 0.0003),
                'volume': np.random.randint(100, 1000),
                'hour': date.hour
            })
        
        mock_data[tf] = pd.DataFrame(data)
    
    # Ejecutar análisis
    analysis = detector.analyze_multi_timeframe_data(mock_data)
    
    # Generar alertas
    alerts = detector.generate_alerts(analysis)
    
    print(f"\n✅ Test completado:")
    print(f"   Total FVGs: {analysis.total_fvgs_detected}")
    print(f"   Confluencias: {len(analysis.confluence_fvgs)}")
    print(f"   Alertas: {len(alerts)}")
    print(f"   Bias: {analysis.market_bias}")

if __name__ == "__main__":
    quick_test_multi_timeframe()
