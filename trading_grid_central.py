"""
🏗️ TRADING GRID CENTRAL - SISTEMA SIMPLIFICADO
============================================

Import central inteligente para Trading Grid
Configuración automática de paths y componentes

OBJETIVO: Resolver imports de una vez por todas
RESULTADO: from trading_grid_central import *

AUTOR: Trading Grid System
FECHA: 2025-08-13
"""

import sys
from pathlib import Path

# Configurar proyecto automáticamente
def configure_trading_grid():
    """🔧 Configurar Trading Grid automáticamente"""
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir
    
    # Paths a configurar
    essential_paths = [
        str(project_root),
        str(project_root / "src"),
        str(project_root / "src" / "core"),
        str(project_root / "src" / "analysis" / "piso_3"),
        str(project_root / "src" / "analysis" / "piso_4"),
        str(project_root / "config")
    ]
    
    # Agregar al system path
    for path in essential_paths:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return project_root

# Configurar automáticamente
PROJECT_ROOT = configure_trading_grid()

# Core system disponible inmediatamente
try:
    from logger_manager import LoggerManager
    LOGGER_AVAILABLE = True
except ImportError:
    LoggerManager = None
    LOGGER_AVAILABLE = False

try:
    from mt5_data_manager import MT5DataManager, DATA_MANAGER
    MT5_AVAILABLE = True
except ImportError:
    MT5DataManager = None
    DATA_MANAGER = None
    MT5_AVAILABLE = False

try:
    from session_manager import SessionManager
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    SessionManager = None
    SESSION_MANAGER_AVAILABLE = False

# Estado del sistema
SYSTEM_STATUS = {
    'project_root': str(PROJECT_ROOT),
    'logger_available': LOGGER_AVAILABLE,
    'mt5_available': MT5_AVAILABLE,
    'session_manager_available': SESSION_MANAGER_AVAILABLE,
    'configured': True
}

def get_trading_grid_status():
    """📊 Estado del sistema Trading Grid"""
    return SYSTEM_STATUS.copy()

def create_logger(name="trading_grid"):
    """🔧 Crear logger si está disponible"""
    if LOGGER_AVAILABLE:
        return LoggerManager().get_logger(name)
    else:
        import logging
        return logging.getLogger(name)

def create_mt5_manager():
    """🏢 Crear MT5 manager si está disponible"""
    if MT5_AVAILABLE:
        return MT5DataManager()
    else:
        return None

def create_session_manager():
    """📅 Crear session manager si está disponible"""
    if SESSION_MANAGER_AVAILABLE:
        return SessionManager()
    else:
        return None

def test_trading_grid_central():
    """🧪 Test del sistema central"""
    print("🏗️ Trading Grid Central - Test")
    print("=" * 40)
    
    status = get_trading_grid_status()
    print(f"📁 Project Root: {status['project_root']}")
    print(f"🔧 Logger: {'✅' if status['logger_available'] else '❌'}")
    print(f"🏢 MT5: {'✅' if status['mt5_available'] else '❌'}")
    print(f"📅 Sessions: {'✅' if status['session_manager_available'] else '❌'}")
    
    # Probar componentes
    if status['logger_available']:
        logger = create_logger("test")
        print("🧪 Logger test: ✅")
    
    if status['mt5_available']:
        mt5_mgr = create_mt5_manager()
        print("🧪 MT5 manager test: ✅")
    
    if status['session_manager_available']:
        session_mgr = create_session_manager()
        print("🧪 Session manager test: ✅")

if __name__ == "__main__":
    test_trading_grid_central()
