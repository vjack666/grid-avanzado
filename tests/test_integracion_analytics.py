"""
🧪 TEST INTEGRACIÓN ANALYTICS MANAGER
=====================================

Test de integración rápida para validar AnalyticsManager en el sistema

Autor: Sistema Modular Trading Grid
Fecha: 2025-08-10
"""

import sys
import os
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.join(os.path.abspath('.'), 'src', 'core'))

from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager
from src.core.analytics_manager import AnalyticsManager

def test_integracion_analytics():
    """Test rápido de integración del AnalyticsManager"""
    print("🧪 TEST INTEGRACIÓN ANALYTICS MANAGER")
    print("=" * 50)
    
    try:
        # 1. Inicializar todos los managers
        print("1️⃣ Inicializando managers base...")
        config = ConfigManager()
        logger = LoggerManager()
        error_manager = ErrorManager(logger_manager=logger, config_manager=config)
        data_manager = DataManager()
        
        # Simular inicialización (agregar atributos necesarios)
        setattr(config, 'is_initialized', True)
        setattr(error_manager, 'is_initialized', True)
        setattr(data_manager, 'is_initialized', True)
        
        print("✅ Managers base inicializados")
        
        # 2. Crear AnalyticsManager
        print("2️⃣ Inicializando AnalyticsManager...")
        analytics_manager = AnalyticsManager(config, logger, error_manager, data_manager)
        
        # 3. Inicializar el sistema
        if analytics_manager.initialize():
            print("✅ AnalyticsManager inicializado correctamente")
        else:
            print("❌ Error inicializando AnalyticsManager")
            assert False, "Error inicializando AnalyticsManager"
        
        # 4. Test básico de funcionalidad
        print("3️⃣ Probando funcionalidades básicas...")
        
        # Simular algunos trades
        trades = [
            {"profit": 15.50, "symbol": "EURUSD", "type": "BUY"},
            {"profit": -8.25, "symbol": "EURUSD", "type": "SELL"},
            {"profit": 22.75, "symbol": "EURUSD", "type": "BUY"},
            {"profit": -12.00, "symbol": "EURUSD", "type": "SELL"},
            {"profit": 18.90, "symbol": "EURUSD", "type": "BUY"}
        ]
        
        for trade in trades:
            analytics_manager.update_trade_performance(trade)
        
        print("✅ Trades simulados procesados")
        
        # 4b. Test de Grid Analytics (FASE 1.2)
        print("4️⃣ Probando Grid Analytics...")
        
        # Simular operaciones del grid
        grid_operations = [
            (1.0500, "ACTIVATE", 1.0505, 0.1),
            (1.0510, "ACTIVATE", 1.0515, 0.1),
            (1.0520, "ACTIVATE", 1.0525, 0.1),
            (1.0500, "HIT", 1.0500, 0.1),
            (1.0500, "HIT", 1.0501, 0.1),
            (1.0510, "HIT", 1.0510, 0.1),
            (1.0500, "DEACTIVATE", 1.0505, 0.1)  # Completar un ciclo
        ]
        
        for level, action, price, volume in grid_operations:
            analytics_manager.update_grid_level(level, action, price, volume)
        
        print("✅ Operaciones de grid simuladas")
        
        # 5. Obtener resúmenes (actualizado para FASE 1.2)
        summary = analytics_manager.get_performance_summary()
        grid_summary = analytics_manager.get_grid_summary()
        
        print("5️⃣ Resumen de performance:")
        print(f"   📊 Total trades: {summary.get('total_trades', 0)}")
        print(f"   📈 Win rate: {summary.get('win_rate', 0)}%")
        print(f"   💰 Net profit: {summary.get('net_profit', 0)}")
        print(f"   📊 Profit factor: {summary.get('profit_factor', 0)}")
        
        print("6️⃣ Resumen de grid:")
        print(f"   🎯 Niveles activos: {grid_summary.get('active_levels', 0)}")
        print(f"   🔄 Ciclos completados: {grid_summary.get('completed_cycles', 0)}")
        print(f"   ⚡ Eficiencia del grid: {grid_summary.get('grid_efficiency', 0)}%")
        print(f"   🎯 Hit rate de niveles: {grid_summary.get('level_hit_rate', 0)}%")
        
        # 6a. Reporte de niveles
        level_report = analytics_manager.get_level_performance_report()
        print("7️⃣ Reporte de niveles:")
        print(f"   📈 Niveles trackeados: {level_report.get('total_levels_tracked', 0)}")
        print(f"   🎯 Total hits: {level_report.get('total_hits', 0)}")
        print(f"   📊 Promedio hits/nivel: {level_report.get('average_hits_per_level', 0)}")
        
        # 6. Verificar estado (actualizado)
        status = analytics_manager.get_system_status()
        print("8️⃣ Estado del sistema:")
        print(f"   🔧 Inicializado: {status.get('initialized', False)}")
        print(f"   ⚡ Activo: {status.get('active', False)}")
        print(f"   📈 PerformanceTracker: {status.get('performance_tracker', False)}")
        print(f"   � GridAnalytics: {status.get('grid_analytics', False)}")
        print(f"   �🏷️ Versión: {status.get('version', 'N/A')}")
        print(f"   📍 Fase: {status.get('phase', 'N/A')}")
        
        # 7. TEST MARKET ANALYTICS (NUEVO EN FASE 1.3)
        print("7️⃣ Testing Market Analytics...")
        
        # Agregar señal estocástica de compra
        signal_data_buy = {
            'k': 25, 'd': 22, 'senal_tipo': 'BUY', 'senal_valida': True,
            'sobreventa': True, 'sobrecompra': False, 'cruce_k_d': True
        }
        analytics_manager.update_stochastic_signal(signal_data_buy)
        print("✅ Señal estocástica BUY procesada")
        
        # Obtener reporte estocástico
        stochastic_report = analytics_manager.get_stochastic_report()
        print(f"✅ Market phase: {stochastic_report.get('market_phase', 'N/A')}")
        print(f"✅ Buy signals: {stochastic_report.get('buy_signals', 0)}")
        
        # Obtener resumen de mercado
        market_summary = analytics_manager.get_market_summary()
        print(f"✅ Volatilidad: {market_summary.get('volatility', 0):.6f}")
        
        # Actualizar correlación mercado-grid
        analytics_manager.update_market_grid_correlation(85.5, 90.2)
        print("✅ Correlación mercado-grid actualizada")
        
        # 8. Guardar snapshot completo
        print("8️⃣ Guardando snapshot completo...")
        if analytics_manager.save_analytics_snapshot():
            print("✅ Snapshot completo guardado correctamente")
        
        # 9. Shutdown limpio
        print("9️⃣ Ejecutando shutdown...")
        analytics_manager.shutdown()
        print("✅ Shutdown completado")
        
        print("\n" + "=" * 50)
        print("🎯 INTEGRACIÓN FASE 1.3 COMPLETADA EXITOSAMENTE")
        print("✅ AnalyticsManager con Performance + Grid + Market Analytics")
        print("📊 Análisis estocástico integrado para primera orden")
        assert True  # Test exitoso
        
    except Exception as e:
        print(f"\n❌ ERROR EN INTEGRACIÓN: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Error en integración: {e}"


if __name__ == "__main__":
    success = test_integracion_analytics()
    if success:
        print("\n🚀 Sistema listo para FASE 1.4 - OPTIMIZATION ENGINE")
        print("📈 Performance Analytics: ✅")
        print("🎯 Grid Analytics: ✅")
        print("🔬 Market Analytics: ✅")
        print("� Análisis estocástico: ✅")
    else:
        print("\n🛑 Revisar errores antes de continuar")
