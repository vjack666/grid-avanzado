"""
🔍 INVESTIGADOR DE ERRORES MT5 - TRADING GRID
============================================

Script para investigar y diagnosticar errores de MT5, especialmente el error 10015.

Autor: GitHub Copilot
Fecha: Agosto 13, 2025
"""

# Códigos de error MT5 Trade Server
MT5_TRADE_RETCODES = {
    10004: "TRADE_RETCODE_REQUOTE - Requote",
    10006: "TRADE_RETCODE_REJECT - Request rejected",
    10007: "TRADE_RETCODE_CANCEL - Request canceled by trader",
    10008: "TRADE_RETCODE_PLACED - Order placed",
    10009: "TRADE_RETCODE_DONE - Request completed",
    10010: "TRADE_RETCODE_DONE_PARTIAL - Only part of the request was completed",
    10011: "TRADE_RETCODE_ERROR - Request processing error",
    10012: "TRADE_RETCODE_TIMEOUT - Request canceled by timeout",
    10013: "TRADE_RETCODE_INVALID - Invalid request",
    10014: "TRADE_RETCODE_INVALID_VOLUME - Invalid volume in the request",
    10015: "TRADE_RETCODE_INVALID_PRICE - Invalid price in the request",
    10016: "TRADE_RETCODE_INVALID_STOPS - Invalid stops in the request", 
    10017: "TRADE_RETCODE_TRADE_DISABLED - Trade is disabled",
    10018: "TRADE_RETCODE_MARKET_CLOSED - Market is closed",
    10019: "TRADE_RETCODE_NO_MONEY - There is not enough money to complete the request",
    10020: "TRADE_RETCODE_PRICE_CHANGED - Prices changed",
    10021: "TRADE_RETCODE_PRICE_OFF - There are no quotes to process the request",
    10022: "TRADE_RETCODE_INVALID_EXPIRATION - Invalid order expiration date in the request",
    10023: "TRADE_RETCODE_ORDER_CHANGED - Order state changed",
    10024: "TRADE_RETCODE_TOO_MANY_REQUESTS - Too frequent requests",
    10025: "TRADE_RETCODE_NO_CHANGES - No changes in request",
    10026: "TRADE_RETCODE_SERVER_DISABLES_AT - Autotrading disabled by server",
    10027: "TRADE_RETCODE_CLIENT_DISABLES_AT - Autotrading disabled by client terminal",
    10028: "TRADE_RETCODE_LOCKED - Request locked for processing",
    10029: "TRADE_RETCODE_FROZEN - Order or position frozen",
    10030: "TRADE_RETCODE_INVALID_FILL - Invalid order filling type",
    10031: "TRADE_RETCODE_CONNECTION - No connection with the trade server",
    10032: "TRADE_RETCODE_ONLY_REAL - Operation is allowed only for live accounts",
    10033: "TRADE_RETCODE_LIMIT_ORDERS - The number of pending orders has reached the limit",
    10034: "TRADE_RETCODE_LIMIT_VOLUME - The volume of orders and positions for the symbol has reached the limit",
    10035: "TRADE_RETCODE_INVALID_ORDER - Incorrect or prohibited order type",
    10036: "TRADE_RETCODE_POSITION_CLOSED - Position with the specified POSITION_IDENTIFIER has already been closed"
}

def analyze_error_10015():
    """Análisis específico del error 10015"""
    print("🔍 ANÁLISIS DEL ERROR 10015 - TRADE_RETCODE_INVALID_PRICE")
    print("=" * 70)
    print()
    print("📊 DESCRIPCIÓN:")
    print("   • Error: Invalid price in the request")
    print("   • Significado: El precio enviado a MT5 no es válido")
    print()
    print("🚨 CAUSAS POSIBLES:")
    print("   1. Precio no normalizado (decimales incorrectos)")
    print("   2. Precio fuera del rango permitido por el broker")
    print("   3. Precio no respeta el tick size del símbolo")
    print("   4. Precio de Stop Loss o Take Profit inválido")
    print("   5. Precio muy alejado del precio actual del mercado")
    print("   6. Símbolo no disponible o suspendido")
    print("   7. Horario de trading cerrado para el símbolo")
    print()
    print("🛠️ SOLUCIONES RECOMENDADAS:")
    print("   1. Verificar symbol_info().digits para normalización correcta")
    print("   2. Validar que price esté dentro de symbol_info().bid/ask ±10%")
    print("   3. Verificar symbol_info().trade_tick_value y tick_size")
    print("   4. Comprobar que el símbolo esté activo con symbol_info().visible")
    print("   5. Validar horarios de trading con symbol_info().trade_time_flags")
    print("   6. Usar symbol_info().point para calcular distancias mínimas")
    print()

