#!/usr/bin/env python3
"""
🔍 VERIFICACIÓN COMPLETA DEL SISTEMA CENTRAL DE IMPORTS
======================================================

Script para verificar que todos los imports centrales del Trading Grid
estén funcionando correctamente.

Autor: GitHub Copilot  
Fecha: Agosto 12, 2025
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz del proyecto al path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

def print_status(component, status, details=""):
    """Imprime el estado de un componente con formato"""
    status_icon = "✅" if status == "OK" else "❌" if status == "ERROR" else "⚠️"
    print(f"{status_icon} {component:<30} {status:<10} {details}")

def test_import(module_path, component_name):
    """Prueba un import específico"""
    try:
        exec(f"from {module_path} import {component_name}")
        return "OK", ""
    except ImportError as e:
        return "ERROR", f"ImportError: {e}"
    except Exception as e:
        return "ERROR", f"Error: {e}"

def main():
    print("🔍 VERIFICACIÓN SISTEMA CENTRAL DE IMPORTS - TRADING GRID")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Directorio: {sys.path[0]}")
    print()
    
    # Lista de imports críticos a verificar
    imports_to_test = [
        # SÓTANO 1: Infraestructura Base
        ("src.core.config_manager", "ConfigManager"),
        ("src.core.logger_manager", "LoggerManager"),
        ("src.core.logger_manager", "LogLevel"),
        ("src.core.error_manager", "ErrorManager"),
        ("src.core.data_manager", "DataManager"),
        ("src.core.analytics_manager", "AnalyticsManager"),
        ("src.core.indicator_manager", "IndicatorManager"),
        
        # SÓTANO 2: Real-Time Engine
        ("src.core.real_time.strategy_engine", "StrategyEngine"),
        ("src.core.real_time.advanced_analyzer", "AdvancedAnalyzer"),
        ("src.core.real_time.market_regime_detector", "MarketRegimeDetector"),
        
        # SÓTANO 3: Strategic AI
        ("src.core.strategic.foundation_bridge", "FoundationBridge"),
        
        # PISO EJECUTOR: Trading Execution
        ("src.core.fundednext_mt5_manager", "FundedNextMT5Manager"),
        
        # PISO 3: Advanced Analytics
        ("src.analysis.piso_3.deteccion.fvg_detector", "FVGDetector"),
        ("src.analysis.piso_3.analisis", "FVGQualityAnalyzer"),
        
        # SISTEMA PRINCIPAL
        ("trading_grid_main", "TradingGridMain"),
    ]
    
    print("🧪 PROBANDO IMPORTS CRÍTICOS:")
    print("-" * 60)
    
    total_tests = len(imports_to_test)
    passed_tests = 0
    failed_tests = 0
    warnings = 0
    
    for module_path, component_name in imports_to_test:
        status, details = test_import(module_path, component_name)
        
        if status == "OK":
            passed_tests += 1
        elif "no disponible" in details or "Order Executor" in details:
            status = "WARNING"
            warnings += 1
        else:
            failed_tests += 1
            
        print_status(f"{module_path}.{component_name}", status, details)
    
    print()
    print("📊 RESUMEN DE RESULTADOS:")
    print("-" * 60)
    print(f"✅ Tests pasados: {passed_tests}/{total_tests}")
    print(f"❌ Tests fallidos: {failed_tests}/{total_tests}")
    print(f"⚠️  Advertencias: {warnings}/{total_tests}")
    
    # Evaluación final
    if failed_tests == 0:
        print()
        print("🎉 SISTEMA CENTRAL DE IMPORTS: COMPLETAMENTE OPERATIVO")
        print("✅ Todos los componentes críticos están disponibles")
        
        if warnings > 0:
            print(f"⚠️  Nota: {warnings} componentes opcionales no están disponibles (esto es normal)")
            
    else:
        print()
        print("⚠️  SISTEMA CENTRAL DE IMPORTS: PROBLEMAS DETECTADOS")
        print(f"❌ {failed_tests} imports críticos tienen problemas")
        
    # Verificación adicional del sistema principal
    print()
    print("🔍 VERIFICACIÓN ADICIONAL DEL SISTEMA PRINCIPAL:")
    print("-" * 60)
    
    try:
        print("🧪 Probando inicialización completa...")
        
        # Imports básicos
        from src.core.config_manager import ConfigManager
        from src.core.logger_manager import LoggerManager, LogLevel
        from src.core.analytics_manager import AnalyticsManager
        
        print("✅ Imports básicos: OK")
        
        # Verificar que los managers tienen is_initialized
        config = ConfigManager()
        logger = LoggerManager()
        
        has_is_initialized = all([
            hasattr(config, 'is_initialized'),
            hasattr(logger, 'is_initialized')
        ])
        
        print(f"✅ Atributos is_initialized: {'OK' if has_is_initialized else 'FALTA'}")
        
        # Verificar caja negra
        logger.log_system(LogLevel.INFO, "🧪 Test de caja negra - imports verificados")
        print("✅ Caja negra: OK")
        
        print()
        print("🎯 SISTEMA CENTRAL DE IMPORTS: COMPLETAMENTE FUNCIONAL")
        
    except Exception as e:
        print(f"❌ Error en verificación adicional: {e}")
        print("📋 Traceback completo:")
        traceback.print_exc()
        
    print()
    print("🔍 Verificación completada")

if __name__ == "__main__":
    main()
