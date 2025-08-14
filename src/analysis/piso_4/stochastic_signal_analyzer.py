"""
🏢 PISO 4 - ANÁLISIS ESTOCÁSTICO AVANZADO
=========================================

Módulo especializado en análisis estocástico integrado con FVG.
Migrado desde analisis_estocastico_m15.py para mejor organización.

FUNCIONALIDADES:
- Análisis estocástico con caché optimizado
- Integración con DataManager centralizado
- Detección de cruces y zonas críticas
- Gestión de señales de trading
- Visualización de checkpoints

FLUJO:
1. Recibe señal de FVG de alta calidad
2. Activa análisis estocástico específico
3. Evalúa timing óptimo de entrada
4. Genera señales de trading

AUTOR: Sistema Trading Grid - Piso 4
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import numpy as np
import pytz
from rich.panel import Panel
from rich.table import Table

# Imports centralizados del core
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))

from data_manager import DataManager
from config import ZONA_HORARIA_LOCAL

class StochasticSignalAnalyzer:
    """
    🎯 ANALIZADOR DE SEÑALES ESTOCÁSTICAS
    Análisis avanzado de señales estocásticas integrado con FVG
    """
    
    def __init__(self, symbol='EURUSD', timeframe='M15'):
        self.symbol = symbol
        self.timeframe = timeframe
        self.data_manager = DataManager()
        
        # Cache para optimización
        self.cache = {
            'timestamp': None,
            'k': None,
            'd': None,
            'cruce_k_d': False,
            'cruce_d_k': False,
            'sobreventa': False,
            'sobrecompra': False,
            'senal_valida': False,
            'senal_tipo': None,
            'ultima_orden_sell': None,
            'ultima_orden_buy': None,
            'vela_cerrada': False
        }
        
        # Configuración estocástica
        self.config = {
            'k_period': 14,
            'd_period': 3,
            'smooth_period': 3,
            'sobreventa_nivel': 20,  # Ajustado para mayor sensibilidad
            'sobrecompra_nivel': 80,  # Ajustado para mayor sensibilidad
            'cache_duration': 60  # segundos
        }
    
    def analyze_stochastic_for_fvg(self, fvg_signal=None, modalidad_operacion='AMBOS'):
        """
        🎯 Análisis estocástico específico para FVG
        
        Args:
            fvg_signal: Señal FVG que activó el análisis
            modalidad_operacion: Tipo de operación permitida
            
        Returns:
            dict: Resultado del análisis estocástico
        """
        zona = pytz.timezone(ZONA_HORARIA_LOCAL)
        ahora = datetime.now(zona)
        
        # Verificar cache
        if (self.cache['timestamp'] is None or 
            (ahora - self.cache['timestamp']).total_seconds() > self.config['cache_duration']):
            
            self._calculate_stochastic_values()
            self._detect_signals(modalidad_operacion)
            self._check_candle_closure()
            
            self.cache['timestamp'] = ahora
        
        # Si hay señal FVG, evaluar confluencia
        if fvg_signal:
            return self._evaluate_fvg_stochastic_confluence(fvg_signal)
        
        return self.cache.copy()
    
    def _calculate_stochastic_values(self):
        """🔢 Calcular valores estocásticos usando DataManager"""
        try:
            # Usar DataManager centralizado
            df_ohlc = self.data_manager.get_ohlc_data(
                self.symbol, 
                self.timeframe, 
                self.config['k_period'] + 10
            )
            
            if df_ohlc is None or len(df_ohlc) < self.config['k_period']:
                return False
            
            # Calcular estocástico usando DataManager
            stoch_data = self.data_manager.calculate_stochastic(
                df_ohlc, 
                k_period=self.config['k_period'],
                d_period=self.config['d_period']
            )
            
            if stoch_data is None or len(stoch_data) < 2:
                return False
            
            # Obtener valores actuales y anteriores
            self.cache['k'] = stoch_data['%K'].iloc[-1]
            self.cache['d'] = stoch_data['%D'].iloc[-1]
            k_anterior = stoch_data['%K'].iloc[-2]
            d_anterior = stoch_data['%D'].iloc[-2]
            
            # Detectar cruces
            self.cache['cruce_k_d'] = (self.cache['k'] > self.cache['d'] and 
                                       k_anterior <= d_anterior)
            self.cache['cruce_d_k'] = (self.cache['k'] < self.cache['d'] and 
                                       k_anterior >= d_anterior)
            
            # Detectar zonas críticas
            self.cache['sobreventa'] = (self.cache['k'] < self.config['sobreventa_nivel'] and 
                                        self.cache['d'] < self.config['sobreventa_nivel'])
            self.cache['sobrecompra'] = (self.cache['k'] > self.config['sobrecompra_nivel'] and 
                                         self.cache['d'] > self.config['sobrecompra_nivel'])
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error calculando estocástico: {e}")
            return self._fallback_calculation()
    
    def _fallback_calculation(self):
        """🔄 Cálculo fallback usando MT5 directo"""
        try:
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M15, 0, 30)
            if rates is None or len(rates) < self.config['k_period']:
                return False
            
            df = pd.DataFrame(rates)
            low = df['low']
            high = df['high'] 
            close = df['close']
            
            # Calcular estocástico manualmente
            period_k = self.config['k_period']
            period_d = self.config['d_period']
            
            lowest = low.rolling(window=period_k).min()
            highest = high.rolling(window=period_k).max()
            k = 100 * (close - lowest) / (highest - lowest)
            d = k.rolling(window=period_d).mean()
            
            self.cache['k'] = k.iloc[-1] if not k.empty else 50
            self.cache['d'] = d.iloc[-1] if not d.empty else 50
            
            if len(k) > 1 and len(d) > 1:
                k_anterior = k.iloc[-2]
                d_anterior = d.iloc[-2]
                
                self.cache['cruce_k_d'] = (self.cache['k'] > self.cache['d'] and 
                                           k_anterior <= d_anterior)
                self.cache['cruce_d_k'] = (self.cache['k'] < self.cache['d'] and 
                                           k_anterior >= d_anterior)
            
            self.cache['sobreventa'] = (self.cache['k'] < self.config['sobreventa_nivel'] and 
                                        self.cache['d'] < self.config['sobreventa_nivel'])
            self.cache['sobrecompra'] = (self.cache['k'] > self.config['sobrecompra_nivel'] and 
                                         self.cache['d'] > self.config['sobrecompra_nivel'])
            
            return True
            
        except Exception as e:
            print(f"❌ Error en fallback estocástico: {e}")
            return False
    
    def _detect_signals(self, modalidad_operacion):
        """🎯 Detectar señales de trading estocásticas"""
        self.cache['senal_valida'] = False
        self.cache['senal_tipo'] = None
        
        # Señal BUY: Cruce alcista en sobreventa
        if (modalidad_operacion in ['AMBOS', 'BUY'] and 
            self.cache['cruce_k_d'] and 
            self.cache['sobreventa']):
            
            self.cache['senal_valida'] = True
            self.cache['senal_tipo'] = 'BUY'
        
        # Señal SELL: Cruce bajista en sobrecompra
        elif (modalidad_operacion in ['AMBOS', 'SELL'] and 
              self.cache['cruce_d_k'] and 
              self.cache['sobrecompra']):
            
            self.cache['senal_valida'] = True
            self.cache['senal_tipo'] = 'SELL'
    
    def _check_candle_closure(self):
        """🕐 Verificar si la vela está cerrada"""
        zona = pytz.timezone(ZONA_HORARIA_LOCAL)
        ahora = datetime.now(zona)
        
        try:
            # Usar DataManager para verificar cierre de vela
            rates_recientes = self.data_manager.get_ohlc_data(self.symbol, self.timeframe, 1)
            if rates_recientes is not None and len(rates_recientes) > 0:
                time_current = pd.Timestamp(rates_recientes.index[-1])
                self.cache['vela_cerrada'] = (ahora - time_current).total_seconds() >= 60
            else:
                self.cache['vela_cerrada'] = True
                
        except Exception:
            # Fallback con MT5
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M15, 0, 1)
            if rates is not None and len(rates) > 0:
                time_current = pd.Timestamp(rates[-1]['time'], unit='s', tz=zona)
                self.cache['vela_cerrada'] = (ahora - time_current).total_seconds() >= 60
            else:
                self.cache['vela_cerrada'] = True
    
    def _evaluate_fvg_stochastic_confluence(self, fvg_signal):
        """
        🎯 Evaluar confluencia entre FVG y Estocástico
        
        Args:
            fvg_signal: Señal FVG recibida
            
        Returns:
            dict: Análisis de confluencia
        """
        confluence_result = self.cache.copy()
        confluence_result['fvg_signal'] = fvg_signal
        confluence_result['confluence_detected'] = False
        confluence_result['confluence_strength'] = 0
        
        if not fvg_signal or not self.cache['senal_valida']:
            return confluence_result
        
        # Evaluar confluencia direccional
        fvg_direction = fvg_signal.get('direction', '').upper()
        stoch_direction = self.cache['senal_tipo']
        
        if fvg_direction == stoch_direction:
            confluence_result['confluence_detected'] = True
            
            # Calcular fuerza de confluencia
            strength = 0
            
            # Factor 1: Calidad FVG (0-40 puntos)
            fvg_quality = fvg_signal.get('quality_score', 0)
            strength += min(40, fvg_quality * 5)
            
            # Factor 2: Intensidad estocástica (0-30 puntos)
            if stoch_direction == 'BUY':
                stoch_intensity = max(0, self.config['sobreventa_nivel'] - self.cache['k'])
            else:
                stoch_intensity = max(0, self.cache['k'] - self.config['sobrecompra_nivel'])
            
            strength += min(30, stoch_intensity)
            
            # Factor 3: Vela cerrada (0-20 puntos)
            if self.cache['vela_cerrada']:
                strength += 20
            
            # Factor 4: Timing FVG reciente (0-10 puntos)
            fvg_age = fvg_signal.get('age_minutes', 0)
            if fvg_age <= 15:  # FVG reciente
                strength += 10
            elif fvg_age <= 60:
                strength += 5
            
            confluence_result['confluence_strength'] = min(100, strength)
        
        return confluence_result
    
    def create_stochastic_checkpoint_panel(self, analysis_result, modalidad_operacion='AMBOS'):
        """
        📊 Crear panel de checkpoint estocástico
        
        Args:
            analysis_result: Resultado del análisis
            modalidad_operacion: Modalidad de operación
            
        Returns:
            Panel: Panel visual con información del checkpoint
        """
        tabla = Table(show_header=False, box=None, expand=False)
        tabla.add_column("Regla", justify="left")
        tabla.add_column("Valor", justify="right")
        
        k_actual = analysis_result.get('k')
        d_actual = analysis_result.get('d')
        cruce_k_d = analysis_result.get('cruce_k_d', False)
        cruce_d_k = analysis_result.get('cruce_d_k', False)
        sobreventa = analysis_result.get('sobreventa', False)
        sobrecompra = analysis_result.get('sobrecompra', False)
        senal_valida = analysis_result.get('senal_valida', False)
        senal_tipo = analysis_result.get('senal_tipo')
        vela_cerrada = analysis_result.get('vela_cerrada', False)
        confluence_detected = analysis_result.get('confluence_detected', False)
        confluence_strength = analysis_result.get('confluence_strength', 0)
        
        # Datos estocásticos
        tabla.add_row("📈 %K actual", f"{k_actual:.2f}" if k_actual is not None else "--")
        tabla.add_row("📉 %D actual", f"{d_actual:.2f}" if d_actual is not None else "--")
        tabla.add_row("🔀 Cruce K>D (alcista)", "✅ SÍ" if cruce_k_d else "❌ NO")
        tabla.add_row("🔀 Cruce D>K (bajista)", "✅ SÍ" if cruce_d_k else "❌ NO")
        
        # Zonas críticas
        tabla.add_row("📉 Sobreventa (<20)", "✅ SÍ" if sobreventa else "❌ NO")
        tabla.add_row("📈 Sobrecompra (>80)", "✅ SÍ" if sobrecompra else "❌ NO")
        
        # Señales
        tabla.add_row("🕒 Vela cerrada", "✅ SÍ" if vela_cerrada else "❌ NO")
        tabla.add_row("📡 Señal estocástica", f"✅ {senal_tipo}" if senal_valida and senal_tipo else "❌ INACTIVA")
        
        # Confluencia FVG
        if 'fvg_signal' in analysis_result:
            tabla.add_row("🎯 Confluencia FVG", "✅ SÍ" if confluence_detected else "❌ NO")
            tabla.add_row("💪 Fuerza confluencia", f"{confluence_strength}%" if confluence_detected else "--")
            
            fvg_quality = analysis_result['fvg_signal'].get('quality_score', 0)
            tabla.add_row("⭐ Calidad FVG", f"{fvg_quality:.1f}")
        
        # Estado posiciones
        posiciones = mt5.positions_get(symbol=self.symbol)
        tabla.add_row("🔄 Posiciones abiertas", f"{len(posiciones) if posiciones else 0}")
        
        # Resultado final
        if confluence_detected and senal_valida:
            resultado = f"🎯 CONFLUENCIA {senal_tipo} ({confluence_strength}%)"
        elif senal_valida:
            resultado = f"📊 SEÑAL {senal_tipo}"
        else:
            resultado = "⏳ ESPERANDO SEÑAL"
        
        tabla.add_row("📊 Resultado final", resultado)
        
        # Título del panel
        title = f"🎯 Estocástico Piso 4 [{modalidad_operacion}]"
        if confluence_detected:
            title += f" - CONFLUENCIA FVG"
        
        return Panel(
            tabla, 
            title=title,
            border_style="green" if confluence_detected else "cyan",
            expand=False
        )

# Instancia global para el Piso 4
stochastic_analyzer = StochasticSignalAnalyzer()

def analyze_stochastic_for_fvg(fvg_signal=None, modalidad_operacion='AMBOS', symbol='EURUSD'):
    """
    🎯 Función principal de análisis estocástico para FVG
    
    Args:
        fvg_signal: Señal FVG que activa el análisis
        modalidad_operacion: Modalidad de trading
        symbol: Símbolo a analizar
        
    Returns:
        dict: Resultado del análisis con confluencia
    """
    global stochastic_analyzer
    
    # Actualizar símbolo si es diferente
    if stochastic_analyzer.symbol != symbol:
        stochastic_analyzer = StochasticSignalAnalyzer(symbol)
    
    return stochastic_analyzer.analyze_stochastic_for_fvg(fvg_signal, modalidad_operacion)

def create_stochastic_checkpoint(analysis_result, modalidad_operacion='AMBOS'):
    """
    📊 Crear checkpoint visual del análisis estocástico
    
    Args:
        analysis_result: Resultado del análisis
        modalidad_operacion: Modalidad de operación
        
    Returns:
        Panel: Panel visual del checkpoint
    """
    return stochastic_analyzer.create_stochastic_checkpoint_panel(analysis_result, modalidad_operacion)

def get_stochastic_analyzer(symbol: str = 'EURUSD'):
    """
    🎯 Obtener instancia del analizador estocástico
    
    Args:
        symbol: Símbolo para el analizador
        
    Returns:
        StochasticSignalAnalyzer: Instancia del analizador
    """
    global stochastic_analyzer
    
    if stochastic_analyzer is None or stochastic_analyzer.symbol != symbol:
        stochastic_analyzer = StochasticSignalAnalyzer(symbol)
    
    return stochastic_analyzer
