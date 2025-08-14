"""
🧪 TEST SCRIPT - ADVANCED POSITION SIZER
=========================================
Script de testing para el sistema de cálculo de posición avanzado

Author: Trading Grid System
Date: 2025-08-13
"""

import sys
import os
from datetime import datetime, timezone

# Agregar el directorio raíz al path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Importar directamente el código del AdvancedPositionSizer
exec(open(os.path.join(project_root, 'src', 'analysis', 'piso_4', 'advanced_position_sizer.py')).read())

class MockLoggerManager:
    """Mock del LoggerManager para testing sin dependencias"""
    
    def get_logger(self, name):
        return MockLogger()

class MockLogger:
    """Mock del Logger para testing"""
    
    def info(self, msg): print(f"ℹ️ {msg}")
    def error(self, msg): print(f"❌ {msg}")
    def warning(self, msg): print(f"⚠️ {msg}")

def test_advanced_position_sizer():
    """Test del AdvancedPositionSizer con múltiples escenarios"""
    
    print("🎯 TESTING ADVANCED POSITION SIZER")
    print("=" * 50)
    
    # Usar mock logger
    logger_manager = MockLoggerManager()
    
    sizer = AdvancedPositionSizer(logger_manager)
    
    # ESCENARIO 1: Trade de alta calidad en Londres
    print("\n📊 ESCENARIO 1: FVG Premium en Londres")
    print("-" * 40)
    
    fvg_data = {
        'quality': 'PREMIUM',
        'size_pips': 30
    }
    
    session_data = {
        'active_session': 'LONDON',
        'is_overlap': False
    }
    
    cycle_data = {
        'trades_executed': 0,
        'daily_pnl_percentage': 0
    }
    
    account_data = {
        'equity': 10000,
        'free_margin': 8000,
        'margin_per_lot': 1000
    }
    
    market_data = {
        'volatility_level': 'NORMAL',
        'pip_value': 10
    }
    
    result1 = sizer.calculate_position_size(
        fvg_data, session_data, cycle_data, account_data, market_data
    )
    
    print(f"Position Size: {result1['position_size']:.2f} lotes")
    print(f"Risk Amount: ${result1['risk_amount']:.2f}")
    print(f"Risk %: {result1['risk_percentage']:.2f}%")
    print(f"Stop Loss: {result1['stop_loss_pips']:.1f} pips")
    print(f"Total Multiplier: {result1['multipliers']['total']:.2f}")
    
    # Análisis del escenario 1
    analysis1 = sizer.get_position_analysis(result1)
    print(f"Categoría: {analysis1['size_category']}")
    print(f"Nivel Riesgo: {analysis1['risk_level']}")
    print(f"Factor Dominante: {analysis1['dominant_factor']}")
    print(f"Score: {analysis1['optimization_score']}/100")
    
    # ESCENARIO 2: Trade de baja calidad fuera de horas
    print("\n📊 ESCENARIO 2: FVG Pobre fuera de horas")
    print("-" * 40)
    
    fvg_data2 = {
        'quality': 'POOR',
        'size_pips': 15
    }
    
    session_data2 = {
        'active_session': 'OFF_HOURS',
        'is_overlap': False
    }
    
    cycle_data2 = {
        'trades_executed': 0,
        'daily_pnl_percentage': 0
    }
    
    result2 = sizer.calculate_position_size(
        fvg_data2, session_data2, cycle_data2, account_data, market_data
    )
    
    print(f"Position Size: {result2['position_size']:.2f} lotes")
    print(f"Risk %: {result2['risk_percentage']:.2f}%")
    print(f"Total Multiplier: {result2['multipliers']['total']:.2f}")
    
    # ESCENARIO 3: Tercer trade del día cerca del límite
    print("\n📊 ESCENARIO 3: 3er trade cerca del límite")
    print("-" * 40)
    
    fvg_data3 = {
        'quality': 'HIGH',
        'size_pips': 25
    }
    
    session_data3 = {
        'active_session': 'NY',
        'is_overlap': False
    }
    
    cycle_data3 = {
        'trades_executed': 2,
        'daily_pnl_percentage': -1.5  # Cerca del límite -2%
    }
    
    result3 = sizer.calculate_position_size(
        fvg_data3, session_data3, cycle_data3, account_data, market_data
    )
    
    print(f"Position Size: {result3['position_size']:.2f} lotes")
    print(f"Risk %: {result3['risk_percentage']:.2f}%")
    print(f"Total Multiplier: {result3['multipliers']['total']:.2f}")
    
    analysis3 = sizer.get_position_analysis(result3)
    print(f"Recomendaciones: {analysis3['recommendations']}")
    
    # ESCENARIO 4: Overlap de sesiones con alta volatilidad
    print("\n📊 ESCENARIO 4: Overlap + Alta volatilidad")
    print("-" * 40)
    
    fvg_data4 = {
        'quality': 'HIGH',
        'size_pips': 35
    }
    
    session_data4 = {
        'active_session': 'LONDON',
        'is_overlap': True
    }
    
    cycle_data4 = {
        'trades_executed': 1,
        'daily_pnl_percentage': 1.2
    }
    
    market_data4 = {
        'volatility_level': 'HIGH',
        'pip_value': 10
    }
    
    result4 = sizer.calculate_position_size(
        fvg_data4, session_data4, cycle_data4, account_data, market_data4
    )
    
    print(f"Position Size: {result4['position_size']:.2f} lotes")
    print(f"Risk %: {result4['risk_percentage']:.2f}%")
    print(f"Multiplicadores:")
    for key, value in result4['multipliers'].items():
        if key != 'total':
            print(f"  {key.capitalize()}: {value:.2f}")
    print(f"  Total: {result4['multipliers']['total']:.2f}")
    
    # RESUMEN COMPARATIVO
    print("\n📈 RESUMEN COMPARATIVO")
    print("=" * 50)
    
    scenarios = [
        ("Premium Londres", result1),
        ("Pobre Off-Hours", result2),
        ("3er trade límite", result3),
        ("Overlap volátil", result4)
    ]
    
    print(f"{'Escenario':<18} {'Lotes':<8} {'Risk%':<8} {'Mult':<8}")
    print("-" * 50)
    
    for name, result in scenarios:
        print(f"{name:<18} {result['position_size']:<8.2f} "
              f"{result['risk_percentage']:<8.2f} "
              f"{result['multipliers']['total']:<8.2f}")
    
    print("\n✅ Testing del AdvancedPositionSizer completado")
    
    # Verificar que el sistema funciona correctamente
    assert result1['position_size'] > result2['position_size'], "Premium debe ser > Pobre"
    assert result3['position_size'] < result1['position_size'], "3er trade debe ser conservador"
    assert all(r['risk_percentage'] <= 2.5 for _, r in scenarios), "Risk nunca debe exceder 2.5%"
    
    print("🎯 Todas las validaciones pasaron correctamente")

