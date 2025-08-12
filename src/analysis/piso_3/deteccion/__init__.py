"""
🔍 OFICINA DE DETECCIÓN - PISO 3
Módulos especializados en detección avanzada de FVGs

Componentes:
- FVGDetector: Detector base mejorado
- MultiTimeframeDetector: Detección multi-timeframe
- ConfluenceAnalyzer: Análisis de confluencias
- RealTimeFVGDetector: Detección en tiempo real
"""

import pandas as pd
from .fvg_detector import FVGDetector
from .multi_timeframe_detector import MultiTimeframeFVGDetector
from .fvg_alert_system import FVGAlertSystem

# Re-exportar componentes del módulo actual
MultiTimeframeDetector = MultiTimeframeFVGDetector

class ConfluenceAnalyzer:
    """
    🔗 ANALIZADOR DE CONFLUENCIAS AVANZADO
    
    Detecta y analiza confluencias entre múltiples timeframes
    con algoritmos optimizados
    """
    
    def __init__(self, timeframes=None, confluence_threshold=7.0):
        """
        Inicializa el analizador de confluencias
        
        Args:
            timeframes: Lista de timeframes a analizar
            confluence_threshold: Umbral mínimo para confluencia válida
        """
        self.timeframes = timeframes or ["M5", "M15", "H1", "H4"]
        self.confluence_threshold = confluence_threshold
        self.confluence_history = []
        
        print(f"🔗 ConfluenceAnalyzer inicializado para {self.timeframes}")
    
    def analyze_confluence_strength(self, fvg1, fvg2):
        """
        Analiza la fuerza de confluencia entre dos FVGs
        
        Args:
            fvg1: Primer FVG
            fvg2: Segundo FVG
            
        Returns:
            float: Fuerza de confluencia (0-10)
        """
        # Análisis de overlap temporal
        time_overlap = self._calculate_time_overlap(fvg1, fvg2)
        
        # Análisis de overlap de precios
        price_overlap = self._calculate_price_overlap(fvg1, fvg2)
        
        # Análisis de dirección
        direction_match = fvg1.type == fvg2.type
        
        # Análisis de tamaño relativo
        size_ratio = self._calculate_size_ratio(fvg1, fvg2)
        
        # Cálculo de fuerza ponderada
        strength = (
            time_overlap * 0.3 +
            price_overlap * 0.4 +
            (10 if direction_match else 2) * 0.2 +
            size_ratio * 0.1
        )
        
        return min(10.0, max(0.0, strength))
    
    def find_confluences(self, fvgs_by_timeframe):
        """
        Encuentra confluencias automáticamente entre múltiples timeframes
        
        Args:
            fvgs_by_timeframe: Dict con timeframe -> lista de FVGs
            
        Returns:
            list: Lista de confluencias encontradas
        """
        confluences = []
        
        # Comparar todos los pares de timeframes
        timeframes = list(fvgs_by_timeframe.keys())
        
        for i, tf1 in enumerate(timeframes):
            for j, tf2 in enumerate(timeframes):
                if i < j:  # Evitar duplicados
                    fvgs1 = fvgs_by_timeframe[tf1]
                    fvgs2 = fvgs_by_timeframe[tf2]
                    
                    # Comparar cada FVG del primer timeframe con cada FVG del segundo
                    for idx1, fvg1 in enumerate(fvgs1):
                        for idx2, fvg2 in enumerate(fvgs2):
                            strength = self.analyze_confluence_strength(fvg1, fvg2)
                            
                            if strength >= self.confluence_threshold:
                                confluence = {
                                    'timeframes': [tf1, tf2],
                                    'fvg_indices': [idx1, idx2],
                                    'fvgs': [fvg1, fvg2],
                                    'strength': strength,
                                    'timestamp': getattr(fvg1, 'timestamp', None)
                                }
                                confluences.append(confluence)
                                
                                # Guardar en historial
                                self.confluence_history.append(confluence)
        
        # Ordenar por fuerza
        confluences.sort(key=lambda x: x['strength'], reverse=True)
        
        return confluences
    
    def get_confluence_summary(self, confluences):
        """
        Genera resumen de confluencias encontradas
        
        Args:
            confluences: Lista de confluencias
            
        Returns:
            dict: Resumen estadístico
        """
        if not confluences:
            return {
                'total_confluences': 0,
                'avg_strength': 0,
                'max_strength': 0,
                'timeframe_pairs': {},
                'direction_analysis': {}
            }
        
        # Estadísticas básicas
        strengths = [c['strength'] for c in confluences]
        
        # Análisis por pares de timeframes
        tf_pairs = {}
        for conf in confluences:
            pair = tuple(sorted(conf['timeframes']))
            tf_pairs[pair] = tf_pairs.get(pair, 0) + 1
        
        # Análisis por dirección
        direction_analysis = {}
        for conf in confluences:
            fvg1, fvg2 = conf['fvgs']
            if hasattr(fvg1, 'type') and hasattr(fvg2, 'type'):
                if fvg1.type == fvg2.type:
                    direction_analysis['same_direction'] = direction_analysis.get('same_direction', 0) + 1
                else:
                    direction_analysis['opposite_direction'] = direction_analysis.get('opposite_direction', 0) + 1
        
        return {
            'total_confluences': len(confluences),
            'avg_strength': sum(strengths) / len(strengths),
            'max_strength': max(strengths),
            'min_strength': min(strengths),
            'timeframe_pairs': tf_pairs,
            'direction_analysis': direction_analysis
        }
    
    def _calculate_time_overlap(self, fvg1, fvg2):
        """Calcula overlap temporal entre FVGs"""
        try:
            # Si tienen timestamp, calcular proximidad temporal
            if hasattr(fvg1, 'timestamp') and hasattr(fvg2, 'timestamp'):
                # Convertir a datetime si es necesario
                time1 = fvg1.timestamp if hasattr(fvg1.timestamp, 'hour') else pd.to_datetime(fvg1.timestamp)
                time2 = fvg2.timestamp if hasattr(fvg2.timestamp, 'hour') else pd.to_datetime(fvg2.timestamp)
                
                # Calcular diferencia en horas
                time_diff = abs((time1 - time2).total_seconds() / 3600)
                
                # Scoring: más cercano en tiempo = mayor score
                if time_diff <= 1:      # Misma hora
                    return 10.0
                elif time_diff <= 4:    # Hasta 4 horas
                    return 8.0
                elif time_diff <= 12:   # Hasta 12 horas
                    return 6.0
                elif time_diff <= 24:   # Hasta 1 día
                    return 4.0
                elif time_diff <= 72:   # Hasta 3 días
                    return 2.0
                else:
                    return 0.5
            
            # Si tienen candle_index, usar proximidad de índices
            elif hasattr(fvg1, 'candle_index') and hasattr(fvg2, 'candle_index'):
                index_diff = abs(fvg1.candle_index - fvg2.candle_index)
                
                if index_diff <= 1:     # Velas consecutivas
                    return 9.0
                elif index_diff <= 5:   # Hasta 5 velas
                    return 7.0
                elif index_diff <= 10:  # Hasta 10 velas
                    return 5.0
                elif index_diff <= 20:  # Hasta 20 velas
                    return 3.0
                else:
                    return 1.0
                    
        except Exception as e:
            print(f"⚠️ Error calculando overlap temporal: {e}")
        
        return 5.0  # Valor por defecto
    
    def _calculate_price_overlap(self, fvg1, fvg2):
        """Calcula overlap de precios entre FVGs mejorado"""
        try:
            # Verificar que tenemos los atributos necesarios
            if (hasattr(fvg1, 'gap_low') and hasattr(fvg1, 'gap_high') and 
                hasattr(fvg2, 'gap_low') and hasattr(fvg2, 'gap_high')):
                
                # Calcular overlap real
                overlap_start = max(fvg1.gap_low, fvg2.gap_low)
                overlap_end = min(fvg1.gap_high, fvg2.gap_high)
                overlap = max(0, overlap_end - overlap_start)
                
                # Calcular rango total
                total_start = min(fvg1.gap_low, fvg2.gap_low)
                total_end = max(fvg1.gap_high, fvg2.gap_high)
                total_range = total_end - total_start
                
                if total_range > 0:
                    overlap_percentage = overlap / total_range
                    return overlap_percentage * 10
                
            # Intentar con otros atributos si están disponibles
            elif hasattr(fvg1, 'price') and hasattr(fvg2, 'price'):
                # Calcular proximidad de precios
                price_diff = abs(fvg1.price - fvg2.price)
                
                # Normalizar por precio promedio
                avg_price = (fvg1.price + fvg2.price) / 2
                if avg_price > 0:
                    price_diff_percentage = price_diff / avg_price
                    
                    # Scoring basado en cercanía
                    if price_diff_percentage <= 0.001:    # 0.1%
                        return 10.0
                    elif price_diff_percentage <= 0.005:  # 0.5%
                        return 8.0
                    elif price_diff_percentage <= 0.01:   # 1%
                        return 6.0
                    elif price_diff_percentage <= 0.02:   # 2%
                        return 4.0
                    elif price_diff_percentage <= 0.05:   # 5%
                        return 2.0
                    else:
                        return 1.0
                        
        except Exception as e:
            print(f"⚠️ Error calculando overlap de precios: {e}")
        
        return 5.0  # Valor por defecto
    
    def _calculate_size_ratio(self, fvg1, fvg2):
        """Calcula ratio de tamaños entre FVGs mejorado"""
        try:
            if hasattr(fvg1, 'gap_size') and hasattr(fvg2, 'gap_size'):
                size1 = float(fvg1.gap_size)
                size2 = float(fvg2.gap_size)
                
                if size1 > 0 and size2 > 0:
                    larger = max(size1, size2)
                    smaller = min(size1, size2)
                    ratio = smaller / larger
                    
                    # Scoring: ratios más cercanos a 1 son mejores
                    if ratio >= 0.8:        # Tamaños muy similares
                        return 10.0
                    elif ratio >= 0.6:      # Tamaños similares
                        return 8.0
                    elif ratio >= 0.4:      # Tamaños moderadamente diferentes
                        return 6.0
                    elif ratio >= 0.2:      # Tamaños diferentes
                        return 4.0
                    else:                   # Tamaños muy diferentes
                        return 2.0
                        
        except Exception as e:
            print(f"⚠️ Error calculando ratio de tamaños: {e}")
        
        return 5.0  # Valor por defecto


