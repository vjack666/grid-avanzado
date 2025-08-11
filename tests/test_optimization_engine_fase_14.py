"""
🧪 TEST OPTIMIZATION ENGINE - FASE 1.4
=======================================

Test unitario para OptimizationEngine - SÓTANO 1 FASE 1.4
Valida motor de optimización automática de parámetros grid

Autor: Sistema Modular Trading Grid
Fecha: 2025-08-10
Protocolo: SÓTANO 1 - FASE 1.4
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

# Imports del sistema
from src.core.optimization_engine import (
    OptimizationEngine, 
    AutoGridOptimizer,
    ParameterTuner,
    MLBasicEngine,
    BacktestValidator,
    OptimizationResult,
    create_optimization_engine,
    validate_optimization_integration
)
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager
from src.core.analytics_manager import AnalyticsManager


class TestOptimizationEngineFase14(unittest.TestCase):
    """Test suite para FASE 1.4 - Optimization Engine"""
    
    def setUp(self):
        """Setup para cada test"""
        # Crear mocks de dependencias
        self.config_manager = Mock(spec=ConfigManager)
        
        self.logger_manager = Mock(spec=LoggerManager)
        self.logger_manager.log_info = Mock()
        self.logger_manager.log_success = Mock()
        self.logger_manager.log_error = Mock()
        self.logger_manager.log_warning = Mock()
        
        self.error_manager = Mock(spec=ErrorManager)
        self.error_manager.handle_system_error = Mock()
        
        self.data_manager = Mock(spec=DataManager)
        self.data_manager.is_initialized = True
        
        # Mock Analytics Manager con datos de muestra
        self.analytics_manager = Mock(spec=AnalyticsManager)
        self.analytics_manager.is_initialized = True
        
        # Mock datos de performance
        self.analytics_manager.get_performance_summary.return_value = {
            'total_trades': 50,
            'win_rate': 65.0,
            'profit_factor': 1.45,
            'net_profit': 150.25,
            'max_drawdown': 5.5
        }
        
        # Mock datos de grid
        self.analytics_manager.get_grid_summary.return_value = {
            'active_levels': 8,
            'completed_cycles': 5,
            'efficiency': 72.5,
            'hit_rate': 85.0
        }
        
        # Mock datos de mercado
        self.analytics_manager.get_market_summary.return_value = {
            'volatility': 0.0015,
            'trend_strength': 35.0,
            'correlation_with_grid': 68.5
        }
        
        # Crear instancia de OptimizationEngine
        self.optimization_engine = OptimizationEngine(
            self.analytics_manager,
            self.config_manager,
            self.logger_manager, 
            self.error_manager,
            self.data_manager
        )
        
        # Inicializar para tests
        self.optimization_engine.initialize()
    
    def test_01_optimization_engine_initialization(self):
        """Test: Inicialización correcta del OptimizationEngine"""
        print("\n🧪 TEST 1.4.1: Inicialización OptimizationEngine")
        
        # Verificar inicialización
        self.assertTrue(self.optimization_engine.is_initialized)
        
        # Verificar subcomponentes
        self.assertIsNotNone(self.optimization_engine.auto_grid_optimizer)
        self.assertIsNotNone(self.optimization_engine.parameter_tuner)
        self.assertIsNotNone(self.optimization_engine.ml_engine)
        self.assertIsNotNone(self.optimization_engine.backtest_validator)
        
        # Verificar estado inicial
        self.assertEqual(len(self.optimization_engine.optimization_results), 0)
        self.assertIsNone(self.optimization_engine.last_optimization)
        
        print("✅ OptimizationEngine inicializado correctamente")
    
    def test_02_auto_grid_optimizer(self):
        """Test: AutoGridOptimizer funcionamiento"""
        print("\n🧪 TEST 1.4.2: AutoGridOptimizer")
        
        optimizer = self.optimization_engine.auto_grid_optimizer
        
        # Test optimización de spacing
        grid_data = {'efficiency': 75.0}
        market_data = {'volatility': 0.002}
        
        optimal_spacing = optimizer.optimize_grid_spacing(grid_data, market_data)
        
        # Verificar resultado
        self.assertIsInstance(optimal_spacing, float)
        self.assertGreaterEqual(optimal_spacing, 0.001)
        self.assertLessEqual(optimal_spacing, 0.005)
        
        # Test optimización de niveles
        performance_data = {'win_rate': 70.0}
        market_conditions = {'trend_strength': 25.0}
        
        optimal_levels = optimizer.optimize_grid_levels(performance_data, market_conditions)
        
        # Verificar resultado
        self.assertIsInstance(optimal_levels, int)
        self.assertGreaterEqual(optimal_levels, 5)
        self.assertLessEqual(optimal_levels, 20)
        
        print(f"✅ Grid spacing optimizado: {optimal_spacing:.4f}")
        print(f"✅ Niveles optimizados: {optimal_levels}")
    
    def test_03_parameter_tuner_basic(self):
        """Test: ParameterTuner funcionamiento básico"""
        print("\n🧪 TEST 1.4.3: ParameterTuner")
        
        tuner = self.optimization_engine.parameter_tuner
        
        # Test tuning de parámetros de riesgo
        performance_data = {
            'profit_factor': 1.2,
            'win_rate': 45.0,
            'max_drawdown': 12.0
        }
        
        risk_adjustments = tuner.tune_risk_parameters(performance_data)
        
        # Verificar que se generaron ajustes
        self.assertIsInstance(risk_adjustments, dict)
        self.assertIn('stop_loss_adjustment', risk_adjustments)
        self.assertIn('take_profit_adjustment', risk_adjustments)
        self.assertIn('risk_per_trade_adjustment', risk_adjustments)
        
        # Test cálculo de improvement score
        optimized_params = {'grid_spacing': 0.0025, 'grid_levels': 10}
        improvement_score = tuner.calculate_improvement_score(performance_data, optimized_params)
        
        self.assertIsInstance(improvement_score, float)
        self.assertGreaterEqual(improvement_score, 0.0)
        self.assertLessEqual(improvement_score, 25.0)
        
        print(f"✅ Risk adjustments: {len(risk_adjustments)} parámetros")
        print(f"✅ Improvement score: {improvement_score:.1f}%")
    
    def test_04_ml_basic_engine(self):
        """Test: MLBasicEngine funcionamiento"""
        print("\n🧪 TEST 1.4.4: MLBasicEngine")
        
        ml_engine = self.optimization_engine.ml_engine
        
        # Test predicción de timeframe óptimo
        market_conditions = {
            'volatility': 0.003,
            'trend_strength': 65.0
        }
        
        optimal_timeframe = ml_engine.predict_optimal_timeframe(market_conditions)
        
        # Verificar predicción
        self.assertIn(optimal_timeframe, ['M5', 'M15', 'H1', 'H4'])
        
        # Test predicción de win rate
        optimized_params = {
            'grid_spacing': 0.0025,
            'grid_levels': 12
        }
        
        predicted_wr = ml_engine.predict_win_rate(optimized_params)
        
        self.assertIsInstance(predicted_wr, float)
        self.assertGreaterEqual(predicted_wr, 30.0)
        self.assertLessEqual(predicted_wr, 80.0)
        
        # Test agregar datos de entrenamiento
        features = {'volatility': 0.002, 'trend': 30.0}
        outcome = {'win_rate': 62.0, 'profit_factor': 1.35}
        
        ml_engine.add_training_data(features, outcome)
        
        self.assertEqual(len(ml_engine.model_data), 1)
        
        print(f"✅ Timeframe óptimo predicho: {optimal_timeframe}")
        print(f"✅ Win rate predicho: {predicted_wr:.1f}%")
    
    def test_05_backtest_validator(self):
        """Test: BacktestValidator funcionamiento"""
        print("\n🧪 TEST 1.4.5: BacktestValidator")
        
        validator = self.optimization_engine.backtest_validator
        
        # Test validación de optimización
        optimized_params = {
            'grid_spacing': 0.0025,
            'grid_levels': 10,
            'volume_per_level': 0.1
        }
        
        validation_score = validator.validate_optimization(optimized_params, lookback_days=7)
        
        # Verificar validación
        self.assertIsInstance(validation_score, float)
        self.assertGreaterEqual(validation_score, 50.0)
        self.assertLessEqual(validation_score, 95.0)
        
        # Verificar que se guardó resultado
        self.assertEqual(len(validator.validation_results), 1)
        result = validator.validation_results[0]
        self.assertEqual(result['parameters'], optimized_params)
        self.assertEqual(result['score'], validation_score)
        
        print(f"✅ Validation score: {validation_score:.1f}%")
    
    def test_06_integrated_optimization(self):
        """Test: Optimización integrada completa"""
        print("\n🧪 TEST 1.4.6: Optimización integrada")
        
        # Test optimización de parámetros grid
        grid_result = self.optimization_engine.optimize_grid_parameters()
        
        # Verificar resultado
        self.assertIsInstance(grid_result, OptimizationResult)
        self.assertEqual(grid_result.optimization_type, "GRID_PARAMETERS")
        self.assertGreater(grid_result.confidence_score, 0.0)
        self.assertGreater(grid_result.expected_improvement, 0.0)
        
        # Verificar parámetros optimizados
        params = grid_result.parameters
        self.assertIn('grid_spacing', params)
        self.assertIn('grid_levels', params)
        self.assertIn('volume_per_level', params)
        
        # Verificar que se guardó en historial
        self.assertEqual(len(self.optimization_engine.optimization_results), 1)
        self.assertIsNotNone(self.optimization_engine.last_optimization)
        
        print(f"✅ Grid optimizado: spacing={params['grid_spacing']:.4f}, levels={params['grid_levels']}")
        print(f"✅ Confianza: {grid_result.confidence_score:.1%}")
        print(f"✅ Mejora esperada: {grid_result.expected_improvement:.1f}%")
    
    def test_07_performance_improvement_tracking(self):
        """Test: Tracking de mejoras de performance"""
        print("\n🧪 TEST 1.4.7: Performance improvement tracking")
        
        # Test tuning basado en performance
        tuning_result = self.optimization_engine.tune_based_on_performance()
        
        # Verificar resultado
        self.assertIsInstance(tuning_result, OptimizationResult)
        self.assertEqual(tuning_result.optimization_type, "PERFORMANCE_TUNING")
        
        # Verificar que se agregó al historial
        self.assertGreaterEqual(len(self.optimization_engine.optimization_results), 1)
        
        # Test obtener resumen de optimizaciones
        summary = self.optimization_engine.get_optimization_summary()
        
        self.assertIn('total_optimizations', summary)
        self.assertIn('average_confidence', summary)
        self.assertIn('average_improvement', summary)
        self.assertGreater(summary['total_optimizations'], 0)
        
        print(f"✅ Total optimizaciones: {summary['total_optimizations']}")
        print(f"✅ Confianza promedio: {summary['average_confidence']:.1%}")
        print(f"✅ Mejora promedio: {summary['average_improvement']:.1f}%")
    
    def test_08_optimization_persistence(self):
        """Test: Persistencia de optimizaciones"""
        print("\n🧪 TEST 1.4.8: Persistencia de optimizaciones")
        
        # Agregar varias optimizaciones
        self.optimization_engine.optimize_grid_parameters()
        self.optimization_engine.tune_based_on_performance()
        
        # Test guardar snapshot
        save_result = self.optimization_engine.save_optimization_snapshot()
        self.assertTrue(save_result)
        
        # Verificar que hay optimizaciones para guardar
        self.assertGreater(len(self.optimization_engine.optimization_results), 0)
        
        print("✅ Snapshot de optimizaciones guardado correctamente")
    
    def test_09_multiple_optimization_cycles(self):
        """Test: Múltiples ciclos de optimización"""
        print("\n🧪 TEST 1.4.9: Múltiples ciclos de optimización")
        
        initial_count = len(self.optimization_engine.optimization_results)
        
        # Ejecutar múltiples ciclos
        for i in range(3):
            grid_result = self.optimization_engine.optimize_grid_parameters()
            self.assertIsInstance(grid_result, OptimizationResult)
            
            tuning_result = self.optimization_engine.tune_based_on_performance()
            self.assertIsInstance(tuning_result, OptimizationResult)
        
        # Verificar que se agregaron todas las optimizaciones
        final_count = len(self.optimization_engine.optimization_results)
        self.assertEqual(final_count - initial_count, 6)  # 3 ciclos × 2 optimizaciones
        
        # Verificar resumen actualizado
        summary = self.optimization_engine.get_optimization_summary()
        self.assertEqual(summary['total_optimizations'], final_count)
        
        print(f"✅ {final_count} optimizaciones ejecutadas exitosamente")
    
    def test_10_complete_optimization_workflow(self):
        """Test: Workflow completo de optimización"""
        print("\n🧪 TEST 1.4.10: Workflow completo")
        
        # 1. Optimización de grid
        grid_result = self.optimization_engine.optimize_grid_parameters()
        self.assertEqual(grid_result.optimization_type, "GRID_PARAMETERS")
        
        # 2. Tuning de performance
        tuning_result = self.optimization_engine.tune_based_on_performance()
        self.assertEqual(tuning_result.optimization_type, "PERFORMANCE_TUNING")
        
        # 3. Predicciones ML
        predictions = self.optimization_engine.predict_optimal_settings()
        self.assertIn('predicted_win_rate', predictions)
        self.assertIn('optimal_timeframe', predictions)
        
        # 4. Resumen completo
        summary = self.optimization_engine.get_optimization_summary()
        self.assertGreater(summary['total_optimizations'], 0)
        
        # 5. Estado del sistema
        status = self.optimization_engine.get_system_status()
        self.assertTrue(status['optimization_engine'])
        self.assertEqual(status['version'], '1.4.0')
        self.assertEqual(status['phase'], 'FASE_1.4_OPTIMIZATION_ENGINE')
        
        # 6. Persistencia
        save_success = self.optimization_engine.save_optimization_snapshot()
        self.assertTrue(save_success)
        
        print("✅ Workflow completo ejecutado exitosamente")
        print(f"   🎯 Grid optimizado: {len(grid_result.parameters)} parámetros")
        print(f"   ⚙️ Performance tuning: {tuning_result.expected_improvement:.1f}% mejora")
        print(f"   🤖 Predicciones: {predictions['optimal_timeframe']}")
        print(f"   📊 Total optimizaciones: {summary['total_optimizations']}")


def ejecutar_tests_fase_14():
    """Ejecuta todos los tests de FASE 1.4"""
    print("=" * 60)
    print("🧪 EJECUTANDO TESTS - SÓTANO 1 FASE 1.4")
    print("OPTIMIZATION ENGINE - MOTOR DE OPTIMIZACIÓN")
    print("=" * 60)
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOptimizationEngineFase14)
    
    # Configurar runner con verbosidad
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    
    # Ejecutar tests
    result = runner.run(suite)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS FASE 1.4")
    print("=" * 60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    
    if result.wasSuccessful():
        print("✅ TODOS LOS TESTS PASARON - FASE 1.4 COMPLETADA")
        print("\n🎯 SÓTANO 1 COMPLETADO - ANALYTICS MANAGER v1.4.0")
        print("📊 Performance + Grid + Market + Optimization Analytics")
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
    ejecutar_tests_fase_14()
