# 🗂️ PLAN DE REORGANIZACIÓN - ARCHIVOS REALES PISO 3

## 🎯 OBJETIVO: Consolidar archivos que trabajarán definitivamente en REAL

### 📊 MOVIMIENTOS NECESARIOS:

#### 1. 🔍 **DETECCIÓN (YA ORGANIZADOS) ✅**
```
src/analysis/piso_3/deteccion/
├── __init__.py ✅ (ConfluenceAnalyzer - REAL VALIDADO)
├── fvg_detector.py ← MOVER desde src/analysis/
├── multi_timeframe_detector.py ← MOVER desde src/analysis/
└── fvg_alert_system.py ← MOVER desde src/analysis/
```

#### 2. 📊 **ANÁLISIS (VALIDAR Y LIMPIAR)**
```
src/analysis/piso_3/analisis/
├── __init__.py (FVGQualityAnalyzer) ← VALIDAR CON DEMO
├── fvg_predictor.py ← EXTRAER de __init__.py
├── session_analyzer.py ← EXTRAER de __init__.py
└── market_regime_detector.py ← EXTRAER de __init__.py
```

#### 3. 🤖 **IA (MODULARIZAR)**
```
src/analysis/piso_3/ia/
├── __init__.py ← LIMPIAR
├── ml_predictor.py ← CREAR ESPECÍFICO
├── pattern_recognizer.py ← CREAR ESPECÍFICO
└── auto_optimizer.py ← CREAR ESPECÍFICO
```

#### 4. 💰 **TRADING (REAL)**
```
src/analysis/piso_3/trading/
├── __init__.py ← VALIDAR
├── signal_generator.py ← EXTRAER
├── risk_manager.py ← EXTRAER
└── live_trader.py ← EXTRAER
```

#### 5. 🔗 **INTEGRACIÓN (DASHBOARD)**
```
src/analysis/piso_3/integracion/
├── __init__.py ← LIMPIAR
├── dashboard.py ← EXTRAER
├── live_monitor.py ← EXTRAER
└── data_integrator.py ← EXTRAER
```

### 🧹 LIMPIEZA NECESARIA:

#### ❌ **ARCHIVOS A DEPRECAR:**
```
src/analysis/ (mantener solo archivos heredados necesarios)
├── analisis_estocastico_m15.py ← EVALUAR SI ES NECESARIO
├── grid_bollinger.py ← EVALUAR SI ES NECESARIO
└── __init__.py ← MANTENER PARA COMPATIBILIDAD
```

### 🎯 RESULTADO FINAL:

#### ✅ **ESTRUCTURA LIMPIA PARA REAL:**
```
src/analysis/piso_3/
├── deteccion/
│   ├── fvg_detector.py ✅ REAL
│   ├── multi_timeframe_detector.py ✅ REAL
│   ├── fvg_alert_system.py ✅ REAL
│   └── __init__.py (ConfluenceAnalyzer) ✅ REAL
├── analisis/
│   ├── fvg_quality_analyzer.py 🎯 SIGUIENTE
│   ├── fvg_predictor.py
│   ├── session_analyzer.py
│   └── market_regime_detector.py
├── ia/
│   ├── ml_predictor.py
│   ├── pattern_recognizer.py
│   └── auto_optimizer.py
├── trading/
│   ├── signal_generator.py
│   ├── risk_manager.py
│   └── live_trader.py
└── integracion/
    ├── dashboard.py
    ├── live_monitor.py
    └── data_integrator.py
```

## 🚀 ACCIÓN INMEDIATA:

### 1. **CONSOLIDAR DETECCIÓN** (5 min)
Mover archivos core validados a piso_3/deteccion/

### 2. **VALIDAR ANÁLISIS** (2-3 horas)
Crear demo para FVGQualityAnalyzer y modularizar

### 3. **LIMPIAR ESTRUCTURA** (30 min)
Eliminar duplicaciones y organizar imports
