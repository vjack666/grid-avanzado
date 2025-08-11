# 🔧 ESPECIFICACIONES TÉCNICAS REALES - SÓTANO 2
**Implementación basada en código actual del SÓTANO 1**

**Fecha:** 2025-08-11  
**Basado en:** AUDIT_SISTEMA_ACTUAL.md  
**Propósito:** Especificaciones técnicas detalladas para implementar SÓTANO 2

---

## 📊 **RESUMEN EJECUTIVO**

### **🎯 ENFOQUE REALISTA:**
- ✅ **Basado en código existente**: Usar APIs reales del SÓTANO 1
- ✅ **Integración garantizada**: Compatible con sistema actual
- ✅ **Testing desde día 1**: Cada componente con tests
- ✅ **Desarrollo incremental**: Funcionalidad básica → avanzada

---

## 🏗️ **ARQUITECTURA TÉCNICA DETALLADA**

### **👁️ COMPONENTE 1: RealTimeMonitor**

#### **📋 PROPÓSITO ESPECÍFICO:**
- Monitorear trades activos usando `MT5Manager.get_positions()`
- Calcular métricas en tiempo real usando `AnalyticsManager`
- Detectar cambios y generar alertas
- Alimentar datos a otros componentes del SÓTANO 2

#### **🔌 INTERFACES DE INTEGRACIÓN:**
```python
# DEPENDENCIAS DEL SÓTANO 1 (YA IMPLEMENTADAS):
from src.core.mt5_manager import MT5Manager           # Conexión y datos MT5
from src.core.analytics_manager import AnalyticsManager # Métricas y análisis
from src.core.data_manager import DataManager         # Datos OHLC y cache
from src.core.logger_manager import LoggerManager     # Logging centralizado
from src.core.error_manager import ErrorManager       # Manejo de errores

class RealTimeMonitor:
    def __init__(self, mt5_manager, analytics_manager, data_manager, logger, error_manager):
        # Integración con componentes existentes
```

#### **📊 ESTRUCTURA DE DATOS ESPECÍFICA:**
```python
@dataclass
class RealTimeMetrics:
    # DATOS BÁSICOS (obtenidos de MT5Manager)
    active_positions: List[Dict]      # MT5Manager.get_positions()
    pending_orders: List[Dict]        # MT5Manager.get_pending_orders()
    account_info: Dict               # MT5Manager.get_account_info()
    current_prices: Dict[str, float] # MT5Manager.get_current_price()
    
    # MÉTRICAS CALCULADAS (usando AnalyticsManager)
    current_performance: PerformanceMetrics  # AnalyticsManager.get_performance_summary()
    grid_status: GridMetrics                # AnalyticsManager.get_grid_summary()
    market_conditions: MarketMetrics        # AnalyticsManager.get_market_summary()
    
    # ALERTAS Y ESTADO
    alerts: List[Alert]              # Alertas generadas
    system_health: Dict[str, bool]   # Estado del sistema
    last_update: datetime           # Última actualización
    update_frequency: int           # Frecuencia de actualización (segundos)
```

#### **🔧 MÉTODOS ESPECÍFICOS:**
```python
class RealTimeMonitor:
    # INICIALIZACIÓN Y CONFIGURACIÓN
    def __init__(self, dependencies)                    # Constructor con dependencias SÓTANO 1
    def start_monitoring(self, update_frequency=30)     # Iniciar monitoreo (cada 30s por defecto)
    def stop_monitoring(self)                          # Detener monitoreo
    def is_monitoring(self) -> bool                    # Estado del monitoreo
    
    # RECOLECCIÓN DE DATOS
    def collect_live_data(self) -> RealTimeMetrics     # Recopilar datos actuales
    def update_metrics(self)                           # Actualizar métricas internas
    def get_current_metrics(self) -> RealTimeMetrics   # Obtener métricas actuales
    
    # SISTEMA DE ALERTAS
    def check_alerts(self) -> List[Alert]              # Verificar condiciones de alerta
    def add_alert_condition(self, condition: AlertCondition) # Agregar nueva condición
    def get_active_alerts(self) -> List[Alert]         # Obtener alertas activas
    
    # INTEGRACIÓN CON OTROS COMPONENTES
    def get_data_for_optimizer(self) -> Dict           # Datos para LiveOptimizer
    def get_data_for_experiments(self) -> Dict         # Datos para ExperimentEngine
```

#### **🧪 CASOS DE PRUEBA ESPECÍFICOS:**
```python
def test_real_time_monitor():
    # Test 1: Inicialización con dependencias reales
    monitor = RealTimeMonitor(mt5_manager, analytics_manager, data_manager, logger, error_manager)
    assert monitor.is_monitoring() == False
    
    # Test 2: Recolección de datos usando APIs existentes
    metrics = monitor.collect_live_data()
    assert len(metrics.active_positions) >= 0  # Puede ser 0 si no hay trades
    assert metrics.account_info is not None
    
    # Test 3: Integración con AnalyticsManager
    performance = monitor.get_current_metrics().current_performance
    assert hasattr(performance, 'win_rate')
    assert hasattr(performance, 'profit_factor')
```

