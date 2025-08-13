"""
🔍 FVG DETECTOR - OFICINA DE DETECCIÓN
Detección automatizada de Fair Value Gaps en tiempo real

Fecha: Agosto 12, 2025
Oficina: Detección - Piso 3
Estado: Implementación Base
"""

# Import centralizado desde SÓTANO 1 CORE
from src.core.common_imports import (
    pd, np, datetime, asyncio, logging,
    Dict, List, Optional, Tuple, dataclass
)
from datetime import timezone
from collections import deque

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FVGData:
    """Estructura de datos para un FVG detectado"""
    type: str  # 'BULLISH' o 'BEARISH'
    formation_time: datetime
    gap_low: float
    gap_high: float
    gap_size: float
    formation_candles: List[Dict]
    status: str = 'ACTIVE'
    quality_score: Optional[float] = None
    timeframe: str = 'UNKNOWN'
    symbol: str = 'UNKNOWN'
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización"""
        return {
            'type': self.type,
            'formation_time': self.formation_time.isoformat(),
            'gap_low': self.gap_low,
            'gap_high': self.gap_high,
            'gap_size': self.gap_size,
            'gap_size_pips': round(self.gap_size * 10000, 1),
            'formation_candles': self.formation_candles,
            'status': self.status,
            'quality_score': self.quality_score,
            'timeframe': self.timeframe,
            'symbol': self.symbol
        }

class FVGDetector:
    """
    🔍 DETECTOR PRINCIPAL DE FVG
    
    Implementa algoritmos de detección de Fair Value Gaps
    con validación automática y procesamiento en tiempo real.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el detector con configuración personalizable
        
        Args:
            config: Diccionario de configuración opcional
        """
        # Configuración por defecto
        default_config = {
            'min_gap_size': 0.0001,      # 1 pip mínimo en EURUSD
            'min_body_ratio': 0.7,       # 70% body ratio para vela fuerte
            'max_gap_size': 0.0050,      # 50 pips máximo (filtro anomalías)
            'validation_enabled': True,   # Activar validación automática
            'real_time_mode': True       # Modo tiempo real
        }
        
        self.config = {**default_config, **(config or {})}
        
        # Métricas de performance
        self.metrics = {
            'total_detections': 0,
            'valid_detections': 0,
            'false_positives': 0,
            'processing_times': deque(maxlen=100)
        }
        
        logger.info(f"FVGDetector inicializado con config: {self.config}")
    
    def detect_bullish_fvg(self, candles: List[Dict]) -> Optional[FVGData]:
        """
        🟢 Detecta FVG Alcista usando patrón de 3 velas
        
        Patrón requerido:
        1. Vela 1: Cualquier configuración (baseline)
        2. Vela 2: Vela alcista fuerte (close > open, body_ratio >= 70%)
        3. Vela 3: Low > High(Vela 1) - forma el gap
        
        Args:
            candles: Lista de las últimas 3+ velas con OHLC
            
        Returns:
            FVGData si se detecta FVG válido, None en caso contrario
        """
        start_time = datetime.now()
        
        try:
            # Validar entrada
            if not self._validate_candle_input(candles):
                return None
            
            # Obtener las últimas 3 velas
            vela1, vela2, vela3 = candles[-3:]
            
            # 1. Validar que vela 2 es alcista fuerte
            if not self._is_strong_bullish_candle(vela2):
                logger.debug("Vela 2 no es alcista fuerte")
                return None
            
            # 2. Verificar formación del gap
            gap_bottom = vela1['high']
            gap_top = vela3['low']
            
            if gap_top <= gap_bottom:
                logger.debug(f"No hay gap: gap_top({gap_top}) <= gap_bottom({gap_bottom})")
                return None
            
            # 3. Validar tamaño del gap
            gap_size = gap_top - gap_bottom
            
            if not self._validate_gap_size(gap_size):
                logger.debug(f"Gap size inválido: {gap_size} ({gap_size * 10000:.1f} pips)")
                return None
            
            # 4. Crear objeto FVG
            fvg = FVGData(
                type='BULLISH',
                formation_time=self._parse_candle_time(vela3),
                gap_low=gap_bottom,
                gap_high=gap_top,
                gap_size=gap_size,
                formation_candles=[vela1, vela2, vela3],
                status='ACTIVE',
                timeframe=vela1.get('timeframe', 'UNKNOWN'),
                symbol=vela1.get('symbol', 'UNKNOWN')
            )
            
            # 5. Validación adicional si está habilitada
            if self.config['validation_enabled']:
                if not self._validate_fvg_structure(fvg):
                    return None
            
            # 6. Registrar métricas
            self._record_detection_metrics(start_time, True)
            self.metrics['total_detections'] += 1
            self.metrics['valid_detections'] += 1
            
            logger.info(f"✅ FVG BULLISH detectado: {gap_size * 10000:.1f} pips en {fvg.symbol} {fvg.timeframe}")
            
            return fvg
            
        except Exception as e:
            logger.error(f"Error detectando FVG bullish: {str(e)}")
            self._record_detection_metrics(start_time, False)
            return None
    
    def detect_bearish_fvg(self, candles: List[Dict]) -> Optional[FVGData]:
        """
        🔴 Detecta FVG Bajista usando patrón de 3 velas
        
        Patrón requerido:
        1. Vela 1: Cualquier configuración (baseline)
        2. Vela 2: Vela bajista fuerte (close < open, body_ratio >= 70%)
        3. Vela 3: High < Low(Vela 1) - forma el gap
        
        Args:
            candles: Lista de las últimas 3+ velas con OHLC
            
        Returns:
            FVGData si se detecta FVG válido, None en caso contrario
        """
        start_time = datetime.now()
        
        try:
            # Validar entrada
            if not self._validate_candle_input(candles):
                return None
            
            # Obtener las últimas 3 velas
            vela1, vela2, vela3 = candles[-3:]
            
            # 1. Validar que vela 2 es bajista fuerte
            if not self._is_strong_bearish_candle(vela2):
                logger.debug("Vela 2 no es bajista fuerte")
                return None
            
            # 2. Verificar formación del gap
            gap_top = vela1['low']
            gap_bottom = vela3['high']
            
            if gap_bottom >= gap_top:
                logger.debug(f"No hay gap: gap_bottom({gap_bottom}) >= gap_top({gap_top})")
                return None
            
            # 3. Validar tamaño del gap
            gap_size = gap_top - gap_bottom
            
            if not self._validate_gap_size(gap_size):
                logger.debug(f"Gap size inválido: {gap_size} ({gap_size * 10000:.1f} pips)")
                return None
            
            # 4. Crear objeto FVG
            fvg = FVGData(
                type='BEARISH',
                formation_time=self._parse_candle_time(vela3),
                gap_low=gap_bottom,
                gap_high=gap_top,
                gap_size=gap_size,
                formation_candles=[vela1, vela2, vela3],
                status='ACTIVE',
                timeframe=vela1.get('timeframe', 'UNKNOWN'),
                symbol=vela1.get('symbol', 'UNKNOWN')
            )
            
            # 5. Validación adicional si está habilitada
            if self.config['validation_enabled']:
                if not self._validate_fvg_structure(fvg):
                    return None
            
            # 6. Registrar métricas
            self._record_detection_metrics(start_time, True)
            self.metrics['total_detections'] += 1
            self.metrics['valid_detections'] += 1
            
            logger.info(f"✅ FVG BEARISH detectado: {gap_size * 10000:.1f} pips en {fvg.symbol} {fvg.timeframe}")
            
            return fvg
            
        except Exception as e:
            logger.error(f"Error detectando FVG bearish: {str(e)}")
            self._record_detection_metrics(start_time, False)
            return None
    
    def detect_all_fvgs(self, candles: List[Dict]) -> List[FVGData]:
        """
        🔍 Detecta todos los FVGs posibles en una secuencia de velas
        
        Args:
            candles: Lista de velas históricas
            
        Returns:
            Lista de FVGs detectados
        """
        if len(candles) < 3:
            return []
        
        detected_fvgs = []
        
        # Procesar velas en ventanas de 3
        for i in range(len(candles) - 2):
            window = candles[i:i+3]
            
            # Intentar detectar FVG bullish
            bullish_fvg = self.detect_bullish_fvg(window)
            if bullish_fvg:
                detected_fvgs.append(bullish_fvg)
            
            # Intentar detectar FVG bearish
            bearish_fvg = self.detect_bearish_fvg(window)
            if bearish_fvg:
                detected_fvgs.append(bearish_fvg)
        
        logger.info(f"Detección batch completada: {len(detected_fvgs)} FVGs encontrados en {len(candles)} velas")
        return detected_fvgs
    
    def _validate_candle_input(self, candles: List[Dict]) -> bool:
        """Valida que la entrada de velas sea correcta"""
        if not candles or len(candles) < 3:
            return False
        
        # Verificar que las velas tengan los campos requeridos
        required_fields = ['open', 'high', 'low', 'close', 'time']
        
        for candle in candles[-3:]:
            for field in required_fields:
                if field not in candle:
                    logger.warning(f"Campo requerido faltante: {field}")
                    return False
            
            # Validar que high >= low y que open/close estén en rango
            if not (candle['low'] <= candle['open'] <= candle['high'] and 
                    candle['low'] <= candle['close'] <= candle['high']):
                logger.warning(f"Datos OHLC inválidos en vela: {candle}")
                return False
        
        return True
    
    def _is_strong_bullish_candle(self, candle: Dict) -> bool:
        """
        Verifica si una vela es alcista fuerte
        
        Criterios:
        - Close > Open (alcista)
        - Body ratio >= min_body_ratio (fuerte)
        """
        body = candle['close'] - candle['open']
        total_range = candle['high'] - candle['low']
        
        if body <= 0:  # Debe ser alcista
            return False
        
        if total_range <= 0:  # Evitar división por cero
            return False
        
        body_ratio = body / total_range
        return body_ratio >= self.config['min_body_ratio']
    
    def _is_strong_bearish_candle(self, candle: Dict) -> bool:
        """
        Verifica si una vela es bajista fuerte
        
        Criterios:
        - Close < Open (bajista)
        - Body ratio >= min_body_ratio (fuerte)
        """
        body = candle['open'] - candle['close']
        total_range = candle['high'] - candle['low']
        
        if body <= 0:  # Debe ser bajista
            return False
        
        if total_range <= 0:  # Evitar división por cero
            return False
        
        body_ratio = body / total_range
        return body_ratio >= self.config['min_body_ratio']
    
    def _validate_gap_size(self, gap_size: float) -> bool:
        """Valida que el tamaño del gap esté en rango aceptable"""
        return (self.config['min_gap_size'] <= gap_size <= self.config['max_gap_size'])
    
    def _validate_fvg_structure(self, fvg: FVGData) -> bool:
        """Validación adicional de la estructura del FVG"""
        # Verificar coherencia matemática
        if fvg.gap_high <= fvg.gap_low:
            logger.warning("FVG inválido: gap_high <= gap_low")
            return False
        
        # Verificar que el gap_size calculado sea correcto
        calculated_size = fvg.gap_high - fvg.gap_low
        if abs(calculated_size - fvg.gap_size) > 0.000001:  # Tolerancia para floating point
            logger.warning("FVG inválido: gap_size calculado no coincide")
            return False
        
        return True
    
    def _parse_candle_time(self, candle: Dict) -> datetime:
        """Convierte el tiempo de la vela a datetime object"""
        time_value = candle['time']
        
        if isinstance(time_value, str):
            # Intentar parsear string ISO
            try:
                return datetime.fromisoformat(time_value.replace('Z', '+00:00'))
            except:
                return datetime.now(timezone.utc)
        elif isinstance(time_value, datetime):
            return time_value
        else:
            # Fallback
            return datetime.now(timezone.utc)
    
    def _record_detection_metrics(self, start_time: datetime, success: bool):
        """Registra métricas de performance de detección"""
        processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        self.metrics['processing_times'].append(processing_time_ms)
        
        if not success:
            self.metrics['false_positives'] += 1
    
    def get_performance_metrics(self) -> Dict:
        """
        Retorna métricas de performance del detector
        
        Returns:
            Dict con métricas actuales
        """
        processing_times = list(self.metrics['processing_times'])
        
        metrics = {
            'total_detections': self.metrics['total_detections'],
            'valid_detections': self.metrics['valid_detections'],
            'false_positives': self.metrics['false_positives'],
            'accuracy_rate': 0.0,
            'avg_processing_time_ms': 0.0,
            'max_processing_time_ms': 0.0,
            'min_processing_time_ms': 0.0
        }
        
        # Calcular accuracy rate
        if self.metrics['total_detections'] > 0:
            metrics['accuracy_rate'] = (self.metrics['valid_detections'] / 
                                      self.metrics['total_detections']) * 100
        
        # Calcular estadísticas de tiempo de procesamiento
        if processing_times:
            metrics['avg_processing_time_ms'] = np.mean(processing_times)
            metrics['max_processing_time_ms'] = np.max(processing_times)
            metrics['min_processing_time_ms'] = np.min(processing_times)
        
        return metrics

class RealTimeFVGDetector:
    """
    ⚡ DETECTOR EN TIEMPO REAL
    
    Extiende FVGDetector para procesamiento en tiempo real
    con buffer de velas y gestión de estado.
    """
    
    def __init__(self, symbols: List[str] = None, timeframes: List[str] = None, config: Dict = None):
        """
        Inicializa detector en tiempo real
        
        Args:
            symbols: Lista de símbolos a monitorear
            timeframes: Lista de timeframes a analizar
            config: Configuración del detector base
        """
        self.detector = FVGDetector(config)
        self.symbols = symbols or ['EURUSD']
        self.timeframes = timeframes or ['M5', 'M15', 'H1']
        
        # Buffers de velas por símbolo/timeframe
        self.candle_buffers = {}
        
        # FVGs activos
        self.active_fvgs = {}
        
        # Callbacks para eventos
        self.on_fvg_detected = None
        self.on_fvg_filled = None
        
        # Inicializar buffers
        for symbol in self.symbols:
            for timeframe in self.timeframes:
                key = f"{symbol}_{timeframe}"
                self.candle_buffers[key] = deque(maxlen=100)  # Buffer circular
        
        logger.info(f"RealTimeFVGDetector inicializado para {self.symbols} en {self.timeframes}")
    
    async def process_new_candle(self, symbol: str, timeframe: str, candle: Dict) -> List[FVGData]:
        """
        🔄 Procesa nueva vela en tiempo real
        
        Args:
            symbol: Símbolo de la vela
            timeframe: Timeframe de la vela
            candle: Datos de la vela
            
        Returns:
            Lista de nuevos FVGs detectados
        """
        key = f"{symbol}_{timeframe}"
        
        # Agregar vela al buffer
        if key not in self.candle_buffers:
            self.candle_buffers[key] = deque(maxlen=100)
        
        # Enriquecer vela con metadatos
        enriched_candle = {
            **candle,
            'symbol': symbol,
            'timeframe': timeframe
        }
        
        self.candle_buffers[key].append(enriched_candle)
        
        new_fvgs = []
        
        # Solo procesar si tenemos al menos 3 velas
        if len(self.candle_buffers[key]) >= 3:
            # Obtener últimas 3 velas
            last_3_candles = list(self.candle_buffers[key])[-3:]
            
            # Detectar FVG bullish
            bullish_fvg = self.detector.detect_bullish_fvg(last_3_candles)
            if bullish_fvg:
                fvg_id = self._generate_fvg_id(bullish_fvg)
                self.active_fvgs[fvg_id] = bullish_fvg
                new_fvgs.append(bullish_fvg)
                
                # Callback para nuevo FVG
                if self.on_fvg_detected:
                    await self.on_fvg_detected(bullish_fvg)
            
            # Detectar FVG bearish
            bearish_fvg = self.detector.detect_bearish_fvg(last_3_candles)
            if bearish_fvg:
                fvg_id = self._generate_fvg_id(bearish_fvg)
                self.active_fvgs[fvg_id] = bearish_fvg
                new_fvgs.append(bearish_fvg)
                
                # Callback para nuevo FVG
                if self.on_fvg_detected:
                    await self.on_fvg_detected(bearish_fvg)
        
        # Actualizar estado de FVGs existentes
        await self._update_existing_fvgs(symbol, timeframe, enriched_candle)
        
        return new_fvgs
    
    async def _update_existing_fvgs(self, symbol: str, timeframe: str, current_candle: Dict):
        """Actualiza estado de FVGs existentes"""
        current_price = current_candle['close']
        filled_fvgs = []
        
        # Revisar FVGs activos para este símbolo/timeframe
        key_pattern = f"{symbol}_{timeframe}"
        
        for fvg_id, fvg in list(self.active_fvgs.items()):
            if not fvg_id.startswith(key_pattern):
                continue
            
            # Verificar si el FVG ha sido llenado
            if self._is_fvg_filled(fvg, current_candle):
                fvg.status = 'FILLED'
                fill_time = self.detector._parse_candle_time(current_candle)
                
                # Notificar llenado
                if self.on_fvg_filled:
                    await self.on_fvg_filled(fvg, current_candle)
                
                filled_fvgs.append(fvg_id)
                
                logger.info(f"🎯 FVG {fvg.type} llenado: {fvg.gap_size * 10000:.1f} pips")
        
        # Remover FVGs llenados de activos
        for fvg_id in filled_fvgs:
            del self.active_fvgs[fvg_id]
    
    def _is_fvg_filled(self, fvg: FVGData, candle: Dict) -> bool:
        """Verifica si un FVG ha sido llenado por la vela actual"""
        if fvg.type == 'BULLISH':
            # FVG alcista se llena si el precio toca o baja del gap_low
            return candle['low'] <= fvg.gap_low
        else:
            # FVG bajista se llena si el precio toca o sube del gap_high
            return candle['high'] >= fvg.gap_high
    
    def _generate_fvg_id(self, fvg: FVGData) -> str:
        """Genera ID único para el FVG"""
        timestamp = fvg.formation_time.strftime("%Y%m%d_%H%M%S")
        return f"{fvg.symbol}_{fvg.timeframe}_{fvg.type}_{timestamp}"
    
    def get_active_fvgs(self, symbol: str = None, timeframe: str = None) -> List[FVGData]:
        """
        Retorna FVGs activos, opcionalmente filtrados
        
        Args:
            symbol: Filtrar por símbolo
            timeframe: Filtrar por timeframe
            
        Returns:
            Lista de FVGs activos
        """
        filtered_fvgs = []
        
        for fvg_id, fvg in self.active_fvgs.items():
            # Aplicar filtros si se especifican
            if symbol and fvg.symbol != symbol:
                continue
            if timeframe and fvg.timeframe != timeframe:
                continue
                
            filtered_fvgs.append(fvg)
        
        return filtered_fvgs
    
    def set_callbacks(self, on_fvg_detected=None, on_fvg_filled=None):
        """
        Configura callbacks para eventos de FVG
        
        Args:
            on_fvg_detected: Callback async para cuando se detecta nuevo FVG
            on_fvg_filled: Callback async para cuando se llena un FVG
        """
        self.on_fvg_detected = on_fvg_detected
        self.on_fvg_filled = on_fvg_filled

# Función de utilidad para testing rápido
def quick_test_detector():
    """🧪 Test rápido del detector"""
    print("🔍 Testing FVG Detector...")
    
    # Datos de prueba: FVG alcista
    test_candles_bullish = [
        {'time': '2025-08-12 10:00', 'open': 1.1000, 'high': 1.1010, 'low': 1.0995, 'close': 1.1005},
        {'time': '2025-08-12 10:05', 'open': 1.1005, 'high': 1.1025, 'low': 1.1003, 'close': 1.1023},  # Strong bull
        {'time': '2025-08-12 10:10', 'open': 1.1020, 'high': 1.1030, 'low': 1.1015, 'close': 1.1025}   # Gap
    ]
    
    # Datos de prueba: FVG bajista
    test_candles_bearish = [
        {'time': '2025-08-12 11:00', 'open': 1.1020, 'high': 1.1025, 'low': 1.1015, 'close': 1.1018},
        {'time': '2025-08-12 11:05', 'open': 1.1018, 'high': 1.1020, 'low': 1.1000, 'close': 1.1002},  # Strong bear
        {'time': '2025-08-12 11:10', 'open': 1.1000, 'high': 1.1010, 'low': 1.0995, 'close': 1.1008}   # Gap
    ]
    
    detector = FVGDetector()
    
    # Test FVG alcista
    bullish_fvg = detector.detect_bullish_fvg(test_candles_bullish)
    if bullish_fvg:
        print(f"✅ FVG Alcista detectado: {bullish_fvg.gap_size * 10000:.1f} pips")
        print(f"   Gap: {bullish_fvg.gap_low:.5f} - {bullish_fvg.gap_high:.5f}")
    else:
        print("❌ No se detectó FVG alcista")
    
    # Test FVG bajista
    bearish_fvg = detector.detect_bearish_fvg(test_candles_bearish)
    if bearish_fvg:
        print(f"✅ FVG Bajista detectado: {bearish_fvg.gap_size * 10000:.1f} pips")
        print(f"   Gap: {bearish_fvg.gap_low:.5f} - {bearish_fvg.gap_high:.5f}")
    else:
        print("❌ No se detectó FVG bajista")
    
    # Mostrar métricas
    metrics = detector.get_performance_metrics()
    print(f"\n📊 Métricas: {metrics}")

if __name__ == "__main__":
    quick_test_detector()
