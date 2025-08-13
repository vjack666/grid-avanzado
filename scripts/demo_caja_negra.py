


import sys
import os
from pathlib import Path


from core.logger_manager import LoggerManager, LogLevel

    
    
    
    
    
    
    
    
    
    
    
    
    


from src.core.config_manager import ConfigManager

# Configuración dinámica anti-hardcoding
try:
    _config_manager = ConfigManager()
except:
    _config_manager = None

"""
Demo del Sistema Caja Negra - Logger Manager Avanzado
======================================================
Demuestra el funcionamiento del nuevo sistema de logging categorizado
que funciona como "caja negra" del sistema Trading Grid.
Autor: GitHub Copilot
Fecha: Agosto 12, 2025
"""
# Agregar src al path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
def demo_sistema_caja_negra():
    """Demostrar todas las capacidades del sistema de caja negra"""
    print("🗃️ DEMO SISTEMA CAJA NEGRA TRADING GRID")
    print("=" * 50)
    # Inicializar caja negra
    logger = LoggerManager()
    # 1. Logs del sistema
    print("\n1️⃣ Logs del Sistema:")
    logger.log_system(LogLevel.INFO, "Sistema Trading Grid iniciado")
    logger.log_system(LogLevel.SUCCESS, "Configuración cargada correctamente")
    # 2. Logs de MT5
    print("\n2️⃣ Logs de MT5:")
    logger.log_mt5(LogLevel.INFO, "Intentando conexión a MT5", {
        "server": "FundedNext-Demo",
        "account": "12345"
    })
    logger.log_mt5(LogLevel.SUCCESS, "Conexión MT5 establecida", {
        "balance": 100000.0,
        "equity": 100000.0
    })
    # 3. Logs de Analytics
    print("\n3️⃣ Logs de Analytics:")
    logger.log_analytics(LogLevel.INFO, "Iniciando análisis de mercado", {
        "symbol": _config_manager.get_primary_symbol() if _config_manager else 'EURUSD',
        "timeframe": _config_manager.get_default_timeframe() if _config_manager else 'H1'
    })
    logger.log_analytics(LogLevel.SUCCESS, "Análisis completado", {
        "patterns_found": 3,
        "signals_generated": 1
    })
    # 4. Logs de FVG
    print("\n4️⃣ Logs de FVG:")
    logger.log_fvg(LogLevel.INFO, "Escaneando FVGs", {
        "timeframes": ["M5", "M15", _config_manager.get_default_timeframe() if _config_manager else 'H1'],
        "symbols": [_config_manager.get_primary_symbol() if _config_manager else 'EURUSD']
    })
    logger.log_fvg(LogLevel.SUCCESS, "FVG detectado", {
        "symbol": _config_manager.get_primary_symbol() if _config_manager else 'EURUSD',
        "timeframe": _config_manager.get_default_timeframe() if _config_manager else 'H1',
        "type": "bullish",
        "top": 1.0950,
        "bottom": 1.0930,
        "confidence": 0.85
    })
    # 5. Logs de Señales
    print("\n5️⃣ Logs de Señales:")
    logger.log_signal(LogLevel.SUCCESS, "Señal de entrada generada", {
        "symbol": _config_manager.get_primary_symbol() if _config_manager else 'EURUSD', 
        "direction": "LONG",
        "entry": 1.0945,
        "stop_loss": 1.0925,
        "take_profit": 1.0975,
        "confidence": 0.87
    })
    # 6. Logs de Trading
    print("\n6️⃣ Logs de Trading:")
    logger.log_trading(LogLevel.INFO, "Ejecutando orden", {
        "symbol": _config_manager.get_primary_symbol() if _config_manager else 'EURUSD',
        "volume": 0.1,
        "type": "BUY"
    })
    logger.log_trading(LogLevel.SUCCESS, "Orden ejecutada", {
        "ticket": 123456,
        "price": 1.0945,
        "profit": 0.0
    })
    # 7. Logs de Performance
    print("\n7️⃣ Logs de Performance:")
    logger.log_performance(LogLevel.INFO, "Medición de rendimiento", {
        "operation": "fvg_detection",
        "execution_time": 0.15,
        "memory_usage": "25MB"
    })
    # 8. Logs de Errores
    print("\n8️⃣ Logs de Errores:")
    logger.log_error("Error simulado de conexión", {
        "error_code": "MT5_CONNECTION_LOST",
        "retry_attempt": 1
    })
    # 9. Métodos de compatibilidad
    print("\n9️⃣ Métodos de Compatibilidad:")
    logger.log_info("Mensaje usando método de compatibilidad")
    logger.log_success("Éxito usando método de compatibilidad")
    logger.log_warning("Advertencia usando método de compatibilidad")
    # 10. Estadísticas de sesión
    print("\n🔟 Estadísticas de Sesión:")
    stats = logger.get_session_stats()
    print(f"Session ID: {stats['session_id']}")
    print(f"Logs creados: {stats['logs_created']}")
    print(f"Categorías usadas: {', '.join(stats['categories_used'])}")
    print(f"Tiempo activo: {stats['uptime']}")
    print("\n✅ Demo completado. Revisa la carpeta logs/ para ver todos los archivos generados.")
    print(f"📁 Logs guardados en: {project_root}/logs/")
if __name__ == "__main__":
    demo_sistema_caja_negra()