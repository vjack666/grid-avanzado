"""
Demo temporal del StrategyEngine para validación
"""
import sys
import os
import time

# Configurar paths
sys.path.insert(0, os.getcwd())

from src.core.real_time.strategy_engine import StrategyEngine, StrategyConfig, StrategyType

def demo_strategy_engine():
    print('🎯 STRATEGY ENGINE - PUERTA-S2-STRATEGY')
    print('=' * 50)
    
    try:
        # Crear engine y configurar estrategia
        engine = StrategyEngine()
        config = StrategyConfig(
            strategy_type=StrategyType.ADAPTIVE_GRID,
            timeframes=['M15', 'H1'],
            symbols=['EURUSD', 'GBPUSD'],
            risk_per_trade=0.02,
            max_concurrent_trades=3
        )
        
        engine.initialize_strategy_config('adaptive_grid_1', config)
        engine.start_strategy('adaptive_grid_1')
        engine.start_strategy_service()
        
        print('🚀 Motor de estrategias iniciado...')
        time.sleep(3)
        
        status = engine.get_strategy_status()
        print(f'📊 Estado: {status["metrics"]["active_strategies_count"]} estrategias activas')
        print(f'🎯 Señales generadas: {status["metrics"]["total_signals_generated"]}')
        
        # Obtener señales activas
        signals = engine.get_active_signals()
        print(f'📡 Señales activas: {len(signals)}')
        
        if signals:
            for key, signal in signals.items():
                print(f'   - {key}: {signal.signal_type} ({signal.strength.name}, {signal.confidence:.1%})')
        
        engine.cleanup()
        print('✅ Demo completado exitosamente')
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    demo_strategy_engine()
