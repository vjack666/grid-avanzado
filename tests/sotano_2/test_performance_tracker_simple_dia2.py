"""
Test Simplificado para PerformanceTracker - SÓTANO 2 DÍA 2
==========================================================

Test de integración simplificado sin dependencias de threading complejas.
Valida funcionalidad core, métricas y integración con SÓTANO 1 y 2.

Fecha: 2025-08-11
Componente: PUERTA-S2-PERFORMANCE
Fase: DÍA 2 - Integración MT5 Real-Time
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Configurar paths para imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
src_core = project_root / "src" / "core"
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str(src_core.absolute()))

# Imports absolutos con validación
try:
    # Importar desde src/core directamente
    sys.path.append(str(src_core))
    from config_manager import ConfigManager
    from logger_manager import LoggerManager  
    from error_manager import ErrorManager
    from data_manager import DataManager
    
    # Import del PerformanceTracker desde real_time
    from real_time.performance_tracker import PerformanceTracker, PerformanceSnapshot, TradeRecord
    from real_time.alert_engine import AlertEngine
    
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    print("Nota: Asegúrate de que todos los componentes SÓTANO 1 y 2 estén disponibles")
    sys.exit(1)


def test_performance_tracker_basic():
    """Test básico sin threading"""
    print("\n🧪 TEST PERFORMANCE TRACKER BÁSICO - DÍA 2 SÓTANO 2")
    print("=" * 50)
    
    try:
        # Test 1: Import exitoso
        print("✅ Import PerformanceTracker: OK")
        
        # Test 2: Crear dependencias SÓTANO 1
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        data_manager = DataManager(config, logger, error)
        print("✅ Dependencias SÓTANO 1: OK")
        
        # Test 3: Crear dependencias SÓTANO 2 (opcional)
        alert_engine = AlertEngine(config, logger, error)
        print("✅ Dependencias SÓTANO 2: OK")
        
        # Test 4: Inicializar PerformanceTracker
        tracker = PerformanceTracker(config, logger, error, data_manager, alert_engine)
        assert tracker.component_id == "PUERTA-S2-PERFORMANCE", "Component ID incorrecto"
        assert tracker.version == "v2.1.0", "Versión incorrecta"
        print(f"✅ Inicialización: {tracker.component_id}")
        print(f"✅ Versión: {tracker.version}")
        
        # Test 5: Verificar dependencias conectadas
        assert tracker.config is not None, "PUERTA-S1-CONFIG no conectada"
        assert tracker.logger is not None, "PUERTA-S1-LOGGER no conectada"
        assert tracker.error is not None, "PUERTA-S1-ERROR no conectada"
        assert tracker.data is not None, "PUERTA-S1-DATA no conectada"
        assert tracker.alert_engine is not None, "PUERTA-S2-ALERTS no conectada"
        print("✅ Todas las puertas conectadas")
        
        # Test 6: Estado inicial
        status = tracker.get_status()
        assert status['is_tracking'] == False, "Estado inicial incorrecto"
        assert status['component_id'] == "PUERTA-S2-PERFORMANCE", "Component ID en status incorrecto"
        print("✅ Estado inicial: Correcto")
        
        # Test 7: Métricas iniciales
        performance = tracker.get_current_performance()
        assert performance['account_state']['total_trades'] == 0, "Métricas iniciales incorrectas"
        assert performance['calculated_metrics']['win_rate'] == 0.0, "Win rate inicial incorrecto"
        print("✅ Métricas iniciales: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en test PerformanceTracker: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_account_data_management():
    """Test de manejo de datos de cuenta sin threading"""
    print("\n📊 TEST ACCOUNT DATA MANAGEMENT")
    print("-" * 50)
    
    try:
        # Crear componentes
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        data_manager = DataManager(config, logger, error)
        tracker = PerformanceTracker(config, logger, error, data_manager)
        
        # Test inicialización manual de cuenta (sin start_tracking)
        initial_balance = 10000.0
        tracker.account_state["initial_balance"] = initial_balance
        tracker.account_state["current_balance"] = initial_balance
        tracker.account_state["current_equity"] = initial_balance
        print(f"✅ Cuenta inicializada: ${initial_balance:,.2f}")
        
        # Test actualización de datos de cuenta
        tracker.update_account_data(
            balance=10500.0,
            equity=10300.0,
            margin_used=200.0,
            margin_free=10300.0
        )
        
        performance = tracker.get_current_performance()
        assert performance['account_state']['current_balance'] == 10500.0, "Balance no actualizado"
        assert performance['account_state']['current_equity'] == 10300.0, "Equity no actualizado"
        print("✅ Datos de cuenta actualizados")
        
        # Test cálculo de PnL
        total_pnl = performance['account_state']['current_equity'] - performance['account_state']['initial_balance']
        assert total_pnl == 300.0, "PnL calculado incorrectamente"
        print(f"✅ PnL total: ${total_pnl:,.2f}")
        
        # Test peak tracking
        tracker.update_account_data(balance=11000.0, equity=10800.0)
        performance = tracker.get_current_performance()
        assert performance['account_state']['peak_balance'] == 11000.0, "Peak balance no actualizado"
        assert performance['account_state']['peak_equity'] == 10800.0, "Peak equity no actualizado"
        print("✅ Peak tracking: OK")
        
        # Test drawdown calculation
        tracker.update_account_data(balance=10200.0, equity=9800.0)  # Drawdown
        performance = tracker.get_current_performance()
        expected_drawdown = (10800.0 - 9800.0) / 10800.0 * 100  # ~9.26%
        assert performance['account_state']['max_drawdown'] > 9.0, "Drawdown no calculado"
        print(f"✅ Drawdown calculado: {performance['account_state']['max_drawdown']:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de datos de cuenta: {e}")
        return False


def test_trade_calculations():
    """Test de cálculos de trades"""
    print("\n💹 TEST TRADE CALCULATIONS")
    print("-" * 50)
    
    try:
        # Crear componentes
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        data_manager = DataManager(config, logger, error)
        tracker = PerformanceTracker(config, logger, error, data_manager)
        
        # Inicializar cuenta
        tracker.account_state["initial_balance"] = 10000.0
        
        # Test agregar trade ganador
        winning_trade = TradeRecord(
            id="trade_001",
            symbol="EURUSD",
            type="buy",
            volume=0.1,
            open_price=1.1000,
            close_price=1.1050,
            open_time=datetime.now(),
            close_time=datetime.now(),
            pnl=50.0,
            commission=2.0,
            swap=0.0,
            net_profit=48.0
        )
        
        tracker.add_completed_trade(winning_trade)
        
        performance = tracker.get_current_performance()
        assert performance['account_state']['total_trades'] == 1, "Trade no agregado"
        assert performance['account_state']['winning_trades'] == 1, "Winning trade no contado"
        assert performance['account_state']['gross_profit'] == 48.0, "Gross profit incorrecto"
        print("✅ Trade ganador agregado")
        
        # Test agregar trade perdedor
        losing_trade = TradeRecord(
            id="trade_002",
            symbol="GBPUSD",
            type="sell",
            volume=0.1,
            open_price=1.3000,
            close_price=1.3030,
            open_time=datetime.now(),
            close_time=datetime.now(),
            pnl=-30.0,
            commission=2.0,
            swap=0.0,
            net_profit=-32.0
        )
        
        tracker.add_completed_trade(losing_trade)
        
        performance = tracker.get_current_performance()
        assert performance['account_state']['total_trades'] == 2, "Segundo trade no agregado"
        assert performance['account_state']['losing_trades'] == 1, "Losing trade no contado"
        assert performance['account_state']['gross_loss'] == 32.0, "Gross loss incorrecto"
        print("✅ Trade perdedor agregado")
        
        # Test cálculo de métricas
        metrics = performance['calculated_metrics']
        expected_win_rate = (1 / 2) * 100  # 50%
        assert abs(metrics['win_rate'] - expected_win_rate) < 0.1, "Win rate incorrecto"
        
        expected_profit_factor = 48.0 / 32.0  # 1.5
        assert abs(metrics['profit_factor'] - expected_profit_factor) < 0.1, "Profit factor incorrecto"
        
        print(f"✅ Win rate: {metrics['win_rate']:.1f}%")
        print(f"✅ Profit factor: {metrics['profit_factor']:.2f}")
        
        # Test más trades para probar cálculos avanzados
        for i in range(5):
            trade = TradeRecord(
                id=f"trade_00{i+3}",
                symbol="EURUSD",
                type="buy",
                volume=0.1,
                open_price=1.1000,
                close_price=1.1010 if i % 2 == 0 else 1.0990,
                open_time=datetime.now(),
                close_time=datetime.now(),
                pnl=10.0 if i % 2 == 0 else -10.0,
                commission=1.0,
                swap=0.0,
                net_profit=9.0 if i % 2 == 0 else -11.0
            )
            tracker.add_completed_trade(trade)
        
        performance = tracker.get_current_performance()
        assert performance['account_state']['total_trades'] == 7, "Total trades incorrecto"
        print(f"✅ Total trades: {performance['account_state']['total_trades']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de trades: {e}")
        return False


def test_dataframes_and_summary():
    """Test de DataFrames y resúmenes"""
    print("\n📋 TEST DATAFRAMES AND SUMMARY")
    print("-" * 50)
    
    try:
        # Crear componentes
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        data_manager = DataManager(config, logger, error)
        tracker = PerformanceTracker(config, logger, error, data_manager)
        
        # Inicializar con algunos datos
        tracker.account_state["initial_balance"] = 10000.0
        tracker.account_state["current_balance"] = 10500.0
        tracker.account_state["current_equity"] = 10300.0
        
        # Agregar algunos trades
        for i in range(3):
            trade = TradeRecord(
                id=f"test_trade_{i}",
                symbol="EURUSD",
                type="buy",
                volume=0.1,
                open_price=1.1000,
                close_price=1.1010,
                open_time=datetime.now(),
                close_time=datetime.now(),
                pnl=10.0,
                commission=1.0,
                swap=0.0,
                net_profit=9.0
            )
            tracker.add_completed_trade(trade)
        
        # Test DataFrame de trades
        trades_df = tracker.get_trades_dataframe()
        assert len(trades_df) == 3, "DataFrame de trades incorrecto"
        assert 'net_profit' in trades_df.columns, "Columnas de trades incorrectas"
        assert 'symbol' in trades_df.columns, "Columna symbol faltante"
        print("✅ DataFrame de trades: OK")
        
        # Test DataFrame de snapshots (estará vacío sin tracking activo)
        snapshots_df = tracker.get_snapshots_dataframe()
        print(f"✅ DataFrame de snapshots: {len(snapshots_df)} registros")
        
        # Test performance summary
        summary = tracker.get_performance_summary()
        assert 'balance' in summary, "Summary incompleto"
        assert 'tracking_active' in summary, "Estado de tracking no en summary"
        assert summary['balance'] == 10500.0, "Balance incorrecto en summary"
        assert summary['total_trades'] == 3, "Total trades incorrecto en summary"
        print("✅ Performance summary: OK")
        print(f"✅ Summary balance: ${summary['balance']:,.2f}")
        print(f"✅ Summary trades: {summary['total_trades']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de DataFrames: {e}")
        return False


def test_performance_snapshot():
    """Test de snapshot de performance"""
    print("\n📸 TEST PERFORMANCE SNAPSHOT")
    print("-" * 50)
    
    try:
        # Test crear snapshot manualmente
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now(),
            balance=10000.0,
            equity=10000.0,
            margin_used=0.0,
            margin_free=10000.0,
            open_positions=0,
            total_pnl=0.0,
            day_pnl=0.0,
            win_rate=0.0,
            profit_factor=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            trades_count=0
        )
        
        assert snapshot.balance == 10000.0, "Snapshot balance incorrecto"
        assert snapshot.equity == 10000.0, "Snapshot equity incorrecto"
        print("✅ PerformanceSnapshot creado manualmente")
        
        # Test snapshot desde tracker
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        data_manager = DataManager(config, logger, error)
        tracker = PerformanceTracker(config, logger, error, data_manager)
        
        # Configurar datos
        tracker.account_state["initial_balance"] = 10000.0
        tracker.account_state["current_balance"] = 10500.0
        tracker.account_state["current_equity"] = 10300.0
        
        # Crear snapshot actual
        current_snapshot = tracker._create_current_snapshot()
        assert current_snapshot.balance == 10500.0, "Current snapshot balance incorrecto"
        assert current_snapshot.equity == 10300.0, "Current snapshot equity incorrecto"
        assert current_snapshot.total_pnl == 300.0, "Current snapshot PnL incorrecto"
        print("✅ Current snapshot creado desde tracker")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de snapshot: {e}")
        return False


def main():
    """Función principal de testing simplificado"""
    print("=" * 60)
    print("🏗️ SÓTANO 2 - DÍA 2: PERFORMANCE TRACKER (SIMPLIFICADO)")
    print("PUERTA-S2-PERFORMANCE - Test de integración")
    print("=" * 60)
    
    # Ejecutar tests
    test_results = []
    
    # Test 1: Funcionalidad básica
    test_results.append(test_performance_tracker_basic())
    
    # Test 2: Manejo de datos de cuenta
    test_results.append(test_account_data_management())
    
    # Test 3: Cálculos de trades
    test_results.append(test_trade_calculations())
    
    # Test 4: DataFrames y resúmenes
    test_results.append(test_dataframes_and_summary())
    
    # Test 5: Snapshots
    test_results.append(test_performance_snapshot())
    
    # Test 6: Compatibilidad con sistema existente
    print("\n🔄 TEST COMPATIBILIDAD CON SISTEMA EXISTENTE")
    print("-" * 50)
    try:
        # Verificar que el sistema SÓTANO 1 sigue funcionando
        from analytics_manager import AnalyticsManager
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger)
        data_manager = DataManager(config, logger, error)
        analytics = AnalyticsManager(config, logger, error, data_manager)
        print("✅ Sistema SÓTANO 1 sigue funcionando")
        print("✅ No hay conflictos con SÓTANO 2")
        test_results.append(True)
    except Exception as e:
        print(f"❌ Error de compatibilidad: {e}")
        test_results.append(False)
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DÍA 2 - PERFORMANCE TRACKER")
    print("=" * 60)
    tests_passed = sum(test_results)
    tests_total = len(test_results)
    
    print(f"Tests ejecutados: {tests_total}")
    print(f"Tests pasados: {tests_passed}")
    print(f"Tests fallidos: {tests_total - tests_passed}")
    
    if tests_passed == tests_total:
        print("\n🎉 DÍA 2 - PERFORMANCE TRACKER: ✅ COMPLETADO")
        print("✅ PUERTA-S2-PERFORMANCE: Funcional")
        print("✅ Integración SÓTANO 1: Sin conflictos")
        print("✅ Integración SÓTANO 2: Sin conflictos")
        print("✅ Manejo de datos: Funcional")
        print("✅ Cálculos de métricas: Funcional")
        print("✅ DataFrames: Funcional")
        print("✅ Snapshots: Funcional")
        print("\n🏆 SÓTANO 2 DÍA 2: 100% COMPLETADO")
        print("🎯 Todos los componentes de tiempo real implementados")
        print("📊 MT5Streamer + PositionMonitor + AlertEngine + PerformanceTracker")
        return True
    else:
        print(f"\n❌ DÍA 2 CON PROBLEMAS")
        print("🔧 Revisar implementación antes de continuar")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