class RealTimeFVGDetector:
    """
    ⚡ DETECTOR FVG EN TIEMPO REAL
    
    Sistema optimizado para detección continua con
    procesamiento de alta frecuencia
    """
    
    def __init__(self, symbol="EURUSD", timeframes=None):
        """
        Inicializa el detector en tiempo real
        
        Args:
            symbol: Símbolo a monitorear
            timeframes: Timeframes a procesar
        """
        self.symbol = symbol
        self.timeframes = timeframes or ["M5", "M15", "H1"]
        self.detectors = {}
        self.alert_system = FVGAlertSystem()
        self.is_running = False
        
        # Inicializar detectores por timeframe
        for tf in self.timeframes:
            self.detectors[tf] = FVGDetector()
        
        print(f"⚡ RealTimeFVGDetector inicializado para {symbol}")
    
    async def start_monitoring(self):
        """Inicia el monitoreo en tiempo real"""
        self.is_running = True
        print(f"🔄 Iniciando monitoreo en tiempo real para {self.symbol}")
        
        # TODO: Implementar loop de monitoreo real
        # while self.is_running:
        #     await self._process_new_candles()
        #     await asyncio.sleep(1)
    
    async def stop_monitoring(self):
        """Detiene el monitoreo"""
        self.is_running = False
        print("⏹️ Monitoreo detenido")
    
    async def _process_new_candles(self):
        """Procesa nuevas velas recibidas"""
        # TODO: Implementar procesamiento real
        pass


# Configuración de la oficina
DETECCION_CONFIG = {
    "default_timeframes": ["M5", "M15", "H1", "H4"],
    "confluence_threshold": 7.0,
    "real_time_enabled": True,
    "alert_system_enabled": True,
    "max_concurrent_detections": 4
}

__all__ = [
    "FVGDetector",
    "MultiTimeframeDetector", 
    "ConfluenceAnalyzer",
    "RealTimeFVGDetector",
    "DETECCION_CONFIG"
]
