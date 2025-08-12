"""
Test rápido del PISO 2 - Backtest Engine
"""
import sys
import os

# Configurar rutas de imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.core.piso_2 import Piso2BacktestManager, BacktestConfig

def test_piso_2():
    print("🏢 TEST RÁPIDO PISO 2 - BACKTEST ENGINE")
    print("=" * 50)
    
    # Crear manager
    manager = Piso2BacktestManager()
    
    # Test backtest rápido
    result = manager.quick_backtest(
        symbol="EURUSD",
        timeframe="M15",
        strategy_type="GRID_BOLLINGER",
        initial_balance=10000.0
    )
    
    if result["success"]:
        summary = result["quick_summary"]
        print("✅ RESULTADO:")
        print(f"Status: {summary['status']}")
        print(f"Score: {summary['score']}")
        print(f"Profit: {summary['profit']}")
        print(f"Win Rate: {summary['win_rate']}")
        print(f"Trades: {summary['trades']}")
        print(f"Drawdown: {summary['drawdown']}")
        print(f"Recomendación: {summary['recommendation']}")
        print()
        print("🎯 PISO 2 FUNCIONA PERFECTAMENTE!")
    else:
        print(f"❌ Error: {result.get('message', 'Error desconocido')}")

if __name__ == "__main__":
    test_piso_2()
