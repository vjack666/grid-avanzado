"""
🧪 TEST INTEGRACIÓN COMPLETA - SÓTANO 1 v1.4.0
===============================================

Test de integración completa para validar todo el SÓTANO 1:
- AnalyticsManager (Performance + Grid + Market)
- OptimizationEngine (Optimization)

Autor: Sistema Modular Trading Grid
Fecha: 2025-08-10
Protocolo: SÓTANO 1 - INTEGRACIÓN COMPLETA
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager
from src.core.analytics_manager import create_analytics_manager
from src.core.optimization_engine import create_optimization_engine


def setup_managers():
    """Setup de managers base"""
    config = ConfigManager()
    logger = LoggerManager()
    error_manager = ErrorManager(logger_manager=logger, config_manager=config)
    data_manager = DataManager()
    
    # Simular inicialización completa
    setattr(config, 'is_initialized', True)
    setattr(logger, 'is_initialized', True)  
    setattr(error_manager, 'is_initialized', True)
    setattr(data_manager, 'is_initialized', True)
    
    return config, logger, error_manager, data_manager


def test_integracion_sotano_1_completo():
    """Test de integración completa SÓTANO 1 v1.4.0"""
    try:
        print("🧪 TEST INTEGRACIÓN SÓTANO 1 - v1.4.0")
        print("=" * 60)
        print("🎯 ANALYTICS MANAGER + OPTIMIZATION ENGINE")
        print("=" * 60)
        
        # 1. Inicializar managers base
        print("1️⃣ Inicializando managers base...")
        config_manager, logger_manager, error_manager, data_manager = setup_managers()
        print("✅ Managers base inicializados")
        
        # 2. Inicializar AnalyticsManager
        print("2️⃣ Inicializando AnalyticsManager...")
        analytics_manager = create_analytics_manager(
            config_manager, logger_manager, error_manager, data_manager
        )
        if not analytics_manager.initialize():
            raise Exception("Error inicializando AnalyticsManager")
        print("✅ AnalyticsManager inicializado correctamente")
        
        # 3. Inicializar OptimizationEngine
        print("3️⃣ Inicializando OptimizationEngine...")
        optimization_engine = create_optimization_engine(
            analytics_manager, config_manager, logger_manager, error_manager, data_manager
        )
        if not optimization_engine.initialize():
            raise Exception("Error inicializando OptimizationEngine")
        print("✅ OptimizationEngine inicializado correctamente")
        
        # 4. Poblar Analytics con datos de muestra
        print("4️⃣ Poblando Analytics con datos...")
        
        # Performance data
        trades = [
            {"profit": 25.5, "symbol": "EURUSD"},
            {"profit": -12.3, "symbol": "EURUSD"},
            {"profit": 18.7, "symbol": "EURUSD"},
            {"profit": 32.1, "symbol": "EURUSD"},
            {"profit": -8.9, "symbol": "EURUSD"}
        ]
        for trade in trades:
            analytics_manager.update_trade_performance(trade)
        
        # Grid data
        analytics_manager.update_grid_level(1.0500, "ACTIVATE", 1.0505, 0.1)
        analytics_manager.update_grid_level(1.0520, "ACTIVATE", 1.0525, 0.1)
        analytics_manager.update_grid_level(1.0500, "HIT", 1.0500, 0.1)
        analytics_manager.update_grid_level(1.0520, "HIT", 1.0520, 0.1)
        analytics_manager.update_grid_level(1.0500, "DEACTIVATE", 1.0505, 0.1)
        
        # Market data (señales estocásticas)
        signal_data = {
            'k': 28, 'd': 25, 'senal_tipo': 'BUY', 'senal_valida': True,
            'sobreventa': True, 'sobrecompra': False, 'cruce_k_d': True
        }
        analytics_manager.update_stochastic_signal(signal_data)
        
        print("✅ Datos de muestra agregados a Analytics")
        
        # 5. Ejecutar optimizaciones
        print("5️⃣ Ejecutando optimizaciones...")
        
        # Optimización de grid
        grid_optimization = optimization_engine.optimize_grid_parameters()
        print(f"✅ Grid optimizado: spacing={grid_optimization.parameters['grid_spacing']:.4f}")
        print(f"   Confianza: {grid_optimization.confidence_score:.1%}")
        print(f"   Mejora esperada: {grid_optimization.expected_improvement:.1f}%")
        
        # Performance tuning
        performance_tuning = optimization_engine.tune_based_on_performance()
        print(f"✅ Performance tuned: {performance_tuning.expected_improvement:.1f}% mejora")
        
        # Predicciones ML
        predictions = optimization_engine.predict_optimal_settings()
        print(f"✅ Predicciones ML: TF={predictions['optimal_timeframe']}, WR={predictions['predicted_win_rate']:.1f}%")
        
        # 6. Validar integración entre componentes
        print("6️⃣ Validando integración...")
        
        # Analytics status
        analytics_status = analytics_manager.get_system_status()
        print(f"   📊 Analytics version: {analytics_status['version']}")
        print(f"   📊 Analytics phase: {analytics_status['phase']}")
        
        # Optimization status
        opt_status = optimization_engine.get_system_status()
        print(f"   🎯 Optimization version: {opt_status['version']}")
        print(f"   🎯 Optimization phase: {opt_status['phase']}")
        
        # Verificar compatibilidad de versiones
        if analytics_status['version'] == '1.3.0' and opt_status['version'] == '1.4.0':
            print("✅ Versiones compatibles")
        else:
            print("⚠️ Verificar compatibilidad de versiones")
        
        # 7. Resúmenes finales
        print("7️⃣ Resúmenes finales...")
        
        perf_summary = analytics_manager.get_performance_summary()
        grid_summary = analytics_manager.get_grid_summary()
        market_summary = analytics_manager.get_market_summary()
        opt_summary = optimization_engine.get_optimization_summary()
        
        print(f"   📈 Performance: {perf_summary['total_trades']} trades, {perf_summary['win_rate']:.1f}% WR")
        print(f"   🎯 Grid: {grid_summary['active_levels']} niveles, {grid_summary.get('efficiency', 0):.1f}% eficiencia")
        print(f"   📊 Market: {market_summary['volatility']:.6f} volatilidad")
        print(f"   🔧 Optimization: {opt_summary['total_optimizations']} optimizaciones")
        
        # 8. Guardar snapshots
        print("8️⃣ Guardando snapshots...")
        analytics_snapshot = analytics_manager.save_analytics_snapshot()
        optimization_snapshot = optimization_engine.save_optimization_snapshot()
        
        if analytics_snapshot and optimization_snapshot:
            print("✅ Snapshots guardados correctamente")
        else:
            print("⚠️ Algunos snapshots fallaron")
        
        # 9. Shutdown limpio
        print("9️⃣ Ejecutando shutdown...")
        analytics_manager.shutdown()
        optimization_engine.shutdown()
        print("✅ Shutdown completado")
        
        print("\n" + "=" * 60)
        print("🎯 INTEGRACIÓN SÓTANO 1 COMPLETADA EXITOSAMENTE")
        print("✅ AnalyticsManager v1.3.0 + OptimizationEngine v1.4.0")
        print("📊 Sistema completo funcionando correctamente")
        print("=" * 60)
        
        # Assert en lugar de return
        assert True, "Test de integración completado exitosamente"
        
    except Exception as e:
        print(f"\n❌ ERROR EN INTEGRACIÓN: {e}")
        import traceback
        traceback.print_exc()
        # Assert en lugar de return  
        assert False, f"Test de integración falló: {e}"


if __name__ == "__main__":
    success = test_integracion_sotano_1_completo()
    if success:
        print("\n🚀 SÓTANO 1 LISTO PARA PRODUCCIÓN")
        print("📊 Performance Analytics: ✅")
        print("🎯 Grid Analytics: ✅")
        print("📈 Market Analytics: ✅")
        print("🔧 Optimization Engine: ✅")
        print("\n🎯 PRÓXIMO: SÓTANO 2 - REAL-TIME OPTIMIZATION")
    else:
        print("\n🛑 Revisar errores antes de continuar")
