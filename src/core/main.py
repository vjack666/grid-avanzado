import sys
import os
from pathlib import Path

# Agregar las rutas necesarias para importar módulos
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "utils"))
sys.path.insert(0, str(project_root / "src" / "analysis"))
sys.path.insert(0, str(project_root / "config"))

from riskbot_mt5 import RiskBotMT5
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
import time
import json
from datetime import datetime, timedelta
import MetaTrader5 as mt5
import pandas as pd
import keyboard
from trading_schedule import esta_en_horario_operacion, mostrar_horario_operacion
from analisis_estocastico_m15 import analizar_estocastico_m15_cacheado, mostrar_checkpoint_estocastico
from grid_bollinger import evaluar_condiciones_grid
from .config_manager import ConfigManager
from .logger_manager import LoggerManager
from error_manager import ErrorManager
from data_manager import DataManager
from indicator_manager import IndicatorManager
from mt5_manager import MT5Manager
from analytics_manager import AnalyticsManager

# Configuración centralizada usando todos los managers (FASE 6 COMPLETA + SÓTANO 1)
config = ConfigManager()
config.ensure_directories()
logger = LoggerManager()
error_manager = ErrorManager(logger_manager=logger, config_manager=config)
data_manager = DataManager()  # FASE 4: Gestión centralizada de datos
indicator_manager = IndicatorManager(data_manager, logger, error_manager)  # FASE 5: Gestión avanzada de indicadores
mt5_manager = MT5Manager(config, logger, error_manager)  # FASE 6: Gestión centralizada MT5
analytics_manager = AnalyticsManager(config, logger, error_manager, data_manager)  # SÓTANO 1: Analytics avanzados

# Crear instancia de Console para Rich
console = Console()

# Variables para compatibilidad hacia atrás
safe_data_dir = config.get_safe_data_dir()
LOG_PATH = config.get_log_operaciones_path()
parametros_path = config.get_parametros_path()

mensajes_runtime = []

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def agregar_mensaje_runtime(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    mensajes_runtime.append(f"[{timestamp}] {msg}")
    if len(mensajes_runtime) > 20:
        del mensajes_runtime[0]

MINIMOS_FILE = os.path.join(safe_data_dir, "data", "minimos_historicos.json")

def cargar_minimos_historicos():
    if os.path.exists(MINIMOS_FILE):
        with open(MINIMOS_FILE, 'r') as f:
            try:
                data = json.load(f)
                for symbol in data:
                    data[symbol]['timestamp'] = datetime.fromisoformat(data[symbol]['timestamp'])
                return data
            except json.JSONDecodeError:
                return {}
    return {}

def guardar_minimos_historicos(data):
    serializable_data = {
        symbol: {'minimo': info['minimo'], 'timestamp': info['timestamp'].isoformat()}
        for symbol, info in data.items()
    }
    os.makedirs(os.path.dirname(MINIMOS_FILE), exist_ok=True)
    with open(MINIMOS_FILE, 'w') as f:
        json.dump(serializable_data, f, indent=2)

def actualizar_minimo_historico(symbol, precio_actual, data):
    ahora = datetime.now()
    minimo_anterior = data[symbol]['minimo'] if symbol in data else None
    if symbol not in data:
        data[symbol] = {'minimo': precio_actual, 'timestamp': ahora}
        agregar_mensaje_runtime(f"Nuevo mínimo histórico para {symbol}: {precio_actual:.5f} (inicializado)")
    else:
        if precio_actual < data[symbol]['minimo']:
            agregar_mensaje_runtime(f"Mínimo histórico actualizado para {symbol}: {data[symbol]['minimo']:.5f} → {precio_actual:.5f} @ {ahora.isoformat()}")
            data[symbol]['minimo'] = precio_actual
            data[symbol]['timestamp'] = ahora
    for sym in list(data.keys()):
        if ahora - data[sym]['timestamp'] > timedelta(hours=24):
            del data[sym]
    return data[symbol]['minimo'], data

SYMBOL = 'EURUSD'
LOTE_MIN = 0.1
LOTE_MAX = 1.0

def registrar_log(tipo, lote, precio, resultado):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()},{tipo},{lote},{precio},{resultado}\n")
    try:
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if len(lines) > 1001:
            with open(LOG_PATH, 'w', encoding='utf-8') as f:
                f.writelines([lines[0]] + lines[-1000:])
    except Exception:
        pass

