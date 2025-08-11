# 🎯 PROTOCOLO TRADING GRID - ADAPTADO 

**Sistema:** Trading Grid v2.0  
**Fecha de Adaptación:** Agosto 10, 2025  
**Versión:** v1.0 - Específico para Trading Grid  

---

## 🚨 **REGLAS FUNDAMENTALES**

### **REGLA #1: REVISAR ANTES DE CREAR**
```bash
🔍 ANTES DE CREAR NUEVAS FUNCIONES:
1. ✅ Revisar documentacion/bitacora/ para entender el contexto
2. ✅ Buscar en src/ si ya existe funcionalidad similar  
3. ✅ Ejecutar tests: python tests/test_sistema.py
4. ❌ NO duplicar código existente
```

### **REGLA #2: DOCUMENTACIÓN OBLIGATORIA**  
```markdown
📚 ARCHIVOS A REVISAR SIEMPRE:
✅ documentacion/arquitectura/estado_actual_sistema.md    # Estado actual
✅ documentacion/bitacora/desarrollo_diario.md           # Última sesión
✅ MIGRACION_COMPLETADA.md                               # Estado de migración
✅ README.md                                            # Información general
```

### **REGLA #3: ESTRUCTURA DEL PROYECTO**
```
grid/
├── src/                          # Código fuente
│   ├── core/                     # Lógica principal
│   │   ├── main.py              # Sistema principal
│   │   ├── riskbot_mt5.py       # Gestión de riesgo  
│   │   └── order_manager.py     # Gestión de órdenes
│   ├── analysis/                # Análisis técnico
│   │   ├── grid_bollinger.py    # Estrategia Grid Bollinger
│   │   └── analisis_estocastico_m15.py # Análisis estocástico
│   └── utils/                   # Utilidades
│       ├── data_logger.py       # Sistema de logging
│       ├── trading_schedule.py  # Gestión de horarios
│       └── descarga_velas.py    # Descarga de datos
├── config/                      # Configuración
│   └── config.py               # Configuración global
├── tests/                       # Pruebas
│   └── test_sistema.py         # Suite de testing
├── documentacion/               # Documentación
├── scripts/                     # Scripts de mantenimiento
└── data/                       # Datos de trading
```

---

## 📋 **FLUJO DE TRABAJO DE 5 FASES**

### **FASE 1: PREPARACIÓN** ⏱️ *5-10 min*

#### **1.1 VERIFICACIÓN DE ESTADO**
```bash
# ✅ COMANDOS DE VERIFICACIÓN:
1. Estructura: tree /f /a
2. Tests: python tests/test_sistema.py  
3. Sistema: python src/core/main.py (verificar que arranca)
4. Última sesión: type documentacion\bitacora\desarrollo_diario.md
```

#### **1.2 LECTURA DE CONTEXTO**
```markdown
📚 ORDEN DE LECTURA OBLIGATORIO:
├── 1️⃣ documentacion/README.md - Orientación general
├── 2️⃣ documentacion/arquitectura/estado_actual_sistema.md - Estado actual  
├── 3️⃣ documentacion/bitacora/desarrollo_diario.md - Última sesión
├── 4️⃣ MIGRACION_COMPLETADA.md - Estado de migración
└── 5️⃣ documentacion/desarrollo/plan_trabajo.md - Plan actual
```

### **FASE 2: ANÁLISIS** ⏱️ *10-15 min*

#### **2.1 BÚSQUEDA DE FUNCIONALIDAD EXISTENTE**
```bash
# 🔍 BÚSQUEDA OBLIGATORIA:
grep -r "función_similar" src/
grep -r "concepto_buscado" documentacion/
find . -name "*.py" -exec grep -l "patrón" {} \;
```

