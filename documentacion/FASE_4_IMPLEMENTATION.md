# FASE 4 IMPLEMENTATION PLAN - DataManager

## 📋 Información del Plan
- **Fase**: 4 de 6
- **Componente**: DataManager
- **Fecha de planificación**: 2025-08-10
- **Responsable**: GitHub Copilot
- **Protocolo**: TRADING GRID v2.0

## 🎯 Objetivo Principal

Implementar un sistema centralizado de manejo de datos (DataManager) que unifique todo el procesamiento, cache y validación de datos de mercado dispersos en el sistema Trading Grid.

## 📊 Análisis de Estado Actual

### ✅ Base Establecida (Fases 1-3)
- **ConfigManager**: Rutas y configuraciones centralizadas
- **LoggerManager**: Logging unificado con Rich UI
- **ErrorManager**: Error handling robusto con validaciones
- **Tests**: 10/10 pasando (100% success rate)

### 🔍 Problemas Identificados en Datos
1. **Duplicación de lógica OHLC** en múltiples archivos
2. **Cache disperso** sin estrategia unificada
3. **Validaciones inconsistentes** de DataFrames
4. **Procesamiento duplicado** de indicadores técnicos
5. **Manejo manual** de timeframes y símbolos

## 🏗️ Diseño de DataManager

### Responsabilidades Centralizadas
```python
class DataManager:
    """
    Sistema centralizado de manejo de datos para Trading Grid.
    
    Unifica 6 sistemas de datos diferentes:
    1. Obtención OHLC -> get_ohlc_data()
    2. Cache inteligente -> cache_manager
    3. Indicadores técnicos -> get_indicators()  
    4. Validación de datos -> validate_data()
    5. Timeframes -> normalize_timeframe()
    6. Limpieza de datos -> clean_data()
    """
```

### Arquitectura Propuesta
```
DataManager
├── 📈 OHLC Data Handler
│   ├── get_ohlc_data(symbol, timeframe, periods)
│   ├── validate_ohlc_data(dataframe)
│   └── normalize_ohlc_columns(dataframe)
│
├── 💾 Cache Manager  
│   ├── cache_data(key, data, ttl)
│   ├── get_cached_data(key)
│   └── clear_cache(pattern)
│
├── 📊 Technical Indicators
│   ├── calculate_bollinger_bands(data, period)
│   ├── calculate_stochastic(data, k_period, d_period)
│   └── calculate_moving_averages(data, periods)
│
├── 🔍 Data Validation
│   ├── validate_dataframe_structure(df)
│   ├── check_data_completeness(df)
│   └── detect_data_anomalies(df)
│
└── 🛠️ Data Utilities
    ├── normalize_timeframe(timeframe_str)
    ├── clean_data(dataframe)
    └── merge_data_sources(sources)
```

## 📁 Archivos a Refactorizar

### Archivos con Lógica de Datos Dispersa
1. **grid_bollinger.py**
   - Lógica OHLC duplicada
   - Cálculo Bollinger Bands
   - Validación de datos manual

2. **analisis_estocastico_m15.py**
   - Obtención datos M15
   - Cálculo estocástico
   - Cache manual

3. **descarga_velas.py**
   - Descarga y guardado CSV
   - Normalización columnas
   - Validación básica

4. **src/core/main.py**
   - Múltiples llamadas MT5
   - Procesamiento datos disperso
   - Validaciones manuales

## 🔧 Implementación Detallada

### 1. Creación de DataManager Core
```python
# src/core/data_manager.py
class DataManager:
    def __init__(self, config_manager=None, logger_manager=None, error_manager=None):
        # Integración con fases anteriores
        self.config = config_manager
        self.logger = logger_manager  
        self.error_manager = error_manager
        
        # Cache configuration
        self.cache = {}
        self.cache_ttl = {}
        
        # Data sources
        self.mt5_available = self._check_mt5_availability()
```

### 2. Métodos de Obtención de Datos
```python
def get_ohlc_data(self, symbol: str, timeframe: str, periods: int = 1000) -> pd.DataFrame:
    """
    Obtiene datos OHLC con cache y validación automática.
    
    Args:
        symbol: Símbolo de trading (ej: 'EURUSD')
        timeframe: Timeframe normalizado ('M5', 'M15', 'H1', 'H4')
        periods: Número de períodos a obtener
        
    Returns:
        DataFrame validado con columnas OHLC estándar
    """
    
def get_indicators(self, data: pd.DataFrame, indicators: list) -> pd.DataFrame:
    """
    Calcula indicadores técnicos de forma centralizada.
    
    Args:
        data: DataFrame con datos OHLC
        indicators: Lista de indicadores ['bb', 'stoch', 'ma']
        
    Returns:
        DataFrame original + columnas de indicadores
    """
```

### 3. Sistema de Cache Inteligente
```python
def cache_data(self, key: str, data: Any, ttl_seconds: int = 300):
    """Cache con TTL automático"""
    
def get_cached_data(self, key: str) -> Optional[Any]:
    """Obtiene datos del cache si están vigentes"""
    
def _generate_cache_key(self, symbol: str, timeframe: str, params: dict) -> str:
    """Genera claves de cache consistentes"""
```

