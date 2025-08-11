# FASE 5 IMPLEMENTATION: IndicatorManager

## 📅 **Información del Plan**
- **Fecha de Inicio:** 2025-08-10
- **Fase:** FASE 5 - IndicatorManager
- **Prerrequisitos:** ✅ FASE 4 (DataManager) completada
- **Objetivo:** Gestión avanzada de indicadores técnicos y señales compuestas

---

## 🎯 **OBJETIVOS PRINCIPALES**

### **1. IndicatorManager Core**
- Crear `src/core/indicator_manager.py`
- Gestión avanzada de indicadores técnicos
- Sistema de señales compuestas
- Optimización automática de parámetros
- Performance analytics de indicadores

### **2. Indicadores Técnicos Avanzados**
- **MACD** (Moving Average Convergence Divergence)
- **EMA** (Exponential Moving Average)
- **Williams %R**
- **ADX** (Average Directional Index)
- **ATR** (Average True Range)
- **CCI** (Commodity Channel Index)

### **3. Sistema de Señales Compuestas**
- Combinación de múltiples indicadores
- Algoritmos de confirmación de señales
- Pesos y scoring de indicadores
- Filtros de calidad de señal

### **4. Integración con DataManager**
- Uso optimizado de DataManager para datos
- Cache específico para indicadores
- Reutilización de cálculos base

---

## 🏗️ **ARQUITECTURA DETALLADA**

### **📁 Estructura IndicatorManager**
```python
class IndicatorManager:
    def __init__(self, data_manager, logger_manager=None):
        # Inicialización con dependencias
        
    # === INDICADORES BÁSICOS (desde DataManager) ===
    def get_bollinger_bands(self, symbol, timeframe, periods=20, deviation=2.0)
    def get_stochastic(self, symbol, timeframe, k_period=14, d_period=3)
    def get_rsi(self, symbol, timeframe, period=14)
    def get_sma(self, symbol, timeframe, period=20)
    
    # === INDICADORES AVANZADOS (FASE 5) ===
    def calculate_macd(self, df, fast=12, slow=26, signal=9)
    def calculate_ema(self, df, period=20)
    def calculate_williams_r(self, df, period=14)
    def calculate_adx(self, df, period=14)
    def calculate_atr(self, df, period=14)
    def calculate_cci(self, df, period=20)
    
    # === SISTEMA DE SEÑALES ===
    def generate_compound_signal(self, symbol, timeframe, strategy="balanced")
    def calculate_signal_strength(self, indicators_data)
    def validate_signal_quality(self, signal_data)
    def get_signal_history(self, symbol, timeframe, limit=100)
    
    # === OPTIMIZACIÓN Y ANALYTICS ===
    def optimize_parameters(self, symbol, timeframe, indicator_name)
    def get_indicator_performance(self, indicator_name, period_days=30)
    def backtest_strategy(self, symbol, timeframe, strategy_config)
    
    # === GESTIÓN DE CACHE ===
    def cache_indicator_result(self, key, result, ttl=300)
    def get_cached_indicator(self, key)
    def clear_indicator_cache(self)
```

### **🎯 Estrategias de Señales Compuestas**

#### **1. Estrategia "Momentum Breakout"**
```python
# Condiciones:
# - RSI > 70 (sobrecompra) o RSI < 30 (sobreventa)
# - MACD crossover positivo/negativo
# - Bollinger Bands breakout
# - Williams %R confirmación
```

#### **2. Estrategia "Trend Following"**
```python
# Condiciones:
# - ADX > 25 (tendencia fuerte)
# - EMA(12) > EMA(26) para alcista
# - RSI entre 40-60 (no sobrecompra/sobreventa)
# - ATR para stop-loss dinámico
```

#### **3. Estrategia "Mean Reversion"**
```python
# Condiciones:
# - Precio toca Bollinger Bands externas
# - RSI en zona extrema (>80 o <20)
# - Estocástico en divergencia
# - CCI confirmación de reversa
```

