# 🤖 **REGLAS PARA COPILOT - TRADING GRID v2.0**

**Sistema:** Trading Grid v2.0  
**Fecha:** Agosto 10, 2025  
**Propósito:** Reglas específicas para el desarrollo del sistema Trading Grid

---

## 🎯 **REGLAS DE ORO PARA COPILOT**

### 📋 **REGLA #1: REVISAR ANTES DE CREAR**
```
🔍 ANTES DE CREAR NUEVAS FUNCIONES:
1. ✅ Revisar documentacion/bitacora/ para entender contexto
2. ✅ Buscar archivos relacionados en src/
3. ✅ Verificar si ya existe lógica similar  
4. ❌ NO duplicar funcionalidad existente
```

### 📚 **REGLA #2: DOCUMENTACIÓN OBLIGATORIA PRE-TRABAJO**

#### **🚨 ARCHIVOS CRÍTICOS - LEER SIEMPRE:**
```
📊 DOCUMENTACIÓN OBLIGATORIA:
✅ documentacion/README.md                               # Orientación general
✅ documentacion/arquitectura/estado_actual_sistema.md   # Estado actual
✅ documentacion/bitacora/desarrollo_diario.md          # Última sesión  
✅ MIGRACION_COMPLETADA.md                              # Estado migración
✅ PROTOCOLO_TRADING_GRID.md                            # Este protocolo
```

#### **📝 DOCUMENTACIÓN POR ÁREA:**
```
🎯 SEGÚN EL ÁREA DE TRABAJO:
├── 🧠 CORE → Revisar src/core/ y documentacion/
├── 📊 ANALYSIS → Revisar src/analysis/ y data/
├── 🛠️ UTILS → Revisar src/utils/ y logs/
├── ⚙️ CONFIG → Revisar config/ y requirements.txt
└── 🧪 TESTING → Revisar tests/ y scripts/
```

### 🔧 **REGLA #3: ESTRUCTURA DE PROYECTO OBLIGATORIA**

#### **📁 DIRECTORIOS PRINCIPALES:**
```
grid/                           # Proyecto Trading Grid
├── src/                        # Código fuente
│   ├── core/                  # Lógica principal del sistema
│   │   ├── main.py           # Sistema principal - PUNTO DE ENTRADA
│   │   ├── riskbot_mt5.py    # Gestión de riesgo y exposición
│   │   └── order_manager.py  # Gestión de órdenes MT5
│   ├── analysis/             # Análisis técnico y estrategias
│   │   ├── grid_bollinger.py # Estrategia Grid con Bollinger Bands
│   │   └── analisis_estocastico_m15.py # Análisis estocástico M15
│   └── utils/                # Utilidades y herramientas
│       ├── data_logger.py    # Sistema de logging
│       ├── trading_schedule.py # Gestión de horarios de trading
│       └── descarga_velas.py # Descarga de datos MT5
├── config/                   # Configuración del sistema
│   └── config.py            # Configuración global
├── tests/                    # Suite de testing
│   └── test_sistema.py      # Tests automatizados
├── documentacion/            # Documentación del proyecto
│   ├── arquitectura/        # Arquitectura del sistema
│   ├── bitacora/           # Bitácoras de desarrollo
│   ├── desarrollo/         # Logs de desarrollo  
│   └── templates/          # Templates de trabajo
├── scripts/                 # Scripts de mantenimiento
│   ├── reorganizar_sistema.py # Reorganización automática
│   └── reparar_imports.py  # Reparación de imports
├── data/                   # Datos de trading (por fechas)
├── logs/                   # Logs del sistema
└── backup/                 # Backups automáticos
```

### 🔍 **REGLA #4: BÚSQUEDA OBLIGATORIA**

#### **🎯 ANTES DE CREAR, BUSCAR EN:**
```bash
# ✅ BÚSQUEDA EN CÓDIGO:
grep -r "función_similar" src/                          # Buscar función
find . -name "*.py" -exec grep -l "concepto" {} \;     # Buscar concepto
grep -r "import.*módulo" src/                          # Buscar imports

# ✅ BÚSQUEDA EN DOCUMENTACIÓN:  
grep -r "tema" documentacion/                          # Buscar tema
type documentacion\bitacora\desarrollo_diario.md      # Ver última sesión
```

### 🧪 **REGLA #5: TESTING CRÍTICO**

#### **🔧 VALIDACIONES OBLIGATORIAS:**
```bash
# ✅ TESTS QUE SIEMPRE DEBEN PASAR:
python tests/test_sistema.py              # Suite completa (debe ser 9/9)
python src/core/main.py                   # Sistema debe arrancar sin errores
python scripts/reparar_imports.py         # Reparar imports si es necesario
```

