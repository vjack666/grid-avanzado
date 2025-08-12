"""
DEMO INTEGRATION: StrategyEngine → OrderExecutor
===============================================
Demo que conecta el StrategyEngine del SÓTANO 2 con el OrderExecutor del PISO EJECUTOR

Este demo demuestra EL OBJETIVO PRINCIPAL del piso ejecutor:
Convertir señales inteligentes del StrategyEngine en órdenes reales ejecutadas en MT5

FLUJO DEMOSTRADO:
StrategyEngine → TradingSignal → OrderExecutor → MT5 (Mock)

PROTOCOLO: Trading Grid - Piso Ejecutor
FECHA: 2025-08-12
"""

import sys
import os
import time
from datetime import datetime

# Configurar paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    # Imports del sistema
    from src.core.config_manager import ConfigManager
    from src.core.logger_manager import LoggerManager
    from src.core.error_manager import ErrorManager
    from src.core.data_manager import DataManager
    from src.core.analytics_manager import AnalyticsManager
    
    # Imports SÓTANO 2
    from src.core.real_time.strategy_engine import StrategyEngine, StrategyConfig, StrategyType, SignalStrength
    
    # Imports PISO EJECUTOR
    from src.core.live_trading.order_executor import OrderExecutor
    
    # Mock para FundedNext (para demo sin MT5 real)
    from unittest.mock import Mock
    
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    sys.exit(1)


def create_mock_fundednext_manager():
    """Crear mock del FundedNext manager para demo"""
    mock_manager = Mock()
    mock_manager.ensure_fundednext_terminal.return_value = True
    mock_manager.connect_to_mt5.return_value = True
    mock_manager.get_connection_status.return_value = "connected (mock)"
    return mock_manager