---

### **⚙️ COMPONENTE 2: LiveOptimizer**

#### **📋 PROPÓSITO ESPECÍFICO:**
- Recibir datos de `RealTimeMonitor`
- Usar `OptimizationEngine` existente para sugerir cambios
- Aplicar cambios seguros usando `MT5Manager`
- Validar resultados con `AnalyticsManager`

#### **🔌 INTERFACES DE INTEGRACIÓN:**
```python
# DEPENDENCIAS ADICIONALES PARA OPTIMIZACIÓN:
from src.core.optimization_engine import OptimizationEngine # Motor de optimización existente
from src.core.config_manager import ConfigManager          # Configuración del sistema

class LiveOptimizer:
    def __init__(self, real_time_monitor, optimization_engine, mt5_manager, config_manager):
        # Integración con RealTimeMonitor y componentes SÓTANO 1
```

#### **📊 ESTRUCTURA DE DATOS ESPECÍFICA:**
```python
@dataclass
class OptimizationAction:
    # IDENTIFICACIÓN
    action_id: str                   # ID único de la acción
    timestamp: datetime             # Cuándo se generó
    component: str                  # Qué se va a optimizar ('grid', 'risk', 'position')
    
    # ACCIÓN ESPECÍFICA
    current_value: Any              # Valor actual del parámetro
    suggested_value: Any            # Valor sugerido por OptimizationEngine
    confidence: float               # Confianza de la sugerencia (0.0-1.0)
    expected_improvement: float     # Mejora esperada (%)
    
    # VALIDACIÓN Y SEGURIDAD
    risk_level: str                 # 'LOW', 'MEDIUM', 'HIGH'
    rollback_plan: Dict             # Cómo deshacer el cambio
    validation_criteria: Dict       # Cómo validar si funcionó
    
    # ESTADO
    status: str                     # 'PENDING', 'APPLIED', 'VALIDATED', 'ROLLED_BACK'
    applied_at: Optional[datetime]  # Cuándo se aplicó
    result: Optional[Dict]          # Resultado de la aplicación
```

#### **🔧 MÉTODOS ESPECÍFICOS:**
```python
class LiveOptimizer:
    # ANÁLISIS Y SUGERENCIAS
    def analyze_performance(self, metrics: RealTimeMetrics) -> List[OptimizationAction]
    def suggest_grid_optimization(self, grid_metrics: GridMetrics) -> OptimizationAction
    def suggest_risk_adjustment(self, performance: PerformanceMetrics) -> OptimizationAction
    
    # APLICACIÓN SEGURA DE CAMBIOS
    def apply_optimization(self, action: OptimizationAction) -> bool
    def validate_optimization(self, action: OptimizationAction) -> bool
    def rollback_optimization(self, action: OptimizationAction) -> bool
    
    # GESTIÓN DE HISTORIAL
    def get_optimization_history(self) -> List[OptimizationAction]
    def get_success_rate(self) -> float
    def get_average_improvement(self) -> float
```

---

### **🧪 COMPONENTE 3: ExperimentEngine**

#### **📋 PROPÓSITO ESPECÍFICO:**
- Diseñar experimentos A/B usando datos de `RealTimeMonitor`
- Ejecutar experimentos usando `LiveOptimizer`
- Validar resultados estadísticamente
- Guardar resultados para aprendizaje futuro

#### **🔌 INTERFACES DE INTEGRACIÓN:**
```python
# DEPENDENCIAS PARA EXPERIMENTACIÓN:
from scipy import stats                    # Validación estadística
import json                               # Persistencia de experimentos

class ExperimentEngine:
    def __init__(self, real_time_monitor, live_optimizer, data_manager):
        # Integración con componentes SÓTANO 2 anteriores
```

#### **📊 ESTRUCTURA DE DATOS ESPECÍFICA:**
```python
@dataclass
class Experiment:
    # IDENTIFICACIÓN
    experiment_id: str              # ID único del experimento
    name: str                       # Nombre descriptivo
    description: str                # Descripción del experimento
    created_at: datetime           # Cuándo se creó
    
    # DISEÑO DEL EXPERIMENTO
    parameter_name: str            # Qué parámetro se está probando
    control_value: Any             # Valor actual (grupo control)
    test_value: Any                # Valor de prueba (grupo test)
    
    # CRITERIOS DE ÉXITO
    success_metric: str            # Métrica principal ('win_rate', 'profit_factor', etc.)
    minimum_sample_size: int       # Mínimo de trades para validez
    confidence_level: float        # Nivel de confianza requerido (0.95)
    minimum_improvement: float     # Mejora mínima para considerar éxito (%)
    
    # ESTADO Y RESULTADOS
    status: str                    # 'RUNNING', 'COMPLETED', 'STOPPED'
    control_results: List[float]   # Resultados del grupo control
    test_results: List[float]      # Resultados del grupo test
    statistical_significance: Optional[float]  # p-value del test
    conclusion: Optional[str]      # 'SUCCESS', 'FAILURE', 'INCONCLUSIVE'
```

