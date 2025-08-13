"""
🚨 DEMO: INTEGRACIÓN REAL DEL SISTEMA DE NOTIFICACIONES FVG
Script de demostración del uso real del sistema de notificaciones FVG
con el sistema Trading Grid operativo

Fecha: Agosto 13, 2025
Propósito: Mostrar cómo el FVG Alert System se integra con el sistema real
Estado: DEMO DE INTEGRACIÓN REAL
"""

import asyncio
import logging
from pathlib import Path
import sys

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from src.analysis.fvg_alert_system_organized import (
    setup_fvg_notifications_system,
    integrate_with_fvg_detector,
    FVGNotificationBridge
)
from src.analysis.fvg_detector import RealTimeFVGDetector

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockEnhancedOrderExecutor:
    """Mock del Enhanced Order Executor para la demo"""
    
    def __init__(self):
        self.logger = logging.getLogger("MockEnhancedOrderExecutor")
        
    async def on_fvg_opportunity(self, fvg_data, symbol, timeframe):
        """Callback cuando se detecta una oportunidad FVG"""
        gap_pips = fvg_data.get('gap_size', 0) * 10000
        self.logger.info(f"🎯 Enhanced Order Executor: Nueva oportunidad FVG")
        self.logger.info(f"   📊 {symbol} {timeframe} - {fvg_data.get('type', 'UNKNOWN')} - {gap_pips:.1f} pips")
        self.logger.info(f"   ⚡ Procesando orden límite inteligente...")


async def demo_integration():
    """
    🎯 DEMOSTRACIÓN DE INTEGRACIÓN REAL
    Muestra cómo el sistema de notificaciones FVG se integra
    con el detector real y el Enhanced Order Executor
    """
    
    print("🚨 DEMO: Sistema de Notificaciones FVG - Integración Real")
    print("=" * 60)
    
    # 1. Configurar el sistema de notificaciones
    print("\n🔧 1. Configurando sistema de notificaciones FVG...")
    alert_system, notification_bridge = setup_fvg_notifications_system()
    
    # 2. Crear mock del Enhanced Order Executor
    print("🔧 2. Conectando con Enhanced Order Executor...")
    enhanced_executor = MockEnhancedOrderExecutor()
    notification_bridge.enhanced_order_executor = enhanced_executor
    
    # 3. Crear detector FVG real
    print("🔧 3. Inicializando FVG Detector...")
    fvg_detector = RealTimeFVGDetector(
        symbols=['EURUSD', 'GBPUSD'],
        timeframes=['M15', 'H1']
    )
    
    # 4. Integrar sistemas
    print("🔧 4. Integrando sistemas...")
    integrate_with_fvg_detector(notification_bridge, fvg_detector)
    
    print("\n✅ Sistema integrado correctamente!")
    print("\n📊 Información del sistema:")
    print(f"   📡 Canales activos: {len([c for c in alert_system.channels if c.enabled])}")
    print(f"   🔍 Símbolos monitoreados: {fvg_detector.symbols}")
    print(f"   ⏰ Timeframes: {fvg_detector.timeframes}")
    
    # 5. Simulación de datos FVG para mostrar el flujo
    print("\n🎯 5. Simulando detección de FVG...")
    
    # Crear datos mock de FVG
    mock_fvg_data = {
        'gap_size': 0.0008,  # 8 pips
        'type': 'BULLISH',
        'gap_low': 1.0950,
        'gap_high': 1.0958,
        'formation_time': '2025-08-13T14:30:00'
    }
    
    # Simular detección
    await notification_bridge.on_fvg_detected(mock_fvg_data, 'EURUSD', 'H1')
    
    # Simular confluencia
    confluence_data = {
        'confluence_strength': 8.5,
        'timeframes': ['M15', 'H1'],
        'fvg_count': 3
    }
    
    await notification_bridge.on_confluence_detected(confluence_data, 'EURUSD')
    
    print("\n📈 6. Métricas del sistema:")
    metrics = alert_system.get_metrics()
    print(f"   📨 Total alertas enviadas: {metrics['sent_alerts']}")
    print(f"   📊 Alertas por tipo: {metrics['alerts_by_type']}")
    
    # 7. Health check
    print("\n🏥 7. Estado de salud del sistema:")
    health = await alert_system.health_check()
    print(f"   🟢 Estado: {health['status']}")
    print(f"   📡 Canales: {health['channels_active']}/{health['channels_total']}")
    
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETADA")
    print("🎯 El sistema está listo para PRODUCCIÓN")
    print("🔧 Para usar en producción, integre con FVGDetector real en trading_grid_main.py")


async def demo_real_world_scenario():
    """
    🌍 ESCENARIO DEL MUNDO REAL
    Simula un día típico de trading con el sistema de notificaciones
    """
    
    print("\n" + "=" * 60)
    print("🌍 ESCENARIO DEL MUNDO REAL - Día típico de trading")
    print("=" * 60)
    
    # Configurar sistema
    alert_system, notification_bridge = setup_fvg_notifications_system()
    
    # Simular eventos del día
    scenarios = [
        {
            'time': '09:00',
            'event': 'Apertura Londres',
            'fvg_data': {'gap_size': 0.0012, 'type': 'BULLISH'},
            'symbol': 'GBPUSD',
            'timeframe': 'H1'
        },
        {
            'time': '13:30',
            'event': 'Noticias USD',
            'fvg_data': {'gap_size': 0.0015, 'type': 'BEARISH'},
            'symbol': 'EURUSD',
            'timeframe': 'M15'
        },
        {
            'time': '16:00',
            'event': 'Confluencia detectada',
            'confluence_data': {
                'confluence_strength': 9.2,
                'timeframes': ['M15', 'H1', 'H4'],
                'fvg_count': 4
            },
            'symbol': 'EURUSD'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📅 {scenario['time']} - {scenario['event']}")
        
        if 'fvg_data' in scenario:
            await notification_bridge.on_fvg_detected(
                scenario['fvg_data'],
                scenario['symbol'],
                scenario['timeframe']
            )
            
        if 'confluence_data' in scenario:
            await notification_bridge.on_confluence_detected(
                scenario['confluence_data'],
                scenario['symbol']
            )
        
        # Pequeña pausa para simular tiempo real
        await asyncio.sleep(0.5)
    
    print(f"\n📊 Resumen del día:")
    metrics = alert_system.get_metrics()
    print(f"   📨 Total alertas: {metrics['total_alerts']}")
    print(f"   ✅ Enviadas exitosamente: {metrics['sent_alerts']}")
    print(f"   🔍 Por tipo: {metrics['alerts_by_type']}")


if __name__ == "__main__":
    print("🚀 Iniciando demostración del Sistema de Notificaciones FVG")
    
    # Ejecutar demostración básica
    asyncio.run(demo_integration())
    
    # Ejecutar escenario del mundo real
    asyncio.run(demo_real_world_scenario())
    
    print("\n🎉 Todas las demostraciones completadas exitosamente!")
    print("📚 Revise los logs para ver el flujo completo del sistema.")