def demo_strategy_to_order_integration():
    """Demo completo: StrategyEngine → OrderExecutor"""
    
    print("🏢 DEMO PISO EJECUTOR: STRATEGY → ORDER INTEGRATION")
    print("=" * 55)
    
    try:
        # 1. INICIALIZAR COMPONENTES SÓTANO 1
        print("1️⃣ INICIALIZANDO SÓTANO 1...")
        config_manager = ConfigManager()
        logger_manager = LoggerManager()
        error_manager = ErrorManager(logger_manager, config_manager)
        data_manager = DataManager()
        analytics_manager = AnalyticsManager(
            config_manager=config_manager,
            logger_manager=logger_manager,
            error_manager=error_manager,
            data_manager=data_manager
        )
        print("   ✅ SÓTANO 1 inicializado")
        
        # 2. INICIALIZAR STRATEGY ENGINE (SÓTANO 2)
        print("\n2️⃣ INICIALIZANDO STRATEGY ENGINE (SÓTANO 2)...")
        strategy_engine = StrategyEngine(
            config_manager=config_manager,
            logger_manager=logger_manager,
            error_manager=error_manager,
            data_manager=data_manager,
            analytics_manager=analytics_manager
        )
        
        # Configurar estrategia
        strategy_config = StrategyConfig(
            strategy_type=StrategyType.ADAPTIVE_GRID,
            timeframes=["M15"],
            symbols=["EURUSD"],
            risk_per_trade=0.02,
            max_concurrent_trades=3,
            min_signal_strength=SignalStrength.MODERATE
        )
        
        strategy_engine.initialize_strategy_config("demo_grid", strategy_config)
        strategy_engine.start_strategy("demo_grid")
        print("   ✅ StrategyEngine configurado y activo")
        
        # 3. INICIALIZAR ORDER EXECUTOR (PISO EJECUTOR)
        print("\n3️⃣ INICIALIZANDO ORDER EXECUTOR (PISO EJECUTOR)...")
        mock_fundednext = create_mock_fundednext_manager()
        
        order_executor = OrderExecutor(
            config_manager=config_manager,
            logger_manager=logger_manager,
            error_manager=error_manager,
            fundednext_manager=mock_fundednext
        )
        
        if order_executor.initialize_executor():
            print("   ✅ OrderExecutor inicializado y conectado")
        else:
            print("   ❌ Error inicializando OrderExecutor")
            return
        
        # 4. DEMOSTRAR INTEGRACIÓN
        print("\n4️⃣ DEMOSTRANDO INTEGRACIÓN STRATEGY → ORDER...")
        print("   🔄 Generando señales del StrategyEngine...")
        
        # Simular datos de mercado
        market_data = {
            'price': 1.0850,
            'volatility': 0.015
        }
        
        # Generar señal desde StrategyEngine
        signal = strategy_engine.generate_adaptive_grid_signal("EURUSD", market_data)
        
        if signal:
            print(f"   📡 Señal generada: {signal.symbol} {signal.signal_type}")
            print(f"   📊 Confianza: {signal.confidence:.2%}")
            print(f"   📈 Precio: {signal.price}")
            print(f"   💪 Fuerza: {signal.strength.name}")
            
            # CONECTAR CON ORDER EXECUTOR
            print("\n   🚀 ENVIANDO SEÑAL AL ORDER EXECUTOR...")
            
            # Mock de MT5 para demo
            with MockMT5OrderSend():
                success = order_executor.process_signal(signal)
                
                if success:
                    print("   ✅ SEÑAL PROCESADA Y ORDEN EJECUTADA (MOCK)")
                    
                    # Mostrar métricas
                    status = order_executor.get_execution_status()
                    print(f"   📊 Señales recibidas: {status['metrics']['total_signals_received']}")
                    print(f"   📊 Órdenes ejecutadas: {status['metrics']['total_orders_executed']}")
                    print(f"   📊 Tasa éxito: {status['metrics']['success_rate']:.1%}")
                    
                else:
                    print("   ❌ Error procesando señal")
        else:
            print("   ⚠️ No se generó señal")
        
        # 5. MOSTRAR ESTADO FINAL
        print("\n5️⃣ ESTADO FINAL DEL SISTEMA...")
        
        # Estado StrategyEngine
        strategy_status = strategy_engine.get_strategy_status()
        print(f"   🎯 Estrategias activas: {strategy_status['metrics']['active_strategies_count']}")
        
        # Estado OrderExecutor
        executor_status = order_executor.get_execution_status()
        print(f"   🏢 Executor activo: {executor_status['is_active']}")
        print(f"   🔄 Órdenes habilitadas: {executor_status['orders_enabled']}")
        
        # 6. CLEANUP
        print("\n6️⃣ LIMPIEZA DEL SISTEMA...")
        strategy_engine.cleanup()
        order_executor.cleanup()
        print("   ✅ Cleanup completado")
        
        print("\n🏆 DEMO INTEGRACIÓN COMPLETADO EXITOSAMENTE")
        print("🎯 OBJETIVO LOGRADO: StrategyEngine → OrderExecutor ✅")
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()


class MockMT5OrderSend:
    """Context manager para mock de MT5 order_send"""
    
    def __enter__(self):
        # Mock del módulo MT5 para demo
        import MetaTrader5 as mt5
        
        # Crear mock result
        mock_result = Mock()
        mock_result.retcode = 10009  # TRADE_RETCODE_DONE
        mock_result.order = 12345
        mock_result.deal = 67890
        mock_result.volume = 0.01
        mock_result.price = 1.0850
        
        # Patch order_send
        self.original_order_send = mt5.order_send
        mt5.order_send = Mock(return_value=mock_result)
        
        # Patch symbol_info
        self.original_symbol_info = mt5.symbol_info
        mt5.symbol_info = Mock(return_value=Mock())
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import MetaTrader5 as mt5
        # Restaurar funciones originales
        mt5.order_send = self.original_order_send
        mt5.symbol_info = self.original_symbol_info


def main():
    """Función principal del demo"""
    print("🚀 INICIANDO DEMO PISO EJECUTOR")
    print("📅 Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    demo_strategy_to_order_integration()


if __name__ == "__main__":
    main()
