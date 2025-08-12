# 🤖 **REGLAS PARA COPILOT - TRADING GRID COMPLETADO**

**Sistema:** Trading Grid v4.0 - COMPLETAMENTE OPERATIVO  
**Fecha:** Agosto 12, 2025  
**Propósito:** Reglas para mantenimiento y mejoras opcionales del sistema completado  
**Estado:** ✅ PROYECTO TERMINADO - SISTEMA 100% FUNCIONAL

---

## 🎯 **REGLAS DE ORO PARA SISTEMA COMPLETADO**

### 📋 **REGLA #1: SISTEMA OPERATIVO - NO MODIFICAR CORE**
```
🏆 SISTEMA 100% FUNCIONAL:
✅ 192/192 tests pasando constantemente
✅ Broker real conectado y validado (FundedNext MT5)
✅ Órdenes reales ejecutándose correctamente
✅ Performance <0.5 segundos tiempo real
❌ NO modificar componentes core sin justificación crítica
```

### 📚 **REGLA #2: DOCUMENTACIÓN FINAL CONSOLIDADA**

#### **🚨 ARCHIVOS CRÍTICOS ACTUALES:**
```
📊 DOCUMENTACIÓN ACTUAL:
✅ documentacion/bitacora/sotano_1/RESUMEN_EJECUTIVO.md      # SÓTANO 1 completado
✅ documentacion/bitacora/sotano_2/DIA_3_COMPLETADO_FINAL.md # SÓTANO 2 completado
✅ documentacion/bitacora/sotano_3/01_RESUMEN_EJECUTIVO.md   # SÓTANO 3 completado
✅ documentacion/bitacora/TEMAS_PENDIENTES.md                # Mejoras opcionales
✅ PROTOCOLO_TRADING_GRID.md                                 # Este protocolo
✅ REGLAS_COPILOT_TRADING_GRID.md                           # Estas reglas
```

### � **REGLA #3: ARQUITECTURA FINAL - NO MODIFICAR SIN NECESIDAD**

#### **📁 ESTRUCTURA COMPLETADA Y OPERATIVA:**
```
🏢 TRADING GRID - ARQUITECTURA COMPLETADA:

src/core/                       # NÚCLEO COMPLETADO ✅
├── config_manager.py          # Configuración centralizada ✅
├── logger_manager.py          # Logging unificado ✅  
├── error_manager.py           # Manejo de errores robusto ✅
├── data_manager.py            # Gestión de datos avanzada ✅
├── analytics_manager.py       # Analytics completos ✅
├── indicator_manager.py       # Indicadores técnicos ✅
├── fundednext_mt5_manager.py  # Conexión broker real ✅
├── optimization_engine.py     # Motor de optimización ✅
├── strategy_engine.py         # Generación de señales ✅
├── real_time_monitor.py       # Monitoreo tiempo real ✅
├── order_executor.py          # Ejecución de órdenes ✅
└── foundation_bridge.py       # Enlace estratégico ✅

tests/                          # SUITE COMPLETA ✅
├── 192 tests pasando          # 100% success rate ✅
├── Validación real            # Con broker MT5 ✅
└── Cobertura completa         # Todos los componentes ✅

scripts/                        # HERRAMIENTAS ✅
└── demo_sistema_completo.py   # Demo end-to-end ✅

documentacion/bitacora/         # DOCUMENTACIÓN FINAL ✅
├── sotano_1/RESUMEN_EJECUTIVO.md       # SÓTANO 1 ✅
├── sotano_2/DIA_3_COMPLETADO_FINAL.md  # SÓTANO 2 ✅
├── sotano_3/01_RESUMEN_EJECUTIVO.md    # SÓTANO 3 ✅
└── TEMAS_PENDIENTES.md                 # Mejoras opcionales ✅
```

### 🔍 **REGLA #4: MANTENIMIENTO, NO DESARROLLO**

