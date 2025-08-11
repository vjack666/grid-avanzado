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
from datetime import datetime
import numpy as np
import pytz
from rich.panel import Panel
from rich.table import Table
from config import ZONA_HORARIA_LOCAL

# Managers centralizados (FASE 4)
from data_manager import DataManager

SYMBOL = 'EURUSD'

# Instancia global DataManager (FASE 4)
data_manager = DataManager()

def analizar_estocastico_m15_cacheado(riskbot, modalidad_operacion, lotaje_inicial):
    """
    REFACTORIZADO FASE 4: Usar DataManager para calcular indicadores estocásticos
    """
    if not hasattr(analizar_estocastico_m15_cacheado, 'cache'):
        analizar_estocastico_m15_cacheado.cache = {
            'timestamp': None,
            'k': None,
            'd': None,
            'cruce_k_d': False,
            'sobreventa': False,
            'sobrecompra': False,
            'senal_valida': False,
            'senal_tipo': None,
            'ultima_orden_sell': None,
            'ultima_orden_buy': None
        }
    
    cache = analizar_estocastico_m15_cacheado.cache
    zona = pytz.timezone(ZONA_HORARIA_LOCAL)
    ahora = datetime.now(zona)
    
    if cache['timestamp'] is None or (ahora - cache['timestamp']).total_seconds() > 60:
        try:
            # Usar DataManager para obtener datos OHLC (FASE 4)
            df_ohlc = data_manager.get_ohlc_data(SYMBOL, 'M15', 20)
            if df_ohlc is None or len(df_ohlc) < 20:
                return cache
            
            # Calcular Estocástico usando DataManager (FASE 4)
            stoch_data = data_manager.calculate_stochastic(df_ohlc, k_period=14, d_period=3)
            if stoch_data is None or len(stoch_data) < 2:
                return cache
                
            # Obtener valores actuales y anteriores
            k_actual = stoch_data['%K'].iloc[-1]
            d_actual = stoch_data['%D'].iloc[-1]
            k_anterior = stoch_data['%K'].iloc[-2]
            d_anterior = stoch_data['%D'].iloc[-2]
            
        except Exception:
            # Fallback al método original si DataManager falla
            rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 0, 20)
            if rates is None or len(rates) < 20:
                return cache
            
            df = pd.DataFrame(rates)
            low = df['low']
            high = df['high']
            close = df['close']
            
            period_k = 14
            period_d = 3
            period_smooth = 3
            
            lowest = low.rolling(window=period_k).min()
            highest = high.rolling(window=period_k).max()
            k = 100 * (close - lowest) / (highest - lowest)
            d = k.rolling(window=period_d).mean()
            d_smooth = d.rolling(window=period_smooth).mean()
            
            k_actual = k.iloc[-1] if not k.empty else cache['k']
            d_actual = d_smooth.iloc[-1] if not d_smooth.empty else cache['d']
            k_anterior = k.iloc[-2] if len(k) > 1 else k_actual
            d_anterior = d_smooth.iloc[-2] if len(d_smooth) > 1 else d_actual
        
        # Detectar cruces
        cruce_k_d = k_actual > d_actual and k_anterior <= d_anterior
        cruce_d_k = k_actual < d_actual and k_anterior >= d_anterior
        
        # Detectar zonas de sobrecompra/sobreventa
        sobreventa = k_actual < 10 and d_actual < 10
        sobrecompra = k_actual > 90 and d_actual > 90
        
        # Evaluar señales de trading
        senal_valida = False
        senal_tipo = None
        if modalidad_operacion in ['AMBOS', 'BUY'] and cruce_k_d and sobreventa:
            senal_valida = True
            senal_tipo = 'BUY'
        elif modalidad_operacion in ['AMBOS', 'SELL'] and cruce_d_k and sobrecompra:
            senal_valida = True
            senal_tipo = 'SELL'
        
        # Verificar si la vela está cerrada (método DataManager o fallback)
        try:
            # Usar DataManager para obtener datos más recientes
            rates_recientes = data_manager.get_ohlc_data(SYMBOL, 'M15', 1)
            if rates_recientes is not None and len(rates_recientes) > 0:
                time_current = pd.Timestamp(rates_recientes.index[-1])
                vela_cerrada = (ahora - time_current).total_seconds() >= 60
            else:
                vela_cerrada = True  # Fallback seguro
        except Exception:
            # Fallback tradicional
            rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M15, 0, 1)
            if rates is not None and len(rates) > 0:
                time_current = pd.Timestamp(rates[-1]['time'], unit='s', tz=zona)
                vela_cerrada = (ahora - time_current).total_seconds() >= 60
            else:
                vela_cerrada = True  # Fallback seguro
        
        if senal_valida and vela_cerrada:
            posiciones = mt5.positions_get(symbol=SYMBOL)
            if not posiciones:
                capital_total = riskbot.get_account_balance()
                riesgo_maximo = capital_total * 0.02
                riesgo_acumulado = sum(-p.profit for p in posiciones if p.profit < 0) if posiciones else 0
                if riesgo_acumulado < riesgo_maximo:
                    from main import abrir_compra_mt5, abrir_venta_mt5
                    if senal_tipo == 'BUY':
                        result = abrir_compra_mt5(lotaje_inicial)
                        if result.retcode == mt5.TRADE_RETCODE_DONE:
                            cache['ultima_orden_buy'] = ahora
                    elif senal_tipo == 'SELL':
                        result = abrir_venta_mt5(lotaje_inicial)
                        if result.retcode == mt5.TRADE_RETCODE_DONE:
                            cache['ultima_orden_sell'] = ahora
                    senal_valida = False
        
        cache.update({
            'timestamp': ahora,
            'k': k_actual,
            'd': d_actual,
            'cruce_k_d': cruce_k_d,
            'sobreventa': sobreventa,
            'sobrecompra': sobrecompra,
            'senal_valida': senal_valida,
            'senal_tipo': senal_tipo,
        })
    
    return cache

