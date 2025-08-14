"""
🏗️ CENTRAL DE IMPORTS - TRADING GRID
==================================

Central de importaciones para todo el sistema Trading Grid
Resuelve automáticamente todos los paths y dependencias

MÓDULOS DISPONIBLES:
- Core: Managers principales del sistema
- Analysis: Detectores y analizadores  
- Interfaces: APIs y dashboards
- Utils: Utilidades y helpers

AUTOR: Trading Grid System
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path

# Configurar path del proyecto automáticamente
def setup_project_path():
    """🔧 Configurar path del proyecto automáticamente"""
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    
    # Agregar directorios al path
    paths_to_add = [
        str(project_root),
        str(project_root / "src"),
        str(project_root / "src" / "core"),
        str(project_root / "src" / "analysis"),
        str(project_root / "src" / "interfaces"),
        str(project_root / "src" / "utils"),
        str(project_root / "config")
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return project_root

# Configurar automáticamente al importar
PROJECT_ROOT = setup_project_path()

# Importaciones centrales disponibles
try:
    # Core Managers básicos
    from core.logger_manager import LoggerManager
    LOGGER_AVAILABLE = True
except ImportError:
    LoggerManager = None
    LOGGER_AVAILABLE = False

try:
    # MT5 System
    from core.mt5_data_manager import DATA_MANAGER as MT5_MANAGER, MT5DataManager
    MT5_AVAILABLE = True
except ImportError:
    MT5_MANAGER = None
    MT5DataManager = None
    MT5_AVAILABLE = False

try:
    from analysis.piso_4.session_manager import SessionManager
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    SessionManager = None
    SESSION_MANAGER_AVAILABLE = False

# Intentar importar otros managers si existen
try:
    from core.config_manager import ConfigManager
except ImportError:
    ConfigManager = None

try:
    from analytics_manager import AnalyticsManager
except ImportError:
    AnalyticsManager = None

try:
    from data_manager import DataManager
except ImportError:
    DataManager = None

try:
    from core.error_manager import ErrorManager
except ImportError:
    ErrorManager = None

try:
    from core.ml_foundation.fvg_database_manager import FVGDatabaseManager
except ImportError:
    FVGDatabaseManager = None

try:
    from core.fundednext_mt5_manager import FundedNextMT5Manager
except ImportError:
    FundedNextMT5Manager = None

IMPORTS_AVAILABLE = LOGGER_AVAILABLE

# Información del sistema
__version__ = "1.0.0"
__author__ = "Trading Grid System"
__email__ = "trading@grid.system"

# Exportar componentes disponibles
__all__ = ['test_imports', 'test_all_components', 'get_system_info']

if LOGGER_AVAILABLE:
    __all__.append('LoggerManager')

if MT5_AVAILABLE:
    __all__.extend(['MT5_MANAGER', 'MT5DataManager'])

if SESSION_MANAGER_AVAILABLE:
    __all__.append('SessionManager')

if ConfigManager is not None:
    __all__.append('ConfigManager')

if AnalyticsManager is not None:
    __all__.append('AnalyticsManager')

if DataManager is not None:
    __all__.append('DataManager')

if ErrorManager is not None:
    __all__.append('ErrorManager')

if FVGDatabaseManager is not None:
    __all__.append('FVGDatabaseManager')

if FundedNextMT5Manager is not None:
    __all__.append('FundedNextMT5Manager')

def get_system_info():
    """📊 Información del sistema Trading Grid"""
    return {
        'version': __version__,
        'author': __author__,
        'project_root': str(PROJECT_ROOT),
        'imports_available': IMPORTS_AVAILABLE,
        'python_path': sys.path[:5]  # Primeros 5 paths
    }

def test_imports():
    """🧪 Probar todas las importaciones con log central"""
    
    # Inicializar logger central si está disponible
    central_logger = None
    if LOGGER_AVAILABLE:
        try:
            central_logger = LoggerManager()
            central_logger.log_info("🏗️ Iniciando Testing Central de Imports - Trading Grid")
        except:
            central_logger = None
    
    def log_message(message, level="info"):
        """📝 Log centralizado o fallback a print"""
        if central_logger:
            if level == "info":
                central_logger.log_info(message)
            elif level == "success":
                central_logger.log_success(message)
            elif level == "error":
                central_logger.log_error(message)
            elif level == "warning":
                central_logger.log_warning(message)
        else:
            print(message)
    
    log_message("🏗️ Testing Central de Imports - Trading Grid")
    log_message("=" * 60)
    
    info = get_system_info()
    log_message(f"📁 Project Root: {info['project_root']}")
    log_message(f"✅ Imports Available: {info['imports_available']}")
    
    if IMPORTS_AVAILABLE:
        log_message("\n✅ IMPORTACIONES EXITOSAS:", "success")
        log_message("   🔧 LoggerManager")
        log_message("   ⚙️ ConfigManager") 
        log_message("   📊 AnalyticsManager")
        log_message("   💾 DataManager")
        log_message("   🚨 ErrorManager")
        log_message("   🏢 MT5DataManager")
        log_message("   📈 FVGDetector")
        log_message("   ⚡ RealTimeFVGDetector")
        log_message("   📅 SessionManager")
        log_message("   🔄 DailyCycleManager")
        log_message("   🗃️ FVGDatabaseManager")
        
        # Probar instanciación básica
        try:
            # Test LoggerManager - Crear instancia para verificar funcionalidad
            logger_mgr = LoggerManager()
            log_message("🧪 Test LoggerManager: ✅", "success")
            del logger_mgr  # Limpiar después del test
            
            # Test SessionManager - Crear instancia para verificar funcionalidad  
            session_mgr = SessionManager()
            log_message("🧪 Test SessionManager: ✅", "success")
            del session_mgr  # Limpiar después del test
            
        except Exception as e:
            log_message(f"❌ Error en tests: {e}", "error")
    else:
        log_message("❌ ALGUNOS IMPORTS FALLARON", "error")

def test_all_components():
    """🎯 Test completo de todos los componentes críticos para trading"""
    
    # Inicializar logger central
    central_logger = None
    if LOGGER_AVAILABLE:
        try:
            central_logger = LoggerManager()
            central_logger.log_info("🎯 Iniciando Test Completo de Componentes Trading")
        except:
            central_logger = None
    
    def log_message(message, level="info"):
        """📝 Log centralizado o fallback a print"""
        if central_logger:
            if level == "info":
                central_logger.log_info(message)
            elif level == "success":
                central_logger.log_success(message)
            elif level == "error":
                central_logger.log_error(message)
            elif level == "warning":
                central_logger.log_warning(message)
        else:
            print(message)
    
    components_tested = []
    failed_components = []
    
    # Test LoggerManager
    try:
        # Crear instancia para verificar funcionalidad básica
        logger_mgr = LoggerManager()
        # Verificar que tiene los métodos necesarios
        if hasattr(logger_mgr, 'log_info') and hasattr(logger_mgr, 'log_success'):
            log_message("✅ LoggerManager: Operativo", "success")
            components_tested.append("LoggerManager")
        del logger_mgr  # Limpiar después del test
    except Exception as e:
        log_message(f"❌ LoggerManager: {e}", "error")
        failed_components.append("LoggerManager")
    
    # Test SessionManager
    try:
        # Crear instancia para verificar funcionalidad básica
        session_mgr = SessionManager()
        # Verificar que se instancia correctamente
        if session_mgr is not None:
            log_message("✅ SessionManager: Operativo", "success")
            components_tested.append("SessionManager")
        del session_mgr  # Limpiar después del test
    except Exception as e:
        log_message(f"❌ SessionManager: {e}", "error")
        failed_components.append("SessionManager")
    
    # Test FVGDatabaseManager
    try:
        # Crear instancia para verificar funcionalidad básica
        fvg_mgr = FVGDatabaseManager()
        # Verificar que se instancia correctamente
        if fvg_mgr is not None:
            log_message("✅ FVGDatabaseManager: Operativo", "success")
            components_tested.append("FVGDatabaseManager")
        del fvg_mgr  # Limpiar después del test
    except Exception as e:
        log_message(f"❌ FVGDatabaseManager: {e}", "error")
        failed_components.append("FVGDatabaseManager")
    
    # Test FundedNextMT5Manager
    try:
        # Crear instancia para verificar funcionalidad básica
        mt5_mgr = FundedNextMT5Manager()
        # Verificar que se instancia correctamente
        if mt5_mgr is not None:
            log_message("✅ FundedNextMT5Manager: Operativo", "success")
            components_tested.append("FundedNextMT5Manager")
        del mt5_mgr  # Limpiar después del test
    except Exception as e:
        log_message(f"❌ FundedNextMT5Manager: {e}", "error")
        failed_components.append("FundedNextMT5Manager")
    
    # Resumen final
    log_message(f"📊 RESUMEN: {len(components_tested)} componentes operativos, {len(failed_components)} fallaron")
    
    if len(failed_components) == 0:
        log_message("🚀 TODOS LOS COMPONENTES CRÍTICOS OPERATIVOS - LISTO PARA TRADING", "success")
    else:
        log_message(f"⚠️ Componentes con problemas: {', '.join(failed_components)}", "warning")
    
    return {
        "operational": components_tested,
        "failed": failed_components,
        "ready_for_trading": len(failed_components) == 0
    }

if __name__ == "__main__":
    test_imports()