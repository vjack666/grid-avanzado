# 💰 OFICINA TRADING - PISO 3
**Gestión de Riesgo y Ejecución de Órdenes FVG**

**Fecha:** Agosto 13, 2025  
**Estado:** En Desarrollo Activo  
**Progreso:** 40%

---

## 🎯 **RESUMEN EJECUTIVO**

La **Oficina Trading** del Piso 3 es responsable de convertir el análisis FVG en operaciones reales de trading, integrando:

- **🛡️ Gestión de Riesgo Específica FVG** basada en RiskBotMT5
- **📊 Cálculo de Lotaje Dinámico** según calidad y confluencias
- **⚡ Ejecución Inteligente de Órdenes** con SL/TP adaptativos
- **📈 Monitoreo de Performance** de estrategias FVG

---

## 🏗️ **COMPONENTES PRINCIPALES**

### 1. **🛡️ FVGRiskManager**
**Archivo:** `src/analysis/piso_3/trading/fvg_risk_manager.py`  
**Estado:** 🔄 En Desarrollo

**Funcionalidades:**
- Hereda de `RiskBotMT5` para mantener compatibilidad
- Cálculo de lotaje basado en calidad FVG (0-10 score)
- Gestión de riesgo por confluencias FVG-Estocástico
- Límites dinámicos según volatilidad del mercado

**Base Técnica:**
```python
# Integración con RiskBotMT5 existente
from src.core.riskbot_mt5 import RiskBotMT5

class FVGRiskManager(RiskBotMT5):
    def __init__(self, symbol='EURUSD'):
        super().__init__(
            risk_target_profit=100,
            max_profit_target=300, 
            risk_percent=2.0,
            comision_por_lote=7.0
        )
        # Extensiones específicas FVG...
```

### 2. **📡 FVGSignalGenerator**
**Archivo:** `src/analysis/piso_3/trading/fvg_signal_generator.py`  
**Estado:** 📋 Planificado

**Funcionalidades:**
- Conversión de análisis FVG en señales ejecutables
- Rate limiting inteligente (máx 5 señales/hora)
- Filtros de calidad y confluencia
- Integración con Machine Learning predictor

### 3. **⚡ FVGOrderExecutor**
**Archivo:** `src/analysis/piso_3/trading/fvg_order_executor.py`  
**Estado:** 📋 Planificado

**Funcionalidades:**
- Ejecución segura de órdenes MT5
- SL/TP calculados según tamaño FVG
- Gestión de múltiples R:R (1.5, 2.5, 4.0)
- Fallback a ejecución tradicional

---

## 🔧 **INTEGRACIÓN CON RISKBOT MT5**

### **✅ Beneficios de la Herencia:**
- Mantiene toda la lógica de riesgo existente
- Compatible con sistema actual de trading
- Aprovecha métodos probados: `get_account_balance()`, `check_and_act()`
- Conserva gestión de posiciones: `get_open_positions()`

### **➕ Extensiones FVG Específicas:**
- **Lotaje Inteligente:** Ajustado por score de calidad FVG
- **Riesgo Confluencia:** Factor multiplicador por fuerza de confluencia
- **SL Dinámico:** Basado en tamaño del FVG (pips)
- **TP Múltiple:** Parciales en R:R 1.5, 2.5, 4.0

---

## 📊 **CASOS DE USO TÍPICOS**

### **Escenario 1: FVG Alta Calidad (Score 8.5+)**
```python
# Cálculo automático de riesgo
fvg_risk = FVGRiskManager('EURUSD')
risk_eval = fvg_risk.evaluate_fvg_trade({
    'quality_score': 8.7,
    'confluence_strength': 85,
    'fvg_size_pips': 12
})

# Resultado esperado:
# - Lotaje: 0.15 (aumentado por alta calidad)
# - SL: 15 pips (basado en tamaño FVG)
# - TP1: 22 pips (R:R 1.5)
# - TP2: 37 pips (R:R 2.5)
```

### **Escenario 2: FVG Calidad Media (Score 6.0-7.0)**
```python
risk_eval = fvg_risk.evaluate_fvg_trade({
    'quality_score': 6.5,
    'confluence_strength': 68,
    'fvg_size_pips': 8
})

# Resultado esperado:
# - Lotaje: 0.08 (reducido por calidad media)
# - SL: 12 pips
# - TP1: 18 pips (R:R 1.5)
```

---

## 🎯 **ROADMAP DE DESARROLLO**

### **Semana 1 (Agosto 13-20, 2025)**
- [x] Documentación técnica completada
- [ ] FVGRiskManager base implementado
- [ ] Tests unitarios para cálculo de lotaje
- [ ] Integración con FVGQualityAnalyzer

### **Semana 2 (Agosto 21-27, 2025)**
- [ ] FVGSignalGenerator implementado
- [ ] Rate limiting y filtros de calidad
- [ ] Integración con FVGMLPredictor
- [ ] Tests de generación de señales

### **Semana 3 (Agosto 28 - Sept 3, 2025)**
- [ ] FVGOrderExecutor implementado
- [ ] SL/TP dinámicos funcionando
- [ ] Ejecución múltiples R:R
- [ ] Tests de ejecución en demo

### **Semana 4 (Sept 4-10, 2025)**
- [ ] Integración completa pipeline
- [ ] Monitoreo de performance
- [ ] Validación en cuenta demo
- [ ] Preparación para producción

---

## 📈 **MÉTRICAS DE ÉXITO**

### **Técnicas:**
- ✅ Herencia correcta de RiskBotMT5
- ✅ Cálculo preciso de lotaje por calidad FVG
- ✅ SL/TP adaptativo según tamaño FVG
- ✅ Rate limiting < 5 señales/hora

### **Operativas:**
- 🎯 Win Rate objetivo: 70%+
- 🎯 Profit Factor objetivo: 1.5+
- 🎯 Max Drawdown: <10%
- 🎯 Tiempo ejecución: <2 segundos

---

## 🛡️ **SEGURIDAD Y RIESGO**

### **Límites Estrictos:**
- **Riesgo Máximo:** 2% por operación (heredado RiskBot)
- **Posiciones Simultáneas:** Máximo 3 FVG
- **Capital Diario:** Máximo 6% en riesgo total
- **Emergency Stop:** Activación automática -5% drawdown

### **Validaciones:**
- Double-check antes de ejecución
- Verificación confluencia > 70%
- Validación calidad FVG > 6.0
- Confirmación ML confidence > 75%

---

**📊 Estado Actual:** Base RiskBotMT5 identificada ✅  
**🎯 Próximo Hito:** FVGRiskManager funcional (Agosto 20)  
**👨‍💻 Responsable:** Sistema Trading Grid - Oficina Trading  

---

*Última actualización: Agosto 13, 2025 - 15:30*