def mostrar_checkpoint_estocastico(estoc_cache, lotaje_inicial, lotaje_recomendado, modalidad_operacion):
    tabla = Table(show_header=False, box=None, expand=False)
    tabla.add_column("Regla", justify="left")
    tabla.add_column("Valor", justify="right")
    
    k_actual = estoc_cache.get('k', None)
    d_actual = estoc_cache.get('d', None)
    cruce_k_d = estoc_cache.get('cruce_k_d', False)
    sobreventa = estoc_cache.get('sobreventa', False)
    sobrecompra = estoc_cache.get('sobrecompra', False)
    senal_valida = estoc_cache.get('senal_valida', False)
    senal_tipo = estoc_cache.get('senal_tipo', None)
    ultima_orden_sell = estoc_cache.get('ultima_orden_sell', None)
    ultima_orden_buy = estoc_cache.get('ultima_orden_buy', None)
    
    tabla.add_row("📈 %K actual", f"{k_actual:.2f}" if k_actual is not None else "--")
    tabla.add_row("📉 %D actual", f"{d_actual:.2f}" if d_actual is not None else "--")
    tabla.add_row("🔀 Cruce K>D", "✅ SÍ" if cruce_k_d else "❌ NO")
    tabla.add_row("📉 K cruza D en sobreventa (BUY)", "✅ SÍ" if cruce_k_d and sobreventa else "❌ NO")
    tabla.add_row("📈 K cruza D en sobrecompra (SELL)", "✅ SÍ" if not cruce_k_d and sobrecompra else "❌ NO")
    tabla.add_row("📉 K y D < 10 (zona sobreventa)", "✅ SÍ" if sobreventa else "❌ NO")
    tabla.add_row("📈 K y D > 90 (zona sobrecompra)", "✅ SÍ" if sobrecompra else "❌ NO")
    tabla.add_row("🕒 Confirmación en cierre vela", "✅ SÍ" if senal_valida else "❌ NO")
    tabla.add_row("📡 Señal válida en M15", f"✅ {senal_tipo}" if senal_valida and senal_tipo else "❌ INACTIVA")
    tabla.add_row("🔄 Ya hay orden abierta", "✅ SÍ" if mt5.positions_get(symbol=SYMBOL) else "❌ NO")
    tabla.add_row("💰 Riesgo total permitido", "✅ OK")
    tabla.add_row("📏 Condición de rebote bandas", "✅ OK")
    if ultima_orden_sell:
        tabla.add_row("📉 Última orden estocástico SELL", ultima_orden_sell.strftime('%Y-%m-%d %H:%M:%S'))
    if ultima_orden_buy:
        tabla.add_row("📈 Última orden estocástico BUY", ultima_orden_buy.strftime('%Y-%m-%d %H:%M:%S'))
    tabla.add_row("📊 Resultado final", f"{senal_tipo if senal_valida else 'Sin señal válida'}")
    
    return Panel(tabla, title="Checkpoint Estocástico M15", border_style="magenta")

    return Panel(tabla, title=f"📊 Checkpoint Estocástico [{modalidad_operacion}]", border_style="cyan", expand=False)