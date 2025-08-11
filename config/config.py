import os
import subprocess
import MetaTrader5 as mt5
from datetime import datetime

# --- Configuración de directorios ---
user_dir = os.path.expanduser("~")
SAFE_DATA_DIR = os.path.join(user_dir, "Documents", "GRID SCALP")
os.makedirs(SAFE_DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(SAFE_DATA_DIR, "data"), exist_ok=True)

# --- Configuración de lotes y ganancias (usuario) ---
LOTE_MINIMO = 0.1
COMISION_POR_LOTE = None  # Lo dispone el usuario
GANANCIA_MINIMA = None    # Lo dispone el usuario
GANANCIA_MAXIMA = None    # Lo dispone el usuario

# --- Configuración operativa ---
DISTANCIA_MINIMA = 0.0010
EFICIENCIA_MINIMA = 0.2
VALOR_PIP_POR_LOTE = 10.0
INTERVALO_SEGUNDOS = 10
LOTE_MAXIMO_TOTAL = 1.0
SIMBOLO = "EURUSD"

# --- Configuración de modos y timeframes ---
MODO_ACTUAL = 'M5'  # default, lo dispone el usuario
BOLLINGER_TIMEFRAME = 'M5'  # default, lo dispone el usuario
ZONA_HORARIA_LOCAL = "America/Guayaquil"
VERBOSE = False

# --- Función de logging debug ---
def log_debug(seccion, mensaje, nivel="INFO"):
    """Función básica de logging debug"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if VERBOSE:
        print(f"[{timestamp}] {seccion}: {mensaje} ({nivel})")

# --- Funciones para actualizar dinámicamente ---
def set_modo_actual(modo):
    global MODO_ACTUAL
    MODO_ACTUAL = modo

def set_bollinger_timeframe(tf):
    global BOLLINGER_TIMEFRAME
    BOLLINGER_TIMEFRAME = tf

def get_bollinger_timeframe():
    return BOLLINGER_TIMEFRAME

def set_ganancias_usuario(ganancia_minima, ganancia_maxima):
    global GANANCIA_MINIMA, GANANCIA_MAXIMA
    GANANCIA_MINIMA = ganancia_minima
    GANANCIA_MAXIMA = ganancia_maxima

# --- Funciones para inicializar CSVs ---
def inicializar_csvs():
    archivos = {
        "data/eventos_sesion.csv": "timestamp,evento,tipo,lote,ticket,extra\n",
        "data/registro_setups.csv": "timestamp,tipo_setup,nivel,timeframe,estado,justificacion\n",
        "data/historial_ordenes.csv": "timestamp,ticket,tipo,lote,precio_entrada,precio_cierre,profit\n",
        "data/log_debug.csv": "timestamp,seccion,mensaje,nivel\n"
    }
    if not os.path.exists("data"):
        os.makedirs("data")
    for ruta, encabezado in archivos.items():
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(encabezado)

# --- Funciones para MetaTrader 5 ---
def inicializar_mt5():
    terminal_path = r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe"
    if not mt5.initialize(path=terminal_path):
        raise Exception(f"Error al conectar con MetaTrader 5 en {terminal_path}")

def cerrar_mt5():
    mt5.shutdown()

def obtener_precio_actual(simbolo):
    tick = mt5.symbol_info_tick(simbolo)
    return tick.ask if tick else None

def obtener_posiciones(tipo=None, simbolo=None):
    posiciones = mt5.positions_get(symbol=simbolo) if simbolo else mt5.positions_get()
    if posiciones is None:
        return []
    if tipo is None:
        return list(posiciones)
    return [p for p in posiciones if p.type == tipo]

def cerrar_posicion(pos, tipo_cierre):
    precio = (mt5.symbol_info_tick(pos.symbol).ask 
              if tipo_cierre == mt5.ORDER_TYPE_BUY 
              else mt5.symbol_info_tick(pos.symbol).bid)
    return mt5.order_send(request={
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pos.symbol,
        "volume": pos.volume,
        "type": tipo_cierre,
        "position": pos.ticket,
        "price": precio,
        "deviation": 10,
        "magic": 123456,
        "comment": "Smart Grid Close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    })

def hay_operacion_abierta():
    posiciones = mt5.positions_get()
    return posiciones is not None and len(posiciones) > 0

def abrir_terminal_mt5():
    terminal_path = r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe"
    if not os.path.exists(terminal_path):
        raise FileNotFoundError(f"No se encontró terminal64.exe en {terminal_path}")
    subprocess.Popen([terminal_path], shell=True)
