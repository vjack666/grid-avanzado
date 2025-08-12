"""
ANÁLISIS Y OPTIMIZACIÓN DE ESTRATEGIA GRID BOLLINGER
===================================================

PROBLEMA IDENTIFICADO:
- Win Rate: 78.4% (EXCELENTE)
- P&L: -$207.90 (MALO)
- Relación: TP 50 pips vs SL 200 pips = 1:4 (PROBLEMA)

SOLUCIONES PROPUESTAS:

1. AJUSTAR RELACIÓN RIESGO/BENEFICIO
   - Cambiar a TP 100 pips, SL 100 pips (1:1)
   - O TP 75 pips, SL 150 pips (1:2)

2. OPTIMIZAR PARÁMETROS BOLLINGER
   - Probar período 15 en lugar de 20
   - Probar desviación 1.5 en lugar de 2.0

3. MEJORAR FILTROS DE ENTRADA
   - Añadir filtro de tendencia (RSI, MACD)
   - Evitar trades contra tendencia principal

4. GESTIÓN AVANZADA
   - Trail stop para proteger ganancias
   - Scaling out parcial en +25 pips

CONFIGURACIÓN OPTIMIZADA SUGERIDA:
"""

from src.core.piso_2 import BacktestConfig

def crear_estrategia_optimizada():
    """Crear configuración optimizada basada en análisis"""
    return BacktestConfig(
        symbol="EURUSD",
        timeframe="M15",
        strategy_type="GRID_BOLLINGER",
        initial_balance=10000.0,
        
        # Parámetros optimizados
        bollinger_period=15,        # Más reactivo
        bollinger_deviation=1.5,    # Menos extremo
        
        # Relación riesgo/beneficio mejorada
        take_profit=75,             # 75 pips ganancia
        stop_loss=150,              # 150 pips pérdida (1:2)
        
        # Gestión de posiciones
        lot_size=0.1,
        grid_spacing=0.0020,        # 20 pips (más denso)
        grid_levels=15              # Más niveles
    )

def test_estrategia_optimizada():
    """Test de la estrategia optimizada"""
    from src.core.piso_2 import Piso2BacktestManager
    
    manager = Piso2BacktestManager()
    config = crear_estrategia_optimizada()
    
    print("🧪 TESTEANDO ESTRATEGIA OPTIMIZADA...")
    result = manager.run_single_backtest(config, include_analysis=True)
    
    if result["success"]:
        summary = result["execution_summary"]
        print("📊 RESULTADOS OPTIMIZADOS:")
        print(f"Trades: {summary['total_trades']}")
        print(f"P&L: ${summary['net_profit']:.2f}")
        print(f"Win Rate: {summary['win_rate']:.1f}%")
        print(f"Drawdown: {summary['max_drawdown']:.1f}%")
        print(f"Score: {result.get('overall_score', 0):.1f}/100")
    
    return result

if __name__ == "__main__":
    test_estrategia_optimizada()
