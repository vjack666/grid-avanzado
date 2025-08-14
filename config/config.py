import os
import subprocess
import MetaTrader5 as mt5
from datetime import datetime
from typing import Optional, List, Any

# --- Configuración de seguridad de terminales ---
# MODO SEGURO ACTIVADO: No interfiere con otros bots
SAFE_TERMINAL_MODE = True
BOT_PROTECTION_ENABLED = True

# --- Configuración de directorios ---
user_dir: str = os.path.expanduser("~")
SAFE_DATA_DIR: str = os.path.join(user_dir, "Documents", "GRID SCALP")
os.makedirs(SAFE_DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(SAFE_DATA_DIR, "data"), exist_ok=True)

# --- Configuración de lotes y ganancias (usuario) ---
LOTE_MINIMO: float = 0.1
COMISION_POR_LOTE: Optional[float] = None  # Lo dispone el usuario
GANANCIA_MINIMA: Optional[float] = None    # Lo dispone el usuario
GANANCIA_MAXIMA: Optional[float] = None    # Lo dispone el usuario

# --- Configuración operativa ---
DISTANCIA_MINIMA: float = 0.0010
EFICIENCIA_MINIMA: float = 0.2
VALOR_PIP_POR_LOTE: float = 10.0
INTERVALO_SEGUNDOS: int = 10
LOTE_MAXIMO_TOTAL: float = 1.0
SIMBOLO: str = "EURUSD"

# --- Configuración de modos y timeframes ---
MODO_ACTUAL: str = 'M5'  # default, lo dispone el usuario
BOLLINGER_TIMEFRAME: str = 'M5'  # default, lo dispone el usuario
ZONA_HORARIA_LOCAL: str = "America/Guayaquil"
VERBOSE: bool = False

# --- Función de logging debug ---
def log_debug(seccion: str, mensaje: str, nivel: str = "INFO") -> None:
    """Función básica de logging debug"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if VERBOSE:
        print(f"[{timestamp}] {seccion}: {mensaje} ({nivel})")

# --- Funciones para actualizar dinámicamente ---
def set_modo_actual(modo: str) -> None:
    global MODO_ACTUAL
    MODO_ACTUAL = modo

def set_bollinger_timeframe(tf: str) -> None:
    global BOLLINGER_TIMEFRAME
    BOLLINGER_TIMEFRAME = tf

def get_bollinger_timeframe() -> str:
    return BOLLINGER_TIMEFRAME

def set_ganancias_usuario(ganancia_minima: float, ganancia_maxima: float) -> None:
    global GANANCIA_MINIMA, GANANCIA_MAXIMA
    GANANCIA_MINIMA = ganancia_minima
    GANANCIA_MAXIMA = ganancia_maxima

# --- Funciones para inicializar CSVs ---
def inicializar_csvs() -> None:
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
def inicializar_mt5() -> None:
    terminal_path = r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe"
    if not mt5.initialize(path=terminal_path):  # type: ignore
        raise Exception(f"Error al conectar con MetaTrader 5 en {terminal_path}")

def cerrar_mt5() -> None:
    mt5.shutdown()  # type: ignore

def obtener_precio_actual(simbolo: str) -> Optional[float]:
    tick = mt5.symbol_info_tick(simbolo)  # type: ignore
    return tick.ask if tick else None  # type: ignore

def obtener_posiciones(tipo: Optional[int] = None, simbolo: Optional[str] = None) -> List[Any]:
    posiciones = mt5.positions_get(symbol=simbolo) if simbolo else mt5.positions_get()  # type: ignore
    if posiciones is None:
        return []
    if tipo is None:
        return list(posiciones)
    return [p for p in posiciones if p.type == tipo]  # type: ignore

def cerrar_posicion(pos: Any, tipo_cierre: int) -> Any:
    precio = (mt5.symbol_info_tick(pos.symbol).ask   # type: ignore
              if tipo_cierre == mt5.ORDER_TYPE_BUY   # type: ignore
              else mt5.symbol_info_tick(pos.symbol).bid)  # type: ignore
    return mt5.order_send(request={  # type: ignore
        "action": mt5.TRADE_ACTION_DEAL,  # type: ignore
        "symbol": pos.symbol,  # type: ignore
        "volume": pos.volume,  # type: ignore
        "type": tipo_cierre,
        "position": pos.ticket,  # type: ignore
        "price": precio,
        "deviation": 10,
        "magic": 123456,
        "comment": "Smart Grid Close",
        "type_time": mt5.ORDER_TIME_GTC,  # type: ignore
        "type_filling": mt5.ORDER_FILLING_IOC  # type: ignore
    })

def hay_operacion_abierta() -> bool:
    posiciones = mt5.positions_get()  # type: ignore
    return posiciones is not None and len(posiciones) > 0

def abrir_terminal_mt5() -> None:
    terminal_path = r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe"
    if not os.path.exists(terminal_path):
        raise FileNotFoundError(f"No se encontró terminal64.exe en {terminal_path}")
    subprocess.Popen([terminal_path], shell=True)
