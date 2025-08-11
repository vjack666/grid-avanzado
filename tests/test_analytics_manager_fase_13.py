"""
🧪 TEST ANALYTICS MANAGER - FASE 1.3
=====================================

Test unitario para AnalyticsManager - SÓTANO 1 FASE 1.3
Valida MarketAnalytics y análisis estocástico para primera orden

Autor: Sistema Modular Trading Grid
Fecha: 2025-08-10
Protocolo: SÓTANO 1 - FASE 1.3
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
    MarketAnalytics,
    MarketMetrics,
    create_analytics_manager,
    validate_analytics_integration
)
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager


class TestAnalyticsManagerFase13(unittest.TestCase):
    """Test suite para FASE 1.3 - Market Analytics"""
    
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
        
        # Mock para get_ohlc_data que simula datos de mercado
        import pandas as pd
        mock_ohlc = pd.DataFrame({
            'open': [1.0500, 1.0510, 1.0505, 1.0515, 1.0520],
            'high': [1.0515, 1.0520, 1.0518, 1.0525, 1.0530],
            'low': [1.0495, 1.0505, 1.0500, 1.0510, 1.0515],
            'close': [1.0510, 1.0505, 1.0515, 1.0520, 1.0525]
        })
        self.data_manager.get_ohlc_data.return_value = mock_ohlc
        
        # Crear instancia de AnalyticsManager
        self.analytics_manager = AnalyticsManager(
            self.config_manager,
            self.logger_manager, 
            self.error_manager,
            self.data_manager
        )
        
        # Inicializar para tests
        self.analytics_manager.initialize()
    
    def test_01_market_analytics_initialization(self):
        """Test: Inicialización correcta del MarketAnalytics"""
        print("\n🧪 TEST 1.3.1: Inicialización MarketAnalytics")
        
        market_analytics = self.analytics_manager.market_analytics
        
        # Verificar inicialización
        self.assertIsNotNone(market_analytics)
        self.assertEqual(len(market_analytics.market_history), 0)
        self.assertEqual(len(market_analytics.stochastic_signals), 0)
        self.assertIsNotNone(market_analytics.current_market_metrics)
        
        print("✅ MarketAnalytics inicializado correctamente")
    
    def test_02_stochastic_signal_processing(self):
        """Test: Procesamiento de señales estocásticas"""
        print("\n🧪 TEST 1.3.2: Señales estocásticas")
        
        # Simular señal estocástica de COMPRA en sobreventa
        signal_data = {
            'k': 15.5,
            'd': 12.8,
            'senal_tipo': 'BUY',
            'senal_valida': True,
            'sobreventa': True,
            'sobrecompra': False,
            'cruce_k_d': True
        }
        
        self.analytics_manager.update_stochastic_signal(signal_data)
        
        # Verificar que se procesó la señal
        stochastic_report = self.analytics_manager.get_stochastic_report()
        self.assertEqual(stochastic_report["total_recent_signals"], 1)
        self.assertEqual(stochastic_report["buy_signals"], 1)
        self.assertEqual(stochastic_report["market_phase"], "OVERSOLD")
        
        print("✅ Señal estocástica de compra procesada correctamente")
    
    def test_03_stochastic_signal_sell(self):
        """Test: Señal estocástica de venta"""
        print("\n🧪 TEST 1.3.3: Señal estocástica SELL")
        
        # Simular señal estocástica de VENTA en sobrecompra
        signal_data = {
            'k': 88.5,
            'd': 85.2,
            'senal_tipo': 'SELL',
            'senal_valida': True,
            'sobreventa': False,
            'sobrecompra': True,
            'cruce_k_d': False
        }
        
        self.analytics_manager.update_stochastic_signal(signal_data)
        
        # Verificar procesamiento
        stochastic_report = self.analytics_manager.get_stochastic_report()
        self.assertEqual(stochastic_report["sell_signals"], 1)
        self.assertEqual(stochastic_report["market_phase"], "OVERBOUGHT")
        self.assertGreater(stochastic_report["signal_strength"], 0)
        
        print("✅ Señal estocástica de venta procesada correctamente")
    
    def test_04_market_volatility_analysis(self):
        """Test: Análisis de volatilidad del mercado"""
        print("\n🧪 TEST 1.3.4: Análisis de volatilidad")
        
        # Forzar análisis de volatilidad
        self.analytics_manager.market_analytics.update_volatility_analysis()
        
        # Obtener resumen del mercado
        market_summary = self.analytics_manager.get_market_summary()
        
        # Verificar que se calculó volatilidad
        self.assertIn("volatility", market_summary)
        self.assertGreaterEqual(market_summary["volatility"], 0)
        
        print(f"✅ Volatilidad calculada: {market_summary['volatility']:.6f}")
    
    def test_05_trend_analysis(self):
        """Test: Análisis de tendencia"""
        print("\n🧪 TEST 1.3.5: Análisis de tendencia")
        
        # Forzar análisis de tendencia
        self.analytics_manager.market_analytics.update_trend_analysis()
        
        # Obtener resumen
        market_summary = self.analytics_manager.get_market_summary()
        
        # Verificar cálculo de tendencia
        self.assertIn("trend_strength", market_summary)
        self.assertGreaterEqual(market_summary["trend_strength"], 0)
        
        print(f"✅ Fuerza de tendencia: {market_summary['trend_strength']:.2f}%")
    
    def test_06_market_grid_correlation(self):
        """Test: Correlación mercado-grid"""
        print("\n🧪 TEST 1.3.6: Correlación mercado-grid")
        
        # Simular datos del grid
        grid_efficiency = 75.5
        grid_hit_rate = 85.2
        
        # Actualizar correlación
        self.analytics_manager.update_market_grid_correlation(grid_efficiency, grid_hit_rate)
        
        # Verificar correlación
        market_summary = self.analytics_manager.get_market_summary()
        self.assertIn("correlation_with_grid", market_summary)
        self.assertIn("market_efficiency", market_summary)
        
        print(f"✅ Correlación: {market_summary['correlation_with_grid']:.2f}%")
        print(f"✅ Eficiencia de mercado: {market_summary['market_efficiency']:.2f}%")
    
    def test_07_market_conditions_report(self):
        """Test: Reporte completo de condiciones del mercado"""
        print("\n🧪 TEST 1.3.7: Reporte de condiciones")
        
        # Agregar datos de muestra
        signal_data = {
            'k': 45.5,
            'd': 42.8,
            'senal_tipo': None,
            'senal_valida': False,
            'sobreventa': False,
            'sobrecompra': False,
            'cruce_k_d': False
        }
        
        self.analytics_manager.update_stochastic_signal(signal_data)
        
        # Obtener reporte completo
        conditions_report = self.analytics_manager.get_market_conditions_report()
        
        # Verificar estructura del reporte
        self.assertIn("volatility", conditions_report)
        self.assertIn("trend", conditions_report)
        self.assertIn("stochastic", conditions_report)
        self.assertIn("grid_optimization", conditions_report)
        
        # Verificar subsecciones
        self.assertIn("level", conditions_report["volatility"])
        self.assertIn("direction", conditions_report["trend"])
        self.assertIn("k_value", conditions_report["stochastic"])
        self.assertIn("optimal_conditions", conditions_report["grid_optimization"])
        
        print("✅ Reporte de condiciones generado correctamente")
    
    def test_08_multiple_signals_tracking(self):
        """Test: Tracking de múltiples señales"""
        print("\n🧪 TEST 1.3.8: Múltiples señales")
        
        # Simular secuencia de señales
        signals_sequence = [
            {'k': 85, 'd': 82, 'senal_tipo': 'SELL', 'senal_valida': True, 'sobrecompra': True},
            {'k': 75, 'd': 78, 'senal_tipo': None, 'senal_valida': False, 'sobrecompra': False},
            {'k': 25, 'd': 28, 'senal_tipo': None, 'senal_valida': False, 'sobreventa': False},
            {'k': 15, 'd': 18, 'senal_tipo': 'BUY', 'senal_valida': True, 'sobreventa': True}
        ]
        
        for signal in signals_sequence:
            signal.update({'sobreventa': signal.get('sobreventa', False),
                          'sobrecompra': signal.get('sobrecompra', False),
                          'cruce_k_d': True})
            self.analytics_manager.update_stochastic_signal(signal)
        
        # Verificar tracking
        stochastic_report = self.analytics_manager.get_stochastic_report()
        self.assertEqual(stochastic_report["total_recent_signals"], 4)
        self.assertEqual(stochastic_report["buy_signals"], 1)
        self.assertEqual(stochastic_report["sell_signals"], 1)
        
        print("✅ Múltiples señales trackeadas correctamente")
    
    def test_09_market_snapshot_functionality(self):
        """Test: Funcionalidad de snapshots del mercado"""
        print("\n🧪 TEST 1.3.9: Snapshots del mercado")
        
        market_analytics = self.analytics_manager.market_analytics
        
        # Agregar datos al mercado
        signal_data = {
            'k': 55, 'd': 52, 'senal_tipo': None, 'senal_valida': False,
            'sobreventa': False, 'sobrecompra': False, 'cruce_k_d': False
        }
        self.analytics_manager.update_stochastic_signal(signal_data)
        
        # Verificar historial inicial
        initial_history_len = len(market_analytics.market_history)
        
        # Guardar snapshot
        market_analytics.save_market_snapshot()
        
        # Verificar que se guardó
        self.assertEqual(len(market_analytics.market_history), initial_history_len + 1)
        
        # Verificar snapshot completo
        result = self.analytics_manager.save_analytics_snapshot()
        self.assertTrue(result)
        
        print("✅ Snapshots del mercado funcionando correctamente")
    
    def test_10_integrated_analytics_with_market(self):
        """Test: Analytics integrado completo (Performance + Grid + Market)"""
        print("\n🧪 TEST 1.3.10: Analytics integrado completo")
        
        # 1. Agregar datos de performance
        trades = [
            {"profit": 18.5, "symbol": "EURUSD"},
            {"profit": -9.2, "symbol": "EURUSD"}
        ]
        for trade in trades:
            self.analytics_manager.update_trade_performance(trade)
        
        # 2. Agregar datos de grid
        self.analytics_manager.update_grid_level(1.0500, "ACTIVATE", 1.0505, 0.1)
        self.analytics_manager.update_grid_level(1.0500, "HIT", 1.0500, 0.1)
        
        # 3. Agregar datos de mercado (señal estocástica)
        signal_data = {
            'k': 25, 'd': 22, 'senal_tipo': 'BUY', 'senal_valida': True,
            'sobreventa': True, 'sobrecompra': False, 'cruce_k_d': True
        }
        self.analytics_manager.update_stochastic_signal(signal_data)
        
        # 4. Obtener todos los resúmenes
        perf_summary = self.analytics_manager.get_performance_summary()
        grid_summary = self.analytics_manager.get_grid_summary()
        market_summary = self.analytics_manager.get_market_summary()
        stochastic_report = self.analytics_manager.get_stochastic_report()
        
        # 5. Verificar integración
        self.assertEqual(perf_summary["total_trades"], 2)
        self.assertEqual(grid_summary["active_levels"], 1)
        self.assertEqual(stochastic_report["buy_signals"], 1)
        self.assertGreaterEqual(market_summary["volatility"], 0)
        
        # 6. Verificar estado del sistema actualizado
        status = self.analytics_manager.get_system_status()
        self.assertTrue(status["market_analytics"])
        self.assertEqual(status["version"], "1.3.0")
        self.assertEqual(status["phase"], "FASE_1.3_MARKET_ANALYTICS")
        
        print("✅ Sistema integrado completo funcionando")
        print(f"   📊 Performance: {perf_summary['total_trades']} trades")
        print(f"   🎯 Grid: {grid_summary['active_levels']} niveles activos")
        print(f"   📈 Market: {stochastic_report['buy_signals']} señales BUY")


def ejecutar_tests_fase_13():
    """Ejecuta todos los tests de FASE 1.3"""
    print("=" * 60)
    print("🧪 EJECUTANDO TESTS - SÓTANO 1 FASE 1.3")
    print("ANALYTICS MANAGER - MARKET ANALYTICS")
    print("=" * 60)
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalyticsManagerFase13)
    
    # Configurar runner con verbosidad
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    
    # Ejecutar tests
    result = runner.run(suite)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS FASE 1.3")
    print("=" * 60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("✅ TODOS LOS TESTS PASARON - FASE 1.3 COMPLETADA")
        print("\n🎯 LISTOS PARA FASE 1.4: OPTIMIZATION ENGINE")
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
    ejecutar_tests_fase_13()