#### **🎯 CRITERIOS DE TESTING:**
```
✅ TESTS DEBEN:
- Ejecutarse en <2 segundos
- Tener resultado claro (PASS/FAIL)
- No requerir intervención manual
- Validar todos los imports críticos
- Verificar conectividad MT5 
- Probar funciones principales
```

### 📝 **REGLA #6: DOCUMENTACIÓN DE CAMBIOS**

#### **📋 ACTUALIZAR SIEMPRE:**
```markdown
🗂️ BITÁCORAS OBLIGATORIAS:
✅ documentacion/bitacora/desarrollo_diario.md          # Lo que se hizo
✅ documentacion/bitacora/componentes_completados.md    # Si se completó algo
✅ documentacion/desarrollo/plan_trabajo.md             # Próximos pasos
✅ documentacion/arquitectura/estado_actual_sistema.md  # Si cambió estado
```

#### **📄 TEMPLATE DE ACTUALIZACIÓN:**
```markdown
## [FECHA] - [TIPO DE CAMBIO]

### ✅ Completado:
- [Descripción específica del cambio]
- [Archivos modificados]
- [Tests realizados]

### 🔧 Modificaciones:
- **Archivos:** `src/[área]/[archivo].py`
- **Función:** `nueva_función()` o `función_modificada()`
- **Propósito:** [Para qué sirve]

### 🧪 Validación:
- [ ] Tests pasan: `python tests/test_sistema.py`
- [ ] Sistema arranca: `python src/core/main.py`
- [ ] Imports funcionan: Sin errores de módulos

### 🎯 Próximo:
- [Qué sigue en la próxima sesión]
```

### 🔧 **REGLA #7: IMPORTS Y RUTAS CORRECTAS**

#### **📁 TEMPLATE DE IMPORTS:**
```python
# ✅ PARA ARCHIVOS EN src/core/:
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis").absolute()))
sys.path.insert(0, str((project_root / "src" / "utils").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))

# ✅ PARA ARCHIVOS EN src/analysis/:  
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "src" / "utils").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))

# ✅ PARA ARCHIVOS EN tests/:
import sys
from pathlib import Path

current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis").absolute()))
sys.path.insert(0, str((project_root / "src" / "utils").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))
```

### 🚨 **REGLA #8: VERIFICACIÓN FINAL OBLIGATORIA**

#### **✅ CHECKLIST ANTES DE FINALIZAR:**
```
📋 VERIFICACIONES FINALES:
- [ ] python tests/test_sistema.py → 9/9 PASS
- [ ] python src/core/main.py → Arranca sin errores  
- [ ] Bitácora actualizada en documentacion/bitacora/
- [ ] Plan actualizado para próxima sesión
- [ ] No hay archivos duplicados en src/
- [ ] Estructura de carpetas intacta
- [ ] Imports funcionan correctamente
```

---

## 🔄 **COMANDOS RÁPIDOS TRADING GRID**

### **🔍 Verificación Rápida:**
```bash
python tests/test_sistema.py                    # Testing completo
python src/core/main.py                         # Sistema principal
tree /f /a                                      # Ver estructura
type documentacion\bitacora\desarrollo_diario.md # Última sesión
```

### **🔧 Reparación:**
```bash
python scripts/reparar_imports.py               # Reparar imports
python scripts/reorganizar_sistema.py           # Reorganizar (si es necesario)
```

### **📊 Búsqueda:**
```bash
grep -r "concepto" src/                         # Buscar en código
grep -r "tema" documentacion/                   # Buscar en docs
find . -name "*.py" -exec grep -l "patrón" {} \ # Buscar archivos
```

---

## 🎯 **APLICACIÓN DE ESTAS REGLAS**

### **✅ SÍ, PODEMOS APLICAR ESTAS REGLAS:**

1. **✅ Están Adaptadas:** Específicas para Trading Grid v2.0
2. **✅ Son Realistas:** Basadas en la estructura actual
3. **✅ Son Verificables:** Con comandos concretos
4. **✅ Son Completas:** Cubren todo el flujo de desarrollo

### **🔧 Diferencias con ICT Engine:**
- ❌ **Removido:** Referencias a BOS/CHOCH, Smart Money, Fair Value Gaps
- ❌ **Removido:** Rutas específicas de ICT Engine
- ❌ **Removido:** Conceptos no aplicables
- ✅ **Adaptado:** Estructura específica de Trading Grid
- ✅ **Adaptado:** Comandos para Windows/PowerShell
- ✅ **Adaptado:** Tests y validaciones reales

---

**¡Reglas específicas para Trading Grid v2.0 listas para aplicar! 🚀**
