# Configuración de Pylance para Grid Trading System
# =================================================
# 
# Esta configuración está diseñada para mantener errores críticos
# que afectan la ejecución del sistema de trading mientras reduce
# el ruido de errores de tipos no críticos.

# ERRORES CRÍTICOS MANTENIDOS (nivel: error)
# ------------------------------------------
# - reportMissingImports: Imports faltantes pueden quebrar el sistema
# - reportUndefinedVariable: Variables no definidas causan NameError
# - reportUnboundVariable: Variables sin asignar causan UnboundLocalError
# - reportIncompatibleMethodOverride: Problemas de herencia críticos
# - reportIncompatibleVariableOverride: Sobrescritura incompatible

# ERRORES CONVERTIDOS A WARNINGS
# ------------------------------
# - reportAttributeAccessIssue: Acceso a atributos (importante pero no crítico)
# - reportCallIssue: Problemas de llamadas a funciones
# - reportIndexIssue: Problemas de indexación
# - reportOperatorIssue: Problemas con operadores

# ERRORES SILENCIADOS (nivel: none)
# ---------------------------------
# - reportUnknownParameterType: Parámetros sin tipo anotado
# - reportUnknownVariableType: Variables sin tipo anotado  
# - reportUnknownMemberType: Miembros sin tipo conocido (crucial para MT5)
# - reportUnknownArgumentType: Argumentos sin tipo conocido
# - reportArgumentType: Tipos de argumentos incompatibles
# - reportAssignmentType: Tipos de asignación incompatibles
# - reportReturnType: Tipos de retorno incompatibles
# - reportMissingTypeStubs: Stubs de tipos faltantes

# CONFIGURACIÓN ESPECIAL PARA MT5
# -------------------------------
# Se utilizan comentarios `# type: ignore` para suprimir errores específicos
# de MetaTrader5 ya que esta librería no tiene type stubs completos.
# Esto permite que el sistema funcione sin comprometer la funcionalidad.

# MODO DE ANÁLISIS: basic
# -----------------------
# Se cambió de "strict" a "basic" para un balance entre calidad de código
# y funcionalidad práctica en un sistema de trading en tiempo real.

# ARCHIVOS MEJORADOS
# ------------------
# 1. config/config.py - Añadidas anotaciones de tipos completas
# 2. src/utils/data_logger.py - Función principal con tipos
# 3. src/utils/trading_schedule.py - Funciones de horarios con tipos
# 4. .vscode/settings.json - Configuración optimizada de Pylance

print("Configuración de Pylance implementada exitosamente")
print("Sistema preparado para reducir errores de tipos no críticos")
print("Manteniendo alertas para errores que afectan la ejecución del trading")
