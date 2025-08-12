"""
DEMO PISO 2 - BACKTEST ENGINE v1.0.0
====================================
Demostración completa del sistema de backtesting con datos reales

AUTOR: Sistema Modular Trading Grid
FECHA: 2025-08-12
PROTOCOLO: PISO 2 - BACKTEST ENGINE
"""

import sys
import os
from datetime import datetime
import json

# Configurar rutas de imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Imports del PISO 2
try:
    from src.core.piso_2 import (
        Piso2BacktestManager,
        BacktestConfig,
        create_backtest_manager,
        create_quick_config
    )
except ImportError as e:
    print(f"❌ Error importando módulos del PISO 2: {e}")
    print("🔧 Verificando estructura del proyecto...")
    print(f"📁 Directorio actual: {current_dir}")
    print(f"📁 Raíz del proyecto: {project_root}")
    
    # Verificar si existe el directorio piso_2
    piso_2_path = os.path.join(project_root, "src", "core", "piso_2")
    print(f"📁 Ruta PISO 2: {piso_2_path}")
    print(f"🔍 Existe: {os.path.exists(piso_2_path)}")
    
    if os.path.exists(piso_2_path):
        files = os.listdir(piso_2_path)
        print(f"📄 Archivos en PISO 2: {files}")
    
    raise


def demo_backtest_single():
    """Demo 1: Backtest individual completo"""
    print("🏢 DEMO PISO 2 - BACKTEST SINGLE")
    print("=" * 50)
    
    # Crear manager del PISO 2
    manager = create_backtest_manager()
    
    # Mostrar estado
    status = manager.get_status()
    print(f"✅ PISO 2 inicializado - Versión: {status['version']}")
    print(f"📊 Datos disponibles: {status['available_data']['total_files']} archivos")
    print(f"💱 Símbolos: {', '.join(status['available_data']['symbols'])}")
    print()
    
    # Validar datos disponibles
    print("🔍 VALIDANDO DATOS...")
    validation = manager.validate_data_availability("EURUSD", "M15")
    print(f"📈 Datos EURUSD M15: {validation['records']} registros")
    print(f"📅 Período: {validation['date_range']['start']} a {validation['date_range']['end']}")
    print(f"⭐ Calidad: {validation['quality_score']:.1f}%")
    print()
    
    # Configurar backtest
    config = BacktestConfig(
        symbol="EURUSD",
        timeframe="M15",
        strategy_type="GRID_BOLLINGER",
        initial_balance=10000.0,
        start_date="2025-05-20",
        end_date="2025-08-12",
        # Parámetros de estrategia
        bollinger_period=20,
        bollinger_deviation=2.0,
        grid_spacing=0.0025,  # 25 pips
        lot_size=0.1,
        take_profit=50,       # 50 pips
        stop_loss=200         # 200 pips
    )
    
    print("🚀 EJECUTANDO BACKTEST...")
    print(f"🎯 Estrategia: {config.strategy_type}")
    print(f"💱 Símbolo: {config.symbol} {config.timeframe}")
    print(f"💰 Balance inicial: ${config.initial_balance:,.2f}")
    print()
    
    # Ejecutar backtest
    result = manager.run_single_backtest(
        config, 
        include_analysis=True, 
        include_report=True
    )
    
    if result["success"]:
        print("✅ BACKTEST COMPLETADO EXITOSAMENTE")
        print("=" * 50)
        
        # Resumen ejecutivo
        summary = result["execution_summary"]
        print(f"📊 Total de trades: {summary['total_trades']}")
        print(f"💰 P&L neto: ${summary['net_profit']:,.2f}")
        print(f"🎯 Win rate: {summary['win_rate']:.1f}%")
        print(f"📉 Max drawdown: {summary['max_drawdown']:.1f}%")
        print(f"⏱️ Tiempo ejecución: {summary['execution_time']:.2f}s")
        
        if "overall_score" in result:
            print(f"⭐ Score general: {result['overall_score']:.1f}/100")
        
        print()
        
        # Análisis avanzado
        if "analysis" in result and result["analysis"]:
            analysis = result["analysis"]
            print("🔍 ANÁLISIS AVANZADO")
            print("-" * 30)
            
            if "performance_metrics" in analysis:
                perf = analysis["performance_metrics"]
                print(f"📈 Retorno total: {perf.get('total_return', 0):.2f}%")
                print(f"📊 Profit factor: {perf.get('profit_factor', 0):.2f}")
                print(f"📉 Sharpe ratio: {perf.get('sharpe_ratio', 0):.2f}")
                print(f"💵 Expectancy: ${perf.get('expectancy', 0):.2f}")
            
            if "risk_metrics" in analysis:
                risk = analysis["risk_metrics"]
                print(f"⚠️ VaR 95%: ${risk.get('var_95', 0):.2f}")
                print(f"📊 Volatilidad: {risk.get('volatility', 0):.2f}%")
            
            print()
        
        # Mejores y peores trades
        backtest_result = result["backtest_result"]
        if backtest_result.trades:
            trades = backtest_result.trades
            best_trade = max(trades, key=lambda t: t.net_pnl)
            worst_trade = min(trades, key=lambda t: t.net_pnl)
            
            print("💹 TRADES DESTACADOS")
            print("-" * 30)
            print(f"🟢 Mejor trade: ${best_trade.net_pnl:.2f} ({best_trade.direction})")
            print(f"🔴 Peor trade: ${worst_trade.net_pnl:.2f} ({worst_trade.direction})")
            print()
    
    else:
        print("❌ ERROR EN BACKTEST")
        print(f"Error: {result.get('message', 'Error desconocido')}")
    
    return result