#### **2.2 IDENTIFICACIÓN DE ÁREA DE TRABAJO**
```markdown
🎯 ÁREAS DEL SISTEMA:
├── 🧠 CORE → src/core/ (main.py, riskbot_mt5.py, order_manager.py)
├── 📊 ANALYSIS → src/analysis/ (grid_bollinger.py, analisis_estocastico_m15.py)  
├── 🛠️ UTILS → src/utils/ (data_logger.py, trading_schedule.py, descarga_velas.py)
├── ⚙️ CONFIG → config/ (config.py)
└── 🧪 TESTING → tests/ (test_sistema.py)
```

### **FASE 3: IMPLEMENTACIÓN** ⏱️ *15-30 min*

#### **3.1 DESARROLLO CON TEMPLATES**
```markdown
📋 USAR TEMPLATES:
✅ documentacion/templates/template_componente.md - Para nuevos componentes
✅ documentacion/templates/template_testing.md - Para nuevos tests  
✅ documentacion/templates/template_bitacora.md - Para documentación
```

#### **3.2 IMPORTS CORRECTOS**
```python
# ✅ ESTRUCTURA DE IMPORTS PARA NUEVOS ARCHIVOS:
import sys
from pathlib import Path

# Configurar rutas (ajustar según ubicación del archivo)
current_dir = Path(__file__).parent
project_root = current_dir / "../.." # Ajustar según nivel
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis").absolute()))  
sys.path.insert(0, str((project_root / "src" / "utils").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))
```

### **FASE 4: TESTING** ⏱️ *5-10 min*

#### **4.1 VALIDACIÓN AUTOMÁTICA**
```bash
# ✅ TESTING OBLIGATORIO:
python tests/test_sistema.py              # Suite completa
python scripts/reparar_imports.py         # Reparar imports si es necesario  
python src/core/main.py                   # Verificar sistema principal
```

#### **4.2 TESTING DE INTEGRACIÓN**
```markdown
🧪 VERIFICACIONES MÍNIMAS:
✅ Todos los imports funcionan
✅ No hay errores de sintaxis
✅ El sistema principal arranca
✅ Los tests pasan (mínimo 8/9)
```

### **FASE 5: DOCUMENTACIÓN** ⏱️ *5-10 min*

#### **5.1 ACTUALIZACIÓN DE BITÁCORAS**
```markdown
📝 ACTUALIZAR SIEMPRE:
✅ documentacion/bitacora/desarrollo_diario.md - Lo que se hizo hoy
✅ documentacion/bitacora/componentes_completados.md - Si se completó algo
✅ documentacion/desarrollo/plan_trabajo.md - Próximos pasos
✅ documentacion/arquitectura/estado_actual_sistema.md - Si cambió el estado
```

---

## 🔧 **COMANDOS RÁPIDOS TRADING GRID**

### **Verificación del Sistema:**
```bash
python tests/test_sistema.py                    # Testing completo
tree /f /a                                      # Ver estructura  
python src/core/main.py                         # Ejecutar sistema
python scripts/reparar_imports.py               # Reparar imports
```

### **Búsqueda de Código:**
```bash
grep -r "función" src/                          # Buscar función en código
grep -r "concepto" documentacion/               # Buscar en documentación
find . -name "*.py" -exec grep -l "patrón" {} \ # Buscar archivos con patrón
```

### **Verificación de Estado:**
```bash
type documentacion\bitacora\desarrollo_diario.md    # Última sesión
type documentacion\arquitectura\estado_actual_sistema.md # Estado actual
type MIGRACION_COMPLETADA.md                        # Estado migración
```

---

## ✅ **CHECKLIST FINAL**

Antes de finalizar cualquier sesión:

- [ ] Tests pasan: `python tests/test_sistema.py`
- [ ] Sistema arranca: `python src/core/main.py`  
- [ ] Bitácora actualizada: `documentacion/bitacora/desarrollo_diario.md`
- [ ] Plan actualizado: `documentacion/desarrollo/plan_trabajo.md`
- [ ] Imports funcionan: Sin errores de módulos
- [ ] Estructura intacta: Archivos en carpetas correctas

---

**¡Protocolo específico para Trading Grid v2.0 listo para uso! 🎯**
