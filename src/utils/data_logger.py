# data_logger.py

# =============================================================================
# SECCIÓN 1: IMPORTACIONES DE LIBRERÍAS
# =============================================================================
import sys
from pathlib import Path

# Configurar rutas para imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent  # Ir dos niveles hacia arriba desde src/utils
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis").absolute()))
sys.path.insert(0, str((project_root / "src" / "utils").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))


import csv
import os
from datetime import datetime
import pytz

# Importar constantes y log_debug desde config
from config import SIMBOLO, SAFE_DATA_DIR, ZONA_HORARIA_LOCAL, log_debug  # type: ignore

# =============================================================================
# SECCIÓN 2: DEFINICIÓN DE RUTAS DE ARCHIVOS CSV DE LOG
# =============================================================================
LOG_OPERACIONES_PATH = os.path.join(SAFE_DATA_DIR, "log_operaciones_ejecutadas.csv")
LOG_POSICIONES_CERRADAS_PATH = os.path.join(SAFE_DATA_DIR, "log_posiciones_cerradas.csv")
LOG_ANALISIS_PERIODICO_PATH = os.path.join(SAFE_DATA_DIR, "log_analisis_periodico.csv")
LOG_ERRORES_CRITICOS_PATH = os.path.join(SAFE_DATA_DIR, "log_errores_criticos.csv")

# =============================================================================
# SECCIÓN 3: FUNCIONES DE INICIALIZACIÓN DE CSVs ESPECÍFICOS
# =============================================================================

def inicializar_csvs_logger() -> None:
    """
    Crea los archivos CSV de log si no existen y escribe los encabezados.
    Esta función complementa a inicializar_csvs en config.py.
    """
    os.makedirs(SAFE_DATA_DIR, exist_ok=True) # Asegurarse de que el directorio exista

    # log_operaciones_ejecutadas.csv
    if not os.path.exists(LOG_OPERACIONES_PATH):
        with open(LOG_OPERACIONES_PATH, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp_utc', 'timestamp_local', 'simbolo', 'tipo_orden',
                'volumen_solicitado', 'precio_solicitado', 'sl_solicitado', 'tp_solicitado',
                'estrategia_origen', 'cruce_estocastico', 'zona_estocastico',
                'fase_bollinger', 'ancho_banda_bollinger', 'resultado_mt5_retcode',
                'resultado_mt5_comment', 'ticket_orden_mt5', 'precio_ejecucion',
                'error_detalle'
            ])
        log_debug("DataLogger", "Archivo log_operaciones_ejecutadas.csv creado.", "INFO")
    else:
        log_debug("DataLogger", "Archivo log_operaciones_ejecutadas.csv ya existe.", "INFO")

    # log_posiciones_cerradas.csv
    if not os.path.exists(LOG_POSICIONES_CERRADAS_PATH):
        with open(LOG_POSICIONES_CERRADAS_PATH, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp_cierre_utc', 'timestamp_cierre_local', 'ticket_posicion',
                'simbolo', 'tipo_posicion', 'volumen_cerrado', 'precio_apertura',
                'precio_cierre', 'profit_bruto_usd', 'comision_usd',
                'profit_neto_usd', 'duracion_segundos', 'motivo_cierre'
            ])
        log_debug("DataLogger", "Archivo log_posiciones_cerradas.csv creado.", "INFO")
    else:
        log_debug("DataLogger", "Archivo log_posiciones_cerradas.csv ya existe.", "INFO")

    # log_analisis_periodico.csv
    if not os.path.exists(LOG_ANALISIS_PERIODICO_PATH):
        with open(LOG_ANALISIS_PERIODICO_PATH, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp_utc', 'timestamp_local', 'simbolo', 'precio_actual_bid',
                'precio_actual_ask', 'spread_actual', 'k_estocastico', 'd_estocastico',
                'k_prev_estocastico', 'd_prev_estocastico', 'cruce_k_up_d', 'cruce_k_down_d',
                'estocastico_sobreventa', 'estocastico_sobrecompra', 'bollinger_upper',
                'bollinger_sma', 'bollinger_lower', 'bollinger_ancho_banda',
                'fase_bollinger', 'balance_cuenta', 'equity_cuenta',
                'profit_flotante_total', 'num_posiciones_abiertas', 'lotaje_total_abierto',
                'accion_sugerida_bot', 'motivo_no_operar'
            ])
        log_debug("DataLogger", "Archivo log_analisis_periodico.csv creado.", "INFO")
    else:
        log_debug("DataLogger", "Archivo log_analisis_periodico.csv ya existe.", "INFO")

    # log_errores_criticos.csv
    if not os.path.exists(LOG_ERRORES_CRITICOS_PATH):
        with open(LOG_ERRORES_CRITICOS_PATH, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp_utc', 'timestamp_local', 'seccion', 'tipo_error',
                'mensaje_error', 'traceback'
            ])
        log_debug("DataLogger", "Archivo log_errores_criticos.csv creado.", "INFO")
    else:
        log_debug("DataLogger", "Archivo log_errores_criticos.csv ya existe.", "INFO")