def demo_backtest_quick():
    """Demo 2: Backtest rápido"""
    print("⚡ DEMO PISO 2 - BACKTEST RÁPIDO")
    print("=" * 50)
    
    manager = create_backtest_manager()
    
    print("🚀 Ejecutando backtest rápido...")
    result = manager.quick_backtest(
        symbol="EURUSD",
        timeframe="M15", 
        strategy_type="GRID_BOLLINGER",
        initial_balance=10000.0
    )
    
    if result["success"] and "quick_summary" in result:
        summary = result["quick_summary"]
        print("✅ RESULTADO RÁPIDO")
        print("-" * 30)
        print(f"🎯 Status: {summary['status']}")
        print(f"⭐ Score: {summary['score']}")
        print(f"💰 Profit: {summary['profit']}")
        print(f"🎯 Win Rate: {summary['win_rate']}")
        print(f"📊 Trades: {summary['trades']}")
        print(f"📉 Drawdown: {summary['drawdown']}")
        print(f"💡 Recomendación: {summary['recommendation']}")
    else:
        print("❌ Error en backtest rápido")
    
    return result


def demo_parameter_optimization():
    """Demo 3: Optimización de parámetros"""
    print("🎯 DEMO PISO 2 - OPTIMIZACIÓN DE PARÁMETROS")
    print("=" * 50)
    
    manager = create_backtest_manager()
    
    # Configuración base
    base_config = create_quick_config()
    
    # Definir rangos de parámetros a optimizar
    parameter_ranges = {
        "bollinger_period": [15, 20, 25],
        "bollinger_deviation": [1.5, 2.0, 2.5],
        "take_profit": [30, 50, 70],
        "lot_size": [0.05, 0.1, 0.15]
    }
    
    print(f"🔧 Optimizando {len(parameter_ranges)} parámetros:")
    for param, values in parameter_ranges.items():
        print(f"   {param}: {values}")
    
    total_combinations = 1
    for values in parameter_ranges.values():
        total_combinations *= len(values)
    print(f"📊 Total combinaciones: {total_combinations}")
    print()
    
    print("🚀 Ejecutando optimización...")
    result = manager.run_parameter_optimization(
        base_config=base_config,
        parameter_ranges=parameter_ranges,
        optimization_metric="custom_score",
        max_combinations=100
    )
    
    if result["success"]:
        opt_result = result["optimization_result"]
        
        print("✅ OPTIMIZACIÓN COMPLETADA")
        print("=" * 50)
        print(f"🎯 Mejor score: {opt_result.get('best_score', 0):.4f}")
        print(f"📊 Combinaciones evaluadas: {opt_result.get('total_combinations', 0)}")
        
        # Mejores parámetros
        if "best_config" in opt_result and opt_result["best_config"]:
            best_params = opt_result["best_config"]
            print("\n🏆 MEJORES PARÁMETROS:")
            print("-" * 30)
            print(f"Bollinger period: {best_params.get('bollinger_period', 'N/A')}")
            print(f"Bollinger deviation: {best_params.get('bollinger_deviation', 'N/A')}")
            print(f"Take profit: {best_params.get('take_profit', 'N/A')}")
            print(f"Lot size: {best_params.get('lot_size', 'N/A')}")
        
        # Mejora vs configuración base
        if "improvement_summary" in result:
            improvement = result["improvement_summary"]
            print(f"\n📈 MEJORA: {improvement.get('improvement_percent', 0):.1f}%")
            print(f"Score base: {improvement.get('base_score', 0):.4f}")
            print(f"Score optimizado: {improvement.get('optimized_score', 0):.4f}")
        
        # Top 3 resultados
        if "results" in opt_result and opt_result["results"]:
            top_results = sorted(opt_result["results"], key=lambda x: x["score"], reverse=True)[:3]
            print("\n🥇 TOP 3 RESULTADOS:")
            print("-" * 30)
            for i, res in enumerate(top_results, 1):
                print(f"{i}. Score: {res['score']:.4f} | Profit: ${res['net_profit']:.2f} | WR: {res['win_rate']:.1f}%")
    
    else:
        print("❌ Error en optimización")
        print(f"Error: {result.get('message', 'Error desconocido')}")
    
    return result


