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

# Imports centralizados
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
from rich.table import Table
from rich.panel import Panel

# Managers centralizados (FASE 4)
from data_manager import DataManager

# Constantes
SYMBOL = 'EURUSD'
DIST_MIN = {'M1': 0.0005, 'M5': 0.0015, 'M15': 0.0020}
BANDWIDTH_MIN = {'M1': 0.0003, 'M5': 0.0008, 'M15': 0.0012}
SPREAD_MAX = 0.00025
LOTE_MIN = 0.1
LOTE_MAX = 1.0
INCREMENTO = 0.1

# Instancia global DataManager (FASE 4)
data_manager = DataManager()

def obtener_bandas_bollinger(period=20, deviation=2.0, timeframe_str='M5'):
    """
    REFACTORIZADO FASE 4: Usar DataManager para calcular Bandas de Bollinger
    """
    try:
        # Usar DataManager para obtener datos OHLC
        df_ohlc = data_manager.get_ohlc_data(SYMBOL, timeframe_str, period + 2)
        if df_ohlc is None or len(df_ohlc) < period:
            return None, None, None
        
        # Calcular Bollinger usando DataManager
        bollinger_data = data_manager.calculate_bollinger_bands(df_ohlc, period, deviation)
        if bollinger_data is None:
            return None, None, None
            
        # Obtener último valor
        last_row = bollinger_data.iloc[-1]
        upper = last_row.get('BB_Upper', None)
        sma = last_row.get('BB_Middle', None) 
        lower = last_row.get('BB_Lower', None)
        
        return upper, sma, lower
        
    except Exception:
        # Fallback al método original si DataManager falla
        tf_mapping = {'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5, 'M15': mt5.TIMEFRAME_M15}
        tf = tf_mapping.get(timeframe_str, mt5.TIMEFRAME_M5)
        rates = mt5.copy_rates_from_pos(SYMBOL, tf, 0, period + 2)
        if rates is None or len(rates) < period:
            return None, None, None
        closes = np.array([r['close'] for r in rates])
        sma = np.mean(closes[-period:])
        std = np.std(closes[-period:])
        upper = sma + deviation * std
        lower = sma - deviation * std
        return upper, sma, lower

def determinar_fase_bollinger(precio_actual, upper, sma, lower):
    if upper is None or sma is None or lower is None:
        return "No calculada"
    if precio_actual >= upper:
        return "Toque banda superior (Sobrecompra)"
    elif precio_actual <= lower:
        return "Toque banda inferior (Sobreventa)"
    elif precio_actual > sma:
        return "Zona alcista (Entre SMA y banda superior)"
    elif precio_actual < sma:
        return "Zona bajista (Entre SMA y banda inferior)"
    else:
        return "En SMA (Neutro)"

def calcular_siguiente_lote(ultimo_lote, lotaje_inicial=None, capital_total=None):
    def siguiente_fibo(a, b):
        return a + b
    if lotaje_inicial is not None and ultimo_lote == 0:
        return round(lotaje_inicial, 2)
    if capital_total is not None and capital_total > 50000:
        if not hasattr(calcular_siguiente_lote, 'fibo_hist'):
            calcular_siguiente_lote.fibo_hist = [round(lotaje_inicial, 2), round(ultimo_lote, 2)]
        else:
            calcular_siguiente_lote.fibo_hist.append(round(ultimo_lote, 2))
            if len(calcular_siguiente_lote.fibo_hist) > 2:
                calcular_siguiente_lote.fibo_hist = calcular_siguiente_lote.fibo_hist[-2:]
        a, b = calcular_siguiente_lote.fibo_hist
        nuevo = siguiente_fibo(a, b)
        return round(nuevo, 2)
    nuevo = round(ultimo_lote + INCREMENTO, 2)
    return max(nuevo, LOTE_MIN)

def obtener_ultima_operacion():
    posiciones = mt5.positions_get(symbol=SYMBOL)
    if not posiciones:
        return None
    ultima = max(posiciones, key=lambda p: p.time)
    return ultima

def mostrar_dashboard_grid(estado, checklist, ultima_accion, lote, tipo, precio_actual, profit, ancho_banda, distancia, lote_proximo=None, upper=None, sma=None, lower=None):
    tabla = Table(show_header=True, header_style="bold magenta")
    tabla.add_column("Regla", justify="left")
    tabla.add_column("Valor", justify="center")
    tabla.add_column("Resultado", justify="center")
    for regla, valor, ok in checklist:
        simbolo = "✅" if ok else "❌"
        tabla.add_row(regla, str(valor), simbolo)
    panel_check = Panel(tabla, title="🟣 Checklist Grid Bollinger", border_style="magenta", expand=False)
    estado_lines = [f"[bold]{estado}[/bold]", "", f"Última acción: {ultima_accion}", f"Tipo: {tipo}", f"Lote: {lote}"]
    if lote_proximo is not None:
        estado_lines.append(f"Próximo lote: [blue]{lote_proximo:.2f}[/blue]")
    estado_lines += [
        f"Precio: {precio_actual}",
        f"Profit: {profit:.2f}",
        f"Ancho banda: {ancho_banda:.5f}",
        f"Distancia: {distancia:.5f}",
        f"Banda superior: {upper:.5f}" if upper else "Banda superior: No calculada",
        f"SMA: {sma:.5f}" if sma else "SMA: No calculada",
        f"Banda inferior: {lower:.5f}" if lower else "Banda inferior: No calculada",
        f"Fase Bollinger: {determinar_fase_bollinger(precio_actual, upper, sma, lower)}"
    ]
    panel_estado = Panel("\n".join(estado_lines), title="Estado Grid", border_style="green", expand=False)
    grid = Table.grid(expand=True)
    grid.add_row(panel_estado, panel_check)
    return Panel(grid, title="[bold cyan]Grid Bollinger Individual (Tiempo Real)", border_style="cyan")

def evaluar_condiciones_grid(riskbot, modalidad_operacion, lotaje_inicial, timeframe_str='M5'):
    tf_str = timeframe_str if timeframe_str in DIST_MIN else 'M5'
    dist_min = DIST_MIN[tf_str]
    bw_min = BANDWIDTH_MIN[tf_str]
    ultima_accion = "-"
    grid_panel = None
    checklist = []
    
    ultima = obtener_ultima_operacion()
    if not ultima:
        return None, ultima_accion, checklist
    
    tipo = 'BUY' if ultima.type == mt5.ORDER_TYPE_BUY else 'SELL'
    lote_ultimo = ultima.volume
    precio_entrada = ultima.price_open
    precio_actual = mt5.symbol_info_tick(SYMBOL).ask if tipo == 'BUY' else mt5.symbol_info_tick(SYMBOL).bid
    profit = ultima.profit
    upper, sma, lower = obtener_bandas_bollinger(timeframe_str=timeframe_str)
    ancho_banda = (upper - lower) if upper and lower else 0
    distancia = abs(precio_actual - precio_entrada)
    tick = mt5.symbol_info_tick(SYMBOL)
    spread_actual = tick.ask - tick.bid if tick else 0
    swap_ultimo = getattr(ultima, 'swap', 0)
    comision_ultimo = getattr(ultima, 'commission', None)
    if comision_ultimo is None or comision_ultimo == 0:
        try:
            import config
            comision_ultimo = getattr(config, 'COMISION_POR_LOTE', 0) * getattr(ultima, 'volume', 0)
        except Exception:
            comision_ultimo = 0
    neto_ultimo = profit + swap_ultimo - comision_ultimo
    
    checklist.append(("Operación abierta", tipo, True))
    checklist.append(("Última en pérdida", f"{neto_ultimo:.2f}", neto_ultimo < 0))
    checklist.append(("Distancia mínima", f"{distancia:.5f} >= {dist_min:.5f}", distancia >= dist_min))
    checklist.append(("Ancho banda mínima", f"{ancho_banda:.5f} >= {bw_min:.5f}", ancho_banda >= bw_min))
    checklist.append(("Spread actual", f"{spread_actual:.5f} <= {SPREAD_MAX:.5f}", spread_actual <= SPREAD_MAX))
    
    cruce_banda = False
    umbral_toque = 0.0002 if timeframe_str != 'M15' else 0.0003
    if not hasattr(evaluar_condiciones_grid, 'puede_abrir_grid'):
        evaluar_condiciones_grid.puede_abrir_grid = False
    
    if tipo == 'BUY' and lower is not None:
        cruce_banda = precio_actual <= lower or abs(precio_actual - lower) <= umbral_toque
        relacion_banda = f"Precio actual {precio_actual:.5f} {'<' if precio_actual < lower else '>' if precio_actual > lower else '='} Lower {lower:.5f}"
        checklist.append(("Toque banda inferior", f"Precio actual {precio_actual:.5f} <= Lower {lower:.5f} o |Δ|<={umbral_toque}", cruce_banda))
        checklist.append(("Relación precio/banda inferior", relacion_banda, True))
    elif tipo == 'SELL' and upper is not None:
        cruce_banda = precio_actual >= upper or abs(precio_actual - upper) <= umbral_toque
        relacion_banda = f"Precio actual {precio_actual:.5f} {'>' if precio_actual > upper else '<' if precio_actual < upper else '='} Upper {upper:.5f}"
        checklist.append(("Toque banda superior", f"Precio actual {precio_actual:.5f} >= Upper {upper:.5f} o |Δ|<={umbral_toque}", cruce_banda))
        checklist.append(("Relación precio/banda superior", relacion_banda, True))
    else:
        checklist.append(("Toque banda", "No datos suficientes", False))
        checklist.append(("Relación precio/banda", "No datos suficientes", False))
    
    puede_grid = all([
        neto_ultimo < 0,
        distancia >= dist_min,
        ancho_banda >= bw_min,
        spread_actual <= SPREAD_MAX,
        cruce_banda
    ])
    
    lote_proximo = calcular_siguiente_lote(lote_ultimo, lotaje_inicial, riskbot.get_account_balance())
    
    if cruce_banda and not puede_grid:
        razones = []
        if neto_ultimo >= 0:
            razones.append("operación en ganancia")
        if distancia < dist_min:
            razones.append(f"distancia insuficiente ({distancia:.5f} < {dist_min:.5f})")
        if ancho_banda < bw_min:
            razones.append(f"volatilidad insuficiente ({ancho_banda:.5f} < {bw_min:.5f})")
        if spread_actual > SPREAD_MAX:
            razones.append(f"spread elevado ({spread_actual:.5f} > {SPREAD_MAX:.5f})")
        ultima_accion = f"Toque detectado pero no se abre: {', '.join(razones)}"
    
    if puede_grid and ((tipo == 'BUY' and modalidad_operacion in ('AMBOS', 'BUY')) or (tipo == 'SELL' and modalidad_operacion in ('AMBOS', 'SELL'))):
        lote_nuevo = lote_proximo
        price = precio_actual
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": lote_nuevo,
            "type": mt5.ORDER_TYPE_BUY if tipo == 'BUY' else mt5.ORDER_TYPE_SELL,
            "price": price,
            "deviation": 10,
            "magic": 20250605,
            "comment": "Grid Bollinger Individual",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            import time
            time.sleep(0.5)
            tick = mt5.symbol_info_tick(SYMBOL)
            new_price = tick.ask if tipo == 'BUY' else tick.bid
            request['price'] = new_price
            result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            ultima_accion = f"✅ Grid: Nueva {tipo} @ {price:.5f} | Lote: {lote_nuevo:.2f}"
        else:
            ultima_accion = f"❌ Error al abrir orden Grid: {result.retcode} | Msg: {getattr(result, 'comment', '')}"
        evaluar_condiciones_grid.puede_abrir_grid = False
    else:
        if not cruce_banda:
            ultima_accion = "No se cumplen condiciones para grid."
    
    grid_panel = mostrar_dashboard_grid(
        estado="[green]Escaneando grid en tiempo real...[/green]",
        checklist=checklist,
        ultima_accion=ultima_accion,
        lote=lote_ultimo,
        tipo=tipo,
        precio_actual=precio_actual,
        profit=profit,
        ancho_banda=ancho_banda,
        distancia=distancia,
        lote_proximo=lote_proximo,
        upper=upper,
        sma=sma,
        lower=lower
    )
    
    return grid_panel, ultima_accion, checklist