#### **🎯 ENFOQUE EN MANTENIMIENTO:**
```bash
# ✅ ACTIVIDADES PERMITIDAS:
✅ Monitoreo de performance del sistema
✅ Verificación de conexión con broker  
✅ Ejecución de tests de validación
✅ Implementación de mejoras opcionales (según TEMAS_PENDIENTES.md)
✅ Optimización de performance existente

# ❌ ACTIVIDADES RESTRINGIDAS:
❌ Modificación de arquitectura core sin justificación crítica
❌ Cambios en componentes validados con broker real
❌ Eliminación de tests que están pasando
❌ Modificación de conexión FundedNextMT5Manager funcional
```

### 🧪 **REGLA #5: VALIDACIÓN CONTINUA**

#### **🔧 VALIDACIONES DE MANTENIMIENTO:**
```bash
# ✅ TESTS DE MANTENIMIENTO DIARIO:
python scripts/demo_sistema_completo.py    # Demo completo end-to-end
python -m pytest tests/ -v                 # Suite completa (debe ser 192/192)
python tests/test_fundednext_mt5_manager_real.py  # Conexión broker real
```

#### **🚨 REGLA CRÍTICA MT5: TERMINAL EXCLUSIVO OBLIGATORIO**
```bash
# ⚠️ ANTES DE CUALQUIER OPERACIÓN MT5:
python verificar_mt5_exclusivo.py

# 🎯 ASEGURAR:
✅ Solo FundedNext MT5 Terminal ejecutándose
✅ Cerrar automáticamente otros terminales MT5
✅ Conexión verificada con cuenta real
✅ Cumplimiento de reglas de exclusividad
```

#### **🎯 CRITERIOS DE TESTING:**
```
✅ TESTS DEBEN:
- Ejecutarse en <2 segundos
- Tener resultado claro (PASS/FAIL)
- No requerir intervención manual
- Validar todos los imports críticos
- Verificar conectividad MT5 exclusivo (FundedNext)
- Probar funciones principales
```

### 🚨 **REGLA #6: TERMINAL MT5 EXCLUSIVO - FUNDEDNEXT OBLIGATORIO**

#### **📋 CONFIGURACIÓN CRÍTICA:**
```
🎯 TERMINAL AUTORIZADO ÚNICO:
✅ Ruta: C:\Program Files\FundedNext MT5 Terminal\terminal64.exe
✅ Proceso: terminal64.exe (solo FundedNext)
✅ Cuenta: 1511236436 (FTMO-Demo)
✅ Balance: $9,996.50
✅ Servidor: FTMO-Demo

❌ TERMINALES PROHIBIDOS:
❌ Cualquier otro terminal64.exe que NO sea FundedNext
❌ MetaTrader 5 estándar
❌ Otros brokers MT5
```

#### **🔧 HERRAMIENTAS DE CUMPLIMIENTO:**
```bash
# ✅ VERIFICAR ESTADO ACTUAL:
python verificar_mt5_exclusivo.py

# 🚨 ACCIONES AUTOMÁTICAS:
- Cerrar terminales MT5 no autorizados
- Abrir FundedNext MT5 si está cerrado
- Verificar conexión y cuenta
- Reportar estado del sistema
```

#### **⚠️ PROTOCOLO DE EMERGENCIA:**
```
🚨 SI SE DETECTA TERMINAL NO AUTORIZADO:
1. ✅ Ejecutar: python verificar_mt5_exclusivo.py
2. ✅ Confirmar cierre de terminales no autorizados
3. ✅ Verificar que solo FundedNext esté ejecutándose
4. ✅ Validar conexión con cuenta real
5. ✅ Proceder con operaciones solo SI TODO ES ✅
```

### 📝 **REGLA #7: DOCUMENTACIÓN DE CAMBIOS**

#### **📋 ACTUALIZAR SIEMPRE:**
```markdown
🗂️ BITÁCORAS OBLIGATORIAS:
✅ documentacion/bitacora/desarrollo_diario.md          # Lo que se hizo
✅ documentacion/bitacora/componentes_completados.md    # Si se completó algo
✅ documentacion/desarrollo/plan_trabajo.md             # Próximos pasos
✅ documentacion/arquitectura/estado_actual_sistema.md  # Si cambió estado
✅ verificar_mt5_exclusivo.py                          # Verificación MT5 obligatoria
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
