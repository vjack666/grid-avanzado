import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import argparse
from pathlib import Path
from rich.console import Console

def parse_arguments():
    """Parsear argumentos de línea de comandos para especificar el rango de descarga"""
    parser = argparse.ArgumentParser(description='Descargar velas históricas de MT5')
    
    # Grupo de argumentos mutuamente excluyentes
    date_group = parser.add_mutually_exclusive_group()
    
    date_group.add_argument('--meses', '-m', type=int, 
                           help='Número de meses hacia atrás desde hoy (ej: --meses 4)')
    
    date_group.add_argument('--dias', '-d', type=int,
                           help='Número de días hacia atrás desde hoy (ej: --dias 120)')
    
    date_group.add_argument('--desde', '-f', type=str,
                           help='Fecha de inicio en formato YYYY-MM-DD (ej: --desde 2025-04-01)')
    
    parser.add_argument('--hasta', '-t', type=str,
                       help='Fecha final en formato YYYY-MM-DD (por defecto: hoy)')
    
    parser.add_argument('--simbolo', '-s', type=str, default='EURUSD',
                       help='Símbolo a descargar (por defecto: EURUSD)')
    
    return parser.parse_args()

def calculate_date_range(args):
    """Calcular el rango de fechas basado en los argumentos"""
    now = datetime.now()
    
    # Fecha final
    if args.hasta:
        try:
            to_date = datetime.strptime(args.hasta, '%Y-%m-%d')
        except ValueError:
            log_error("Formato de fecha inválido para --hasta. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        to_date = now
    
    # Fecha inicial
    if args.desde:
        try:
            from_date = datetime.strptime(args.desde, '%Y-%m-%d')
        except ValueError:
            log_error("Formato de fecha inválido para --desde. Use YYYY-MM-DD")
            sys.exit(1)
    elif args.meses:
        from_date = now - timedelta(days=args.meses * 30)  # Aproximadamente 30 días por mes
    elif args.dias:
        from_date = now - timedelta(days=args.dias)
    else:
        # Por defecto: desde abril (aproximadamente 4 meses)
        from_date = datetime(now.year, 4, 1)
        if from_date > now:
            from_date = datetime(now.year - 1, 4, 1)
    
    return from_date, to_date

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
def main():
    """Función principal del script"""
    
    # Parsear argumentos de línea de comandos
    args = parse_arguments()
    
    # Calcular rango de fechas
    from_date, to_date = calculate_date_range(args)
    
    # Usar el símbolo especificado o el por defecto
    SYMBOL = args.simbolo.upper()
    
    TIMEFRAMES = {
        'H4': mt5.TIMEFRAME_H4,
        'H1': mt5.TIMEFRAME_H1,
        'M15': mt5.TIMEFRAME_M15,
        'M5': mt5.TIMEFRAME_M5
    }
    
    # Mostrar información del rango de descarga
    days_diff = (to_date - from_date).days
    log_info(f"Configuración de descarga:")
    log_info(f"  Símbolo: {SYMBOL}")
    log_info(f"  Desde: {from_date.strftime('%Y-%m-%d %H:%M:%S')}")
    log_info(f"  Hasta: {to_date.strftime('%Y-%m-%d %H:%M:%S')}")
    log_info(f"  Período: {days_diff} días (~{days_diff/30:.1f} meses)")

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

    # Crear carpeta de salida
    output_dir = os.path.join('data', to_date.strftime('%Y-%m-%d'))
    os.makedirs(output_dir, exist_ok=True)
    
    # Nombre del archivo basado en el período
    period_suffix = f"{days_diff}dias"
    if days_diff >= 30:
        months = round(days_diff / 30, 1)
        if months == int(months):
            period_suffix = f"{int(months)}meses"
        else:
            period_suffix = f"{months}meses"

    for tf_name, tf in TIMEFRAMES.items():
        rates = mt5.copy_rates_range(
            SYMBOL,
            tf,
            from_date,
            to_date
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
        
        out_path = os.path.join(output_dir, f'velas_{SYMBOL}_{tf_name}_{period_suffix}.csv')
        df.to_csv(out_path, index=False)
        log_success(f"Guardado: {out_path} - {len(df)} velas descargadas")

    log_success(f"\nDescarga completada. Archivos guardados en: {output_dir}")
    mt5.shutdown()

SYMBOL = 'EURUSD'  # Cambia el símbolo si lo deseas
TIMEFRAMES = {
    'H4': mt5.TIMEFRAME_H4,
    'H1': mt5.TIMEFRAME_H1,
    'M15': mt5.TIMEFRAME_M15,
    'M5': mt5.TIMEFRAME_M5
}

if __name__ == "__main__":
    main()
