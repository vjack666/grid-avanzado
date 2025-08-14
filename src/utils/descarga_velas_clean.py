#!/usr/bin/env python3
"""
DESCARGADOR DE VELAS MT5 - Sin warnings Pylance
===============================================
Versión optimizada que evita warnings de análisis estático
"""

import sys
import pandas as pd
from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Optional, Any

# Configuración simple de logging
def log_info(mensaje: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ℹ️ {mensaje}")

def log_success(mensaje: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {mensaje}")

def log_error(mensaje: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {mensaje}")

def log_warning(mensaje: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ {mensaje}")

# Configuración
SYMBOL = 'EURUSD'
WEEKS_TO_DOWNLOAD = 6

def safe_mt5_call(mt5_module: Any, function_name: str, *args, **kwargs) -> Any:
    """Llamada segura a funciones MT5 que evita warnings de Pylance"""
    try:
        func = getattr(mt5_module, function_name)
        return func(*args, **kwargs)
    except AttributeError:
        log_error(f"Función {function_name} no encontrada en MT5")
        return None
    except Exception as e:
        log_error(f"Error ejecutando {function_name}: {e}")
        return None

def initialize_mt5() -> Optional[Any]:
    """Inicializar conexión con MetaTrader 5 sin warnings"""
    try:
        # Importar MT5
        import MetaTrader5 as mt5
        
        log_info("Inicializando conexión con MetaTrader 5...")
        
        # Llamada segura a initialize
        if not safe_mt5_call(mt5, 'initialize'):
            # Obtener error de forma segura
            error_info = safe_mt5_call(mt5, 'last_error')
            if error_info:
                error_code = error_info[0] if error_info else "Desconocido"
                error_msg = error_info[1] if len(error_info) > 1 else "Sin descripción"
                log_error(f"Error MT5 - Código: {error_code}, Mensaje: {error_msg}")
            else:
                log_error("Error MT5 - No se pudo obtener detalle")
            
            log_error("Soluciones:")
            log_error("  1. Abrir MetaTrader 5")
            log_error("  2. Iniciar sesión en cuenta")
            log_error("  3. Verificar que MT5 esté disponible")
            
            return None
        
        log_success("MetaTrader 5 conectado exitosamente")
        
        # Información de conexión de forma segura
        try:
            version = safe_mt5_call(mt5, 'version')
            account = safe_mt5_call(mt5, 'account_info')
            terminal = safe_mt5_call(mt5, 'terminal_info')
            
            if version:
                log_info(f"Versión MT5: {version}")
            if account:
                log_info(f"Cuenta: {account.login} - {account.server}")
            if terminal:
                log_info(f"Terminal: {terminal.name}")
                
        except Exception as e:
            log_warning(f"No se pudo obtener información detallada: {e}")
        
        return mt5
        
    except ImportError:
        log_error("MetaTrader5 no está instalado")
        log_error("Instalar con: pip install MetaTrader5")
        return None
    except Exception as e:
        log_error(f"Error inesperado inicializando MT5: {e}")
        return None

def get_timeframe_constants(mt5_module: Any) -> dict:
    """Obtener constantes de timeframe de forma segura"""
    try:
        return {
            'H4': getattr(mt5_module, 'TIMEFRAME_H4', 16385),
            'H1': getattr(mt5_module, 'TIMEFRAME_H1', 16385),
            'M15': getattr(mt5_module, 'TIMEFRAME_M15', 15),
            'M5': getattr(mt5_module, 'TIMEFRAME_M5', 5)
        }
    except Exception as e:
        log_warning(f"Usando valores por defecto para timeframes: {e}")
        return {
            'H4': 16385,
            'H1': 16385, 
            'M15': 15,
            'M5': 5
        }

def download_timeframe_data(mt5_module: Any, symbol: str, timeframe_name: str, 
                          timeframe_value: int, from_date: datetime, 
                          to_date: datetime, output_dir: str) -> bool:
    """Descargar datos para un timeframe específico"""
    try:
        log_info(f"Descargando {symbol} {timeframe_name}...")
        
        # Llamada segura a copy_rates_range
        rates = safe_mt5_call(mt5_module, 'copy_rates_range', 
                             symbol, timeframe_value, from_date, to_date)
        
        if rates is None or len(rates) == 0:
            log_error(f"No se pudieron obtener datos para {timeframe_name}")
            return False
        
        # Convertir a DataFrame
        df = pd.DataFrame(rates)
        
        # Procesar timestamps
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Renombrar columnas
        column_mapping = {
            'time': 'datetime',
            'open': 'open',
            'high': 'high', 
            'low': 'low',
            'close': 'close',
            'tick_volume': 'volume'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})
        
        # Verificar columnas esenciales
        required_cols = ['datetime', 'open', 'high', 'low', 'close']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            log_error(f"Faltan columnas esenciales: {missing}")
            return False
        
        # Agregar metadatos
        df['symbol'] = symbol
        df['timeframe'] = timeframe_name
        df['weekday'] = df['datetime'].dt.day_name()
        df['hour'] = df['datetime'].dt.hour
        df['date'] = df['datetime'].dt.date
        
        # Seleccionar columnas finales
        final_columns = ['datetime', 'open', 'high', 'low', 'close']
        
        # Agregar columnas opcionales
        optional_cols = ['volume', 'spread', 'real_volume']
        for col in optional_cols:
            if col in df.columns:
                final_columns.append(col)
        
        final_columns.extend(['symbol', 'timeframe', 'weekday', 'hour', 'date'])
        df = df[final_columns]
        
        # Guardar archivo
        filename = f'velas_{symbol}_{timeframe_name}_{WEEKS_TO_DOWNLOAD}semanas.csv'
        filepath = os.path.join(output_dir, filename)
        
        df.to_csv(filepath, index=False)
        log_success(f"Guardado: {filename} ({len(df)} velas)")
        
        return True
        
    except Exception as e:
        log_error(f"Error descargando {timeframe_name}: {str(e)}")
        return False

def main() -> bool:
    """Función principal"""
    print("🚀 DESCARGADOR DE VELAS MT5 - Trading Grid")
    print("="*50)
    
    mt5_module = None
    
    try:
        # Inicializar MT5
        mt5_module = initialize_mt5()
        if not mt5_module:
            log_error("No se pudo conectar con MetaTrader 5")
            return False
        
        # Obtener timeframes
        timeframes = get_timeframe_constants(mt5_module)
        
        # Calcular fechas
        now = datetime.now()
        from_date = now - timedelta(weeks=WEEKS_TO_DOWNLOAD)
        
        log_info(f"Período: {from_date.strftime('%Y-%m-%d')} a {now.strftime('%Y-%m-%d')}")
        log_info(f"Símbolo: {SYMBOL}")
        
        # Crear directorio
        output_dir = os.path.join('data', now.strftime('%Y-%m-%d'))
        os.makedirs(output_dir, exist_ok=True)
        log_info(f"Directorio: {output_dir}")
        
        # Descargar cada timeframe
        successful_downloads = 0
        
        for tf_name, tf_value in timeframes.items():
            success = download_timeframe_data(
                mt5_module, SYMBOL, tf_name, tf_value, 
                from_date, now, output_dir
            )
            if success:
                successful_downloads += 1
        
        # Resumen
        log_success(f"Descarga completada: {successful_downloads}/{len(timeframes)} timeframes")
        
        if successful_downloads > 0:
            log_success(f"Archivos guardados en: {output_dir}")
            
            # Listar archivos
            log_info("Archivos creados:")
            for file in Path(output_dir).glob(f"velas_{SYMBOL}_*.csv"):
                size_mb = file.stat().st_size / (1024 * 1024)
                log_info(f"  📄 {file.name} ({size_mb:.2f} MB)")
        
        return successful_downloads > 0
        
    except Exception as e:
        log_error(f"Error crítico: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cerrar MT5 de forma segura
        if mt5_module:
            try:
                safe_mt5_call(mt5_module, 'shutdown')
                log_info("Conexión MT5 cerrada")
            except:
                log_warning("No se pudo cerrar MT5 correctamente")

if __name__ == "__main__":
    success = main()
    
    print("\n" + "="*50)
    if success:
        print("🎉 DESCARGA EXITOSA")
        print("✅ Los datos están listos para usar en el backtest")
    else:
        print("❌ DESCARGA FALLÓ")
        print("⚠️ Revisa la configuración de MT5")
    print("="*50)
    
    sys.exit(0 if success else 1)