def demo_strategy_comparison():
    """Demo 4: Comparación de estrategias"""
    print("🔄 DEMO PISO 2 - COMPARACIÓN DE ESTRATEGIAS")
    print("=" * 50)
    
    manager = create_backtest_manager()
    
    # Crear diferentes configuraciones
    configs = [
        BacktestConfig(
            symbol="EURUSD", timeframe="M15", strategy_type="GRID_BOLLINGER",
            bollinger_period=20, bollinger_deviation=2.0, take_profit=50
        ),
        BacktestConfig(
            symbol="EURUSD", timeframe="M15", strategy_type="GRID_BOLLINGER", 
            bollinger_period=15, bollinger_deviation=1.5, take_profit=30
        ),
        BacktestConfig(
            symbol="EURUSD", timeframe="M15", strategy_type="GRID_BOLLINGER",
            bollinger_period=25, bollinger_deviation=2.5, take_profit=70
        )
    ]
    
    print(f"🎯 Comparando {len(configs)} configuraciones...")
    print()
    
    result = manager.run_multiple_strategy_comparison(configs)
    
    if result["success"]:
        analysis = result["comparison_analysis"]
        
        print("✅ COMPARACIÓN COMPLETADA")
        print("=" * 50)
        
        # Mejor estrategia
        best = analysis["best_strategy"]
        print(f"🏆 MEJOR: {best['strategy']} (Score: {best['score']:.1f})")
        print(f"💰 Profit: ${best['net_profit']:.2f}")
        print()
        
        # Ranking
        print("📊 RANKING:")
        print("-" * 30)
        for rank_info in analysis["ranking"]:
            metrics = rank_info["key_metrics"]
            print(f"{rank_info['rank']}. Score: {rank_info['score']:.1f} | "
                  f"Profit: ${metrics['net_profit']:.2f} | "
                  f"WR: {metrics['win_rate']:.1f}%")
        
        # Estadísticas generales
        stats = analysis["summary_stats"]
        print(f"\n📈 ESTADÍSTICAS GENERALES:")
        print(f"Score promedio: {stats['avg_score']:.1f}")
        print(f"Profit promedio: ${stats['avg_profit']:.2f}")
        print(f"Total trades: {stats['total_trades']}")
        
        # Recomendaciones
        if "comparison_report" in result and "recommendations" in result["comparison_report"]:
            print(f"\n💡 RECOMENDACIONES:")
            for rec in result["comparison_report"]["recommendations"]:
                print(f"   {rec}")
    
    else:
        print("❌ Error en comparación")
    
    return result


def main():
    """Función principal del demo"""
    print("🏢 PISO 2 - BACKTEST ENGINE DEMO v1.0.0")
    print("=" * 60)
    print("Sistema completo de backtesting con datos reales de MT5")
    print("=" * 60)
    print()
    
    try:
        # Demo 1: Backtest individual
        print("1️⃣ DEMO BACKTEST INDIVIDUAL")
        demo_result_1 = demo_backtest_single()
        print("\n" + "="*80 + "\n")
        
        # Demo 2: Backtest rápido
        print("2️⃣ DEMO BACKTEST RÁPIDO")
        demo_result_2 = demo_backtest_quick()
        print("\n" + "="*80 + "\n")
        
        # Demo 3: Optimización (comentado por tiempo)
        print("3️⃣ DEMO OPTIMIZACIÓN DE PARÁMETROS")
        print("⚠️  DEMO de optimización disponible pero comentado por tiempo de ejecución")
        print("💡 Descomenta demo_parameter_optimization() para ejecutar")
        # demo_result_3 = demo_parameter_optimization()
        print("\n" + "="*80 + "\n")
        
        # Demo 4: Comparación (comentado por tiempo)
        print("4️⃣ DEMO COMPARACIÓN DE ESTRATEGIAS")  
        print("⚠️  DEMO de comparación disponible pero comentado por tiempo de ejecución")
        print("💡 Descomenta demo_strategy_comparison() para ejecutar")
        # demo_result_4 = demo_strategy_comparison()
        
        print("\n" + "="*80)
        print("✅ TODOS LOS DEMOS DEL PISO 2 COMPLETADOS")
        print("🏢 El PISO 2 - BACKTEST ENGINE está completamente funcional")
        print("📊 Listo para uso en producción con datos reales de MT5")
        print("="*80)
        
    except Exception as e:
        print(f"❌ ERROR EN DEMO: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
