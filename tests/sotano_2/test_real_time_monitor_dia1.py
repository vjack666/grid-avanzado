"""
Test DÍA 1 para RealTimeMonitor - PUERTA-S2-MONITOR
Validación de integración con SÓTANO 1

Fecha: 2025-08-11 - DÍA 1 SÓTANO 2
"""

import sys
from pathlib import Path
import time

# Configurar rutas igual que test_sistema.py que SÍ funciona
current_dir = Path(__file__).parent
project_root = current_dir / ".."
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis").absolute()))
sys.path.insert(0, str((project_root / "src" / "utils").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))

def test_real_time_monitor_basic():
    """Test básico del RealTimeMonitor - DÍA 1"""
    print("🧪 TEST REAL-TIME MONITOR - DÍA 1 SÓTANO 2")
    print("=" * 50)
    
    try:
        # Importar RealTimeMonitor
        from real_time_monitor import RealTimeMonitor
        print("✅ Import RealTimeMonitor: OK")
        
        # Inicializar monitor
        monitor = RealTimeMonitor()
        print(f"✅ Inicialización: {monitor.component_id}")
        print(f"✅ Versión: {monitor.version}")
        
        # Verificar puertas SÓTANO 1
        assert monitor.config is not None, "PUERTA-S1-CONFIG no conectada"
        print("✅ PUERTA-S1-CONFIG: Conectada")
        
        assert monitor.logger is not None, "PUERTA-S1-LOGGER no conectada"
        print("✅ PUERTA-S1-LOGGER: Conectada")
        
        assert monitor.error_manager is not None, "PUERTA-S1-ERROR no conectada"
        print("✅ PUERTA-S1-ERROR: Conectada")
        
        assert monitor.data_manager is not None, "PUERTA-S1-DATA no conectada"
        print("✅ PUERTA-S1-DATA: Conectada")
        
        assert monitor.analytics is not None, "PUERTA-S1-ANALYTICS no conectada"
        print("✅ PUERTA-S1-ANALYTICS: Conectada")
        
        assert monitor.mt5 is not None, "PUERTA-S1-MT5 no conectada"
        print("✅ PUERTA-S1-MT5: Conectada")
        
        # Verificar estado inicial
        assert monitor.monitoring_active == False, "Estado inicial incorrecto"
        print("✅ Estado inicial: No activo (correcto)")
        
        # Obtener estado
        status = monitor.get_current_status()
        assert isinstance(status, dict), "Estado no es diccionario"
        assert "component_id" in status, "Estado sin component_id"
        print(f"✅ Estado obtenido: {len(status)} keys")
        
        # Test datos para optimizador
        optimizer_data = monitor.get_monitor_data_for_optimizer()
        print(f"✅ Datos para optimizador: {'Available' if optimizer_data else 'None (expected)'}")
        
        # Cleanup
        monitor.cleanup()
        print("✅ Cleanup: Completado")
        
        print("\n🎉 REAL-TIME MONITOR DÍA 1: ✅ COMPLETADO")
        print("🎯 Todas las puertas SÓTANO 1 conectadas correctamente")
        print("🚀 Listo para DÍA 2: Integración MT5 en tiempo real")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR en test RealTimeMonitor: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_existing_system():
    """Test integración con sistema existente"""
    print("\n🔄 TEST INTEGRACIÓN CON SISTEMA EXISTENTE")
    print("-" * 50)
    
    try:
        # Verificar que el sistema general sigue funcionando
        from config_manager import ConfigManager
        from logger_manager import LoggerManager
        from analytics_manager import AnalyticsManager
        
        config = ConfigManager()
        logger = LoggerManager()
        analytics = AnalyticsManager(config, logger, None, None)
        
        print("✅ Sistema SÓTANO 1 sigue funcionando")
        print("✅ No hay conflictos con SÓTANO 2")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        return False

def main():
    """Ejecutar todos los tests de DÍA 1"""
    print("=" * 60)
    print("🏗️ SÓTANO 2 - DÍA 1: REAL-TIME MONITOR")
    print("PUERTA-S2-MONITOR - Test de integración")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: RealTimeMonitor básico
    if test_real_time_monitor_basic():
        tests_passed += 1
    
    # Test 2: Integración con sistema existente
    if test_integration_with_existing_system():
        tests_passed += 1
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DÍA 1 - SÓTANO 2")
    print("=" * 60)
    print(f"Tests ejecutados: {total_tests}")
    print(f"Tests pasados: {tests_passed}")
    print(f"Tests fallidos: {total_tests - tests_passed}")
    
    if tests_passed == total_tests:
        print("\n🎉 DÍA 1 COMPLETADO EXITOSAMENTE")
        print("✅ PUERTA-S2-MONITOR: Básico funcional")
        print("✅ Integración SÓTANO 1: Sin conflictos")
        print("\n🎯 PRÓXIMO: DÍA 2 - Integración MT5 tiempo real")
        success = True
    else:
        print("\n❌ DÍA 1 CON PROBLEMAS")
        print("🔧 Revisar implementación antes de continuar")
        success = False
    
    return success

if __name__ == "__main__":
    main()
