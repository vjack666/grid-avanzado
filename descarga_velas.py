import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
from rich.console import Console

# Agregar el directorio padre al path para importar managers
sys.path.append(str(Path(__file__).parent))
try:
    from src.core.logger_manager import LoggerManager
    from src.core.data_manager import DataManager  # FASE 4
    logger = LoggerManager()
    data_manager = DataManager()  # FASE 4: Gestión centralizada de datos
    has_logger = True
    has_data_manager = True
except ImportError:
    console = Console()
    has_logger = False
    has_data_manager = False

def log_info(message):
    if has_logger:
        logger.log_info(message)
    else:
        console.print(f"[cyan]INFO:[/cyan] {message}")

def log_error(message):
    if has_logger:
        logger.log_error(message)
    else:
        console.print(f"[red]ERROR:[/red] {message}")

def log_success(message):
    if has_logger:
        logger.log_success(message)
    else:
        console.print(f"[green]SUCCESS:[/green] {message}")

# Configuración de símbolos y timeframes
SYMBOL = 'EURUSD'  # Cambia el símbolo si lo deseas
TIMEFRAMES = {
    'H4': mt5.TIMEFRAME_H4,
    'H1': mt5.TIMEFRAME_H1,
    'M15': mt5.TIMEFRAME_M15,
    'M5': mt5.TIMEFRAME_M5
}

# Inicializar MetaTrader 5
log_info("Intentando conectar con MetaTrader 5...")
if not mt5.initialize():
    error_code, error_message = mt5.last_error()
    log_error(f"Error al inicializar MT5:")
    log_error(f"Código: {error_code}")
    log_error(f"Mensaje: {error_message}")
    log_info("\nPosibles soluciones:")
    log_info("1. Asegúrate de que MetaTrader 5 esté abierto")
    log_info("2. Verifica que estés logueado en MT5")
    log_info("3. Comprueba que la cuenta esté activa")
    log_info("4. Reinicia MetaTrader 5 e intenta de nuevo")
    raise RuntimeError(f"No se pudo inicializar MT5: {error_code} - {error_message}")

log_success("MetaTrader 5 conectado exitosamente")
try:
    version_info = mt5.version()
    if version_info:
        log_info(f"Versión MT5: {version_info[0]}.{version_info[1]} build {version_info[2]}")
except AttributeError:
    log_info("Versión MT5: Información no disponible")

try:
    account_info = mt5.account_info()
    if account_info:
        log_info(f"Cuenta: {account_info.name} | Balance: ${account_info.balance:.2f} | Servidor: {account_info.server}")
except AttributeError:
    log_info("Información de la cuenta: No disponible")

try:
    terminal_info = mt5.terminal_info()
    if terminal_info:
        log_info(f"Terminal: {terminal_info.name} | Build: {terminal_info.build} | Conectado: {'Sí' if terminal_info.connected else 'No'}")
except AttributeError:
    log_info("Terminal: Información no disponible")

# Calcular fechas - últimos 3 meses (12 semanas)
now = datetime.now()
from_date = now - timedelta(weeks=12)  # 3 meses = ~12 semanas

# Crear carpeta de salida
output_dir = os.path.join('data', now.strftime('%Y-%m-%d'))
os.makedirs(output_dir, exist_ok=True)

for tf_name, tf in TIMEFRAMES.items():
    rates = mt5.copy_rates_range(
        SYMBOL,
        tf,
        from_date,
        now
    )
    if rates is None or len(rates) == 0:
        log_error(f"No se pudieron descargar velas para {tf_name}")
        continue
    
    # Crear DataFrame con todas las columnas OHLC y información adicional
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Renombrar columnas para mayor claridad
    df = df.rename(columns={
        'time': 'datetime',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'tick_volume': 'volume',
        'spread': 'spread',
        'real_volume': 'real_volume'
    })
    
    # Reordenar columnas para formato OHLC estándar
    column_order = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'spread', 'real_volume']
    df = df[column_order]
    
    # Agregar información adicional para IA externa
    df['symbol'] = SYMBOL
    df['timeframe'] = tf_name
    df['weekday'] = df['datetime'].dt.day_name()
    df['hour'] = df['datetime'].dt.hour
    
    out_path = os.path.join(output_dir, f'velas_{SYMBOL}_{tf_name}_3meses.csv')
    df.to_csv(out_path, index=False)
    log_success(f"Guardado: {out_path} - {len(df)} velas descargadas")

log_success(f"\nDescarga completada. Archivos guardados en: {output_dir}")
mt5.shutdown()
