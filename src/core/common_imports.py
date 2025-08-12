"""
Imports Comunes - SÓTANO 1 CORE
================================

Módulo centralizado que provee todos los imports comunes utilizados en el proyecto.
Esto permite tener una sola fuente de dependencias y evita duplicar imports.

Fecha: 2025-08-12
Componente: PUERTA-S1-IMPORTS  
Fase: CORE - Centralización de dependencias
"""

# === LIBRERÍAS ESTÁNDAR ===
import os
import sys
import time
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field
import json
import logging

# === LIBRERÍAS DE DATOS Y ANÁLISIS ===
import pandas as pd
import numpy as np

# === LIBRERÍAS DE TRADING ===
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None

# === LIBRERÍAS DE ANÁLISIS AVANZADO (OPCIONALES) ===
try:
    from scipy import stats
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    ADVANCED_ANALYTICS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYTICS_AVAILABLE = False
    stats = None
    RandomForestRegressor = None
    LinearRegression = None
    StandardScaler = None

# === PYTEST PARA TESTS ===
try:
    import pytest
    from unittest.mock import Mock, patch, MagicMock
    TESTING_AVAILABLE = True
except ImportError:
    TESTING_AVAILABLE = False
    pytest = None
    Mock = None
    patch = None
    MagicMock = None

# === CONSTANTES DE CONFIGURACIÓN ===
# Versión del sistema de imports
IMPORTS_VERSION = "v1.0.0"

# Configuración de pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# === FUNCIONES DE UTILIDAD ===

def get_available_libraries() -> Dict[str, bool]:
    """
    Obtener estado de disponibilidad de librerías
    
    Returns:
        Dict con estado de cada librería
    """
    return {
        'pandas': True,
        'numpy': True,
        'mt5': MT5_AVAILABLE,
        'advanced_analytics': ADVANCED_ANALYTICS_AVAILABLE,
        'testing': TESTING_AVAILABLE,
        'asyncio': True,
        'datetime': True,
        'typing': True
    }

def validate_dependencies() -> Tuple[bool, List[str]]:
    """
    Validar que las dependencias críticas estén disponibles
    
    Returns:
        Tuple[bool, List[str]]: (todo_ok, lista_de_errores)
    """
    errors = []
    
    # Dependencias críticas
    critical_deps = ['pandas', 'numpy']
    for dep in critical_deps:
        try:
            if dep == 'pandas' and pd is None:
                errors.append(f"Dependencia crítica faltante: {dep}")
            elif dep == 'numpy' and np is None:
                errors.append(f"Dependencia crítica faltante: {dep}")
        except Exception:
            errors.append(f"Error validando dependencia: {dep}")
    
    return len(errors) == 0, errors

def log_dependencies_status():
    """Log del estado de dependencias al inicializar"""
    available = get_available_libraries()
    print("🔧 SÓTANO 1 - IMPORTS CORE INICIALIZADO")
    print(f"📦 Versión: {IMPORTS_VERSION}")
    print("📋 Estado de dependencias:")
    
    for lib, status in available.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {lib}: {'Disponible' if status else 'No disponible'}")
    
    # Validar dependencias críticas
    is_valid, errors = validate_dependencies()
    if not is_valid:
        print("⚠️  ERRORES EN DEPENDENCIAS CRÍTICAS:")
        for error in errors:
            print(f"   🚨 {error}")
    else:
        print("✅ Todas las dependencias críticas OK")

# === INICIALIZACIÓN AUTOMÁTICA ===
if __name__ != "__main__":
    # Solo mostrar en modo de desarrollo o debug
    import os
    if os.getenv("GRID_DEBUG") == "1":
        log_dependencies_status()

# === EXPORTS PRINCIPALES ===
__all__ = [
    # Librerías estándar
    'os', 'sys', 'time', 'threading', 'asyncio', 'datetime', 'timedelta',
    'Dict', 'List', 'Tuple', 'Optional', 'Any', 'Union', 'Callable',
    'Path', 'dataclass', 'field', 'json', 'logging',
    
    # Librerías de datos
    'pd', 'np',
    
    # Trading
    'mt5', 'MT5_AVAILABLE',
    
    # Analytics avanzado
    'stats', 'RandomForestRegressor', 'LinearRegression', 'StandardScaler',
    'ADVANCED_ANALYTICS_AVAILABLE',
    
    # Testing
    'pytest', 'Mock', 'patch', 'MagicMock', 'TESTING_AVAILABLE',
    
    # Utilidades
    'get_available_libraries', 'validate_dependencies', 'log_dependencies_status',
    'IMPORTS_VERSION'
]
