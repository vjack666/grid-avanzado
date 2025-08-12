"""
TEST ESTRATEGIA GRID OPTIMIZADA
===============================
"""
import sys
import os

# Configurar rutas de imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.core.piso_2 import Piso2BacktestManager, BacktestConfig

def test_estrategia_original_vs_optimizada():
    """Comparar estrategia original vs optimizada"""
    print("🔬 COMPARACIÓN: ORIGINAL vs OPTIMIZADA")
    print("=" * 60)
    
    manager = Piso2BacktestManager()
    
    # CONFIGURACIÓN ORIGINAL
    config_original = BacktestConfig(
        symbol="EURUSD",
        timeframe="M15",
        strategy_type="GRID_BOLLINGER",
        initial_balance=10000.0,
        bollinger_period=20,
        bollinger_deviation=2.0,
        take_profit=50,      # 50 pips
        stop_loss=200,       # 200 pips (1:4 MALO)
        lot_size=0.1
    )
    
    # CONFIGURACIÓN OPTIMIZADA
    config_optimizada = BacktestConfig(
        symbol="EURUSD", 
        timeframe="M15",
        strategy_type="GRID_BOLLINGER",
        initial_balance=10000.0,
        bollinger_period=15,     # Más reactivo
        bollinger_deviation=1.5, # Menos extremo
        take_profit=75,          # 75 pips
        stop_loss=150,           # 150 pips (1:2 MEJOR)
        lot_size=0.1
    )
    
    print("1️⃣ TESTEANDO ESTRATEGIA ORIGINAL...")
    result_original = manager.quick_backtest(
        symbol="EURUSD", timeframe="M15", 
        strategy_type="GRID_BOLLINGER", initial_balance=10000.0
    )
    
    print("\n2️⃣ TESTEANDO ESTRATEGIA OPTIMIZADA...")
    result_optimizada = manager.run_single_backtest(config_optimizada, include_analysis=True)
    
    # COMPARACIÓN
    print("\n" + "="*60)
    print("📊 COMPARACIÓN DE RESULTADOS")
    print("="*60)
    
    if result_original["success"] and result_optimizada["success"]:
        orig = result_original["quick_summary"]
        opt = result_optimizada["execution_summary"]
        
        print(f"{'MÉTRICA':<20} {'ORIGINAL':<15} {'OPTIMIZADA':<15} {'MEJORA':<10}")
        print("-" * 65)
        
        # Extraer valores numéricos
        orig_profit = float(orig["profit"].replace("$", "").replace(",", ""))
        opt_profit = opt["net_profit"]
        profit_mejora = ((opt_profit - orig_profit) / abs(orig_profit)) * 100 if orig_profit != 0 else 0
        
        orig_wr = float(orig["win_rate"].replace("%", ""))
        opt_wr = opt["win_rate"]
        wr_mejora = opt_wr - orig_wr
        
        orig_trades = int(orig["trades"])
        opt_trades = opt["total_trades"]
        trades_mejora = opt_trades - orig_trades
        
        print(f"{'Profit':<20} ${orig_profit:<14.2f} ${opt_profit:<14.2f} {profit_mejora:>+7.1f}%")
        print(f"{'Win Rate':<20} {orig_wr:<14.1f}% {opt_wr:<14.1f}% {wr_mejora:>+7.1f}%")
        print(f"{'Trades':<20} {orig_trades:<14} {opt_trades:<14} {trades_mejora:>+7}")
        
        print(f"\n💡 ANÁLISIS:")
        if opt_profit > orig_profit:
            print("✅ La estrategia optimizada ES MEJOR en rentabilidad")
        else:
            print("❌ La estrategia optimizada aún necesita más ajustes")
            
        if opt_wr > orig_wr:
            print("✅ Mejor precisión (win rate)")
        else:
            print("⚠️ Win rate similar o menor")
            
        # Score general
        if "overall_score" in result_optimizada:
            score = result_optimizada["overall_score"]
            print(f"📈 Score optimizado: {score:.1f}/100")
            if score > 50:
                print("✅ Estrategia viable para trading")
            else:
                print("⚠️ Necesita más optimización")
    
    else:
        print("❌ Error en alguno de los backtests")

if __name__ == "__main__":
    test_estrategia_original_vs_optimizada()
