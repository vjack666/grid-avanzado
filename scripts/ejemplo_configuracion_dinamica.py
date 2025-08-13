#!/usr/bin/env python3
"""
📚 EJEMPLO DE USO - CONFIGURACIÓN DINÁMICA
==========================================

Este archivo muestra cómo usar ConfigManager para eliminar hardcoding.

Autor: GitHub Copilot
Fecha: Agosto 13, 2025
"""

from src.core.config_manager import ConfigManager

# Configuración dinámica anti-hardcoding
try:
    _config_manager = ConfigManager()
except:
    _config_manager = None

def ejemplo_configuracion_dinamica():
    """Ejemplo de cómo usar configuración dinámica"""
    
    # ❌ HARDCODEADO (MALO):
    # symbol = 'EURUSD'
    # timeframe = 'H1'
    # session = 'LONDON'
    
    # ✅ DINÁMICO (BUENO):
    symbol = _config_manager.get_primary_symbol() if _config_manager else 'EURUSD'
    timeframe = _config_manager.get_default_timeframe() if _config_manager else 'H1'
    session = _config_manager.get_current_session() if _config_manager else 'LONDON'
    
    print(f"🎯 Símbolo: {symbol}")
    print(f"⏰ Timeframe: {timeframe}")
    print(f"🌍 Sesión: {session}")
    
    # Obtener múltiples valores
    all_symbols = _config_manager.get_symbols() if _config_manager else ['EURUSD']
    all_timeframes = _config_manager.get_timeframes() if _config_manager else ['H1']
    
    print(f"📊 Símbolos disponibles: {all_symbols}")
    print(f"⏱️  Timeframes disponibles: {all_timeframes}")
    
    # Detección automática de tendencia
    if _config_manager:
        trend_value = 0.5  # Esto vendría del análisis real
        market_trend = _config_manager.detect_market_trend(trend_value)
        print(f"📈 Tendencia detectada: {market_trend}")
    
    # Configuraciones específicas
    fvg_config = _config_manager.get_fvg_config() if _config_manager else {}
    alerts_config = _config_manager.get_alerts_config() if _config_manager else {}
    
    print(f"🎯 Config FVG: {len(fvg_config)} parámetros")
    print(f"🚨 Config Alertas: {len(alerts_config)} parámetros")

if __name__ == "__main__":
    ejemplo_configuracion_dinamica()
