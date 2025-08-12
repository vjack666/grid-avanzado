"""
Test para AlertEngine - SÓTANO 2 DÍA 2
======================================

Test de integración para el motor de alertas avanzado en tiempo real.
Valida envío, filtrado, priorización, canales de notificación y métricas.

Fecha: 2025-08-11
Componente: PUERTA-S2-ALERTS
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
    
    # Import del AlertEngine desde real_time
    from src.core.real_time.alert_engine import AlertEngine, AlertPriority, AlertChannel, Alert
    
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    print("Nota: Asegúrate de que todos los componentes SÓTANO 1 estén disponibles")
    sys.exit(1)


def test_alert_engine_basic():
    """Test básico de AlertEngine"""
    print("\n🧪 TEST ALERT ENGINE - DÍA 2 SÓTANO 2")
    print("=" * 50)
    
    try:
        # Test 1: Import exitoso
        print("✅ Import AlertEngine: OK")
        
        # Test 2: Crear dependencias SÓTANO 1
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        print("✅ Dependencias SÓTANO 1: OK")
        
        # Test 3: Inicializar AlertEngine
        engine = AlertEngine(config, logger, error)
        assert engine.component_id == "PUERTA-S2-ALERTS", "Component ID incorrecto"
        assert engine.version == "v2.1.0", "Versión incorrecta"
        print(f"✅ Inicialización: {engine.component_id}")
        print(f"✅ Versión: {engine.version}")
        
        # Test 4: Verificar dependencias conectadas
        assert engine.config is not None, "PUERTA-S1-CONFIG no conectada"
        assert engine.logger is not None, "PUERTA-S1-LOGGER no conectada"
        assert engine.error is not None, "PUERTA-S1-ERROR no conectada"
        print("✅ PUERTA-S1-CONFIG: Conectada")
        print("✅ PUERTA-S1-LOGGER: Conectada")
        print("✅ PUERTA-S1-ERROR: Conectada")
        
        # Test 5: Verificar configuración
        assert hasattr(engine, 'alert_config'), "Configuración no inicializada"
        assert 'enabled' in engine.alert_config, "Configuración básica faltante"
        assert 'default_channels' in engine.alert_config, "Canales por defecto faltantes"
        print(f"✅ Configuración: {len(engine.alert_config)} parámetros")
        print(f"✅ Canales default: {len(engine.alert_config['default_channels'])}")
        
        # Test 6: Estado inicial
        status = engine.get_status()
        assert status['is_running'] == False, "Estado inicial incorrecto"
        assert status['component_id'] == "PUERTA-S2-ALERTS", "Component ID en status incorrecto"
        print("✅ Estado inicial: No running (correcto)")
        print(f"✅ Status keys: {len(status)} propiedades")
        
        # Test 7: Métricas iniciales
        metrics = engine.get_metrics()
        assert metrics['total_alerts_received'] == 0, "Métricas iniciales incorrectas"
        assert metrics['alerts_acknowledged'] == 0, "Alert count inicial incorrecto"
        print("✅ Métricas iniciales: OK")
        
        # Test 8: Enums y tipos
        assert AlertPriority.HIGH.value == "high", "Enum AlertPriority incorrecto"
        assert AlertChannel.LOG.value == "log", "Enum AlertChannel incorrecto"
        print("✅ Enums y tipos: OK")
        
        print("\n🎉 ALERT ENGINE BÁSICO DÍA 2: ✅ COMPLETADO")
        print("🎯 Motor de alertas inicializado correctamente")
        print("🔗 Integración SÓTANO 1 validada")
        
    except Exception as e:
        print(f"\n❌ ERROR en test AlertEngine: {e}")
        import traceback
        traceback.print_exc()
        raise AssertionError(f"Test AlertEngine failed: {e}")


def test_alert_sending_and_management():
    """Test de envío y manejo de alertas"""
    print("\n📨 TEST ALERT SENDING AND MANAGEMENT")
    print("-" * 50)
    
    try:
        # Crear componentes
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        engine = AlertEngine(config, logger, error)
        
        # Test envío de alerta básica
        alert_id = engine.send_alert(
            priority=AlertPriority.HIGH,
            category="test",
            title="Test Alert",
            message="Esta es una alerta de prueba",
            data={"test_value": 123}
        )
        
        assert alert_id != "", "Alert ID no generado"
        print(f"✅ Alerta enviada: {alert_id}")
        
        # Verificar métricas actualizadas
        metrics = engine.get_metrics()
        assert metrics['total_alerts_received'] == 1, "Métrica no actualizada"
        assert metrics['alerts_by_priority']['high'] == 1, "Prioridad no contada"
        print("✅ Métricas actualizadas: OK")
        
        # Test obtener alertas activas
        active_alerts = engine.get_active_alerts()
        assert len(active_alerts) == 1, "Alerta no agregada a activas"
        assert active_alerts[0].id == alert_id, "ID de alerta no coincide"
        assert active_alerts[0].priority == AlertPriority.HIGH, "Prioridad no coincide"
        print("✅ Alerta activa: Verificada")
        
        # Test reconocer alerta
        result = engine.acknowledge_alert(alert_id)
        assert result == True, "Acknowledge falló"
        assert active_alerts[0].acknowledged == True, "Alerta no marcada como acknowledged"
        print("✅ Acknowledge: OK")
        
        # Test resolver alerta
        result = engine.resolve_alert(alert_id)
        assert result == True, "Resolve falló"
        
        # Verificar que se movió al historial
        active_alerts = engine.get_active_alerts()
        assert len(active_alerts) == 0, "Alerta no removida de activas"
        
        history = engine.get_alert_history()
        assert len(history) == 1, "Alerta no agregada al historial"
        print("✅ Resolve: OK")
        
        # Test múltiples alertas
        for i in range(3):
            engine.send_alert(
                priority=AlertPriority.MEDIUM,
                category=f"test_{i}",
                title=f"Test Alert {i}",
                message=f"Mensaje {i}"
            )
        
        active_alerts = engine.get_active_alerts()
        assert len(active_alerts) == 3, "Múltiples alertas no enviadas"
        print("✅ Múltiples alertas: OK")
        
    except Exception as e:
        print(f"❌ Error en test de alertas: {e}")
        raise AssertionError(f"Test alert sending failed: {e}")


def test_notification_channels():
    """Test del sistema de canales de notificación"""
    print("\n📢 TEST NOTIFICATION CHANNELS")
    print("-" * 50)
    
    try:
        # Crear componentes
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        engine = AlertEngine(config, logger, error)
        
        # Test suscripción a canales
        log_notifications = []
        email_notifications = []
        
        def log_callback(alert: Alert):
            log_notifications.append(f"LOG:{alert.title}")
            
        def email_callback(alert: Alert):
            email_notifications.append(f"EMAIL:{alert.title}")
            
        engine.subscribe_channel(AlertChannel.LOG, log_callback)
        engine.subscribe_channel(AlertChannel.EMAIL, email_callback)
        print("✅ Callbacks suscritos: LOG, EMAIL")
        
        # Test envío con canal específico
        alert_id = engine.send_alert(
            priority=AlertPriority.CRITICAL,
            category="notification_test",
            title="Test Notification",
            message="Test de notificaciones",
            channels=[AlertChannel.LOG, AlertChannel.EMAIL]
        )
        
        # Esperar procesamiento
        time.sleep(0.1)
        
        # Verificar notificaciones recibidas
        assert "LOG:Test Notification" in log_notifications, "Notificación LOG no recibida"
        assert "EMAIL:Test Notification" in email_notifications, "Notificación EMAIL no recibida"
        print("✅ Notificaciones enviadas: LOG, EMAIL")
        
        # Test desuscripción
        engine.unsubscribe_channel(AlertChannel.LOG, log_callback)
        
        # Enviar otra alerta
        engine.send_alert(
            priority=AlertPriority.LOW,
            category="notification_test",
            title="Test Notification 2",
            message="Segunda notificación",
            channels=[AlertChannel.LOG, AlertChannel.EMAIL]
        )
        
        time.sleep(0.1)
        
        # Solo EMAIL debería haber recibido la segunda
        assert "EMAIL:Test Notification 2" in email_notifications, "Segunda notificación EMAIL no recibida"
        assert "LOG:Test Notification 2" not in log_notifications, "LOG recibió notificación después de desuscribirse"
        print("✅ Desuscripción: Funcional")
        
    except Exception as e:
        print(f"❌ Error en test de canales: {e}")
        raise AssertionError(f"Test notification channels failed: {e}")


def test_filtering_and_throttling():
    """Test de filtrado y throttling"""
    print("\n🚦 TEST FILTERING AND THROTTLING")
    print("-" * 50)
    
    try:
        # Crear componentes
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        engine = AlertEngine(config, logger, error)
        
        # Configurar throttling corto para testing
        engine.alert_config["throttle_seconds"] = 1
        
        # Test filtro personalizado
        def test_filter(alert: Alert) -> bool:
            # Filtrar alertas que contienen "SPAM"
            return "SPAM" in alert.title
            
        engine.add_filter(test_filter)
        print("✅ Filtro personalizado agregado")
        
        # Test: alerta normal debería pasar
        alert_id1 = engine.send_alert(
            priority=AlertPriority.MEDIUM,
            category="filter_test",
            title="Normal Alert",
            message="Esta debería pasar"
        )
        
        assert alert_id1 != "", "Alerta normal no pasó el filtro"
        print("✅ Alerta normal: Pasó filtro")
        
        # Test: alerta con SPAM debería ser filtrada
        alert_id2 = engine.send_alert(
            priority=AlertPriority.HIGH,
            category="filter_test",
            title="SPAM Alert",
            message="Esta debería ser filtrada"
        )
        
        assert alert_id2 == "", "Alerta SPAM no fue filtrada"
        print("✅ Filtro SPAM: Funcional")
        
        # Test throttling - enviar la misma alerta dos veces rápido
        alert_id3 = engine.send_alert(
            priority=AlertPriority.LOW,
            category="throttle_test",
            title="Throttle Test",
            message="Primera vez"
        )
        
        alert_id4 = engine.send_alert(
            priority=AlertPriority.LOW,
            category="throttle_test",
            title="Throttle Test",
            message="Segunda vez (debería ser throttled)"
        )
        
        assert alert_id3 != "", "Primera alerta throttle no enviada"
        assert alert_id4 == "", "Segunda alerta no fue throttled"
        print("✅ Throttling: Funcional")
        
        # Verificar métricas de filtrado
        metrics = engine.get_metrics()
        assert metrics['alerts_filtered'] >= 2, "Métricas de filtrado incorrectas"
        print("✅ Métricas de filtrado: Actualizadas")
        
    except Exception as e:
        print(f"❌ Error en test de filtrado: {e}")
        raise AssertionError(f"Test filtering failed: {e}")


def test_engine_lifecycle():
    """Test del ciclo de vida del motor"""
    print("\n🔄 TEST ENGINE LIFECYCLE")
    print("-" * 50)
    
    try:
        # Crear componentes
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        engine = AlertEngine(config, logger, error)
        
        # Test estado inicial
        status = engine.get_status()
        assert status['is_running'] == False, "Estado inicial incorrecto"
        print("✅ Estado inicial: Parado")
        
        # Test iniciar motor
        result = engine.start_engine()
        assert result == True, "Motor no se pudo iniciar"
        assert engine.is_running == True, "Estado is_running incorrecto"
        print("✅ Motor iniciado: OK")
        
        # Esperar un poco para que el thread se establezca
        time.sleep(0.5)
        
        # Test enviar alertas con motor ejecutándose
        alert_id = engine.send_alert(
            priority=AlertPriority.CRITICAL,
            category="lifecycle_test",
            title="Test con motor ejecutándose",
            message="Motor activo"
        )
        
        assert alert_id != "", "Alerta no enviada con motor activo"
        print("✅ Alerta con motor activo: OK")
        
        # Test detener motor
        result = engine.stop_engine()
        assert result == True, "Motor no se pudo detener"
        assert engine.is_running == False, "Estado después de stop incorrecto"
        print("✅ Motor detenido: OK")
        
        # Verificar que las alertas siguen funcionando (sin auto-resolve)
        alert_id2 = engine.send_alert(
            priority=AlertPriority.LOW,
            category="lifecycle_test",
            title="Test con motor parado",
            message="Motor inactivo"
        )
        
        assert alert_id2 != "", "Alerta no enviada con motor parado"
        print("✅ Alerta con motor parado: OK")
        
    except Exception as e:
        print(f"❌ Error en test de ciclo de vida: {e}")
        raise AssertionError(f"Test lifecycle failed: {e}")


def main():
    """Función principal de testing"""
    print("=" * 60)
    print("🏗️ SÓTANO 2 - DÍA 2: ALERT ENGINE")
    print("PUERTA-S2-ALERTS - Test de integración")
    print("=" * 60)
    
    # Ejecutar tests
    test_results = []
    
    try:
        # Test 1: Funcionalidad básica
        test_alert_engine_basic()
        test_results.append(True)
    except Exception:
        test_results.append(False)
    
    try:
        # Test 2: Envío y manejo de alertas
        test_alert_sending_and_management()
        test_results.append(True)
    except Exception:
        test_results.append(False)
    
    try:
        # Test 3: Canales de notificación
        test_notification_channels()
        test_results.append(True)
    except Exception:
        test_results.append(False)
    
    try:
        # Test 4: Filtrado y throttling
        test_filtering_and_throttling()
        test_results.append(True)
    except Exception:
        test_results.append(False)
    
    try:
        # Test 5: Ciclo de vida del motor
        test_engine_lifecycle()
        test_results.append(True)
    except Exception:
        test_results.append(False)
    
    # Test 6: Compatibilidad con sistema existente
    print("\n🔄 TEST COMPATIBILIDAD CON SISTEMA EXISTENTE")
    print("-" * 50)
    try:
        # Verificar que el sistema SÓTANO 1 sigue funcionando
        from src.core.analytics_manager import AnalyticsManager
        from src.core.data_manager import DataManager
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
    print("📊 RESUMEN DÍA 2 - ALERT ENGINE")
    print("=" * 60)
    tests_passed = sum(test_results)
    tests_total = len(test_results)
    
    print(f"Tests ejecutados: {tests_total}")
    print(f"Tests pasados: {tests_passed}")
    print(f"Tests fallidos: {tests_total - tests_passed}")
    
    if tests_passed == tests_total:
        print("\n🎉 DÍA 2 - ALERT ENGINE: ✅ COMPLETADO")
        print("✅ PUERTA-S2-ALERTS: Funcional")
        print("✅ Integración SÓTANO 1: Sin conflictos")
        print("✅ Sistema de notificaciones: Funcional")
        print("✅ Filtrado y throttling: Funcional")
        print("✅ Ciclo de vida: Funcional")
        print("🎯 PRÓXIMO: Performance Tracker - Seguimiento de rendimiento")
        assert tests_passed == tests_total, f"Tests fallidos: {tests_total - tests_passed}"
    else:
        print(f"\n❌ DÍA 2 CON PROBLEMAS")
        print("🔧 Revisar implementación antes de continuar")
        raise AssertionError(f"Tests fallidos: {tests_total - tests_passed}")


if __name__ == "__main__":
    main()