# =============================================================================
# SECCIÓN 4: FUNCIONES PARA REGISTRAR DATOS
# =============================================================================

def log_operacion_ejecutada(
    simbolo: str, tipo_orden: str, volumen_solicitado: float, precio_solicitado: float, 
    sl_solicitado: float, tp_solicitado: float, estrategia_origen: str, cruce_estocastico: str, 
    zona_estocastico: str, fase_bollinger: str, ancho_banda_bollinger: float,
    resultado_mt5_retcode: int, resultado_mt5_comment: str, ticket_orden_mt5: int, 
    precio_ejecucion: float, error_detalle: str = ""
) -> None:
    """Registra los detalles de cada intento de operación."""
    tz = pytz.timezone(ZONA_HORARIA_LOCAL)
    now_utc = datetime.utcnow()
    now_local = datetime.now(tz=tz)
    
    with open(LOG_OPERACIONES_PATH, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            now_utc.strftime('%Y-%m-%d %H:%M:%S'),
            now_local.strftime('%Y-%m-%d %H:%M:%S'),
            simbolo, tipo_orden, volumen_solicitado, precio_solicitado,
            sl_solicitado, tp_solicitado, estrategia_origen, cruce_estocastico,
            zona_estocastico, fase_bollinger, ancho_banda_bollinger,
            resultado_mt5_retcode, resultado_mt5_comment, ticket_orden_mt5,
            precio_ejecucion, error_detalle
        ])
    log_debug("DataLogger", f"Operación {tipo_orden} {ticket_orden_mt5} registrada en CSV.", "INFO")


def log_posicion_cerrada(
    ticket_posicion, simbolo, tipo_posicion, volumen_cerrado, precio_apertura,
    precio_cierre, profit_bruto_usd, comision_usd, profit_neto_usd,
    duracion_segundos, motivo_cierre
):
    """Registra los detalles de cada posición cerrada."""
    tz = pytz.timezone(ZONA_HORARIA_LOCAL)
    now_utc = datetime.utcnow()
    now_local = datetime.now(tz=tz)

    with open(LOG_POSICIONES_CERRADAS_PATH, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            now_utc.strftime('%Y-%m-%d %H:%M:%S'),
            now_local.strftime('%Y-%m-%d %H:%M:%S'),
            ticket_posicion, simbolo, tipo_posicion, volumen_cerrado,
            precio_apertura, precio_cierre, profit_bruto_usd, comision_usd,
            profit_neto_usd, duracion_segundos, motivo_cierre
        ])
    log_debug("DataLogger", f"Posición {ticket_posicion} cerrada ({motivo_cierre}) registrada en CSV.", "INFO")


def log_analisis_periodico(
    simbolo, precio_actual_bid, precio_actual_ask, spread_actual,
    k_estocastico, d_estocastico, k_prev_estocastico, d_prev_estocastico,
    cruce_k_up_d, cruce_k_down_d, estocastico_sobreventa, estocastico_sobrecompra,
    bollinger_upper, bollinger_sma, bollinger_lower, bollinger_ancho_banda,
    fase_bollinger, balance_cuenta, equity_cuenta, profit_flotante_total,
    num_posiciones_abiertas, lotaje_total_abierto, accion_sugerida_bot, motivo_no_operar
):
    """Registra un snapshot detallado del estado del bot y del mercado en cada ciclo."""
    tz = pytz.timezone(ZONA_HORARIA_LOCAL)
    now_utc = datetime.utcnow()
    now_local = datetime.now(tz=tz)

    with open(LOG_ANALISIS_PERIODICO_PATH, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            now_utc.strftime('%Y-%m-%d %H:%M:%S'),
            now_local.strftime('%Y-%m-%d %H:%M:%S'),
            simbolo, precio_actual_bid, precio_actual_ask, spread_actual,
            k_estocastico, d_estocastico, k_prev_estocastico, d_prev_estocastico,
            cruce_k_up_d, cruce_k_down_d, estocastico_sobreventa, estocastico_sobrecompra,
            bollinger_upper, bollinger_sma, bollinger_lower, bollinger_ancho_banda,
            fase_bollinger, balance_cuenta, equity_cuenta, profit_flotante_total,
            num_posiciones_abiertas, lotaje_total_abierto, accion_sugerida_bot, motivo_no_operar
        ])
    # log_debug("DataLogger", "Análisis periódico registrado en CSV.", "DEBUG") # Demasiado verboso si es cada 0.5s

def log_error_critico(seccion, tipo_error, mensaje_error, traceback_info=""):
    """Registra errores críticos o inesperados con detalles del traceback."""
    tz = pytz.timezone(ZONA_HORARIA_LOCAL)
    now_utc = datetime.utcnow()
    now_local = datetime.now(tz=tz)

    with open(LOG_ERRORES_CRITICOS_PATH, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            now_utc.strftime('%Y-%m-%d %H:%M:%S'),
            now_local.strftime('%Y-%m-%d %H:%M:%S'),
            seccion, tipo_error, mensaje_error, traceback_info
        ])
    log_debug("DataLogger", f"Error crítico registrado: {mensaje_error}", "ERROR")