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

### 📁 **REGLA #7: ORGANIZACIÓN DE BITÁCORAS Y ESTRUCTURA DE CARPETAS**

#### **🎯 PRINCIPIOS DE ORGANIZACIÓN:**
```
📋 ESTRUCTURA MODULAR POR SÓTANOS:
✅ CADA SÓTANO = CARPETA INDEPENDIENTE
✅ DOCUMENTACIÓN SEPARADA POR FASE
✅ ESTRUCTURA ESCALABLE PARA FUTURO
✅ NO MEZCLAR PROYECTOS COMPLETADOS
```

#### **📁 ESTRUCTURA ESTÁNDAR DE DOCUMENTACIÓN:**
```
documentacion/
├── 📖 README.md                    # Documentación principal - SIEMPRE EN RAÍZ
├── 🏗️ arquitectura/               # Documentos técnicos permanentes
├── 📝 bitacora/                   # Bitácoras de desarrollo por proyecto
│   ├── sotano_1/                  # SÓTANO 1 - Analytics & Optimization
│   ├── sotano_2/                  # SÓTANO 2 - Real-Time Optimization  
│   ├── sotano_3/                  # SÓTANO 3 - ML & AI (futuro)
│   ├── sotano_N/                  # Proyectos futuros
│   ├── desarrollo_diario.md       # Bitácora general del día
│   └── componentes_completados.md # Log de componentes finalizados
├── ✅ completos/                  # Fases y documentos completados (archivo)
├── 🔧 desarrollo/                 # Planes e implementaciones activas
└── 📋 templates/                  # Templates para nuevos documentos
```

#### **🏗️ PROTOCOLO PARA NUEVOS SÓTANOS:**
```
🚀 CREACIÓN DE NUEVO SÓTANO:
1. ✅ Crear carpeta: documentacion/bitacora/sotano_N/
2. ✅ Crear archivos base:
   - 01_RESUMEN_EJECUTIVO.md        # Explicación simple para cualquier persona
   - 02_ARQUITECTURA_TECNICA.md     # Diseño técnico detallado
   - 03_PLAN_FASES_DETALLADO.md     # Cronograma y fases específicas
3. ✅ Actualizar README.md principal con referencia al nuevo sótano
4. ✅ NO mover/modificar sótanos anteriores (son archivo histórico)
```

#### **📋 PROTOCOLO PARA ARCHIVOS COMPLETADOS:**
```
✅ CUANDO SE COMPLETA UNA FASE:
1. ✅ Mover documentos completados → documentacion/completos/
2. ✅ Eliminar originales para evitar duplicación
3. ✅ Mantener solo documentos activos en desarrollo
4. ✅ Actualizar bitacora/desarrollo_diario.md con logros
```

#### **🔄 PROTOCOLO PARA EXPANSIÓN FUTURA:**
```
🎯 ESCALABILIDAD GARANTIZADA:
├── SÓTANO 3: Machine Learning & AI
│   └── documentacion/bitacora/sotano_3/
├── SÓTANO 4: Portfolio Management
│   └── documentacion/bitacora/sotano_4/
├── SÓTANO 5: Risk Management Avanzado
│   └── documentacion/bitacora/sotano_5/
└── SÓTANO N: Proyectos futuros
    └── documentacion/bitacora/sotano_N/

🚨 REGLA CRÍTICA: NUNCA MODIFICAR SÓTANOS ANTERIORES
✅ Cada sótano es independiente y versionado
✅ No contaminar documentación de proyectos completados
✅ Mantener trazabilidad histórica completa
```

#### **🎯 NOMENCLATURA ESTÁNDAR:**
```
📝 ARCHIVOS POR SÓTANO:
├── 01_RESUMEN_EJECUTIVO.md         # Explicación para no técnicos
├── 02_ARQUITECTURA_TECNICA.md      # Diseño y especificaciones
├── 03_PLAN_FASES_DETALLADO.md      # Cronograma con subfases
├── 04_CONFIGURACION_INICIAL.md     # Setup e instalación (opcional)
├── 05_GUIA_OPERACION.md           # Manual de uso (opcional)
└── NN_DOCUMENTO_ESPECIFICO.md     # Documentos específicos del sótano
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
---

## 🏗️ **PROTOCOLO ESPECÍFICO: ORGANIZACIÓN Y ESTRUCTURA DE CARPETAS**

### **📋 PROTOCOLO #1: CREACIÓN DE NUEVOS SÓTANOS**

#### **🎯 PROCESO OBLIGATORIO PARA NUEVOS PROYECTOS:**
```bash
# 1. CREAR ESTRUCTURA BASE
mkdir "documentacion\bitacora\sotano_N"

# 2. CREAR ARCHIVOS ESTÁNDAR (obligatorios)
echo. > "documentacion\bitacora\sotano_N\01_RESUMEN_EJECUTIVO.md"
echo. > "documentacion\bitacora\sotano_N\02_ARQUITECTURA_TECNICA.md" 
echo. > "documentacion\bitacora\sotano_N\03_PLAN_FASES_DETALLADO.md"

# 3. ACTUALIZAR REFERENCIAS
# - Agregar link en documentacion/README.md
# - Mencionar en REGLAS_COPILOT_TRADING_GRID.md
# - Actualizar estructura en este protocolo
```

#### **🔧 TEMPLATE PARA NUEVOS SÓTANOS:**
```markdown
# SÓTANO N - [NOMBRE DEL PROYECTO]

