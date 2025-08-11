"""
Real-Time Module for SÓTANO 2
=============================

Módulo principal de optimización en tiempo real.
Integra streaming MT5, monitoreo de posiciones, alertas y análisis de rendimiento.

Estructura:
- mt5_streamer.py: Stream de datos MT5 en tiempo real
- position_monitor.py: Monitoreo de posiciones y órdenes (próximamente)
- alert_engine.py: Sistema de alertas automático (próximamente)
- performance_tracker.py: Seguimiento de métricas de rendimiento (próximamente)

Autor: Trading Grid System v2.0
Fecha: 2025-08-11
Sótano: 2 - Real-Time Optimization
"""

# Importar solo los módulos que existen actualmente
try:
    from .mt5_streamer import MT5Streamer
    __all__ = ['MT5Streamer']
except ImportError:
    __all__ = []

# Los siguientes se importarán cuando se implementen:
# from .position_monitor import PositionMonitor
# from .alert_engine import AlertEngine
# from .performance_tracker import PerformanceTracker

__version__ = "2.1.0"
__author__ = "Trading Grid System"
__description__ = "SÓTANO 2 - Real-Time Optimization Module"
