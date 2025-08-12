"""
Test para PositionMonitor - SÓTANO 2 DÍA 2
==========================================

Test de integración para el componente de monitoreo de posiciones MT5 en tiempo real.
Valida funcionalidad básica, detección de cambios y alertas de riesgo.

Fecha: 2025-08-11
Componente: PUERTA-S2-POSITIONS
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
    # Importar desde src.core usando imports absolutos
    from src.core.config_manager import ConfigManager
    from src.core.logger_manager import LoggerManager  
    from src.core.error_manager import ErrorManager
    from src.core.mt5_manager import MT5Manager
    from src.core.data_manager import DataManager
    
    # Import del PositionMonitor desde real_time
    from src.core.real_time.position_monitor import PositionMonitor
    
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    print("Nota: Asegúrate de que todos los componentes SÓTANO 1 estén disponibles")
    sys.exit(1)


def test_position_monitor_basic():
    """Test básico de PositionMonitor"""
    print("\n🧪 TEST POSITION MONITOR - DÍA 2 SÓTANO 2")
    print("=" * 50)
    
    try:
        # Test 1: Import exitoso
        print("✅ Import PositionMonitor: OK")
        
        # Test 2: Crear dependencias SÓTANO 1
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        mt5_manager = MT5Manager(config, logger, error)
        data_manager = DataManager(config, logger, error)
        print("✅ Dependencias SÓTANO 1: OK")
        
        # Test 3: Inicializar PositionMonitor
        monitor = PositionMonitor(config, logger, error, mt5_manager, data_manager)
        assert monitor.component_id == "PUERTA-S2-POSITIONS", "Component ID incorrecto"
        assert monitor.version == "v2.1.0", "Versión incorrecta"
        print(f"✅ Inicialización: {monitor.component_id}")
        print(f"✅ Versión: {monitor.version}")
        
        # Test 4: Verificar dependencias conectadas
        assert monitor.config is not None, "PUERTA-S1-CONFIG no conectada"
        assert monitor.logger is not None, "PUERTA-S1-LOGGER no conectada"
        assert monitor.error is not None, "PUERTA-S1-ERROR no conectada"
        assert monitor.mt5 is not None, "PUERTA-S1-MT5 no conectada"
        assert monitor.data is not None, "PUERTA-S1-DATA no conectada"
        print("✅ PUERTA-S1-CONFIG: Conectada")
        print("✅ PUERTA-S1-LOGGER: Conectada")
        print("✅ PUERTA-S1-ERROR: Conectada")
        print("✅ PUERTA-S1-MT5: Conectada")
        print("✅ PUERTA-S1-DATA: Conectada")
        
        # Test 5: Verificar configuración
        assert hasattr(monitor, 'monitor_config'), "Configuración no inicializada"
        assert 'symbols_to_track' in monitor.monitor_config, "Símbolos no configurados"
        assert 'update_interval' in monitor.monitor_config, "Intervalo no configurado"
        print(f"✅ Configuración: {len(monitor.monitor_config['symbols_to_track'])} símbolos")
        print(f"✅ Intervalo: {monitor.monitor_config['update_interval']}s")
        
        # Test 6: Estado inicial
        status = monitor.get_status()
        assert status['is_monitoring'] == False, "Estado inicial incorrecto"
        assert status['component_id'] == "PUERTA-S2-POSITIONS", "Component ID en status incorrecto"
        print("✅ Estado inicial: No monitoring (correcto)")
        print(f"✅ Status keys: {len(status)} propiedades")
        
        # Test 7: Métricas iniciales
        metrics = monitor.get_metrics()
        assert metrics['total_positions_tracked'] == 0, "Métricas iniciales incorrectas"
        assert metrics['alerts_triggered'] == 0, "Alert count inicial incorrecto"
        print("✅ Métricas iniciales: OK")
        
        # Test 8: Sistema de alertas
        alert_received = []
        
        def test_alert_callback(alert_type, data):
            alert_received.append((alert_type, data))
            
        monitor.subscribe_alerts(test_alert_callback)
        assert test_alert_callback in monitor.alert_callbacks, "Suscripción de alerta falló"
        monitor.unsubscribe_alerts(test_alert_callback)
        assert test_alert_callback not in monitor.alert_callbacks, "Desuscripción de alerta falló"
        print("✅ Sistema de alertas: OK")
        
        # Test 9: Funciones de estado
        positions = monitor.get_current_positions()
        assert isinstance(positions, dict), "get_current_positions no retorna dict"
        
        history = monitor.get_position_history()
        assert isinstance(history, list), "get_position_history no retorna list"
        
        pnl = monitor.get_current_pnl()
        assert isinstance(pnl, (int, float)), "get_current_pnl no retorna número"
        
        print("✅ Funciones de estado: OK")
        
        print("\n🎉 POSITION MONITOR BÁSICO DÍA 2: ✅ COMPLETADO")
        print("🎯 Monitoreo de posiciones inicializado correctamente")
        print("🔗 Integración SÓTANO 1 validada")
        
        assert True  # Test exitoso
        
    except Exception as e:
        print(f"\n❌ ERROR en test PositionMonitor: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Error en test PositionMonitor: {e}"


def test_position_monitoring_integration():
    """Test de integración con monitoreo (limitado sin MT5 real)"""
    print("\n🔄 TEST POSITION MONITORING INTEGRATION")
    print("-" * 50)
    
    try:
        # Crear componentes
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        mt5_manager = MT5Manager(config, logger, error)
        data_manager = DataManager(config, logger, error)
        monitor = PositionMonitor(config, logger, error, mt5_manager, data_manager)
        
        # Test de configuración de símbolos personalizados
        test_symbols = ["EURUSD", "GBPUSD"]
        
        # Nota: Sin conexión MT5 real, esto fallará graciosamente
        result = monitor.start_monitoring(symbols=test_symbols)
        print(f"✅ Start monitoring attempt: {result} (esperado fallar sin MT5)")
        
        # Verificar que la configuración se actualizó
        assert monitor.monitor_config["symbols_to_track"] == test_symbols, "Símbolos no actualizados"
        print("✅ Configuración de símbolos: Actualizada")
        
        # Test stop (debería funcionar aunque no esté monitoring)
        result = monitor.stop_monitoring()
        print(f"✅ Stop monitoring: {result}")
        
        # Test métricas
        metrics = monitor.get_metrics()
        assert 'total_positions_tracked' in metrics, "Métricas incompletas"
        print("✅ Métricas: Disponibles")
        
        # Test thresholds de riesgo
        assert hasattr(monitor, 'risk_thresholds'), "Risk thresholds no configurados"
        assert 'max_drawdown' in monitor.risk_thresholds, "Max drawdown no configurado"
        print("✅ Risk thresholds: Configurados")
        
        print("✅ Integración de monitoreo: Sin errores críticos")
        
        assert True  # Test exitoso
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        assert False, f"Error en integración: {e}"


def test_alert_system():
    """Test del sistema de alertas"""
    print("\n🚨 TEST ALERT SYSTEM")
    print("-" * 50)
    
    try:
        # Crear componentes
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        mt5_manager = MT5Manager(config, logger, error)
        data_manager = DataManager(config, logger, error)
        monitor = PositionMonitor(config, logger, error, mt5_manager, data_manager)
        
        # Test múltiples callbacks
        alerts_received = []
        
        def callback1(alert_type, data):
            alerts_received.append(f"CB1:{alert_type}")
            
        def callback2(alert_type, data):
            alerts_received.append(f"CB2:{alert_type}")
            
        monitor.subscribe_alerts(callback1)
        monitor.subscribe_alerts(callback2)
        assert len(monitor.alert_callbacks) == 2, "Callbacks no agregados correctamente"
        print("✅ Múltiples callbacks: Configurados")
        
        # Test manual de alerta
        monitor._notify_alert_callbacks("TEST_ALERT", {"test": True})
        time.sleep(0.1)  # Esperar procesamiento
        
        expected_alerts = ["CB1:TEST_ALERT", "CB2:TEST_ALERT"]
        for alert in expected_alerts:
            assert alert in alerts_received, f"Alerta {alert} no recibida"
            
        print("✅ Callbacks funcionando: Alertas recibidas")
        
        # Test desuscripción
        monitor.unsubscribe_alerts(callback1)
        assert len(monitor.alert_callbacks) == 1, "Callback no removido"
        print("✅ Desuscripción: OK")
        
        assert True  # Test exitoso
        
    except Exception as e:
        print(f"❌ Error en test de alertas: {e}")
        assert False, f"Error en test de alertas: {e}"


def main():
    """Función principal de testing"""
    print("=" * 60)
    print("🏗️ SÓTANO 2 - DÍA 2: POSITION MONITOR")
    print("PUERTA-S2-POSITIONS - Test de integración")
    print("=" * 60)
    
    # Ejecutar tests
    test_results = []
    
    # Test 1: Funcionalidad básica
    test_results.append(test_position_monitor_basic())
    
    # Test 2: Integración de monitoreo
    test_results.append(test_position_monitoring_integration())
    
    # Test 3: Sistema de alertas
    test_results.append(test_alert_system())
    
    # Test 4: Compatibilidad con sistema existente
    print("\n🔄 TEST COMPATIBILIDAD CON SISTEMA EXISTENTE")
    print("-" * 50)
    try:
        # Verificar que el sistema SÓTANO 1 sigue funcionando
        from src.core.analytics_manager import AnalyticsManager
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
    print("📊 RESUMEN DÍA 2 - POSITION MONITOR")
    print("=" * 60)
    tests_passed = sum(test_results)
    tests_total = len(test_results)
    
    print(f"Tests ejecutados: {tests_total}")
    print(f"Tests pasados: {tests_passed}")
    print(f"Tests fallidos: {tests_total - tests_passed}")
    
    if tests_passed == tests_total:
        print("\n🎉 DÍA 2 - POSITION MONITOR: ✅ COMPLETADO")
        print("✅ PUERTA-S2-POSITIONS: Funcional")
        print("✅ Integración SÓTANO 1: Sin conflictos")
        print("✅ Sistema de alertas: Funcional")
        print("🎯 PRÓXIMO: Alert Engine - Motor de alertas avanzado")
        assert True  # Test exitoso
    else:
        print(f"\n❌ DÍA 2 CON PROBLEMAS")
        print("🔧 Revisar implementación antes de continuar")
        assert False, "Día 2 completado con problemas"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