---

### **🤖 COMPONENTE 4: AdaptiveController**

#### **📋 PROPÓSITO ESPECÍFICO:**
- Coordinar todos los componentes de SÓTANO 2
- Tomar decisiones basadas en múltiples fuentes
- Gestionar el flujo de datos entre componentes
- Proporcionar interface unificada para el sistema

#### **🔌 INTERFACES DE INTEGRACIÓN:**
```python
class AdaptiveController:
    def __init__(self, real_time_monitor, live_optimizer, experiment_engine):
        # Coordinador de todos los componentes SÓTANO 2
```

---

## 📋 **PLAN DE IMPLEMENTACIÓN ESPECÍFICO**

### **🚀 SEMANA 1: RealTimeMonitor**
```python
# DÍA 1-2: Estructura básica
- Crear clase RealTimeMonitor con constructor
- Implementar collect_live_data() usando MT5Manager
- Test básico de integración

# DÍA 3-4: Métricas y alertas
- Implementar update_metrics() usando AnalyticsManager
- Sistema básico de alertas
- Tests de funcionalidad

# DÍA 5-7: Optimización y polish
- Cache de métricas para performance
- Logging completo
- Tests de stress y validación
```

### **🔧 DEPENDENCIAS TÉCNICAS ESPECÍFICAS**
```python
# NUEVAS LIBRERÍAS REQUERIDAS (agregar a requirements.txt):
scipy>=1.10.0                    # Para validación estadística en ExperimentEngine
threading>=3.11                  # Para RealTimeMonitor asíncrono
queue>=3.11                      # Para comunicación entre componentes
flask>=2.3.0                     # Para dashboard web (opcional)
```

### **🗄️ ESQUEMAS DE BASE DE DATOS**
```sql
-- TABLAS PARA PERSISTENCIA DE SÓTANO 2
CREATE TABLE real_time_metrics (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    metrics_json TEXT,           -- JSON con todas las métricas
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE optimization_actions (
    id INTEGER PRIMARY KEY,
    action_id TEXT UNIQUE,
    action_json TEXT,            -- JSON con la acción completa
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE experiments (
    id INTEGER PRIMARY KEY,
    experiment_id TEXT UNIQUE,
    experiment_json TEXT,        -- JSON con el experimento completo
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🧪 **ESTRATEGIA DE TESTING**

### **📋 TESTS POR COMPONENTE**
```python
# tests/test_real_time_monitor.py
def test_initialization_with_dependencies()     # Dependencias SÓTANO 1
def test_collect_live_data_integration()        # Integración MT5Manager
def test_metrics_calculation()                  # Cálculos con AnalyticsManager
def test_alert_system()                         # Sistema de alertas
def test_monitoring_loop()                      # Loop de monitoreo

# tests/test_live_optimizer.py  
def test_optimization_suggestions()             # Sugerencias OptimizationEngine
def test_safe_application()                     # Aplicación segura de cambios
def test_rollback_functionality()               # Sistema de rollback
def test_validation_criteria()                  # Validación de resultados

# tests/test_experiment_engine.py
def test_experiment_design()                    # Diseño de experimentos
def test_statistical_validation()               # Validación estadística
def test_result_persistence()                   # Guardado de resultados

# tests/test_adaptive_controller.py
def test_component_coordination()               # Coordinación de componentes
def test_decision_making()                      # Toma de decisiones
def test_unified_interface()                    # Interface unificada
```

---

## 🎯 **CRITERIOS DE ÉXITO ESPECÍFICOS**

### **✅ MÉTRICAS DE ACEPTACIÓN**
```python
# PERFORMANCE
- RealTimeMonitor: Actualización cada 30s máximo
- LiveOptimizer: Decisión en <5 segundos
- ExperimentEngine: Validación estadística >95% confianza
- AdaptiveController: Coordinación sin bloqueos

# INTEGRACIÓN
- 100% compatible con SÓTANO 1 existente
- Tests de integración 15/15 pasando
- Sin degradación de performance del sistema base
- Rollback completo en caso de problemas

# FUNCIONALIDAD
- Monitoreo 24/7 sin interrupciones
- Optimizaciones automáticas con mejora >5%
- Experimentos A/B con resultados estadísticamente significativos
- Dashboard básico funcionando
```

---

## ✅ **SIGUIENTE PASO INMEDIATO**

### **🔧 IMPLEMENTACIÓN DÍA 1:**
1. **Crear estructura básica** de `RealTimeMonitor`
2. **Implementar constructor** con dependencias SÓTANO 1
3. **Test básico** de inicialización
4. **Documentar progreso** real vs planificado

---

**ESPECIFICACIONES TÉCNICAS COMPLETADAS** ✅  
**Fecha:** 2025-08-11  
**Basado en:** Código real del SÓTANO 1  
**Próximo:** Implementación de RealTimeMonitor básico