def test_edge_cases():
    """Test de casos extremos y situaciones límite"""
    
    print("\n🔬 TESTING CASOS EXTREMOS")
    print("=" * 50)
    
    logger_manager = MockLoggerManager()
    sizer = AdvancedPositionSizer(logger_manager)
    
    # Caso 1: Cuenta muy pequeña
    print("\n💰 Caso 1: Cuenta micro ($100)")
    
    account_small = {
        'equity': 100,
        'free_margin': 80,
        'margin_per_lot': 1000
    }
    
    fvg_normal = {'quality': 'MEDIUM', 'size_pips': 20}
    session_normal = {'active_session': 'LONDON', 'is_overlap': False}
    cycle_normal = {'trades_executed': 0, 'daily_pnl_percentage': 0}
    market_normal = {'volatility_level': 'NORMAL', 'pip_value': 10}
    
    result_small = sizer.calculate_position_size(
        fvg_normal, session_normal, cycle_normal, account_small, market_normal
    )
    
    print(f"Position: {result_small['position_size']:.2f} lotes")
    print(f"Risk: {result_small['risk_percentage']:.2f}%")
    
    # Caso 2: Datos faltantes (modo emergencia)
    print("\n🚨 Caso 2: Modo emergencia")
    
    try:
        # Simular datos incompletos que causan error
        result_emergency = sizer._get_emergency_position_size(account_small)
        print(f"Emergency Position: {result_emergency['position_size']:.2f} lotes")
        print(f"Emergency Risk: {result_emergency['risk_percentage']:.2f}%")
        print(f"Emergency Mode: {result_emergency.get('emergency_mode', False)}")
    except Exception as e:
        print(f"Error manejado: {e}")
    
    print("✅ Testing de casos extremos completado")

if __name__ == "__main__":
    # Ejecutar todos los tests
    test_advanced_position_sizer()
    test_edge_cases()
    
    print(f"\n🎯 ADVANCED POSITION SIZER - TESTING COMPLETADO")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