## ESTRUCTURA OBLIGATORIA:
documentacion/bitacora/sotano_N/
├── 01_RESUMEN_EJECUTIVO.md         # Para cualquier persona (no técnico)
├── 02_ARQUITECTURA_TECNICA.md      # Diseño técnico detallado  
├── 03_PLAN_FASES_DETALLADO.md      # Cronograma con subfases
├── 04_CONFIGURACION_INICIAL.md     # Setup e instalación (si aplica)
├── 05_GUIA_OPERACION.md           # Manual de uso (si aplica)
└── [documentos específicos]        # Según necesidades del proyecto
```

### **📋 PROTOCOLO #2: GESTIÓN DE DOCUMENTOS COMPLETADOS**

#### **🎯 PROCESO DE ARCHIVO:**
```bash
# 1. IDENTIFICAR DOCUMENTOS COMPLETADOS
# - Buscar archivos con sufijo "_COMPLETED.md"
# - Buscar archivos de fases finalizadas

# 2. MOVER A CARPETA DE ARCHIVO
Move-Item -Path "documentacion\FASE_*_COMPLETED.md" -Destination "documentacion\completos\"

# 3. ELIMINAR ORIGINALES (evitar duplicación)
Remove-Item -Path "documentacion\FASE_*_COMPLETED.md" -Force

# 4. ACTUALIZAR ÍNDICES
# - Actualizar documentacion/README.md
# - Actualizar bitacora/componentes_completados.md
```

### **📋 PROTOCOLO #3: EXPANSIÓN FUTURA PLANIFICADA**

#### **🚀 ROADMAP DE SÓTANOS PROYECTADOS:**
```
ESTRUCTURA FUTURA GARANTIZADA:

documentacion/bitacora/
├── sotano_1/                       # ✅ COMPLETADO - Analytics & Optimization
├── sotano_2/                       # 🚧 ACTUAL - Real-Time Optimization
├── sotano_3/                       # 📋 PLANIFICADO - Machine Learning & AI
│   ├── 01_RESUMEN_EJECUTIVO.md     # Predictive models, sentiment analysis
│   ├── 02_ARQUITECTURA_TECNICA.md  # ML pipeline, data processing
│   └── 03_PLAN_FASES_DETALLADO.md  # Training, validation, deployment
├── sotano_4/                       # 📋 PLANIFICADO - Portfolio Management
│   ├── 01_RESUMEN_EJECUTIVO.md     # Multi-asset, diversification
│   ├── 02_ARQUITECTURA_TECNICA.md  # Portfolio engine, correlation
│   └── 03_PLAN_FASES_DETALLADO.md  # Asset allocation, rebalancing
├── sotano_5/                       # 📋 PLANIFICADO - Risk Management Avanzado
│   ├── 01_RESUMEN_EJECUTIVO.md     # Advanced risk models, stress testing
│   ├── 02_ARQUITECTURA_TECNICA.md  # VaR, Monte Carlo, scenario analysis
│   └── 03_PLAN_FASES_DETALLADO.md  # Implementation, validation
└── sotano_N/                       # 🔮 FUTURO - Proyectos no definidos
    └── [estructura estándar]
```

#### **🔒 REGLAS INVIOLABLES DE EXPANSIÓN:**
```
🚨 NUNCA:
❌ Modificar sótanos completados
❌ Mover archivos entre sótanos  
❌ Cambiar estructura de sótanos anteriores
❌ Mezclar documentación de diferentes proyectos

✅ SIEMPRE:
✅ Crear nueva carpeta sotano_N para nuevo proyecto
✅ Usar nomenclatura estándar 01_, 02_, 03_
✅ Mantener independencia entre sótanos
✅ Archivar documentos completados en completos/
```

### **📋 PROTOCOLO #4: MANTENIMIENTO DE ESTRUCTURA**

#### **🔄 REVISIÓN PERIÓDICA OBLIGATORIA:**
```bash
# COMANDO DE VERIFICACIÓN ESTRUCTURA:
tree /f /a documentacion

# RESULTADO ESPERADO:
documentacion/
├── README.md                       # ✅ Documentación principal
├── arquitectura/                   # ✅ Docs técnicos permanentes
├── bitacora/                      # ✅ Bitácoras por proyecto
│   ├── sotano_1/                  # ✅ Proyecto completado
│   ├── sotano_2/                  # ✅ Proyecto actual
│   ├── desarrollo_diario.md       # ✅ Bitácora general
│   └── componentes_completados.md # ✅ Log de completados
├── completos/                     # ✅ Archivo de documentos
├── desarrollo/                    # ✅ Planes activos
└── templates/                     # ✅ Templates estándar
```

#### **🧹 COMANDO DE LIMPIEZA AUTOMÁTICA:**
```bash
# SCRIPT DE ORGANIZACIÓN (ejecutar mensualmente):
# 1. Verificar duplicados
# 2. Mover completados a completos/
# 3. Limpiar archivos temporales
# 4. Validar estructura estándar
```

---

## 🎯 **APLICACIÓN INMEDIATA DE ESTOS PROTOCOLOS**

### **✅ ESTRUCTURA ACTUAL VALIDADA:**
- 🏗️ **SÓTANO 1**: Completado y archivado ✅
- 🚧 **SÓTANO 2**: En desarrollo con estructura estándar ✅  
- 📁 **Organización**: Carpetas separadas y limpias ✅
- 📋 **Documentación**: Templates y protocolos definidos ✅

### **🚀 PREPARADO PARA FUTURO:**
- 🔮 **Escalabilidad**: Hasta SÓTANO N sin límites
- 🛡️ **Integridad**: Estructura protegida contra modificaciones
- 📚 **Consistencia**: Templates y nomenclatura estándar
- 🎯 **Mantenimiento**: Protocolos de limpieza y organización

---

**¡Protocolos de organización implementados y listos para uso inmediato! 🎉**

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
