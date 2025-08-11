# FASE 6 - MT5Manager: Plan de Implementación

## 📋 Objetivo de FASE 6
Centralizar toda la lógica de conectividad MT5, gestión de órdenes y posiciones en un único manager robusto y reutilizable.

## 🎯 Componentes a Centralizar

### 1. Conectividad MT5
- **Fuentes actuales**: `main.py`, `riskbot_mt5.py`, `order_manager.py`
- **Funcionalidades**:
  - Inicialización y conexión a MT5
  - Verificación de estado de conexión
  - Gestión de reconexión automática
  - Obtención de información de cuenta

### 2. Gestión de Órdenes
- **Fuentes actuales**: `order_manager.py`, `grid_bollinger.py`, `main.py`
- **Funcionalidades**:
  - Envío de órdenes (market, pending)
  - Modificación de órdenes
  - Cancelación de órdenes
  - Validación pre-envío

### 3. Gestión de Posiciones
- **Fuentes actuales**: `main.py`, `grid_bollinger.py`, `riskbot_mt5.py`
- **Funcionalidades**:
  - Obtención de posiciones abiertas
  - Cierre de posiciones
  - Modificación de SL/TP
  - Cálculo de exposición

### 4. Información de Mercado
- **Fuentes actuales**: `main.py`, `grid_bollinger.py`
- **Funcionalidades**:
  - Obtención de precios actuales
  - Información de símbolos
  - Spreads y puntos
  - Estado del mercado

## 🏗️ Estructura de MT5Manager

```python
class MT5Manager:
    def __init__(self, config_manager, logger_manager, error_manager):
        self.config = config_manager
        self.logger = logger_manager
        self.error = error_manager
        self._is_connected = False
        self._account_info = None
        
    # === CONECTIVIDAD ===
    def connect(self) -> bool
    def disconnect(self) -> bool
    def is_connected(self) -> bool
    def reconnect(self) -> bool
    def get_account_info(self) -> dict
    
    # === GESTIÓN DE ÓRDENES ===
    def send_order(self, symbol, order_type, volume, price=None, sl=None, tp=None) -> dict
    def modify_order(self, ticket, price=None, sl=None, tp=None) -> bool
    def cancel_order(self, ticket) -> bool
    def get_pending_orders(self, symbol=None) -> list
    
    # === GESTIÓN DE POSICIONES ===
    def get_positions(self, symbol=None) -> list
    def close_position(self, ticket) -> bool
    def modify_position(self, ticket, sl=None, tp=None) -> bool
    def get_total_exposure(self, symbol=None) -> dict
    
    # === INFORMACIÓN DE MERCADO ===
    def get_current_price(self, symbol) -> dict
    def get_symbol_info(self, symbol) -> dict
    def get_market_status(self, symbol) -> bool
```

## 🧪 Tests a Implementar

### 1. Test de Conectividad
```python
def test_mt5_connection():
    # Verificar conexión/desconexión
    # Verificar manejo de errores de conexión
    # Verificar reconexión automática
```

### 2. Test de Órdenes (Mock)
```python
def test_order_management():
    # Verificar validación de parámetros
    # Verificar formato de órdenes
    # Verificar manejo de errores
```

### 3. Test de Posiciones (Mock)
```python
def test_position_management():
    # Verificar obtención de posiciones
    # Verificar cálculo de exposición
    # Verificar formato de respuestas
```

## 📝 Integración Prevista

### 1. main.py
```python
# Reemplazar toda la lógica MT5 dispersa por:
mt5_manager = MT5Manager(config_manager, logger_manager, error_manager)
```

### 2. grid_bollinger.py
```python
# Usar MT5Manager para órdenes y posiciones
# Eliminar lógica MT5 duplicada
```

### 3. order_manager.py
```python
# Refactorizar para usar MT5Manager
# Mantener solo lógica de alto nivel
```

## 🔄 Estrategia de Implementación

### Paso 1: Crear MT5Manager Base
- Implementar conectividad básica
- Añadir métodos de información de cuenta
- Validar con tests de conectividad

### Paso 2: Añadir Gestión de Órdenes
- Implementar envío, modificación, cancelación
- Añadir validaciones robustas
- Tests con datos mock

### Paso 3: Añadir Gestión de Posiciones
- Implementar obtención y modificación
- Cálculos de exposición
- Tests con datos mock

### Paso 4: Información de Mercado
- Precios, símbolos, estado
- Cache inteligente
- Tests de respuesta

### Paso 5: Integración Gradual
- Refactorizar main.py
- Actualizar grid_bollinger.py
- Refactorizar order_manager.py

### Paso 6: Validación Final
- Tests completos del sistema
- Verificar funcionalidad end-to-end
- Documentar completion

## 🎯 Criterios de Éxito

### Funcionalidad
- [ ] Conexión MT5 robusta con reconexión
- [ ] Gestión completa de órdenes
- [ ] Gestión completa de posiciones  
- [ ] Información de mercado centralizada

### Calidad
- [ ] Tests unitarios completos
- [ ] Manejo de errores robusto
- [ ] Logging unificado
- [ ] Documentación completa

### Integración
- [ ] main.py refactorizado
- [ ] Módulos existentes actualizados
- [ ] Funcionalidad end-to-end preservada
- [ ] Performance mantenida

## 📈 Beneficios Esperados

### Técnicos
- Eliminación completa de duplicación MT5
- Manejo centralizado de errores MT5
- Testing más robusto
- Mantenimiento simplificado

### Operacionales
- Reconexión automática
- Logging unificado de operaciones
- Validaciones consistentes
- Monitoreo centralizado

---
**Próximo paso**: Implementar MT5Manager base y validar conectividad
**Estimación**: 45-60 minutos para implementación completa
**Prioridad**: Alta - Fase final crítica
