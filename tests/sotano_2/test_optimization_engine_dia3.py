"""
Test OptimizationEngine - SÓTANO 2 DÍA 3
========================================

Pruebas unitarias para el motor de optimización automática.
Valida algoritmos genéticos, optimización multi-objetivo y servicio automático.

Componente: test_optimization_engine_dia3.py
Versión: v3.1.0
"""

import unittest
import time
import threading
from datetime import datetime
from typing import Dict

# Imports del sistema
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager  
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager
from src.core.real_time.optimization_engine import OptimizationEngine, OptimizationMethod, OptimizationObjective
from src.core.real_time.performance_tracker import PerformanceTracker
from src.core.real_time.alert_engine import AlertEngine


class TestOptimizationEngine(unittest.TestCase):
    """Tests para OptimizationEngine"""
    
    def setUp(self):
        """Configurar test environment"""
        # Crear dependencias
        self.config = ConfigManager()
        self.logger = LoggerManager()
        self.error = ErrorManager()
        self.data = DataManager()
        
        # Crear dependencias SÓTANO 2  
        self.performance = PerformanceTracker(
            config=self.config,
            logger=self.logger,
            error=self.error
        )
        
        self.alerts = AlertEngine(
            config=self.config,
            logger=self.logger,
            error=self.error
        )
        
        # Crear OptimizationEngine
        self.optimizer = OptimizationEngine(
            config=self.config,
            logger=self.logger,
            error=self.error,
            data_manager=self.data,
            performance_tracker=self.performance,
            alert_engine=self.alerts
        )
    
    def tearDown(self):
        """Limpiar después de cada test"""
        if hasattr(self.optimizer, 'stop_optimization_service'):
            self.optimizer.stop_optimization_service()
    
    def test_optimizer_initialization(self):
        """Test inicialización del OptimizationEngine"""
        # Verificar metadatos del componente
        self.assertEqual(self.optimizer.component_id, "PUERTA-S2-OPTIMIZER")
        self.assertEqual(self.optimizer.version, "v3.1.0")
        self.assertEqual(self.optimizer.status, "initialized")
        
        # Verificar dependencias
        self.assertIsNotNone(self.optimizer.config)
        self.assertIsNotNone(self.optimizer.logger)
        self.assertIsNotNone(self.optimizer.error)
        self.assertIsNotNone(self.optimizer.data)
        self.assertIsNotNone(self.optimizer.performance)
        self.assertIsNotNone(self.optimizer.alerts)
        
        # Verificar configuración por defecto
        self.assertIsInstance(self.optimizer.optimizer_config, dict)
        self.assertTrue(self.optimizer.optimizer_config["enabled"])
        self.assertEqual(self.optimizer.optimizer_config["optimization_interval_hours"], 24)
        
        # Verificar parámetros optimizables
        self.assertGreater(len(self.optimizer.parameters), 0)
        self.assertIn("grid_distance", self.optimizer.parameters)
        self.assertIn("lot_size", self.optimizer.parameters)
        self.assertIn("max_levels", self.optimizer.parameters)
        
        # Verificar estado inicial
        self.assertFalse(self.optimizer.is_optimizing)
        self.assertEqual(len(self.optimizer.optimization_history), 0)
        self.assertEqual(len(self.optimizer.best_results), 0)
        
        print("✓ OptimizationEngine inicializado correctamente")
    
    def test_optimization_service_lifecycle(self):
        """Test ciclo de vida del servicio de optimización"""
        # Test start service
        success = self.optimizer.start_optimization_service()
        self.assertTrue(success)
        self.assertTrue(self.optimizer.is_optimizing)
        self.assertEqual(self.optimizer.status, "running")
        self.assertIsNotNone(self.optimizer.optimization_thread)
        
        # Esperar un momento para que el servicio se ejecute
        time.sleep(0.5)
        
        # Test stop service
        success = self.optimizer.stop_optimization_service()
        self.assertTrue(success)
        self.assertFalse(self.optimizer.is_optimizing)
        self.assertEqual(self.optimizer.status, "stopped")
        
        print("✓ Ciclo de vida del servicio funciona correctamente")
    
    def test_genetic_algorithm_optimization(self):
        """Test optimización con algoritmo genético"""
        # Ejecutar optimización genética
        result = self.optimizer.optimize_parameters(
            method=OptimizationMethod.GENETIC_ALGORITHM,
            objective=OptimizationObjective.MAXIMIZE_SHARPE
        )
        
        # Verificar resultado
        self.assertIsNotNone(result)
        assert result is not None  # Type hint para Pylance
        self.assertEqual(result.method, OptimizationMethod.GENETIC_ALGORITHM)
        self.assertEqual(result.objective, OptimizationObjective.MAXIMIZE_SHARPE)
        self.assertIsInstance(result.parameters, dict)
        self.assertGreater(len(result.parameters), 0)
        self.assertGreaterEqual(result.fitness_score, 0)
        self.assertIsInstance(result.timestamp, datetime)
        self.assertGreater(result.execution_time, 0)
        
        # Verificar que los parámetros están en rangos válidos
        for param_name, value in result.parameters.items():
            if param_name in self.optimizer.parameters:
                param_def = self.optimizer.parameters[param_name]
                self.assertGreaterEqual(value, param_def.min_value)
                self.assertLessEqual(value, param_def.max_value)
        
        # Verificar que se agregó al histórico
        self.assertEqual(len(self.optimizer.optimization_history), 1)
        self.assertIn(OptimizationObjective.MAXIMIZE_SHARPE, self.optimizer.best_results)
        
        print(f"✓ Algoritmo genético: fitness={result.fitness_score:.4f}, tiempo={result.execution_time:.2f}s")
    
    def test_multi_objective_optimization(self):
        """Test optimización multi-objetivo"""
        result = self.optimizer.optimize_parameters(
            method=OptimizationMethod.GENETIC_ALGORITHM,
            objective=OptimizationObjective.MULTI_OBJECTIVE
        )
        
        self.assertIsNotNone(result)
        assert result is not None  # Type hint para Pylance
        self.assertEqual(result.objective, OptimizationObjective.MULTI_OBJECTIVE)
        self.assertGreaterEqual(result.fitness_score, 0)
        
        # Verificar que consideró múltiples métricas
        self.assertGreaterEqual(result.sharpe_ratio, 0)
        self.assertGreaterEqual(result.max_drawdown, 0)
        self.assertGreaterEqual(result.win_rate, 0)
        self.assertGreaterEqual(result.net_profit, 0)
        
        print(f"✓ Multi-objetivo: fitness={result.fitness_score:.4f}, sharpe={result.sharpe_ratio:.2f}")
    
    def test_grid_search_optimization(self):
        """Test optimización con grid search"""
        result = self.optimizer.optimize_parameters(
            method=OptimizationMethod.GRID_SEARCH,
            objective=OptimizationObjective.MAXIMIZE_PROFIT
        )
        
        self.assertIsNotNone(result)
        assert result is not None  # Type hint para Pylance
        self.assertEqual(result.method, OptimizationMethod.GRID_SEARCH)
        self.assertEqual(result.objective, OptimizationObjective.MAXIMIZE_PROFIT)
        self.assertGreaterEqual(result.fitness_score, 0)
        
        print(f"✓ Grid search: fitness={result.fitness_score:.4f}")
    
    def test_random_search_optimization(self):
        """Test optimización con random search"""
        result = self.optimizer.optimize_parameters(
            method=OptimizationMethod.RANDOM_SEARCH,
            objective=OptimizationObjective.MINIMIZE_DRAWDOWN
        )
        
        self.assertIsNotNone(result)
        assert result is not None  # Type hint para Pylance
        self.assertEqual(result.method, OptimizationMethod.RANDOM_SEARCH)
        self.assertEqual(result.objective, OptimizationObjective.MINIMIZE_DRAWDOWN)
        self.assertGreaterEqual(result.fitness_score, 0)
        
        print(f"✓ Random search: fitness={result.fitness_score:.4f}")
    
    def test_custom_fitness_function(self):
        """Test optimización con función de fitness personalizada"""
        
        def custom_fitness(params: Dict[str, float]) -> float:
            """Función de fitness personalizada que favorece grid_distance alto"""
            return params.get("grid_distance", 0) / 100.0
        
        result = self.optimizer.optimize_parameters(
            method=OptimizationMethod.GENETIC_ALGORITHM,
            objective=OptimizationObjective.MAXIMIZE_PROFIT,  # Se ignora con custom_fitness
            custom_fitness_function=custom_fitness
        )
        
        self.assertIsNotNone(result)
        assert result is not None  # Type hint para Pylance
        self.assertGreaterEqual(result.fitness_score, 0)
        
        # Verificar que los parámetros reflejan la función personalizada
        # (grid_distance debería ser relativamente alto)
        grid_distance = result.parameters.get("grid_distance", 0)
        self.assertGreater(grid_distance, 20)  # Debería ser mayor que el mínimo
        
        print(f"✓ Fitness personalizada: grid_distance={grid_distance:.1f}")
    
    def test_parameter_application(self):
        """Test aplicación de parámetros optimizados"""
        # Obtener parámetros iniciales
        initial_params = {name: param.current_value for name, param in self.optimizer.parameters.items()}
        
        # Ejecutar optimización
        result = self.optimizer.optimize_parameters(
            method=OptimizationMethod.GENETIC_ALGORITHM,
            objective=OptimizationObjective.MAXIMIZE_SHARPE
        )
        
        self.assertIsNotNone(result)
        assert result is not None  # Type hint para Pylance
        
        # Aplicar parámetros optimizados
        self.optimizer._apply_optimized_parameters(result.parameters)
        
        # Verificar que los parámetros se actualizaron
        updated_params = {name: param.current_value for name, param in self.optimizer.parameters.items()}
        
        # Al menos algunos parámetros deberían haber cambiado
        different_params = sum(1 for name in initial_params 
                             if abs(initial_params[name] - updated_params[name]) > 0.001)
        self.assertGreater(different_params, 0)
        
        print(f"✓ Parámetros aplicados: {different_params} parámetros actualizados")
    
    def test_optimization_history_and_metrics(self):
        """Test histórico y métricas de optimización"""
        # Ejecutar varias optimizaciones
        methods = [
            OptimizationMethod.GENETIC_ALGORITHM,
            OptimizationMethod.GRID_SEARCH,
            OptimizationMethod.RANDOM_SEARCH
        ]
        
        for method in methods:
            result = self.optimizer.optimize_parameters(
                method=method,
                objective=OptimizationObjective.MAXIMIZE_SHARPE
            )
            self.assertIsNotNone(result)
        
        # Verificar histórico
        history = self.optimizer.get_optimization_history()
        self.assertEqual(len(history), 3)
        
        # Verificar métricas
        metrics = self.optimizer.optimization_metrics
        self.assertEqual(metrics["total_optimizations"], 3)
        self.assertGreaterEqual(metrics["successful_optimizations"], 0)
        self.assertGreater(metrics["best_fitness_ever"], 0)
        self.assertGreater(metrics["optimization_time_avg"], 0)
        
        # Verificar estado
        status = self.optimizer.get_optimization_status()
        self.assertEqual(status["component_id"], "PUERTA-S2-OPTIMIZER")
        self.assertEqual(status["total_optimizations"], 3)
        self.assertGreaterEqual(status["best_results_count"], 1)
        
        print(f"✓ Histórico: {len(history)} optimizaciones, métricas actualizadas")
    
    def test_best_parameters_retrieval(self):
        """Test obtención de mejores parámetros"""
        # Ejecutar optimización
        result = self.optimizer.optimize_parameters(
            method=OptimizationMethod.GENETIC_ALGORITHM,
            objective=OptimizationObjective.MAXIMIZE_SHARPE
        )
        
        self.assertIsNotNone(result)
        assert result is not None  # Type hint para Pylance
        
        # Obtener mejores parámetros para objetivo específico
        best_params = self.optimizer.get_best_parameters(OptimizationObjective.MAXIMIZE_SHARPE)
        self.assertIsInstance(best_params, dict)
        self.assertGreater(len(best_params), 0)
        
        # Deberían coincidir con el resultado de la optimización
        for param_name, value in result.parameters.items():
            self.assertAlmostEqual(best_params[param_name], value, places=6)
        
        # Obtener parámetros actuales (sin objetivo específico)
        current_params = self.optimizer.get_best_parameters()
        self.assertIsInstance(current_params, dict)
        self.assertGreater(len(current_params), 0)
        
        print("✓ Obtención de mejores parámetros funciona correctamente")
    
    def test_optimization_convergence(self):
        """Test convergencia del algoritmo genético"""
        # Configurar convergencia rápida para el test
        original_generations = self.optimizer.optimizer_config["generations"]
        original_threshold = self.optimizer.optimizer_config["convergence_threshold"]
        
        self.optimizer.optimizer_config["generations"] = 20
        self.optimizer.optimizer_config["convergence_threshold"] = 0.1
        
        try:
            result = self.optimizer.optimize_parameters(
                method=OptimizationMethod.GENETIC_ALGORITHM,
                objective=OptimizationObjective.MAXIMIZE_SHARPE
            )
            
            self.assertIsNotNone(result)
            assert result is not None  # Type hint para Pylance
            # La convergencia debería ocurrir antes de las 20 generaciones
            self.assertLessEqual(result.generation, 20)
            
            print(f"✓ Convergencia en generación {result.generation}")
            
        finally:
            # Restaurar configuración original
            self.optimizer.optimizer_config["generations"] = original_generations
            self.optimizer.optimizer_config["convergence_threshold"] = original_threshold
    
    def test_parameter_validation(self):
        """Test validación de parámetros"""
        # Verificar que todos los parámetros tienen rangos válidos
        for param in self.optimizer.parameters.values():
            self.assertLess(param.min_value, param.max_value)
            self.assertGreater(param.step, 0)
            self.assertIn(param.type, ["float", "int", "bool"])
            
            # Verificar que current_value está en rango
            self.assertGreaterEqual(param.current_value, param.min_value)
            self.assertLessEqual(param.current_value, param.max_value)
        
        print(f"✓ Validación de {len(self.optimizer.parameters)} parámetros")
    
    def test_optimization_thread_safety(self):
        """Test thread safety de las optimizaciones"""
        results = []
        exceptions = []
        
        def run_optimization():
            try:
                result = self.optimizer.optimize_parameters(
                    method=OptimizationMethod.GENETIC_ALGORITHM,
                    objective=OptimizationObjective.MAXIMIZE_SHARPE
                )
                results.append(result)
            except Exception as e:
                exceptions.append(e)
        
        # Ejecutar múltiples optimizaciones en paralelo 
        # Con el lock, deberían ejecutarse secuencialmente
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=run_optimization)
            threads.append(thread)
            thread.start()
        
        # Esperar a que terminen
        for thread in threads:
            thread.join(timeout=10.0)
        
        # Todas las optimizaciones deberían haberse ejecutado exitosamente
        # debido al lock que serializa las ejecuciones
        successful_results = [r for r in results if r is not None]
        self.assertEqual(len(successful_results), 3)  # Todas ejecutadas secuencialmente
        self.assertEqual(len(exceptions), 0)  # Sin errores
        
        print(f"✓ Thread safety: {len(successful_results)} optimizaciones ejecutadas secuencialmente")
    
    def test_error_handling(self):
        """Test manejo de errores"""
        # Test que el método no implementado devuelve None (manejado gracefully)
        result = self.optimizer.optimize_parameters(
            method=OptimizationMethod.BAYESIAN_OPTIMIZATION,  # No implementado
            objective=OptimizationObjective.MAXIMIZE_SHARPE
        )
        
        # El error se maneja gracefully y devuelve None
        self.assertIsNone(result)
        
        # Test con función de fitness que falla
        def failing_fitness(params):
            raise Exception("Test error")
        
        result = self.optimizer.optimize_parameters(
            method=OptimizationMethod.GENETIC_ALGORITHM,
            objective=OptimizationObjective.MAXIMIZE_SHARPE,
            custom_fitness_function=failing_fitness
        )
        
        # Debería manejar el error gracefully y devolver None
        self.assertIsNone(result)
        
        print("✓ Manejo de errores funciona correctamente")


def run_tests():
    """Ejecutar todos los tests"""
    print("="*60)
    print("TESTS OPTIMIZATION ENGINE - SÓTANO 2 DÍA 3")
    print("="*60)
    
    # Crear test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOptimizationEngine)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Tests exitosos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    
    if result.failures:
        print("\nFALLOS:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORES:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nEstado: {'✓ TODOS LOS TESTS PASARON' if success else '✗ HAY TESTS FALLIDOS'}")
    print("="*60)
    
    return success


if __name__ == "__main__":
    run_tests()
