"""
🧪 TEST ANALYTICS MANAGER - FASE 1.2
=====================================

Test unitario para AnalyticsManager - SÓTANO 1 FASE 1.2
Valida GridAnalytics y análisis específico del grid trading

Autor: Sistema Modular Trading Grid
Fecha: 2025-08-10
Protocolo: SÓTANO 1 - FASE 1.2
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
    GridAnalytics,
    GridMetrics,
    create_analytics_manager,
    validate_analytics_integration
)
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager


class TestAnalyticsManagerFase12(unittest.TestCase):
    """Test suite para FASE 1.2 - Grid Analytics"""
    
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
        
        # Inicializar para tests
        self.analytics_manager.initialize()
    
    def test_01_grid_analytics_initialization(self):
        """Test: Inicialización correcta del GridAnalytics"""
        print("\n🧪 TEST 1.2.1: Inicialización GridAnalytics")
        
        grid_analytics = self.analytics_manager.grid_analytics
        
        # Verificar inicialización
        self.assertIsNotNone(grid_analytics)
        self.assertEqual(len(grid_analytics.grid_history), 0)
        self.assertEqual(len(grid_analytics.active_levels), 0)
        self.assertEqual(grid_analytics.current_grid_metrics.active_levels, 0)
        
        print("✅ GridAnalytics inicializado correctamente")
    
    def test_02_grid_level_activation(self):
        """Test: Activación de niveles del grid"""
        print("\n🧪 TEST 1.2.2: Activación de niveles")
        
        # Activar algunos niveles
        levels_to_activate = [
            (1.0500, 1.0505, 0.1),
            (1.0510, 1.0515, 0.1),
            (1.0520, 1.0525, 0.1)
        ]
        
        for level, price, volume in levels_to_activate:
            self.analytics_manager.update_grid_level(level, "ACTIVATE", price, volume)
        
        # Verificar niveles activos
        grid_metrics = self.analytics_manager.grid_analytics.get_current_grid_metrics()
        self.assertEqual(grid_metrics.active_levels, 3)
        
        # Verificar que los niveles están registrados
        active_levels = self.analytics_manager.grid_analytics.active_levels
        self.assertEqual(len(active_levels), 3)
        
        print("✅ Niveles activados correctamente")
    
    def test_03_grid_level_hits(self):
        """Test: Hits en niveles del grid"""
        print("\n🧪 TEST 1.2.3: Hits en niveles")
        
        # Activar niveles primero
        self.analytics_manager.update_grid_level(1.0500, "ACTIVATE", 1.0505, 0.1)
        self.analytics_manager.update_grid_level(1.0510, "ACTIVATE", 1.0515, 0.1)
        
        # Simular hits
        hit_scenarios = [
            (1.0500, 1.0500, 0.1),
            (1.0500, 1.0501, 0.1),  # Segundo hit en el mismo nivel
            (1.0510, 1.0510, 0.1)
        ]
        
        for level, price, volume in hit_scenarios:
            self.analytics_manager.update_grid_level(level, "HIT", price, volume)
        
        # Verificar performance por nivel
        level_performance = self.analytics_manager.grid_analytics.level_performance
        self.assertIn("1.05000", level_performance)
        self.assertIn("1.05100", level_performance)
        self.assertEqual(level_performance["1.05000"]["hits"], 2)
        self.assertEqual(level_performance["1.05100"]["hits"], 1)
        
        print("✅ Hits registrados correctamente")
    
    def test_04_grid_level_deactivation_and_cycles(self):
        """Test: Desactivación de niveles y ciclos completados"""
        print("\n🧪 TEST 1.2.4: Ciclos completados")
        
        # Activar nivel
        self.analytics_manager.update_grid_level(1.0500, "ACTIVATE", 1.0505, 0.1)
        
        # Hacer algunos hits
        self.analytics_manager.update_grid_level(1.0500, "HIT", 1.0500, 0.1)
        self.analytics_manager.update_grid_level(1.0500, "HIT", 1.0501, 0.1)
        
        # Desactivar nivel
        self.analytics_manager.update_grid_level(1.0500, "DEACTIVATE", 1.0505, 0.1)
        
        # Verificar ciclo completado
        grid_analytics = self.analytics_manager.grid_analytics
        self.assertEqual(len(grid_analytics.completed_cycles), 1)
        self.assertEqual(grid_analytics.current_grid_metrics.completed_cycles, 1)
        self.assertEqual(grid_analytics.current_grid_metrics.active_levels, 0)
        
        print("✅ Ciclos completados registrados correctamente")
    
    def test_05_grid_metrics_calculation(self):
        """Test: Cálculo de métricas del grid"""
        print("\n🧪 TEST 1.2.5: Cálculo de métricas")
        
        # Crear escenario complejo
        levels = [1.0500, 1.0510, 1.0520, 1.0530]
        
        # Activar niveles
        for level in levels:
            self.analytics_manager.update_grid_level(level, "ACTIVATE", level + 0.0005, 0.1)
        
        # Hacer hits en algunos niveles
        for level in levels[:2]:  # Solo primeros 2 niveles
            self.analytics_manager.update_grid_level(level, "HIT", level, 0.1)
        
        # Completar un ciclo
        self.analytics_manager.update_grid_level(levels[0], "DEACTIVATE", levels[0], 0.1)
        
        # Obtener resumen
        summary = self.analytics_manager.get_grid_summary()
        
        self.assertEqual(summary["active_levels"], 3)  # 4 activados - 1 desactivado
        self.assertEqual(summary["completed_cycles"], 1)
        self.assertGreater(summary["grid_efficiency"], 0)
        self.assertGreater(summary["level_hit_rate"], 0)
        self.assertGreater(summary["grid_spread"], 0)
        
        print("✅ Métricas calculadas correctamente")
    
    def test_06_level_performance_report(self):
        """Test: Reporte de performance por nivel"""
        print("\n🧪 TEST 1.2.6: Reporte de performance")
        
        # Crear datos de prueba
        test_levels = [1.0500, 1.0510, 1.0520]
        
        for i, level in enumerate(test_levels):
            self.analytics_manager.update_grid_level(level, "ACTIVATE", level + 0.0005, 0.1)
            
            # Hacer diferentes números de hits
            for _ in range(i + 1):
                self.analytics_manager.update_grid_level(level, "HIT", level, 0.1)
        
        # Obtener reporte
        report = self.analytics_manager.get_level_performance_report()
        
        self.assertIn("total_levels_tracked", report)
        self.assertIn("total_hits", report)
        self.assertIn("top_performing_levels", report)
        self.assertEqual(report["total_levels_tracked"], 3)
        self.assertEqual(report["total_hits"], 6)  # 1+2+3 hits
        
        # Verificar que el nivel con más hits está primero
        top_levels = report["top_performing_levels"]
        self.assertEqual(top_levels[0]["hits"], 3)  # Nivel 1.0520 con 3 hits
        
        print("✅ Reporte de performance generado correctamente")
    
    def test_07_grid_snapshot_functionality(self):
        """Test: Funcionalidad de snapshots del grid"""
        print("\n🧪 TEST 1.2.7: Snapshots del grid")
        
        grid_analytics = self.analytics_manager.grid_analytics
        
        # Agregar datos
        self.analytics_manager.update_grid_level(1.0500, "ACTIVATE", 1.0505, 0.1)
        self.analytics_manager.update_grid_level(1.0500, "HIT", 1.0500, 0.1)
        
        # Verificar historial inicial
        initial_history_len = len(grid_analytics.grid_history)
        
        # Guardar snapshot
        grid_analytics.save_grid_snapshot()
        
        # Verificar que se guardó
        self.assertEqual(len(grid_analytics.grid_history), initial_history_len + 1)
        
        # Verificar snapshot completo
        result = self.analytics_manager.save_analytics_snapshot()
        self.assertTrue(result)
        
        print("✅ Snapshots del grid funcionando correctamente")
    
    def test_08_integrated_analytics_summary(self):
        """Test: Resumen integrado de analytics"""
        print("\n🧪 TEST 1.2.8: Resumen integrado")
        
        # Agregar datos de performance
        trades = [
            {"profit": 15.0, "symbol": "EURUSD"},
            {"profit": -8.0, "symbol": "EURUSD"},
            {"profit": 12.0, "symbol": "EURUSD"}
        ]
        
        for trade in trades:
            self.analytics_manager.update_trade_performance(trade)
        
        # Agregar datos de grid
        self.analytics_manager.update_grid_level(1.0500, "ACTIVATE", 1.0505, 0.1)
        self.analytics_manager.update_grid_level(1.0500, "HIT", 1.0500, 0.1)
        self.analytics_manager.update_grid_level(1.0510, "ACTIVATE", 1.0515, 0.1)
        
        # Obtener ambos resúmenes
        perf_summary = self.analytics_manager.get_performance_summary()
        grid_summary = self.analytics_manager.get_grid_summary()
        
        # Verificar datos de performance
        self.assertEqual(perf_summary["total_trades"], 3)
        self.assertAlmostEqual(perf_summary["win_rate"], 66.67, places=1)
        
        # Verificar datos de grid
        self.assertEqual(grid_summary["active_levels"], 2)
        self.assertGreater(grid_summary["level_hit_rate"], 0)
        
        print("✅ Resúmenes integrados funcionando correctamente")
    
    def test_09_system_status_updated(self):
        """Test: Estado del sistema actualizado para FASE 1.2"""
        print("\n🧪 TEST 1.2.9: Estado del sistema")
        
        status = self.analytics_manager.get_system_status()
        
        self.assertTrue(status["initialized"])
        self.assertTrue(status["active"])
        self.assertTrue(status["performance_tracker"])
        self.assertTrue(status["grid_analytics"])
        self.assertEqual(status["version"], "1.3.0")  # Actualizada a versión actual
        self.assertEqual(status["phase"], "FASE_1.3_MARKET_ANALYTICS")  # Actualizada a fase actual
        
        print("✅ Estado del sistema actualizado correctamente")
    
    def test_10_error_handling_grid_analytics(self):
        """Test: Manejo de errores en grid analytics"""
        print("\n🧪 TEST 1.2.10: Manejo de errores")
        
        # Test con analytics inactivo
        self.analytics_manager.analytics_active = False
        
        # Estas operaciones no deberían fallar pero tampoco hacer nada
        self.analytics_manager.update_grid_level(1.0500, "ACTIVATE", 1.0505, 0.1)
        
        summary = self.analytics_manager.get_grid_summary()
        self.assertIn("error", summary)
        
        report = self.analytics_manager.get_level_performance_report()
        self.assertIn("error", report)
        
        # Restaurar para otras pruebas
        self.analytics_manager.analytics_active = True
        
        print("✅ Manejo de errores validado")


def ejecutar_tests_fase_12():
    """Ejecuta todos los tests de FASE 1.2"""
    print("=" * 60)
    print("🧪 EJECUTANDO TESTS - SÓTANO 1 FASE 1.2")
    print("ANALYTICS MANAGER - GRID ANALYTICS")
    print("=" * 60)
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalyticsManagerFase12)
    
    # Configurar runner con verbosidad
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    
    # Ejecutar tests
    result = runner.run(suite)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS FASE 1.2")
    print("=" * 60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("✅ TODOS LOS TESTS PASARON - FASE 1.2 COMPLETADA")
        print("\n🎯 LISTOS PARA FASE 1.3: MARKET ANALYTICS")
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
    ejecutar_tests_fase_12()