def abrir_venta_mt5(lote=0.1):
    precio = mt5.symbol_info_tick(SYMBOL).bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": lote,
        "type": mt5.ORDER_TYPE_SELL,
        "price": precio,
        "deviation": 10,
        "magic": 123456,
        "comment": "Venta estocástico M15",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Venta ejecutada: {lote} lotes @ {precio}")
        registrar_log("SELL", lote, precio, "OK")
        
        # SÓTANO 1: Trackear apertura de trade
        try:
            trade_data = {
                "type": "SELL",
                "symbol": SYMBOL,
                "volume": lote,
                "open_price": precio,
                "timestamp": datetime.now(),
                "ticket": result.order if hasattr(result, 'order') else None
            }
            # Note: profit será calculado al cierre
        except Exception as e:
            logger.log_warning(f"Error tracking trade aperture: {e}")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error al abrir venta: {result.retcode} | {getattr(result, 'comment', '')}")
        registrar_log("SELL", lote, precio, f"ERROR:{result.retcode}")
    return result

def abrir_compra_mt5(lote=0.1):
    precio = mt5.symbol_info_tick(SYMBOL).ask
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": lote,
        "type": mt5.ORDER_TYPE_BUY,
        "price": precio,
        "deviation": 10,
        "magic": 123456,
        "comment": "Compra estocástico M15",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Compra ejecutada: {lote} lotes @ {precio}")
        registrar_log("BUY", lote, precio, "OK")
        
        # SÓTANO 1: Trackear apertura de trade
        try:
            trade_data = {
                "type": "BUY",
                "symbol": SYMBOL,
                "volume": lote,
                "open_price": precio,
                "timestamp": datetime.now(),
                "ticket": result.order if hasattr(result, 'order') else None
            }
            # Note: profit será calculado al cierre
        except Exception as e:
            logger.log_warning(f"Error tracking trade aperture: {e}")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error al abrir compra: {result.retcode} | {getattr(result, 'comment', '')}")
        registrar_log("BUY", lote, precio, f"ERROR:{result.retcode}")
    return result