---

## 📊 **DISEÑO DE IMPLEMENTACIÓN**

### **🔧 Paso 1: Core Implementation**
```python
# src/core/indicator_manager.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

class IndicatorManager:
    def __init__(self, data_manager, logger_manager=None, error_manager=None):
        self.data_manager = data_manager
        self.logger = logger_manager
        self.error_manager = error_manager
        self.indicator_cache = {}
        self.signal_history = {}
        
        if self.logger:
            self.logger.log_info("IndicatorManager inicializado correctamente")
```

### **🔧 Paso 2: Indicadores Avanzados**
```python
def calculate_macd(self, df: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
    """Calcular MACD (Moving Average Convergence Divergence)"""
    try:
        close = df['close'] if 'close' in df.columns else df['Close']
        
        # EMA rápida y lenta
        ema_fast = close.ewm(span=fast).mean()
        ema_slow = close.ewm(span=slow).mean()
        
        # MACD Line
        macd_line = ema_fast - ema_slow
        
        # Signal Line
        signal_line = macd_line.ewm(span=signal).mean()
        
        # Histograma
        histogram = macd_line - signal_line
        
        result = df.copy()
        result['MACD'] = macd_line
        result['MACD_Signal'] = signal_line
        result['MACD_Histogram'] = histogram
        
        return result
        
    except Exception as e:
        if self.error_manager:
            self.error_manager.handle_error(e, "IndicatorManager.calculate_macd")
        return None
```

### **🔧 Paso 3: Sistema de Señales**
```python
def generate_compound_signal(self, symbol: str, timeframe: str, strategy="balanced") -> Dict:
    """Generar señal compuesta basada en múltiples indicadores"""
    try:
        # Obtener datos OHLC
        df = self.data_manager.get_ohlc_data(symbol, timeframe, 50)
        if df is None:
            return {"signal": "NO_DATA", "strength": 0, "indicators": {}}
            
        # Calcular indicadores
        bollinger = self.data_manager.calculate_bollinger_bands(df)
        rsi_data = self.data_manager.calculate_rsi(df)
        macd_data = self.calculate_macd(df)
        stoch_data = self.data_manager.calculate_stochastic(df)
        
        # Obtener valores actuales
        current_price = df['close'].iloc[-1]
        bb_upper = bollinger['BB_Upper'].iloc[-1]
        bb_lower = bollinger['BB_Lower'].iloc[-1]
        rsi = rsi_data['RSI'].iloc[-1]
        macd = macd_data['MACD'].iloc[-1]
        macd_signal = macd_data['MACD_Signal'].iloc[-1]
        stoch_k = stoch_data['%K'].iloc[-1]
        stoch_d = stoch_data['%D'].iloc[-1]
        
        # Lógica de estrategia
        if strategy == "momentum_breakout":
            return self._momentum_breakout_strategy(
                current_price, bb_upper, bb_lower, rsi, macd, macd_signal, stoch_k, stoch_d
            )
        elif strategy == "trend_following":
            return self._trend_following_strategy(df, rsi, macd, macd_signal)
        else:  # balanced
            return self._balanced_strategy(
                current_price, bb_upper, bb_lower, rsi, macd, macd_signal, stoch_k, stoch_d
            )
            
    except Exception as e:
        if self.error_manager:
            self.error_manager.handle_error(e, "IndicatorManager.generate_compound_signal")
        return {"signal": "ERROR", "strength": 0, "indicators": {}}
```

---

## 🧪 **PLAN DE TESTING**

