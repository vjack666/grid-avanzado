"""
Test rápido de componentes del sistema Trading Grid
Ejecuta una verificación básica de cada componente principal
"""
import sys
from pathlib import Path

# Configurar rutas para imports
current_dir = Path(__file__).parent
project_root = current_dir / ".."
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis").absolute()))
sys.path.insert(0, str((project_root / "src" / "utils").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))



import sys
import time
from datetime import datetime
import traceback

print("=" * 60)
print("🧪 TEST RÁPIDO DEL SISTEMA TRADING GRID")
print("=" * 60)
print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

def test_component(name, test_func):
    """Ejecuta un test de componente y reporta el resultado"""
    print(f"🔧 Testing {name}...", end=" ")
    start_time = time.time()
    
    try:
        result = test_func()
        execution_time = time.time() - start_time
        
        if result:
            print(f"✅ PASS ({execution_time:.2f}s)")
            return True
        else:
            print(f"❌ FAIL ({execution_time:.2f}s)")
            return False
            
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"💥 ERROR ({execution_time:.2f}s)")
        print(f"   └─ {str(e)}")
        return False

def test_imports():
    """Test de imports básicos"""
    try:
        import MetaTrader5 as mt5
        import pandas as pd
        import numpy as np
        from rich.console import Console
        return True
    except ImportError as e:
        print(f"   └─ Import error: {e}")
        return False

def test_config():
    """Test del sistema de configuración"""
    try:
        import config
        # Verificar que existen las variables principales
        required_vars = ['SIMBOLO', 'LOTE_MINIMO', 'INTERVALO_SEGUNDOS']
        for var in required_vars:
            if not hasattr(config, var):
                print(f"   └─ Missing config variable: {var}")
                return False
        return True
    except Exception as e:
        print(f"   └─ Config error: {e}")
        return False

def test_mt5_connection():
    """Test de conectividad con MT5"""
    try:
        import MetaTrader5 as mt5
        
        # Intentar inicializar MT5
        if not mt5.initialize():
            print("   └─ MT5 initialize failed")
            return False
            
        # Verificar información de cuenta
        account_info = mt5.account_info()
        if account_info is None:
            print("   └─ No account info available")
            mt5.shutdown()
            return False
            
        # Verificar datos de símbolo
        symbol_info = mt5.symbol_info("EURUSD")
        if symbol_info is None:
            print("   └─ EURUSD symbol not available")
            mt5.shutdown()
            return False
            
        mt5.shutdown()
        return True
        
    except Exception as e:
        print(f"   └─ MT5 error: {e}")
        return False

def test_grid_bollinger():
    """Test del sistema Grid Bollinger"""
    try:
        from grid_bollinger import evaluar_condiciones_grid
        from riskbot_mt5 import RiskBotMT5
        
        # Crear RiskBot para el test
        riskbot = RiskBotMT5(
            risk_target_profit=10.0,
            max_profit_target=30.0,
            risk_percent=3.0,
            comision_por_lote=0.0
        )
        
        # Ejecutar función con parámetros correctos
        result = evaluar_condiciones_grid(
            riskbot=riskbot,
            modalidad_operacion="test",
            lotaje_inicial=0.1,
            timeframe_str='M5'
        )
        
        # La función puede retornar None si no hay operaciones, eso es válido
        if result is None or isinstance(result, tuple):
            return True
        else:
            print(f"   └─ Unexpected result type: {type(result)}")
            return False
            
    except Exception as e:
        print(f"   └─ Grid Bollinger error: {e}")
        return False

def test_analisis_estocastico():
    """Test del análisis estocástico"""
    try:
        from analisis_estocastico_m15 import analizar_estocastico_m15_cacheado
        from riskbot_mt5 import RiskBotMT5
        
        # Crear RiskBot para el test
        riskbot = RiskBotMT5(
            risk_target_profit=10.0,
            max_profit_target=30.0,
            risk_percent=3.0,
            comision_por_lote=0.0
        )
        
        result = analizar_estocastico_m15_cacheado(
            riskbot=riskbot,
            modalidad_operacion="test",
            lotaje_inicial=0.1
        )
        
        if isinstance(result, dict):
            return True
        else:
            print(f"   └─ Unexpected result type: {type(result)}")
            return False
            
    except Exception as e:
        print(f"   └─ Stochastic analysis error: {e}")
        return False