### 4. Validaciones Centralizadas
```python
def validate_ohlc_data(self, data: pd.DataFrame) -> bool:
    """
    Valida estructura y calidad de datos OHLC.
    
    Checks:
    - Columnas requeridas: ['open', 'high', 'low', 'close', 'volume']
    - Consistencia OHLC: high >= open/close >= low
    - Datos faltantes críticos
    - Anomalías de precio
    """
```

## 🧪 Plan de Testing

### Tests de DataManager Aislado
```python
def test_data_manager():
    """Test completo de DataManager"""
    dm = DataManager(config, logger, error_manager)
    
    # Test obtención datos
    data = dm.get_ohlc_data('EURUSD', 'M15', 100)
    assert isinstance(data, pd.DataFrame)
    assert len(data) > 0
    
    # Test validación
    valid = dm.validate_ohlc_data(data)
    assert valid == True
    
    # Test cache
    cached = dm.get_cached_data('test_key')
    # etc...
```

### Integración con Tests Existentes
- Actualizar tests existentes para usar DataManager
- Mantener 10/10 tests pasando durante transición
- Agregar test específico de DataManager (11/11 total)

## 📈 Beneficios Esperados

### Centralización de Datos
- **Punto único** para toda obtención de datos
- **Cache inteligente** reduce llamadas MT5
- **Validación automática** de calidad de datos
- **Indicadores centralizados** sin duplicación

### Performance
- **Cache con TTL** reduce latencia
- **Validación eficiente** evita procesamiento inválido
- **Batch processing** para múltiples timeframes
- **Memory management** optimizado

### Mantenibilidad
- **Lógica unificada** fácil de mantener
- **Testing centralizado** de toda funcionalidad de datos
- **Debugging simplificado** con logging estructurado
- **Escalabilidad** para nuevos indicadores

## 🔄 Plan de Integración

### Fase 4A: Implementación Core
1. Crear `src/core/data_manager.py`
2. Implementar métodos básicos OHLC
3. Probar en aislamiento
4. Agregar test específico

### Fase 4B: Cache System
1. Implementar sistema de cache con TTL
2. Integrar con ConfigManager para configuración
3. Probar performance del cache
4. Validar con ErrorManager

### Fase 4C: Indicadores Técnicos
1. Migrar cálculo Bollinger Bands
2. Migrar cálculo Estocástico
3. Implementar Moving Averages
4. Validar contra implementaciones existentes

### Fase 4D: Refactorización
1. Refactorizar `grid_bollinger.py` para usar DataManager
2. Refactorizar `analisis_estocastico_m15.py`
3. Actualizar `main.py` con DataManager
4. Validar 11/11 tests pasando

## 📋 Checklist de Implementación

### Preparación
- [ ] Analizar archivos existentes con lógica de datos
- [ ] Identificar patrones comunes de uso
- [ ] Diseñar interfaz DataManager
- [ ] Crear estructura base del archivo

### Implementación Core
- [ ] Clase DataManager con integración tri-fase
- [ ] Método get_ohlc_data() con cache
- [ ] Sistema de validación de DataFrames
- [ ] Manejo de errores con ErrorManager

### Cache System
- [ ] Cache con TTL configurable
- [ ] Generación de claves consistentes
- [ ] Limpieza automática de cache expirado
- [ ] Métricas de hit/miss ratio

### Indicadores Técnicos
- [ ] Bollinger Bands centralizadas
- [ ] Estocástico centralizado
- [ ] Moving Averages básicas
- [ ] Framework para nuevos indicadores

### Testing y Validación
- [ ] Test aislado de DataManager
- [ ] Test de integración con fases anteriores
- [ ] Validación de performance
- [ ] 11/11 tests pasando

### Refactorización
- [ ] grid_bollinger.py usando DataManager
- [ ] analisis_estocastico_m15.py usando DataManager
- [ ] main.py usando DataManager
- [ ] descarga_velas.py usando DataManager

## 🎯 Criterios de Éxito

### Funcionalidad
- ✅ DataManager funciona en aislamiento
- ✅ Cache reduce latencia en 80%+
- ✅ Validación automática detecta anomalías
- ✅ Indicadores coinciden con implementación actual

### Calidad
- ✅ 11/11 tests pasando (100%)
- ✅ Integración con ConfigManager + LoggerManager + ErrorManager
- ✅ Logging estructurado de toda actividad de datos
- ✅ Error handling robusto para fallos de datos

### Performance
- ✅ Tiempo de obtención datos < 1s
- ✅ Cache hit ratio > 70%
- ✅ Memory usage optimizado
- ✅ Sin duplicación de procesamiento

---

**Próximo paso**: Implementar DataManager core siguiendo este plan detallado y manteniendo el protocolo de calidad establecido (testing continuo, documentación exhaustiva, integración progresiva).
