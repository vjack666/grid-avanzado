"""
PISO EJECUTOR - EXECUTION OPERATIONS CENTER
===========================================
Módulo central para operaciones de trading en vivo

Este paquete implementa los componentes críticos para convertir
las señales del StrategyEngine en ejecución real en MT5.

PUERTAS PISO EJECUTOR:
- PUERTA-PE-EXECUTOR: OrderExecutor (TradingSignal → MT5 Order) ✅
- PUERTA-PE-MONITOR: PositionMonitor (Monitoreo posiciones reales)
- PUERTA-PE-RISK: LiveRiskManager (Gestión riesgo tiempo real)
- PUERTA-PE-ALERTS: AlertEngine (Sistema notificaciones críticas)

DEPENDENCIAS:
- SÓTANO 1: ConfigManager, LoggerManager, ErrorManager, MT5Manager
- SÓTANO 2: StrategyEngine, RealTimeMonitor
- SÓTANO 3: FoundationBridge (análisis estratégico)

PROTOCOLO: Trading Grid - Piso Ejecutor
FECHA: 2025-08-12
"""

# Exports principales del piso ejecutor
__all__ = [
    'OrderExecutor',
    'PositionMonitor', 
    'LiveRiskManager',
    'AlertEngine'
]

# Versión del piso ejecutor
__version__ = "1.0.0"

# Metadata
__author__ = "Copilot & AI Assistant"
__date__ = "2025-08-12"
__status__ = "Núcleo Operativo - OrderExecutor Completado"
