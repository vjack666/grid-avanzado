

import sys
import os

from datetime import datetime
import random

    
        from src.core.live_trading.enhanced_order_executor import EnhancedOrderExecutor
        from src.utils.unified_logger import UnifiedLogger
        
        
        
        
        
        
        
            
        


    
        from src.core.ml_foundation.fvg_database_manager import FVGDatabaseManager
        
        
            
            
        
        
            
            
            


    
        from trading_grid_main import TradingGridMain
        
        
        
        
        
            
                
            
        import traceback


    
        from trading_grid_main import TradingGridMain
        
        
        
            
            
            
        import traceback


    
    
    
    
    
    
    
    
    



from src.core.config_manager import ConfigManager

# Configuración dinámica anti-hardcoding
try:
    _config_manager = ConfigManager()
except:
    _config_manager = None

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 TEST ENHANCED ORDER SYSTEM
Test del sistema completo de órdenes mejoradas con FVG
Este script valida:
1. Enhanced Order Executor
2. Integración FVG → Órdenes límite
3. ML Database storage
4. Sistema completo end-to-end
"""
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def test_enhanced_order_executor():
    """Test del Enhanced Order Executor independiente"""
    print("🎯 Iniciando test Enhanced Order Executor...")
    try:
        # Configurar logger
        logger = UnifiedLogger()
        # Crear executor
        executor = EnhancedOrderExecutor(logger)
        # Crear FVG de prueba
        class MockFVGData:
            def __init__(self):
                self.symbol = _config_manager.get_primary_symbol() if _config_manager else 'EURUSD'
                self.timeframe = _config_manager.get_default_timeframe() if _config_manager else 'H1'
                self.type = 'bullish'
                self.gap_high = 1.0950
                self.gap_low = 1.0940
                self.gap_size = 0.0010
                self.quality_score = 0.85
                self.formation_time = datetime.now()
        fvg_data = MockFVGData()
        # Contexto de mercado
        market_context = {
            'trend': 'BULLISH',
            'volatility': 'NORMAL',
            'session': _config_manager.get_current_session() if _config_manager else 'LONDON',
            'volume_profile': 'HIGH'
        }
        # Procesar señal FVG
        result = executor.process_fvg_signal(fvg_data, market_context)
        if result:
            print("✅ Enhanced Order Executor: Test EXITOSO")
            print(f"   - FVG procesado: {fvg_data.symbol} {fvg_data.type}")
            print(f"   - Gap: {fvg_data.gap_low} - {fvg_data.gap_high}")
            print(f"   - Calidad: {fvg_data.quality_score}")
        else:
            print("❌ Enhanced Order Executor: Test FALLIDO")
        return result
    except Exception as e:
        print(f"❌ Error en test Enhanced Order Executor: {e}")
        return False
def test_ml_database_integration():
    """Test de integración con ML Database"""
    print("\n🎯 Iniciando test ML Database...")
    try:
        # Crear manager
        db_manager = FVGDatabaseManager()
        # Datos de prueba
        fvg_record = {
            'timestamp_creation': datetime.now(),
            'symbol': _config_manager.get_primary_symbol() if _config_manager else 'EURUSD',
            'timeframe': _config_manager.get_default_timeframe() if _config_manager else 'H1',
            'gap_type': 'BULLISH',  # Usar mayúsculas para coincidir con constraint
            'gap_high': 1.0950,
            'gap_low': 1.0940,
            'gap_size_pips': 10.0,
            'quality_score': 0.85,
            # Velas
            'vela1_open': 1.0935, 'vela1_high': 1.0945, 'vela1_low': 1.0930, 'vela1_close': 1.0940, 'vela1_volume': 1000,
            'vela2_open': 1.0940, 'vela2_high': 1.0955, 'vela2_low': 1.0938, 'vela2_close': 1.0952, 'vela2_volume': 1200,
            'vela3_open': 1.0952, 'vela3_high': 1.0960, 'vela3_low': 1.0948, 'vela3_close': 1.0955, 'vela3_volume': 800,
            'current_price': 1.0948,
            'distance_to_gap': 0.0002
        }
        # Insertar registro
        fvg_id = db_manager.insert_fvg(fvg_record)
        if fvg_id:
            print("✅ ML Database: Test EXITOSO")
            print(f"   - FVG almacenado con ID: {fvg_id}")
            # Probar consulta usando método que existe
            stats = db_manager.get_database_stats()
            if stats and stats.get('total_fvgs', 0) > 0:
                print(f"   - Consulta exitosa: {stats['total_fvgs']} FVG(s) en total")
            return True
        else:
            print("❌ ML Database: Test FALLIDO")
            return False
    except Exception as e:
        print(f"❌ Error en test ML Database: {e}")
        return False
def test_main_system_integration():
    """Test de integración completa del sistema principal"""
    print("\n🎯 Iniciando test Sistema Principal...")
    try:
        # Crear sistema
        system = TradingGridMain()
        # Validar que el Enhanced Order Executor esté configurado
        if hasattr(system, 'enhanced_order_executor') and system.enhanced_order_executor:
            print("✅ Enhanced Order Executor integrado en sistema principal")
        else:
            print("⚠️  Enhanced Order Executor no encontrado en sistema principal")
            return False
        # Validar que el ML Database esté configurado
        if hasattr(system, 'fvg_db_manager') and system.fvg_db_manager:
            print("✅ ML Database integrado en sistema principal")
        else:
            print("⚠️  ML Database no encontrado en sistema principal")
            return False
        # Probar integración FVG
        integration_result = system.integrate_fvg_ml_system()
        if integration_result:
            print("✅ Integración FVG-ML: Test EXITOSO")
            # Validar callback
            if hasattr(system, '_fvg_trading_callback'):
                print("✅ Callback Enhanced Order Executor configurado")
            else:
                print("⚠️  Callback no configurado")
            return True
        else:
            print("❌ Integración FVG-ML: Test FALLIDO")
            return False
    except Exception as e:
        print(f"❌ Error en test Sistema Principal: {e}")
        traceback.print_exc()
        return False
def test_end_to_end_flow():
    """Test del flujo completo end-to-end"""
    print("\n🎯 Iniciando test End-to-End...")
    try:
        # Crear sistema completo
        system = TradingGridMain()
        # Configurar integración
        if not system.integrate_fvg_ml_system():
            print("❌ No se pudo configurar integración")
            return False
        # Simular detección de FVG
        if hasattr(system, '_fvg_trading_callback'):
            # Crear FVG de prueba
            class MockFVGData:
                def __init__(self):
                    self.symbol = _config_manager.get_primary_symbol() if _config_manager else 'EURUSD'
                    self.timeframe = _config_manager.get_default_timeframe() if _config_manager else 'H1'
                    self.type = 'bearish'
                    self.gap_high = 1.0930
                    self.gap_low = 1.0920
                    self.gap_size = 0.0010
                    self.quality_score = 0.75
                    self.formation_time = datetime.now()
            fvg_data = MockFVGData()
            # Ejecutar callback completo
            try:
                system._fvg_trading_callback(fvg_data)
                print("✅ Flujo End-to-End: Test EXITOSO")
                print(f"   - FVG {fvg_data.type} procesado completamente")
                print(f"   - Símbolo: {fvg_data.symbol}")
                print(f"   - Gap: {fvg_data.gap_low} - {fvg_data.gap_high}")
                return True
            except Exception as callback_error:
                print(f"❌ Error en callback: {callback_error}")
                return False
        else:
            print("❌ Callback no disponible")
            return False
    except Exception as e:
        print(f"❌ Error en test End-to-End: {e}")
        traceback.print_exc()
        return False
def main():
    """Ejecutar todos los tests"""
    print("=" * 60)
    print("🎯 VALIDACIÓN SISTEMA ENHANCED ORDER + FVG + ML")
    print("=" * 60)
    tests = [
        ("Enhanced Order Executor", test_enhanced_order_executor),
        ("ML Database", test_ml_database_integration),
        ("Sistema Principal", test_main_system_integration),
        ("End-to-End Flow", test_end_to_end_flow)
    ]
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 60)
    passed = 0
    total = len(results)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
        if result:
            passed += 1
    print(f"\nResultado: {passed}/{total} tests pasaron")
    if passed == total:
        print("🎉 ¡TODOS LOS TESTS PASARON! Sistema listo para producción.")
    else:
        print("⚠️  Algunos tests fallaron. Revisar logs para detalles.")
    return passed == total
if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)