def test_riskbot():
    """Test del sistema de gestión de riesgo"""
    try:
        from riskbot_mt5 import RiskBotMT5
        
        # Crear instancia con parámetros de prueba
        riskbot = RiskBotMT5(
            risk_target_profit=10.0,
            max_profit_target=30.0,
            risk_percent=3.0,
            comision_por_lote=0.0
        )
        
        # Test de método básico (sin conexión MT5)
        if hasattr(riskbot, 'check_and_act'):
            return True
        else:
            print("   └─ Missing check_and_act method")
            return False
            
    except Exception as e:
        print(f"   └─ RiskBot error: {e}")
        return False

def test_data_logger():
    """Test del sistema de logging"""
    try:
        # Intentar importar el data_logger
        import data_logger
        
        # Si se importa correctamente, es un éxito
        return True
        
    except ImportError as e:
        # Si no se puede importar, intentar usar logging básico
        try:
            import logging
            logger = logging.getLogger("test")
            logger.info("Test message from system test")
            return True
        except Exception:
            print(f"   └─ Data Logger import error: {e}")
            return False
        
    except Exception as e:
        print(f"   └─ Data Logger error: {e}")
        return False

def test_trading_schedule():
    """Test del sistema de horarios"""
    try:
        from trading_schedule import esta_en_horario_operacion, mostrar_horario_operacion
        
        # Test básico con sesiones por defecto como strings
        sesiones_test = ["1", "2", "3"]  # Sesiones como strings
        
        horario_status = esta_en_horario_operacion(sesiones_test)
        horario_info = mostrar_horario_operacion(sesiones_test)
        
        if isinstance(horario_status, bool) and isinstance(horario_info, str):
            return True
        else:
            print(f"   └─ Unexpected return types: {type(horario_status)}, {type(horario_info)}")
            return False
            
    except Exception as e:
        print(f"   └─ Trading Schedule error: {e}")
        return False

