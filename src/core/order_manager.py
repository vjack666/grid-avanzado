# order_manager.py

# =============================================================================
# SECCIÓN 1: IMPORTACIONES DE LIBRERÍAS
# =============================================================================
import sys
from pathlib import Path

# Configurar rutas para imports
current_dir = Path(__file__).parent
project_root = current_dir / "."
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis").absolute()))
sys.path.insert(0, str((project_root / "src" / "utils").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))


import MetaTrader5 as mt5
# Importamos SIMBOLO y log_debug desde config
from config import SIMBOLO, log_debug 
from data_logger import log_operacion_ejecutada # Importamos la función de logging de operaciones

# =============================================================================
# SECCIÓN 2: FUNCIONES DE GESTIÓN DE ÓRDENES MT5
# =============================================================================

def abrir_orden_mt5(symbol, tipo, volume, price, sl, tp, deviation=10, magic=1001, comment="Python Script"):
    """
    Envía una solicitud de orden al terminal MetaTrader 5.
    Esta es una función interna que las funciones de compra/venta usan.
    """
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": tipo,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    return result

def abrir_compra_mt5(volume, symbol=SIMBOLO, estrategia_origen="Desconocida", bollinger_info=None, estocastico_info=None): 
    """
    Abre una orden de compra en MetaTrader 5.
    Calcula SL/TP básicos y registra la operación.
    Args:
        volume (float): Volumen de la orden.
        symbol (str): Símbolo de trading.
        estrategia_origen (str): Nombre de la estrategia que genera la orden (ej. "Estocastico M15", "Grid Bollinger").
        bollinger_info (dict): Información de Bollinger al momento de la señal (fase, ancho_banda).
        estocastico_info (dict): Información de Estocástico al momento de la señal (cruce_tipo, zona, k_val, d_val).
    """
    log_debug("order_manager", f"Intentando abrir orden de COMPRA para {symbol} con volumen {volume}", "INFO")
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        log_debug("order_manager", f"Error: No se pudo obtener información del símbolo {symbol}.", "ERROR")
        return None
    point = symbol_info.point
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        log_debug("order_manager", f"Error: No se pudo obtener el tick para {symbol}.", "ERROR")
        return None
    price = tick.ask
    sl = price - 200 * point # Ejemplo de Stop Loss. Considerar hacerlo dinámico.
    tp = price + 300 * point # Ejemplo de Take Profit. Considerar hacerlo dinámico.
    result = abrir_orden_mt5(symbol, mt5.ORDER_TYPE_BUY, volume, price, sl, tp)

    # Preparar datos para log_operacion_ejecutada
    retcode = result.retcode if result else None
    comment = result.comment if result else "No_Result"
    ticket = result.order if result and result.retcode == mt5.TRADE_RETCODE_DONE else 0
    exec_price = result.price if result and result.retcode == mt5.TRADE_RETCODE_DONE else price 

    # Información detallada para el log
    bb_fase = bollinger_info.get('fase', 'N/A') if bollinger_info else 'N/A'
    bb_ancho = bollinger_info.get('ancho_banda', 'N/A') if bollinger_info else 'N/A'
    estoc_cruce = estocastico_info.get('cruce_tipo', 'N/A') if estocastico_info else 'N/A'
    estoc_zona = estocastico_info.get('zona', 'N/A') if estocastico_info else 'N/A'
    
    log_operacion_ejecutada(
        symbol, 'BUY', volume, price, sl, tp, estrategia_origen,
        estoc_cruce, estoc_zona, bb_fase, bb_ancho,
        retcode, comment, ticket, exec_price,
        error_detalle=f"MT5 Error: {comment}" if retcode != mt5.TRADE_RETCODE_DONE else ""
    )

    if result and result.retcode != mt5.TRADE_RETCODE_DONE:
        log_debug("order_manager", f"Error al abrir COMPRA: {result.retcode} - {result.comment}", "ERROR")
    else:
        log_debug("order_manager", f"Orden de COMPRA abierta con éxito: {result.order}", "INFO")
    return result

def abrir_venta_mt5(volume, symbol=SIMBOLO, estrategia_origen="Desconocida", bollinger_info=None, estocastico_info=None): 
    """
    Abre una orden de venta en MetaTrader 5.
    Calcula SL/TP básicos y registra la operación.
    Args:
        volume (float): Volumen de la orden.
        symbol (str): Símbolo de trading.
        estrategia_origen (str): Nombre de la estrategia que genera la orden (ej. "Estocastico M15", "Grid Bollinger").
        bollinger_info (dict): Información de Bollinger al momento de la señal (fase, ancho_banda).
        estocastico_info (dict): Información de Estocástico al momento de la señal (cruce_tipo, zona, k_val, d_val).
    """
    log_debug("order_manager", f"Intentando abrir orden de VENTA para {symbol} con volumen {volume}", "INFO")
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        log_debug("order_manager", f"Error: No se pudo obtener información del símbolo {symbol}.", "ERROR")
        return None
    point = symbol_info.point
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        log_debug("order_manager", f"Error: No se pudo obtener el tick para {symbol}.", "ERROR")
        return None
    price = tick.bid
    sl = price + 200 * point 
    tp = price - 300 * point 
    result = abrir_orden_mt5(symbol, mt5.ORDER_TYPE_SELL, volume, price, sl, tp)

    # Preparar datos para log_operacion_ejecutada
    retcode = result.retcode if result else None
    comment = result.comment if result else "No_Result"
    ticket = result.order if result and result.retcode == mt5.TRADE_RETCODE_DONE else 0
    exec_price = result.price if result and result.retcode == mt5.TRADE_RETCODE_DONE else price

    # Información detallada para el log
    bb_fase = bollinger_info.get('fase', 'N/A') if bollinger_info else 'N/A'
    bb_ancho = bollinger_info.get('ancho_banda', 'N/A') if bollinger_info else 'N/A'
    estoc_cruce = estocastico_info.get('cruce_tipo', 'N/A') if estocastico_info else 'N/A'
    estoc_zona = estocastico_info.get('zona', 'N/A') if estocastico_info else 'N/A'
    
    log_operacion_ejecutada(
        symbol, 'SELL', volume, price, sl, tp, estrategia_origen,
        estoc_cruce, estoc_zona, bb_fase, bb_ancho,
        retcode, comment, ticket, exec_price,
        error_detalle=f"MT5 Error: {comment}" if retcode != mt5.TRADE_RETCODE_DONE else ""
    )

    if result and result.retcode != mt5.TRADE_RETCODE_DONE:
        log_debug("order_manager", f"Error al abrir VENTA: {result.retcode} - {result.comment}", "ERROR")
    else:
        log_debug("order_manager", f"Orden de VENTA abierta con éxito: {result.order}", "INFO")
    return result