### **📋 Tests Unitarios**
```python
def test_indicator_manager():
    """Test completo de IndicatorManager"""
    
    # 1. Inicialización
    assert indicator_manager is not None
    
    # 2. Indicadores avanzados
    df_test = create_test_ohlc_data()
    macd_result = indicator_manager.calculate_macd(df_test)
    assert 'MACD' in macd_result.columns
    
    # 3. Señales compuestas
    signal = indicator_manager.generate_compound_signal("EURUSD", "M15")
    assert signal['signal'] in ['BUY', 'SELL', 'HOLD', 'NO_DATA']
    
    # 4. Performance analytics
    performance = indicator_manager.get_indicator_performance('RSI')
    assert isinstance(performance, dict)
```

### **📊 Tests de Integración**
```python
def test_integration_with_datamanager():
    """Verificar integración correcta con DataManager"""
    
    # Verificar que usa DataManager para datos base
    signal = indicator_manager.generate_compound_signal("EURUSD", "M15")
    
    # Verificar cache de indicadores
    cached_result = indicator_manager.get_cached_indicator("EURUSD_M15_MACD")
    
    # Verificar logs
    assert "IndicatorManager" in recent_logs
```

---

## 📋 **PLAN DE IMPLEMENTACIÓN**

### **🔄 Fase 5.1: Core Implementation (30 minutos)**
1. Crear `src/core/indicator_manager.py`
2. Implementar estructura base y inicialización
3. Integrar con DataManager existente
4. Añadir logging y error handling

### **🔄 Fase 5.2: Indicadores Avanzados (45 minutos)**
1. Implementar MACD
2. Implementar EMA
3. Implementar Williams %R
4. Implementar ADX
5. Implementar ATR
6. Añadir tests unitarios

### **🔄 Fase 5.3: Sistema de Señales (30 minutos)**
1. Implementar lógica de señales compuestas
2. Crear estrategias predefinidas
3. Sistema de scoring y validación
4. Tests de integración

### **🔄 Fase 5.4: Integración y Validación (15 minutos)**
1. Integrar en main.py
2. Actualizar tests del sistema
3. Validar funcionamiento completo
4. Documentar y finalizar

---

## 📊 **MÉTRICAS DE ÉXITO**

### **✅ Criterios de Aceptación**
- [ ] IndicatorManager implementado y funcional
- [ ] Al menos 5 indicadores avanzados funcionando
- [ ] Sistema de señales compuestas operativo
- [ ] Tests 12/12 pasando (nueva adición)
- [ ] Integración exitosa con DataManager
- [ ] Performance satisfactoria (<1.5s tests)

### **📈 KPIs Esperados**
- **Cobertura de Indicadores:** 10+ indicadores técnicos
- **Estrategias de Señales:** 3 estrategias implementadas
- **Performance:** Tests en <1.5 segundos
- **Robustez:** 100% tests pasando

---

## 🎯 **RESULTADO ESPERADO**

Al finalizar FASE 5, el sistema tendrá:

1. **🎯 Gestión Avanzada de Indicadores**
   - 10+ indicadores técnicos centralizados
   - Sistema de cache optimizado para indicadores
   - Reutilización eficiente de cálculos

2. **🚀 Señales de Trading Inteligentes**
   - Señales compuestas multi-indicador
   - Estrategias predefinidas optimizadas
   - Sistema de scoring y validación

3. **📊 Analytics y Optimización**
   - Performance tracking de indicadores
   - Optimización automática de parámetros
   - Backtesting básico de estrategias

4. **🔗 Integración Completa**
   - IndicatorManager integrado en main.py
   - Uso optimizado de DataManager
   - Tests ampliados y validados

---

## ✅ **LISTO PARA COMENZAR IMPLEMENTACIÓN**

Todos los aspectos de FASE 5 están planificados y documentados. El sistema está preparado para la implementación de IndicatorManager con:

- ✅ Arquitectura definida
- ✅ Plan de implementación detallado  
- ✅ Tests planificados
- ✅ Métricas de éxito establecidas
- ✅ Integración con FASE 4 asegurada

**🚀 COMENZANDO IMPLEMENTACIÓN DE FASE 5**
