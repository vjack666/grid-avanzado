import MetaTrader5 as mt5
im    log_error(f"Código: {error_code}")
    log_error(f"Mensaje: {error_message}")
    log_info("Posibles soluciones:")
    log_info("1. Asegúrate de que MetaTrader 5 esté abierto")
    log_info("2. Verifica que estés logueado en MT5")
    log_info("3. Comprueba que la cuenta esté activa")
    log_info("4. Reinicia MetaTrader 5 e intenta de nuevo")
    raise RuntimeError(f"No se pudo inicializar MT5: {error_code} - {error_message}")

log_success("MetaTrader 5 conectado exitosamente")
log_info(f"Versión MT5: {mt5.version()}")
log_info(f"Información de la cuenta: {mt5.account_info()}")
log_info(f"Terminal: {mt5.terminal_info()}")s pd
from datetime import datetime, timedelta
import os

# Configuración simple de logging para este archivo  
def log_info(mensaje):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ℹ️ {mensaje}")

def log_success(mensaje):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {mensaje}")

def log_error(mensaje):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {mensaje}")

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
    logger.log_error(f"Mensaje: {error_message}")
    logger.log_info("Posibles soluciones:")
    logger.log_info("1. Asegúrate de que MetaTrader 5 esté abierto")
    logger.log_info("2. Verifica que estés logueado en MT5")
    logger.log_info("3. Comprueba que la cuenta esté activa")
    logger.log_info("4. Reinicia MetaTrader 5 e intenta de nuevo")
    raise RuntimeError(f"No se pudo inicializar MT5: {error_code} - {error_message}")

logger.log_success("MetaTrader 5 conectado exitosamente")
logger.log_info(f"Versión MT5: {mt5.version()}")
logger.log_info(f"Información de la cuenta: {mt5.account_info()}")
logger.log_info(f"Terminal: {mt5.terminal_info()}")

# Calcular fechas - último mes y medio (6 semanas)
now = datetime.now()
from_date = now - timedelta(weeks=6)

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
        print(f"No se pudieron descargar velas para {tf_name}")
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
    
    out_path = os.path.join(output_dir, f'velas_{SYMBOL}_{tf_name}_6semanas.csv')
    df.to_csv(out_path, index=False)
    logger.log_success(f"Guardado: {out_path} - {len(df)} velas descargadas")

logger.log_success(f"Descarga completada. Archivos guardados en: {output_dir}")
mt5.shutdown()