def get_symbol_diagnostics(symbol="EURUSD"):
    """Obtener diagnósticos completos de un símbolo"""
    try:
        import MetaTrader5 as mt5
        
        print(f"🔬 DIAGNÓSTICO DEL SÍMBOLO: {symbol}")
        print("=" * 50)
        
        # Inicializar MT5 si no está ya inicializado
        if not mt5.initialize():
            print("❌ Error: No se pudo inicializar MT5")
            return
        
        # Obtener información del símbolo
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"❌ Error: No se pudo obtener información del símbolo {symbol}")
            return
        
        print(f"📈 INFORMACIÓN BÁSICA:")
        print(f"   • Símbolo: {symbol_info.name}")
        print(f"   • Descripción: {symbol_info.description}")
        print(f"   • Dígitos: {symbol_info.digits}")
        print(f"   • Point: {symbol_info.point}")
        print(f"   • Visible: {symbol_info.visible}")
        print(f"   • Trade mode: {symbol_info.trade_mode}")
        
        # Información de precios
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            print(f"\n💱 PRECIOS ACTUALES:")
            print(f"   • Bid: {tick.bid:.{symbol_info.digits}f}")
            print(f"   • Ask: {tick.ask:.{symbol_info.digits}f}")
            print(f"   • Spread: {(tick.ask - tick.bid) * 10**symbol_info.digits:.1f} puntos")
        
        # Información de trading
        print(f"\n📊 ESPECIFICACIONES DE TRADING:")
        print(f"   • Volumen mínimo: {symbol_info.volume_min}")
        print(f"   • Volumen máximo: {symbol_info.volume_max}")
        print(f"   • Paso de volumen: {symbol_info.volume_step}")
        print(f"   • Tick value: {symbol_info.trade_tick_value}")
        print(f"   • Tick size: {symbol_info.trade_tick_size}")
        print(f"   • Contract size: {symbol_info.trade_contract_size}")
        
        # Verificar niveles de stop
        if hasattr(symbol_info, 'trade_stops_level'):
            print(f"   • Nivel de stops: {symbol_info.trade_stops_level} puntos")
        if hasattr(symbol_info, 'trade_freeze_level'):
            print(f"   • Nivel de freeze: {symbol_info.trade_freeze_level} puntos")
        
        return symbol_info, tick
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        return None, None

def validate_price(symbol, price, price_type="entry"):
    """Validar si un precio es correcto para un símbolo"""
    try:
        import MetaTrader5 as mt5
        
        symbol_info, tick = get_symbol_diagnostics(symbol)
        if not symbol_info or not tick:
            return False, "No se pudo obtener información del símbolo"
        
        print(f"\n🔍 VALIDACIÓN DE PRECIO: {price}")
        print("=" * 40)
        
        # 1. Verificar normalización
        normalized_price = round(price, symbol_info.digits)
        if abs(price - normalized_price) > 0.0000001:
            return False, f"Precio no normalizado: {price} vs {normalized_price}"
        
        # 2. Verificar rango razonable (±10% del precio actual)
        current_price = (tick.bid + tick.ask) / 2
        max_deviation = current_price * 0.10  # 10%
        
        if abs(price - current_price) > max_deviation:
            return False, f"Precio muy alejado del actual: {price} vs {current_price:.{symbol_info.digits}f}"
        
        # 3. Verificar tick size
        if hasattr(symbol_info, 'trade_tick_size') and symbol_info.trade_tick_size > 0:
            remainder = price % symbol_info.trade_tick_size
            if remainder > 0.0000001:
                return False, f"Precio no respeta tick size: {price} (tick: {symbol_info.trade_tick_size})"
        
        print("✅ Precio validado correctamente")
        return True, "Precio válido"
        
    except Exception as e:
        return False, f"Error en validación: {e}"

def main():
    """Función principal del investigador"""
    import sys
    
    if len(sys.argv) < 2:
        print("🔍 INVESTIGADOR DE ERRORES MT5 v1.0")
        print("=" * 50)
        print("Uso: python mt5_error_investigator.py <comando> [opciones]")
        print()
        print("COMANDOS:")
        print("  analyze_10015           - Análisis detallado del error 10015")
        print("  diagnose <symbol>       - Diagnóstico completo de un símbolo")
        print("  validate <symbol> <price> - Validar un precio para un símbolo")
        print("  all_errors              - Mostrar todos los códigos de error")
        print()
        print("EJEMPLOS:")
        print("  python mt5_error_investigator.py analyze_10015")
        print("  python mt5_error_investigator.py diagnose EURUSD")
        print("  python mt5_error_investigator.py validate EURUSD 1.09534")
        return
    
    command = sys.argv[1].lower()
    
    if command == "analyze_10015":
        analyze_error_10015()
    
    elif command == "diagnose":
        symbol = sys.argv[2] if len(sys.argv) > 2 else "EURUSD"
        get_symbol_diagnostics(symbol)
    
    elif command == "validate":
        if len(sys.argv) < 4:
            print("❌ Error: Se requiere símbolo y precio")
            print("Uso: python mt5_error_investigator.py validate <symbol> <price>")
            return
        
        symbol = sys.argv[2]
        try:
            price = float(sys.argv[3])
            is_valid, message = validate_price(symbol, price)
            print(f"Resultado: {'✅ VÁLIDO' if is_valid else '❌ INVÁLIDO'}")
            print(f"Mensaje: {message}")
        except ValueError:
            print("❌ Error: Precio debe ser un número válido")
    
    elif command == "all_errors":
        print("📋 CÓDIGOS DE ERROR MT5 TRADE SERVER")
        print("=" * 60)
        for code, description in MT5_TRADE_RETCODES.items():
            print(f"{code:5d}: {description}")
    
    else:
        print(f"❌ Comando desconocido: {command}")

if __name__ == "__main__":
    main()
