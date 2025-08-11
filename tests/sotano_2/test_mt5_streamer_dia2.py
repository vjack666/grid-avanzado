"""
Test para MT5Streamer - SÓTANO 2 DÍA 2
=====================================

Test de integración para el componente de streaming MT5 en tiempo real.
Valida funcionalidad básica, rendimiento y integración con SÓTANO 1.

Fecha: 2025-08-11
Componente: PUERTA-S2-STREAMER
Fase: DÍA 2 - Integración MT5 Real-Time
"""

import sys
import os
from pathlib import Path
import unittest
import time
import threading
from datetime import datetime

# Configurar paths para imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
src_core = project_root / "src" / "core"
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str(src_core.absolute()))

# Imports absolutos con validación
try:
    # Importar desde src/core directamente
    sys.path.append(str(src_core))
    from config_manager import ConfigManager
    from logger_manager import LoggerManager  
    from error_manager import ErrorManager
    from mt5_manager import MT5Manager
    
    # Import del MT5Streamer desde real_time
    from real_time.mt5_streamer import MT5Streamer
    
    # Import para test de compatibilidad
    from analytics_manager import AnalyticsManager
    
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    print("Nota: Asegúrate de que todos los componentes SÓTANO 1 estén disponibles")
    sys.exit(1)


def test_mt5_streamer_basic():
    """Test básico de MT5Streamer"""
    print("\n🧪 TEST MT5STREAMER - DÍA 2 SÓTANO 2")
    print("=" * 50)
    
    try:
        # Test 1: Import exitoso
        print("✅ Import MT5Streamer: OK")
        
        # Test 2: Crear dependencias SÓTANO 1
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        mt5_manager = MT5Manager(config, logger, error)
        print("✅ Dependencias SÓTANO 1: OK")
        
        # Test 3: Inicializar MT5Streamer
        streamer = MT5Streamer(config, logger, error, mt5_manager)
        assert streamer.component_id == "PUERTA-S2-STREAMER", "Component ID incorrecto"
        assert streamer.version == "v2.1.0", "Versión incorrecta"
        print(f"✅ Inicialización: {streamer.component_id}")
        print(f"✅ Versión: {streamer.version}")
        
        # Test 4: Verificar dependencias conectadas
        assert streamer.config is not None, "PUERTA-S1-CONFIG no conectada"
        assert streamer.logger is not None, "PUERTA-S1-LOGGER no conectada"
        assert streamer.error is not None, "PUERTA-S1-ERROR no conectada"
        assert streamer.mt5 is not None, "PUERTA-S1-MT5 no conectada"
        print("✅ PUERTA-S1-CONFIG: Conectada")
        print("✅ PUERTA-S1-LOGGER: Conectada")
        print("✅ PUERTA-S1-ERROR: Conectada")
        print("✅ PUERTA-S1-MT5: Conectada")
        
        # Test 5: Verificar configuración
        assert hasattr(streamer, 'streaming_config'), "Configuración no inicializada"
        assert 'symbols' in streamer.streaming_config, "Símbolos no configurados"
        assert 'update_interval' in streamer.streaming_config, "Intervalo no configurado"
        print(f"✅ Configuración: {len(streamer.streaming_config['symbols'])} símbolos")
        print(f"✅ Intervalo: {streamer.streaming_config['update_interval']}s")
        
        # Test 6: Estado inicial
        status = streamer.get_status()
        assert status['is_streaming'] == False, "Estado inicial incorrecto"
        assert status['component_id'] == "PUERTA-S2-STREAMER", "Component ID en status incorrecto"
        print("✅ Estado inicial: No streaming (correcto)")
        print(f"✅ Status keys: {len(status)} propiedades")
        
        # Test 7: Métricas iniciales
        metrics = streamer.get_metrics()
        assert metrics['total_ticks'] == 0, "Métricas iniciales incorrectas"
        assert metrics['errors'] == 0, "Error count inicial incorrecto"
        print("✅ Métricas iniciales: OK")
        
        # Test 8: Funciones de suscripción
        def dummy_callback(data):
            pass
            
        streamer.subscribe(dummy_callback)
        assert dummy_callback in streamer._subscribers, "Suscripción falló"
        streamer.unsubscribe(dummy_callback)
        assert dummy_callback not in streamer._subscribers, "Desuscripción falló"
        print("✅ Sistema de suscripción: OK")
        
        print("\n🎉 MT5STREAMER BÁSICO DÍA 2: ✅ COMPLETADO")
        print("🎯 Streaming MT5 inicializado correctamente")
        print("🔗 Integración SÓTANO 1 validada")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR en test MT5Streamer: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_streaming_integration():
    """Test de integración con streaming (limitado sin MT5 real)"""
    print("\n🔄 TEST STREAMING INTEGRATION")
    print("-" * 50)
    
    try:
        # Crear componentes
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        mt5_manager = MT5Manager(config, logger, error)
        streamer = MT5Streamer(config, logger, error, mt5_manager)
        
        # Test de configuración de símbolos personalizados
        test_symbols = ["EURUSD", "GBPUSD"]
        
        # Nota: Sin conexión MT5 real, esto fallará graciosamente
        result = streamer.start_streaming(symbols=test_symbols)
        print(f"✅ Start streaming attempt: {result} (esperado fallar sin MT5)")
        
        # Verificar que la configuración se actualizó
        assert streamer.streaming_config["symbols"] == test_symbols, "Símbolos no actualizados"
        print("✅ Configuración de símbolos: Actualizada")
        
        # Test stop (debería funcionar aunque no esté streaming)
        result = streamer.stop_streaming()
        print(f"✅ Stop streaming: {result}")
        
        # Test datos más recientes (debería ser None sin datos)
        latest = streamer.get_latest_data()
        assert latest is None, "Datos inesperados sin streaming"
        print("✅ Latest data: None (correcto sin streaming)")
        
        print("✅ Integración de streaming: Sin errores críticos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        return False


def main():
    """Función principal de testing"""
    print("=" * 60)
    print("🏗️ SÓTANO 2 - DÍA 2: MT5 STREAMER")
    print("PUERTA-S2-STREAMER - Test de integración")
    print("=" * 60)
    
    # Ejecutar tests
    test_results = []
    
    # Test 1: Funcionalidad básica
    test_results.append(test_mt5_streamer_basic())
    
    # Test 2: Integración de streaming
    test_results.append(test_streaming_integration())
    
    # Test 3: Compatibilidad con sistema existente
    print("\n🔄 TEST COMPATIBILIDAD CON SISTEMA EXISTENTE")
    print("-" * 50)
    try:
        # Verificar que el sistema SÓTANO 1 sigue funcionando
        from analytics_manager import AnalyticsManager
        from data_manager import DataManager
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        data_manager = DataManager(config, logger, error)
        analytics = AnalyticsManager(config, logger, error, data_manager)
        print("✅ Sistema SÓTANO 1 sigue funcionando")
        print("✅ No hay conflictos con SÓTANO 2")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Error de compatibilidad: {e}")
        test_results.append(False)
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DÍA 2 - MT5 STREAMER")
    print("=" * 60)
    tests_passed = sum(test_results)
    tests_total = len(test_results)
    
    print(f"Tests ejecutados: {tests_total}")
    print(f"Tests pasados: {tests_passed}")
    print(f"Tests fallidos: {tests_total - tests_passed}")
    
    if tests_passed == tests_total:
        print("\n🎉 DÍA 2 - MT5 STREAMER: ✅ COMPLETADO")
        print("✅ PUERTA-S2-STREAMER: Funcional")
        print("✅ Integración SÓTANO 1: Sin conflictos")
        print("🎯 PRÓXIMO: Position Monitor - Monitoreo de posiciones")
        return True
    else:
        print(f"\n❌ DÍA 2 CON PROBLEMAS")
        print("🔧 Revisar implementación antes de continuar")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
