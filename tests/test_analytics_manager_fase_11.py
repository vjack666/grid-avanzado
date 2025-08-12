"""
🧪 TEST ANALYTICS MANAGER - FASE 1.1
=====================================

Test unitario para AnalyticsManager - SÓTANO 1
Valida la arquitectura core y PerformanceTracker

Autor: Sistema Modular Trading Grid
Fecha: 2025-08-10
Protocolo: SÓTANO 1 - FASE 1.1
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

# Imports del sistema
from src.core.analytics_manager import (
    AnalyticsManager, 
    PerformanceTracker, 
    PerformanceMetrics,
    create_analytics_manager,
    validate_analytics_integration
)
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager


class TestAnalyticsManagerFase11(unittest.TestCase):
    """Test suite para FASE 1.1 - Arquitectura Core"""
    
    def setUp(self):
        """Setup para cada test"""
        # Crear mocks de dependencias
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.is_initialized = True
        
        self.logger_manager = Mock(spec=LoggerManager)
        self.logger_manager.log_info = Mock()
        self.logger_manager.log_success = Mock()
        self.logger_manager.log_error = Mock()
        self.logger_manager.log_warning = Mock()
        
        self.error_manager = Mock(spec=ErrorManager)
        self.error_manager.is_initialized = True
        self.error_manager.handle_system_error = Mock()
        
        self.data_manager = Mock(spec=DataManager)
        self.data_manager.is_initialized = True
        
        # Crear instancia de AnalyticsManager
        self.analytics_manager = AnalyticsManager(
            self.config_manager,
            self.logger_manager, 
            self.error_manager,
            self.data_manager
        )
    
    def test_01_analytics_manager_initialization(self):
        """Test: Inicialización correcta del AnalyticsManager"""
        print("\n🧪 TEST 1.1.1: Inicialización AnalyticsManager")
        
        # Verificar estado inicial
        self.assertFalse(self.analytics_manager.is_initialized)
        self.assertFalse(self.analytics_manager.analytics_active)
        self.assertIsNotNone(self.analytics_manager.performance_tracker)
        
        # Verificar que se guardaron las dependencias
        self.assertEqual(self.analytics_manager.config, self.config_manager)
        self.assertEqual(self.analytics_manager.logger, self.logger_manager)
        self.assertEqual(self.analytics_manager.error_manager, self.error_manager)
        self.assertEqual(self.analytics_manager.data_manager, self.data_manager)
        
        print("✅ AnalyticsManager inicializado correctamente")
    
    def test_02_performance_tracker_initialization(self):
        """Test: Inicialización correcta del PerformanceTracker"""
        print("\n🧪 TEST 1.1.2: Inicialización PerformanceTracker")
        
        tracker = self.analytics_manager.performance_tracker
        
        # Verificar estado inicial
        self.assertIsNotNone(tracker.current_metrics)
        self.assertEqual(len(tracker.metrics_history), 0)
        self.assertEqual(tracker.current_metrics.total_trades, 0)
        self.assertEqual(tracker.current_metrics.win_rate, 0.0)
        
        print("✅ PerformanceTracker inicializado correctamente")
    
    def test_03_analytics_manager_initialization_process(self):
        """Test: Proceso de inicialización del sistema"""
        print("\n🧪 TEST 1.1.3: Proceso de inicialización")
        
        # Test inicialización exitosa
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            result = self.analytics_manager.initialize()
            
            self.assertTrue(result)
            self.assertTrue(self.analytics_manager.is_initialized)
            self.assertTrue(self.analytics_manager.analytics_active)
            mock_mkdir.assert_called_once_with(exist_ok=True)
        
        print("✅ Inicialización completada correctamente")
    
    def test_04_performance_metrics_update(self):
        """Test: Actualización de métricas de performance"""
        print("\n🧪 TEST 1.1.4: Actualización de métricas")
        
        self.analytics_manager.initialize()
        tracker = self.analytics_manager.performance_tracker
        
        # Simular trade ganador
        trade_data_win = {"profit": 150.0, "symbol": "EURUSD"}
        tracker.update_trade_metrics(trade_data_win)
        
        metrics = tracker.get_current_metrics()
        self.assertEqual(metrics.total_trades, 1)
        self.assertEqual(metrics.winning_trades, 1)
        self.assertEqual(metrics.total_profit, 150.0)
        self.assertEqual(metrics.win_rate, 100.0)
        
        # Simular trade perdedor
        trade_data_loss = {"profit": -75.0, "symbol": "EURUSD"}
        tracker.update_trade_metrics(trade_data_loss)
        
        metrics = tracker.get_current_metrics()
        self.assertEqual(metrics.total_trades, 2)
        self.assertEqual(metrics.losing_trades, 1)
        self.assertEqual(metrics.total_loss, 75.0)
        self.assertEqual(metrics.win_rate, 50.0)
        self.assertEqual(metrics.net_profit, 75.0)
        
        print("✅ Métricas actualizadas correctamente")
    
    def test_05_performance_summary_generation(self):
        """Test: Generación de resumen de performance"""
        print("\n🧪 TEST 1.1.5: Generación de resumen")
        
        self.analytics_manager.initialize()
        
        # Agregar algunos trades
        trades = [
            {"profit": 100.0},
            {"profit": -50.0},
            {"profit": 75.0},
            {"profit": -25.0}
        ]
        
        for trade in trades:
            self.analytics_manager.update_trade_performance(trade)
        
        # Obtener resumen
        summary = self.analytics_manager.get_performance_summary()
        
        self.assertIn("total_trades", summary)
        self.assertIn("win_rate", summary)
        self.assertIn("net_profit", summary)
        self.assertIn("profit_factor", summary)
        self.assertEqual(summary["total_trades"], 4)
        self.assertEqual(summary["win_rate"], 50.0)
        self.assertEqual(summary["net_profit"], 100.0)
        
        print("✅ Resumen generado correctamente")
    
    def test_06_system_status_reporting(self):
        """Test: Reporte de estado del sistema"""
        print("\n🧪 TEST 1.1.6: Estado del sistema")
        
        # Estado antes de inicializar
        status = self.analytics_manager.get_system_status()
        self.assertFalse(status["initialized"])
        self.assertFalse(status["active"])
        self.assertTrue(status["performance_tracker"])
        self.assertEqual(status["version"], "1.3.0")  # Actualizada a versión actual
        self.assertEqual(status["phase"], "FASE_1.3_MARKET_ANALYTICS")  # Actualizada a fase actual
        
        # Estado después de inicializar
        self.analytics_manager.initialize()
        status = self.analytics_manager.get_system_status()
        self.assertTrue(status["initialized"])
        self.assertTrue(status["active"])
        
        print("✅ Estado del sistema reportado correctamente")
    
    def test_07_snapshot_functionality(self):
        """Test: Funcionalidad de snapshots"""
        print("\n🧪 TEST 1.1.7: Funcionalidad de snapshots")
        
        self.analytics_manager.initialize()
        tracker = self.analytics_manager.performance_tracker
        
        # Agregar datos
        tracker.update_trade_metrics({"profit": 100.0})
        
        # Verificar snapshot inicial
        initial_history_len = len(tracker.metrics_history)
        
        # Guardar snapshot
        tracker.save_snapshot()
        
        # Verificar que se guardó el snapshot
        self.assertEqual(len(tracker.metrics_history), initial_history_len + 1)
        
        # Verificar snapshot a nivel de analytics manager
        result = self.analytics_manager.save_analytics_snapshot()
        self.assertTrue(result)
        
        print("✅ Snapshots funcionando correctamente")
    
    def test_08_factory_functions(self):
        """Test: Funciones factory y utilidades"""
        print("\n🧪 TEST 1.1.8: Funciones factory")
        
        # Test create_analytics_manager
        analytics = create_analytics_manager(
            self.config_manager,
            self.logger_manager,
            self.error_manager,
            self.data_manager
        )
        
        self.assertIsInstance(analytics, AnalyticsManager)
        
        # Test validate_analytics_integration antes de inicializar
        result = validate_analytics_integration(analytics)
        self.assertFalse(result)
        
        # Test después de inicializar
        analytics.initialize()
        result = validate_analytics_integration(analytics)
        self.assertTrue(result)
        
        print("✅ Funciones factory validadas correctamente")
    
    def test_09_error_handling(self):
        """Test: Manejo de errores"""
        print("\n🧪 TEST 1.1.9: Manejo de errores")
        
        # Test con dependencias no inicializadas
        self.data_manager.is_initialized = False
        
        result = self.analytics_manager.initialize()
        self.assertFalse(result)
        
        # Verificar que se llamó al error manager
        self.error_manager.handle_system_error.assert_called()
        
        # Restaurar para pruebas posteriores
        self.data_manager.is_initialized = True
        
        print("✅ Manejo de errores validado")
    
    def test_10_shutdown_process(self):
        """Test: Proceso de cierre limpio"""
        print("\n🧪 TEST 1.1.10: Proceso de shutdown")
        
        # Inicializar y agregar datos
        self.analytics_manager.initialize()
        self.analytics_manager.update_trade_performance({"profit": 50.0})
        
        # Verificar estado activo
        self.assertTrue(self.analytics_manager.analytics_active)
        
        # Ejecutar shutdown
        self.analytics_manager.shutdown()
        
        # Verificar estado después del shutdown
        self.assertFalse(self.analytics_manager.analytics_active)
        
        print("✅ Shutdown ejecutado correctamente")
    

def ejecutar_tests_fase_11():
    """Ejecuta todos los tests de FASE 1.1"""
    print("=" * 60)
    print("🧪 EJECUTANDO TESTS - SÓTANO 1 FASE 1.1")
    print("ANALYTICS MANAGER - ARQUITECTURA CORE")
    print("=" * 60)
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalyticsManagerFase11)
    
    # Configurar runner con verbosidad
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    
    # Ejecutar tests
    result = runner.run(suite)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS FASE 1.1")
    print("=" * 60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("✅ TODOS LOS TESTS PASARON - FASE 1.1 COMPLETADA")
        print("\n🎯 LISTOS PARA FASE 1.2: GRID ANALYTICS")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        if result.errors:
            print("\nErrores encontrados:")
            for test, error in result.errors:
                print(f"- {test}: {error}")
        if result.failures:
            print("\nFallos encontrados:")
            for test, failure in result.failures:
                print(f"- {test}: {failure}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    ejecutar_tests_fase_11()