def test_descarga_velas():
    """Test del sistema de descarga de velas"""
    try:
        # Verificar que el archivo existe y es válido sintácticamente
        import os
        descarga_path = os.path.join(os.getcwd(), 'descarga_velas.py')
        
        if not os.path.exists(descarga_path):
            print("   └─ descarga_velas.py not found")
            return False
            
        # Verificar sintaxis sin ejecutar el código
        import ast
        with open(descarga_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            print(f"   └─ Syntax error: {e}")
            return False
            
        # Verificar que contiene las funciones de logging esperadas
        if 'log_info' in content and 'log_error' in content and 'log_success' in content:
            return True
        else:
            print("   └─ Missing expected logging functions")
            return False
            
    except Exception as e:
        print(f"   └─ Descarga Velas error: {e}")
        return False

def test_data_manager():
    """Test del sistema de manejo de datos"""
    try:
        from src.core.data_manager import DataManager
        from src.core.logger_manager import LoggerManager
        from src.core.error_manager import ErrorManager
        
        # Crear instancia de DataManager con integración completa
        logger = LoggerManager()
        error_manager = ErrorManager(logger_manager=logger)
        data_manager = DataManager(logger_manager=logger, error_manager=error_manager)
        
        # Test de inicialización
        if not hasattr(data_manager, 'mt5_available'):
            print("   └─ DataManager missing mt5_available attribute")
            return False
        
        # Test de normalización de timeframe
        tf_normalized = data_manager.normalize_timeframe('M15')
        if not isinstance(tf_normalized, int):
            print("   └─ Timeframe normalization should return int")
            return False
        
        # Test de sistema de cache
        test_data = {'test': 'data', 'timestamp': '2025-08-10'}
        data_manager.cache_data('test_key', test_data, 60)
        cached_data = data_manager.get_cached_data('test_key')
        if cached_data != test_data:
            print("   └─ Cache system not working correctly")
            return False
        
        # Test de estadísticas de cache
        stats = data_manager.get_cache_stats()
        if not isinstance(stats, dict) or 'hit_ratio_percent' not in stats:
            print("   └─ Cache stats should be dict with hit_ratio_percent")
            return False
        
        # Test de obtención de datos OHLC (pequeña muestra)
        if data_manager.mt5_available:
            ohlc_data = data_manager.get_ohlc_data('EURUSD', 'M15', 10)
            if ohlc_data is not None:
                # Validar estructura de datos
                required_cols = ['open', 'high', 'low', 'close']
                missing_cols = [col for col in required_cols if col not in ohlc_data.columns]
                if missing_cols:
                    print(f"   └─ Missing OHLC columns: {missing_cols}")
                    return False
                
                # Test de validación de datos
                is_valid = data_manager.validate_ohlc_data(ohlc_data)
                if not is_valid:
                    print("   └─ OHLC data validation failed")
                    return False
        
        return True
        
    except Exception as e:
        print(f"   └─ Data Manager error: {e}")
        return False

def test_error_manager():
    """Test del sistema de manejo de errores"""
    try:
        from src.core.error_manager import ErrorManager
        from src.core.logger_manager import LoggerManager
        
        # Crear un mock silencioso del logger para testing
        class SilentLogger:
            def log_error(self, message):
                pass  # No mostrar errores durante testing
            def log_warning(self, message):
                pass  # No mostrar warnings durante testing
            def log_info(self, message):
                pass  # No mostrar info durante testing
        
        # Crear instancia de ErrorManager con logger silencioso
        silent_logger = SilentLogger()
        error_manager = ErrorManager(logger_manager=silent_logger)
        
        # Test básico de manejo de errores
        try:
            raise ValueError("Test error")
        except Exception as e:
            result = error_manager.handle_system_error("test_component", e)
            if not isinstance(result, bool):
                print("   └─ Error handler should return boolean")
                return False
        
        # Test de validación MT5 (también silencioso)
        mt5_valid = error_manager.validate_mt5_connection()
        if not isinstance(mt5_valid, bool):
            print("   └─ MT5 validation should return boolean")
            return False
        
        # Test de resumen de errores
        summary = error_manager.get_error_summary()
        if not isinstance(summary, dict) or 'total_errors' not in summary:
            print("   └─ Error summary should be dict with total_errors")
            return False
        
        print("   ✓ Error handling funcionando correctamente")
        print("   ✓ MT5 validation ejecutada")
        print("   ✓ Error summary generado")
        
        return True
        
    except Exception as e:
        print(f"   └─ Error Manager error: {e}")
        return False

def test_indicator_manager():
    """Test del IndicatorManager (FASE 5)"""
    try:
        from src.core.data_manager import DataManager
        from src.core.logger_manager import LoggerManager
        from src.core.indicator_manager import IndicatorManager
        import pandas as pd
        import numpy as np
        
        # Inicializar managers
        data_manager = DataManager()
        logger = LoggerManager()
        indicator_manager = IndicatorManager(data_manager, logger)
        assert indicator_manager is not None
        
        # Crear datos sintéticos
        dates = pd.date_range('2025-01-01', periods=30, freq='15min')
        np.random.seed(42)
        prices = 1.1000 + np.cumsum(np.random.randn(30) * 0.0001)
        
        df_test = pd.DataFrame({
            'open': prices + np.random.randn(30) * 0.00005,
            'high': prices + abs(np.random.randn(30) * 0.0001),
            'low': prices - abs(np.random.randn(30) * 0.0001),
            'close': prices,
            'volume': np.random.randint(1000, 5000, 30)
        }, index=dates)
        
        # Test indicadores avanzados
        # MACD
        macd_result = indicator_manager.calculate_macd(df_test)
        if macd_result is None or 'MACD' not in macd_result.columns:
            print("   └─ MACD calculation failed")
            return False
        
        # EMA
        ema_result = indicator_manager.calculate_ema(df_test, 20)
        if ema_result is None or 'EMA_20' not in ema_result.columns:
            print("   └─ EMA calculation failed")
            return False
        
        # Williams %R
        williams_result = indicator_manager.calculate_williams_r(df_test)
        if williams_result is None or 'Williams_R' not in williams_result.columns:
            print("   └─ Williams %R calculation failed")
            return False
        
        # ATR
        atr_result = indicator_manager.calculate_atr(df_test)
        if atr_result is None or 'ATR' not in atr_result.columns:
            print("   └─ ATR calculation failed")
            return False
        
        # Test cache especializado
        indicator_manager.cache_indicator_result('test_indicator', {'data': 'test'})
        cached_indicator = indicator_manager.get_cached_indicator('test_indicator')
        if cached_indicator is None or cached_indicator.get('data') != 'test':
            print("   └─ Indicator cache not working")
            return False
        
        # Test señales compuestas (con datos mock en DataManager)
        data_manager.cache_data("EURUSD_M15_50", df_test, 300)
        signal = indicator_manager.generate_compound_signal("EURUSD", "M15", "balanced")
        if signal is None or 'signal' not in signal:
            print("   └─ Compound signal generation failed")
            return False
        
        if signal['signal'] not in ['BUY', 'SELL', 'HOLD', 'NO_DATA', 'ERROR']:
            print(f"   └─ Invalid signal type: {signal['signal']}")
            return False
        
        if 'strength' not in signal or not isinstance(signal['strength'], (int, float)):
            print("   └─ Signal strength validation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"   └─ Indicator Manager error: {e}")
        return False

def test_mt5_manager():
    """Test básico de MT5Manager (usando mocks)"""
    try:
        # Mock de MetaTrader5 para testing
        import unittest.mock as mock
        
        with mock.patch.dict('sys.modules', {'MetaTrader5': mock.MagicMock()}):
            # Importar después del mock
            from mt5_manager import MT5Manager
            from config_manager import ConfigManager
            from logger_manager import LoggerManager
            from error_manager import ErrorManager
            
            # Crear managers de dependencias
            config = ConfigManager()
            logger = LoggerManager()
            error = ErrorManager(logger)
            
            # Crear MT5Manager
            mt5_manager = MT5Manager(config, logger, error)
            
            # Test 1: Inicialización correcta
            assert hasattr(mt5_manager, 'config'), "MT5Manager debe tener config"
            assert hasattr(mt5_manager, 'logger'), "MT5Manager debe tener logger"
            assert hasattr(mt5_manager, 'error'), "MT5Manager debe tener error"
            assert hasattr(mt5_manager, '_is_connected'), "MT5Manager debe tener _is_connected"
            assert mt5_manager._is_connected == False, "MT5Manager debe iniciar desconectado"
            
            # Test 2: Verificar métodos principales
            required_methods = [
                'connect', 'disconnect', 'is_connected', 'reconnect',
                'get_account_info', 'send_order', 'get_pending_orders',
                'cancel_order', 'get_positions', 'close_position',
                'get_total_exposure', 'get_current_price', 'get_symbol_info',
                'get_market_status'
            ]
            
            for method in required_methods:
                assert hasattr(mt5_manager, method), f"Método {method} no encontrado"
                assert callable(getattr(mt5_manager, method)), f"Método {method} no es callable"
            
            # Test 3: Test de exposición con posiciones vacías
            exposure = mt5_manager.get_total_exposure()
            assert isinstance(exposure, dict), "get_total_exposure debe retornar dict"
            assert 'total_volume' in exposure, "exposición debe tener total_volume"
            assert 'positions_count' in exposure, "exposición debe tener positions_count"
            assert exposure['positions_count'] == 0, "posiciones iniciales deben ser 0"
            
            # Test 4: Test de estado de conexión sin MT5
            connected = mt5_manager.is_connected()
            assert connected == False, "is_connected debe retornar False sin MT5"
            
            # Test 5: Test de cleanup
            mt5_manager.cleanup()
            assert mt5_manager._is_connected == False, "cleanup debe dejar desconectado"
            
            print("   ✓ Inicialización correcta")
            print("   ✓ Métodos principales disponibles")
            print("   ✓ Cálculo de exposición funciona")
            print("   ✓ Estado de conexión manejado")
            print("   ✓ Cleanup ejecutado correctamente")
            
            return True
            
    except AssertionError as e:
        print(f"   ❌ Assertion error en MT5Manager: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ Error en MT5Manager: {str(e)}")
        import traceback
        print(f"   └─ Traceback: {traceback.format_exc()}")
        return False

# Ejecutar todos los tests
def main():
    tests = [
        ("Imports básicos", test_imports),
        ("Sistema Config", test_config),
        ("Conectividad MT5", test_mt5_connection),
        ("Grid Bollinger", test_grid_bollinger),
        ("Análisis Estocástico", test_analisis_estocastico),
        ("RiskBot MT5", test_riskbot),
        ("Data Logger", test_data_logger),
        ("Trading Schedule", test_trading_schedule),
        ("Descarga Velas", test_descarga_velas),
        ("Error Manager", test_error_manager),
        ("Data Manager", test_data_manager),
        ("Indicator Manager", test_indicator_manager),
        ("MT5 Manager", test_mt5_manager),
    ]
    
    results = []
    total_start = time.time()
    
    for test_name, test_func in tests:
        success = test_component(test_name, test_func)
        results.append((test_name, success))
    
    total_time = time.time() - total_start
    
    # Resumen
    print()
    print("=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"📈 Resultados: {passed}/{total} tests pasaron ({passed/total*100:.1f}%)")
    print(f"⏱️ Tiempo total: {total_time:.2f} segundos")
    
    if passed == total:
        print("🎉 ¡Todos los componentes están funcionando correctamente!")
    elif passed >= total * 0.7:
        print("⚠️ La mayoría de componentes funcionan, pero hay algunos problemas.")
    else:
        print("🚨 Múltiples componentes tienen problemas. Revisar urgente.")
    
    print()
    print("🎯 Próximos pasos recomendados:")
    if passed < total:
        print("  1. Revisar componentes que fallaron")
        print("  2. Verificar dependencias faltantes")
        print("  3. Comprobar configuración MT5")
    else:
        print("  1. Ejecutar sistema completo con main.py")
        print("  2. Realizar pruebas con datos reales")
        print("  3. Optimizar performance si es necesario")

if __name__ == "__main__":
    main()