def solicitar_modalidad():
    modalidad_previa = None
    if os.path.exists(parametros_path):
        try:
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
                modalidad_previa = datos.get("modalidad")
        except Exception:
            modalidad_previa = None
    print("🎯 Selecciona la modalidad de trabajo para hoy:")
    print("   1 → M1  (Scalping agresivo)")
    print("   2 → M5  (Scalping intermedio) ✅ Recomendado")
    print("   3 → M15 (Swing corto)\n")
    if modalidad_previa:
        print(f"[Enter] para usar la última modalidad: {modalidad_previa}")
    opcion = input("👉 Ingresa el número de la modalidad deseada: ").strip()
    mapa = {'1': 'M1', '2': 'M5', '3': 'M15'}
    if opcion == "" and modalidad_previa:
        timeframe = modalidad_previa
    else:
        timeframe = mapa.get(opcion, modalidad_previa or 'M5')
    print(f"✅ Modalidad seleccionada: {timeframe} (Análisis sobre velas de {timeframe})\n")
    try:
        os.makedirs(os.path.dirname(parametros_path), exist_ok=True)
        datos = {}
        if os.path.exists(parametros_path):
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
        datos["modalidad"] = timeframe
        with open(parametros_path, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.log_warning(f"No se pudo guardar la modalidad: {e}")
    return timeframe

def solicitar_parametros_riesgo():
    ganancia_minima = ganancia_maxima = riesgo_sesion = comision_por_lote = None
    if os.path.exists(parametros_path):
        try:
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
                ganancia_minima = datos.get("ganancia_minima")
                ganancia_maxima = datos.get("ganancia_maxima")
                riesgo_sesion = datos.get("riesgo_sesion")
                comision_por_lote = datos.get("comision_por_lote")
        except Exception:
            pass
    try:
        prompt_ganancia_min = f"💰 Ingresa la ganancia mínima deseada (ej. 10.0)"
        if ganancia_minima is not None:
            prompt_ganancia_min += f" [Enter={ganancia_minima}]"
        prompt_ganancia_min += ": "
        entrada_min = input(prompt_ganancia_min).strip()
        if entrada_min == "" and ganancia_minima is not None:
            entrada_min = ganancia_minima
        else:
            entrada_min = float(entrada_min)

        prompt_ganancia_max = f"💎 Ingresa la ganancia máxima esperada (ej. 50.0)"
        if ganancia_maxima is not None:
            prompt_ganancia_max += f" [Enter={ganancia_maxima}]"
        prompt_ganancia_max += ": "
        entrada_max = input(prompt_ganancia_max).strip()
        if entrada_max == "" and ganancia_maxima is not None:
            entrada_max = ganancia_maxima
        else:
            entrada_max = float(entrada_max)

        prompt_riesgo = f"📉 Ingresa el % de riesgo máximo permitido (ej. 3)"
        if riesgo_sesion is not None:
            prompt_riesgo += f" [Enter={riesgo_sesion}]"
        prompt_riesgo += ": "
        entrada_riesgo = input(prompt_riesgo).strip()
        if entrada_riesgo == "" and riesgo_sesion is not None:
            entrada_riesgo = riesgo_sesion
        else:
            entrada_riesgo = float(entrada_riesgo)

        import config
        comision_actual = getattr(config, 'COMISION_POR_LOTE', None)
        os.makedirs(os.path.dirname(parametros_path), exist_ok=True)
        datos = {}
        if os.path.exists(parametros_path):
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
        datos.update({
            "ganancia_minima": entrada_min,
            "ganancia_maxima": entrada_max,
            "riesgo_sesion": entrada_riesgo,
            "comision_por_lote": comision_actual
        })
        with open(parametros_path, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        return entrada_min, entrada_max, entrada_riesgo
    except ValueError:
        print("⚠️ Error: por favor ingresa valores numéricos válidos.")
        return solicitar_parametros_riesgo()

def obtener_sesiones_seleccionadas(opcion, sesiones_previas=None):
    sesiones_map = {
        '1': ['SIDNEY'],
        '2': ['TOKIO'],
        '3': ['LONDRES'],
        '4': ['NUEVA_YORK'],
        '5': ['LONDRES_NY'],
        '6': ['SIDNEY', 'TOKIO', 'LONDRES', 'NUEVA_YORK', 'LONDRES_NY']
    }
    print("\n⏰ Configura las sesiones de trading (Horario Ecuador, UTC-5)")
    print("   1 → Sídney (17:00 - 02:00)")
    print("   2 → Tokio (19:00 - 04:00)")
    print("   3 → Londres (02:00 - 11:00)")
    print("   4 → Nueva York (07:00 - 16:00)")
    print("   5 → Solapamiento Londres-NY (07:00 - 11:00)")
    print("   6 → TODAS las sesiones")
    if sesiones_previas:
        print(f"[Enter] para usar las sesiones previas: {', '.join(sesiones_previas)}")
    if opcion == "" and sesiones_previas:
        sesiones = sesiones_previas
    else:
        try:
            opciones = [o.strip() for o in opcion.split(',')]
            sesiones = []
            for op in opciones:
                if op in sesiones_map:
                    sesiones.extend(sesiones_map[op])
            sesiones = list(set(sesiones))  # Eliminar duplicados
            if not sesiones:
                sesiones = sesiones_previas or ['LONDRES_NY']
        except Exception:
            sesiones = sesiones_previas or ['LONDRES_NY']
    print(f"✅ Sesiones de operación configuradas: {', '.join(sesiones)}\n")
    try:
        os.makedirs(os.path.dirname(parametros_path), exist_ok=True)
        datos = {}
        if os.path.exists(parametros_path):
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
        datos["sesiones"] = sesiones
        with open(parametros_path, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        console.print(f"[yellow]⚠️ No se pudo guardar las sesiones: {e}[/yellow]")
    return sesiones

def solicitar_modalidad_operacion():
    modalidad_previa = None
    if os.path.exists(parametros_path):
        try:
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
                modalidad_previa = datos.get("modalidad_operacion")
        except Exception:
            modalidad_previa = None
    print("\n🟢 Selecciona la modalidad de operación:")
    print("   1 → Solo COMPRAS (BUY)")
    print("   2 → Solo VENTAS (SELL)")
    print("   3 → Ambos (BUY y SELL) ✅ Recomendado\n")
    if modalidad_previa:
        print(f"[Enter] para usar la última modalidad: {modalidad_previa}")
    opcion = input("👉 Ingresa el número de la modalidad deseada: ").strip()
    mapa = {'1': 'BUY', '2': 'SELL', '3': 'AMBOS'}
    if opcion == "" and modalidad_previa:
        modalidad = modalidad_previa
    else:
        modalidad = mapa.get(opcion, modalidad_previa or 'AMBOS')
    print(f"✅ Modalidad de operación seleccionada: {modalidad}\n")
    try:
        os.makedirs(os.path.dirname(parametros_path), exist_ok=True)
        datos = {}
        if os.path.exists(parametros_path):
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
        datos["modalidad_operacion"] = modalidad
        with open(parametros_path, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        console.print(f"[yellow]⚠️ No se pudo guardar la modalidad de operación: {e}[/yellow]")
    return modalidad

def calcular_lotaje_recomendado(capital, riesgo_sesion, stop_loss_pips=100, valor_pip=10):
    riesgo_decimal = riesgo_sesion / 100.0
    lotaje = (capital * riesgo_decimal) / (stop_loss_pips * valor_pip)
    return max(LOTE_MIN, min(round(lotaje, 2), LOTE_MAX))

def solicitar_lotaje_inicial(capital_total, riesgo_sesion):
    lotaje_previo = None
    lotaje_recomendado = calcular_lotaje_recomendado(capital_total, riesgo_sesion)
    try:
        if os.path.exists(parametros_path):
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
                lotaje_previo = datos.get("lotaje_inicial")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        console.print(f"[yellow]⚠️ No se pudo cargar lotaje previo: {e}. Usando valor recomendado.[/yellow]")
        lotaje_previo = None

    prompt = f"📏 Ingresa el lotaje inicial a utilizar (ej. 0.1)\n[Sugerido: {lotaje_recomendado:.2f} lotes]"
    if lotaje_previo is not None:
        prompt += f" [Enter={lotaje_previo}]"
    else:
        prompt += f" [Enter={lotaje_recomendado}]"
    prompt += ": "

    entrada = input(prompt).strip()
    if entrada == "" and lotaje_previo is not None:
        lotaje = float(lotaje_previo)
    elif entrada == "":
        lotaje = float(lotaje_recomendado)
    else:
        try:
            lotaje = float(entrada)
            if lotaje <= 0:
                console.print("⚠️ El lotaje debe ser mayor a 0.")
                return solicitar_lotaje_inicial(capital_total, riesgo_sesion)
        except ValueError:
            console.print("⚠️ Ingresa un valor numérico válido para el lotaje.")
            return solicitar_lotaje_inicial(capital_total, riesgo_sesion)

    try:
        os.makedirs(os.path.dirname(parametros_path), exist_ok=True)
        datos = {}
        if os.path.exists(parametros_path):
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
        datos["lotaje_inicial"] = lotaje
        with open(parametros_path, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.log_warning(f"No se pudo guardar el lotaje inicial: {e}")

    logger.log_success(f"Lotaje inicial seleccionado: {lotaje:.2f}")
    return lotaje, lotaje_recomendado

def construir_checklist_gestion_riesgo(capital_total, riesgo_acumulado, riesgo_maximo, ganancia_total_actual, ganancia_minima, ganancia_maxima, margen_suficiente, comision_total, comision_maxima, perdidas_extremas, lotaje_total):
    tabla = Table(show_header=True, header_style="bold magenta", expand=False)
    tabla.add_column("Regla", justify="left")
    tabla.add_column("Valor", justify="center")
    tabla.add_column("Resultado", justify="center")
    checklist = [
        ("Capital Total", f"${capital_total:,.2f}", capital_total > 0),
        ("Riesgo Acumulado", f"${riesgo_acumulado:,.2f}", riesgo_acumulado <= riesgo_maximo),
        ("Ganancia Actual", f"${ganancia_total_actual:,.2f}", ganancia_total_actual >= ganancia_minima),
        ("Margen Suficiente", "SÍ" if margen_suficiente else "NO", margen_suficiente),
        ("Comisión Total", f"${comision_total:,.2f}", comision_total <= (comision_maxima or float('inf'))),
        ("Pérdidas Extremas", "NO" if not perdidas_extremas else "SÍ", not perdidas_extremas),
        ("Lotaje Total", f"{lotaje_total:.2f}", lotaje_total <= LOTE_MAX)
    ]
    for regla, valor, ok in checklist:
        simbolo = "✅" if ok else "❌"
        tabla.add_row(regla, str(valor), simbolo)
    return Panel(tabla, title="🟣 Checklist Gestión de Riesgo", border_style="magenta", expand=False)

def mostrar_resumen_configuracion(modalidad, sesiones_seleccionadas, modalidad_operacion, ganancia_minima, ganancia_maxima, riesgo_sesion, lotaje_inicial, lotaje_recomendado):
    tabla = Table(show_header=False, box=None, expand=False)
    tabla.add_column("Parámetro", justify="left")
    tabla.add_column("Valor", justify="right")
    tabla.add_row("Modalidad de trabajo", modalidad)
    tabla.add_row("Sesiones de trading", ", ".join(sesiones_seleccionadas) if sesiones_seleccionadas else "NINGUNA")
    tabla.add_row("Modalidad de operación", modalidad_operacion)
    tabla.add_row("Ganancia mínima", f"${ganancia_minima:.2f}")
    tabla.add_row("Ganancia máxima", f"${ganancia_maxima:.2f}")
    tabla.add_row("Riesgo máximo", f"{riesgo_sesion:.2f}%")
    tabla.add_row("Lotaje inicial", f"{lotaje_inicial:.2f}")
    tabla.add_row("Lotaje recomendado", f"{lotaje_recomendado:.2f}")
    return Panel(tabla, title="⚙️ Resumen de Configuración", border_style="blue", expand=False)

def mostrar_panel_financiero_y_riesgo(riskbot, ganancia_minima, ganancia_maxima, riesgo_sesion):
    capital_total = riskbot.get_account_balance()
    operaciones_abiertas = riskbot.get_open_positions()
    
    comision_total = 0.0
    swap_total = 0.0
    ganancia_total_bruta = 0.0
    lotaje_total = 0.0
    riesgo_acumulado = 0.0
    
    if operaciones_abiertas:
        for p in operaciones_abiertas:
            try:
                ganancia_total_bruta += safe_float(getattr(p, 'profit', 0.0))
                lotaje_total += safe_float(getattr(p, 'volume', 0.0))
                swap_total += safe_float(getattr(p, 'swap', 0.0))
                comision_total += safe_float(getattr(p, 'commission', 0.0))
                profit_val = safe_float(getattr(p, 'profit', 0.0))
                if profit_val < 0:
                    riesgo_acumulado += abs(profit_val)
            except Exception as e:
                console.print(f"[red]Error al procesar operación {getattr(p, 'ticket', 'N/A')}: {e}[/red]")
                continue

    ganancia_total_neta = ganancia_total_bruta + swap_total + comision_total
    riesgo_maximo = capital_total * (riesgo_sesion / 100.0)
    riesgo_disponible = max(0, riesgo_maximo - riesgo_acumulado)
    porcentaje_acumulado = (riesgo_acumulado / capital_total) * 100 if capital_total else 0
    
    account_info = mt5.account_info()
    margen_libre = safe_float(getattr(account_info, 'margin_free', 0.0))
    margen_usado = safe_float(getattr(account_info, 'margin', 0.0))

    tabla = Table.grid(expand=False)
    tabla.add_column(justify="left")
    tabla.add_column(justify="right")
    tabla.add_row("💰 Balance:", f"${capital_total:,.2f}")
    tabla.add_row("📈 Ganancia neta:", f"${ganancia_total_neta:,.2f}")
    tabla.add_row("📊 Riesgo acumulado:", f"${riesgo_acumulado:,.2f} ({porcentaje_acumulado:.2f}%)")
    tabla.add_row("💣 Riesgo disponible:", f"${riesgo_disponible:,.2f}")
    tabla.add_row("💎 Ganancia máxima:", f"${ganancia_maxima:,.2f}")
    tabla.add_row("🔄 Margen libre:", f"${margen_libre:,.2f}")
    tabla.add_row("🔧 Margen usado:", f"${margen_usado:,.2f}")
    tabla.add_row("📏 Lotaje total:", f"{lotaje_total:.2f}")
    tabla.add_row("💸 Comisión:", f"${comision_total:,.2f}")
    tabla.add_row("🔄 Swap:", f"${swap_total:,.2f}")
    return Panel(tabla, title="💵 Finanzas y Riesgo", border_style="green", expand=False)

def ciclo_riesgo_continuo(riskbot, ganancia_minima, ganancia_maxima, riesgo_sesion, comision_por_lote, sesiones_seleccionadas, modalidad_operacion=None, lotaje_inicial=None, lotaje_recomendado=None, modalidad=None):
    global BOLLINGER_TIMEFRAME
    BOLLINGER_TIMEFRAME = modalidad or BOLLINGER_TIMEFRAME
    
    operaciones_abiertas = riskbot.get_open_positions()
    
    resumen_config = mostrar_resumen_configuracion(modalidad, sesiones_seleccionadas, modalidad_operacion, ganancia_minima, ganancia_maxima, riesgo_sesion, lotaje_inicial, lotaje_recomendado)
    panel_financiero_y_riesgo = mostrar_panel_financiero_y_riesgo(riskbot, ganancia_minima, ganancia_maxima, riesgo_sesion)
    
    if not operaciones_abiertas and not esta_en_horario_operacion(sesiones_seleccionadas):
        mensaje = f"[yellow]Fuera de las sesiones seleccionadas (Sesiones activas: {mostrar_horario_operacion(sesiones_seleccionadas) if sesiones_seleccionadas else 'NINGUNA'}).[/yellow]"
        return Group(resumen_config, panel_financiero_y_riesgo, Panel(mensaje, title="⏳ Estado", border_style="yellow")), (modalidad, ganancia_minima, ganancia_maxima, riesgo_sesion, sesiones_seleccionadas, modalidad_operacion, lotaje_inicial, lotaje_recomendado)
    
    if not hasattr(ciclo_riesgo_continuo, 'descanso_hasta'):
        ciclo_riesgo_continuo.descanso_hasta = None
    if ciclo_riesgo_continuo.descanso_hasta:
        ahora = time.time()
        if ahora < ciclo_riesgo_continuo.descanso_hasta:
            minutos_rest = safe_int((ciclo_riesgo_continuo.descanso_hasta - ahora) // 60)
            segundos_rest = safe_int((ciclo_riesgo_continuo.descanso_hasta - ahora) % 60)
            mensaje = f"[yellow]Descanso tras cierre de todas las operaciones. El bot se reanudará en {minutos_rest:02d}:{segundos_rest:02d} min.[/yellow]"
            return Group(resumen_config, panel_financiero_y_riesgo, Panel(mensaje, title="⏳ Descanso Grid", border_style="yellow")), (modalidad, ganancia_minima, ganancia_maxima, riesgo_sesion, sesiones_seleccionadas, modalidad_operacion, lotaje_inicial, lotaje_recomendado)
        else:
            ciclo_riesgo_continuo.descanso_hasta = None
    
    capital_total = riskbot.get_account_balance()
    try:
        comision_total_abiertas = sum(safe_float(getattr(p, 'commission', 0.0)) for p in operaciones_abiertas) if operaciones_abiertas else 0.0
        swap_total_abiertas = sum(safe_float(getattr(p, 'swap', 0.0)) for p in operaciones_abiertas) if operaciones_abiertas else 0.0
        ganancia_total_bruta = sum(safe_float(getattr(p, 'profit', 0.0)) for p in operaciones_abiertas) if operaciones_abiertas else 0.0
        lotaje_total = sum(safe_float(getattr(p, 'volume', 0.0)) for p in operaciones_abiertas) if operaciones_abiertas else 0.0
        riesgo_acumulado = sum(-safe_float(getattr(p, 'profit', 0.0)) for p in operaciones_abiertas if safe_float(getattr(p, 'profit', 0.0)) < 0) if operaciones_abiertas else 0.0
    except Exception as e:
        console.print(f"[red]Error al procesar datos de operaciones: {e}[/red]")
        comision_total_abiertas = swap_total_abiertas = ganancia_total_bruta = lotaje_total = riesgo_acumulado = 0.0
    
    ganancia_total_neta = ganancia_total_bruta + swap_total_abiertas + comision_total_abiertas
    
    checklist_gestion_riesgo = construir_checklist_gestion_riesgo(
        capital_total=capital_total,
        riesgo_acumulado=riesgo_acumulado,
        riesgo_maximo=capital_total * (riesgo_sesion / 100.0),
        ganancia_total_actual=ganancia_total_neta,
        ganancia_minima=ganancia_minima,
        ganancia_maxima=ganancia_maxima,
        margen_suficiente=True,
        comision_total=comision_total_abiertas,
        comision_maxima=None,
        perdidas_extremas=False,
        lotaje_total=lotaje_total
    )
    tabla_operaciones = construir_tabla_operaciones(operaciones_abiertas)
    
    if operaciones_abiertas:
        agregar_mensaje_runtime(f"Comisión total aplicada: ${comision_total_abiertas:.2f} | Swap total: ${swap_total_abiertas:.2f} | Flotante neto: ${ganancia_total_neta:.2f}")
    
    grid_panel = None
    try:
        grid_panel, ultima_accion, checklist = evaluar_condiciones_grid(riskbot, modalidad_operacion, lotaje_inicial, BOLLINGER_TIMEFRAME)
        registrar_log("DIAGNOSTICO", 0, mt5.symbol_info_tick(SYMBOL).bid, f"ULTIMA_ACCION:{ultima_accion}")
    except Exception as e:
        grid_panel = Panel(f"[red]Error en lógica Grid Bollinger: {e}[/red]", title="Grid Bollinger Error", border_style="red")
        registrar_log("ERROR", 0, mt5.symbol_info_tick(SYMBOL).bid, f"EXCEPCION:{e}")
    
    if operaciones_abiertas and len(operaciones_abiertas) > 0:
        cierre_realizado = False
        motivo_cierre = None
        if riesgo_acumulado >= capital_total * (riesgo_sesion / 100.0):
            riskbot.close_all_positions()
            motivo_cierre = f"🛑 Límite de pérdida alcanzado (${riesgo_acumulado:.2f} >= ${capital_total * (riesgo_sesion / 100.0):.2f}). Todas las posiciones han sido cerradas para proteger el capital."
            cierre_realizado = True
        elif len(operaciones_abiertas) > 3:
            if ganancia_total_bruta >= ganancia_minima + abs(comision_total_abiertas) + abs(swap_total_abiertas):
                riskbot.close_all_positions()
                motivo_cierre = f"✅ Ganancia mínima neta alcanzada (${ganancia_total_neta:.2f}, comisión descontada: ${comision_total_abiertas:.2f}, swap: ${swap_total_abiertas:.2f}). Todas las posiciones han sido cerradas para reducir riesgo."
                cierre_realizado = True
        else:
            if ganancia_total_neta >= ganancia_maxima:
                riskbot.close_all_positions()
                motivo_cierre = f"💎 Ganancia máxima neta alcanzada (${ganancia_total_neta:.2f}, comisión descontada: ${comision_total_abiertas:.2f}). Todas las posiciones han sido cerradas."
                cierre_realizado = True
        if cierre_realizado and motivo_cierre:
            agregar_mensaje_runtime(motivo_cierre)
            ciclo_riesgo_continuo.descanso_hasta = time.time() + 15*60
        return Group(resumen_config, panel_financiero_y_riesgo, tabla_operaciones, grid_panel, checklist_gestion_riesgo), (modalidad, ganancia_minima, ganancia_maxima, riesgo_sesion, sesiones_seleccionadas, modalidad_operacion, lotaje_inicial, lotaje_recomendado)
    else:
        if hasattr(ciclo_riesgo_continuo, 'descanso_hasta') and ciclo_riesgo_continuo.descanso_hasta:
            ahora = time.time()
            if ahora < ciclo_riesgo_continuo.descanso_hasta:
                minutos_rest = safe_int((ciclo_riesgo_continuo.descanso_hasta - ahora) // 60)
                segundos_rest = safe_int((ciclo_riesgo_continuo.descanso_hasta - ahora) % 60)
                mensaje = f"[yellow]Descanso tras cierre de todas las operaciones. El bot se reanudará en {minutos_rest:02d}:{segundos_rest:02d} min.[/yellow]"
                return Group(resumen_config, panel_financiero_y_riesgo, Panel(mensaje, title="⏳ Descanso Grid", border_style="yellow")), (modalidad, ganancia_minima, ganancia_maxima, riesgo_sesion, sesiones_seleccionadas, modalidad_operacion, lotaje_inicial, lotaje_recomendado)
        
        estoc_cache = analizar_estocastico_m15_cacheado(riskbot, modalidad_operacion, lotaje_inicial)
        checklist_panel = mostrar_checkpoint_estocastico(estoc_cache, lotaje_inicial, lotaje_recomendado, modalidad_operacion)
        return Group(resumen_config, panel_financiero_y_riesgo, checklist_panel), (modalidad, ganancia_minima, ganancia_maxima, riesgo_sesion, sesiones_seleccionadas, modalidad_operacion, lotaje_inicial, lotaje_recomendado)

def construir_tabla_operaciones(operaciones):
    tabla = Table(show_header=True, header_style="bold cyan", expand=False)
    tabla.add_column("Ticket", justify="right")
    tabla.add_column("Símbolo", justify="left")
    tabla.add_column("Tipo", justify="center")
    tabla.add_column("Lotes", justify="right")
    tabla.add_column("Precio", justify="right")
    tabla.add_column("SL", justify="right")
    tabla.add_column("TP", justify="right")
    tabla.add_column("Precio Actual", justify="right")
    tabla.add_column("Beneficio", justify="right")
    tabla.add_column("Swap", justify="right")
    tabla.add_column("Comisión", justify="right")
    total_beneficio = 0.0
    for op in operaciones:
        try:
            tipo = 'BUY' if op.type == mt5.ORDER_TYPE_BUY else 'SELL'
            precio_actual = mt5.symbol_info_tick(op.symbol).ask if tipo == 'BUY' else mt5.symbol_info_tick(op.symbol).bid
            beneficio = safe_float(getattr(op, 'profit', 0.0))
            total_beneficio += beneficio
            swap = safe_float(getattr(op, 'swap', 0.0))
            commission = safe_float(getattr(op, 'commission', 0.0))
            sl = safe_float(getattr(op, 'sl', 0.0))
            tp = safe_float(getattr(op, 'tp', 0.0))
            
            tabla.add_row(
                str(op.ticket),
                op.symbol,
                tipo,
                f"{safe_float(op.volume):.2f}",
                f"{safe_float(op.price_open):.5f}",
                f"{sl:.5f}" if sl != 0 else "-",
                f"{tp:.5f}" if tp != 0 else "-",
                f"{precio_actual:.5f}",
                f"{beneficio:.2f}",
                f"{swap:.2f}" if swap != 0 else "-",
                f"{commission:.2f}" if commission != 0 else "-"
            )
        except Exception as e:
            console.print(f"[red]Error al procesar operación {op.ticket}: {e}[/red]")
            continue
    tabla.add_row("", "", "", "", "", "", "", "", f"[bold]Total: {total_beneficio:.2f}[/bold]", "", "")
    return Panel(tabla, title="📋 Operaciones Abiertas", border_style="cyan", expand=False)

def main():
    # FASE 6: Usar MT5Manager para conectividad
    logger.log_info("Iniciando Trading Grid con MT5Manager...")
    
    if not mt5_manager.connect():
        logger.log_error("❌ No se pudo inicializar MetaTrader 5.")
        return
    
    logger.log_success("✅ MT5Manager conectado exitosamente")
    
    # SÓTANO 1: Inicializar AnalyticsManager
    logger.log_info("Inicializando AnalyticsManager...")
    if analytics_manager.initialize():
        logger.log_success("✅ AnalyticsManager inicializado correctamente")
    else:
        logger.log_warning("⚠️ AnalyticsManager no se pudo inicializar, continuando sin analytics")
    
    # Primero obtenemos los parámetros necesarios
    modalidad = solicitar_modalidad()
    ganancia_minima, ganancia_maxima, riesgo_sesion = solicitar_parametros_riesgo()
    
    # Inicializamos RiskBot con los parámetros requeridos
    riskbot = RiskBotMT5(
        risk_target_profit=ganancia_minima,
        max_profit_target=ganancia_maxima,
        risk_percent=riesgo_sesion,
        comision_por_lote=0.0  # Valor por defecto, se actualizará después
    )
    
    sesiones_previas = None
    if os.path.exists(parametros_path):
        try:
            with open(parametros_path, "r", encoding="utf-8") as f:
                datos = json.load(f)
                sesiones_previas = datos.get("sesiones")
        except Exception:
            sesiones_previas = None
    opcion_sesiones = input("👉 Ingresa las sesiones de trading (1-6, separadas por comas) o [Enter] para usar las previas: ").strip()
    sesiones_seleccionadas = obtener_sesiones_seleccionadas(opcion_sesiones, sesiones_previas)
    
    modalidad_operacion = solicitar_modalidad_operacion()
    capital_total = riskbot.get_account_balance()
    lotaje_inicial, lotaje_recomendado = solicitar_lotaje_inicial(capital_total, riesgo_sesion)
    
    try:
        import config
        comision_por_lote = getattr(config, "COMISION_POR_LOTE", 0)
    except Exception:
        comision_por_lote = 0
    
    with Live(auto_refresh=False) as live:
        while True:
            try:
                paneles, params = ciclo_riesgo_continuo(
                    riskbot, ganancia_minima, ganancia_maxima, riesgo_sesion,
                    comision_por_lote, sesiones_seleccionadas, modalidad_operacion,
                    lotaje_inicial, lotaje_recomendado, modalidad
                )
                live.update(paneles, refresh=True)
                time.sleep(1)
            except Exception as e:
                console.print(f"[red]Error en ciclo principal: {e}[/red]")
                time.sleep(5)
    
    mt5.shutdown()

if __name__ == "__main__":
    main()