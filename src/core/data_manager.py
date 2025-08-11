"""
🎯 DATA MANAGER - TRADING GRID v2.0
===================================

Sistema de manejo de datos centralizado para Trading Grid.
Unifica todo el procesamiento, cache y validación de datos dispersos.

Autor: GitHub Copilot
Fecha: Agosto 10, 2025
Protocolo: TRADING GRID v2.0
Fase: 4 de 6
"""

import os
import sys
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
import pandas as pd
import numpy as np

# Imports para MT5
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

class DataManager:
    """
    Sistema de manejo de datos centralizado para Trading Grid.
    
    Unifica 6 sistemas de datos diferentes:
    1. Obtención OHLC -> get_ohlc_data()
    2. Cache inteligente -> cache_manager
    3. Indicadores técnicos -> get_indicators()  
    4. Validación de datos -> validate_data()
    5. Timeframes -> normalize_timeframe()
    6. Limpieza de datos -> clean_data()
    """
    
    def __init__(self, config_manager=None, logger_manager=None, error_manager=None):
        """
        Inicializa el DataManager.
        
        Args:
            config_manager: Instancia de ConfigManager de FASE 1
            logger_manager: Instancia de LoggerManager de FASE 2  
            error_manager: Instancia de ErrorManager de FASE 3
        """
        self.config = config_manager
        self.logger = logger_manager
        self.error_manager = error_manager
        
        # Sistema de cache con TTL
        self.cache = {}
        self.cache_ttl = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
        
        # Configuración de timeframes MT5
        self.timeframe_map = {
            'M1': mt5.TIMEFRAME_M1 if MT5_AVAILABLE else 1,
            'M5': mt5.TIMEFRAME_M5 if MT5_AVAILABLE else 5,
            'M15': mt5.TIMEFRAME_M15 if MT5_AVAILABLE else 15,
            'M30': mt5.TIMEFRAME_M30 if MT5_AVAILABLE else 30,
            'H1': mt5.TIMEFRAME_H1 if MT5_AVAILABLE else 60,
            'H4': mt5.TIMEFRAME_H4 if MT5_AVAILABLE else 240,
            'D1': mt5.TIMEFRAME_D1 if MT5_AVAILABLE else 1440
        }
        
        # Columnas estándar OHLC
        self.ohlc_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        
        # Configuración de períodos recomendados por timeframe para trading
        self.recommended_periods = {
            'M1': 1440,   # 1 día
            'M5': 2016,   # 1 semana  
            'M15': 2016,  # 2 semanas
            'M30': 2016,  # 1 mes
            'H1': 2160,   # 3 meses
            'H4': 2160,   # 1 año 
            'D1': 365     # 1 año
        }
        
        # Verificar disponibilidad MT5
        self.mt5_available = self._check_mt5_availability()
        
        # Log de inicialización
        if self.logger:
            self.logger.log_info("DataManager inicializado correctamente")
    
    def is_valid_trading_data(self, data: pd.DataFrame) -> bool:
        """
        Verifica si los datos son válidos para trading (no vacíos, no None).
        
        Args:
            data: DataFrame a verificar
            
        Returns:
            bool: True si los datos son seguros para trading
        """
        if data is None:
            return False
        if not isinstance(data, pd.DataFrame):
            return False
        if data.empty:
            return False
        if len(data) == 0:
            return False
        return True
    
    def _check_mt5_availability(self) -> bool:
        """Verifica si MetaTrader5 está disponible y funcionando."""
        if not MT5_AVAILABLE:
            if self.logger:
                self.logger.log_warning("MetaTrader5 no está disponible")
            return False
        
        try:
            # Intentar inicializar MT5 si no está inicializado
            if not mt5.initialize():
                if self.error_manager:
                    self.error_manager.handle_mt5_error("check_availability")
                return False
            return True
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_system_error("mt5_availability_check", e)
            return False
    
    def _log_info(self, message: str):
        """Helper para logging de info."""
        if self.logger:
            self.logger.log_info(message)
        else:
            print(f"INFO: {message}")
    
    def _log_error(self, message: str):
        """Helper para logging de errores."""
        if self.logger:
            self.logger.log_error(message)
        else:
            print(f"ERROR: {message}")
    
    def _log_warning(self, message: str):
        """Helper para logging de warnings."""
        if self.logger:
            self.logger.log_warning(message)
        else:
            print(f"WARNING: {message}")
    
    def get_recommended_periods(self, timeframe: str) -> int:
        """
        Obtiene el número de períodos recomendado para un timeframe específico.
        
        Args:
            timeframe: Timeframe string ('M5', 'M15', 'H1', 'H4')
            
        Returns:
            int: Número de períodos recomendado para análisis efectivo
        """
        timeframe_upper = timeframe.upper()
        return self.recommended_periods.get(timeframe_upper, 1000)  # Default 1000 si no encuentra
    
    def normalize_timeframe(self, timeframe_str: str) -> int:
        """
        Normaliza string de timeframe a valor MT5.
        
        Args:
            timeframe_str: String del timeframe ('M5', 'H1', etc.)
            
        Returns:
            int: Valor MT5 del timeframe
        """
        timeframe_upper = timeframe_str.upper()
        if timeframe_upper in self.timeframe_map:
            return self.timeframe_map[timeframe_upper]
        else:
            self._log_warning(f"Timeframe no reconocido: {timeframe_str}, usando M15")
            return self.timeframe_map['M15']
    
    def _generate_cache_key(self, symbol: str, timeframe: str, periods: int, params: Optional[Dict] = None) -> str:
        """
        Genera clave de cache consistente.
        
        Args:
            symbol: Símbolo de trading
            timeframe: Timeframe string
            periods: Número de períodos
            params: Parámetros adicionales
            
        Returns:
            str: Clave de cache única
        """
        # Usar dict vacío por defecto para evitar None en trading
        if params is None:
            params = {}
            
        base_key = f"{symbol}_{timeframe}_{periods}"
        if params:
            params_str = str(sorted(params.items()))
            base_key += f"_{hashlib.md5(params_str.encode()).hexdigest()[:8]}"
        return base_key
    
    def cache_data(self, key: str, data: Any, ttl_seconds: int = 300):
        """
        Almacena datos en cache con TTL.
        
        Args:
            key: Clave de cache
            data: Datos a cachear
            ttl_seconds: Tiempo de vida en segundos (default: 5 minutos)
        """
        expiry_time = datetime.now() + timedelta(seconds=ttl_seconds)
        self.cache[key] = data
        self.cache_ttl[key] = expiry_time
        
        self._log_info(f"Datos cacheados: {key} (TTL: {ttl_seconds}s)")
    
    def get_cached_data(self, key: str) -> Any:
        """
        Obtiene datos del cache si están vigentes.
        
        Args:
            key: Clave de cache
            
        Returns:
            Any: Datos cacheados o DataFrame vacío si no existen/expiraron
        """
        if key not in self.cache:
            self.cache_stats['misses'] += 1
            # TRADING-SAFE: Retornar DataFrame vacío en lugar de None
            return pd.DataFrame()
        
        # Verificar TTL
        if key in self.cache_ttl:
            if datetime.now() > self.cache_ttl[key]:
                # Cache expirado, eliminar
                del self.cache[key]
                del self.cache_ttl[key]
                self.cache_stats['misses'] += 1
                # TRADING-SAFE: Retornar DataFrame vacío en lugar de None
                return pd.DataFrame()
        
        # Cache hit
        self.cache_stats['hits'] += 1
        self._log_info(f"Cache hit: {key}")
        return self.cache[key]
    
    def clear_cache(self, pattern: str = ""):
        """
        Limpia cache por patrón o completamente.
        
        Args:
            pattern: Patrón para limpiar específicas (vacío = limpiar todo)
        """
        if pattern:
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
                if key in self.cache_ttl:
                    del self.cache_ttl[key]
            self._log_info(f"Cache limpiado con patrón: {pattern} ({len(keys_to_delete)} entradas)")
        else:
            self.cache.clear()
            self.cache_ttl.clear()
            self._log_info("Cache completamente limpiado")
    
    def validate_ohlc_data(self, data: pd.DataFrame) -> bool:
        """
        Valida estructura y calidad de datos OHLC.
        
        Args:
            data: DataFrame con datos OHLC
            
        Returns:
            bool: True si los datos son válidos
        """
        try:
            # Verificar que sea DataFrame
            if not isinstance(data, pd.DataFrame):
                self._log_error("Los datos no son un DataFrame válido")
                return False
            
            # Verificar que no esté vacío
            if data.empty:
                self._log_error("DataFrame de datos está vacío")
                return False
            
            # Verificar columnas básicas requeridas
            required_cols = ['open', 'high', 'low', 'close']
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                self._log_error(f"Columnas OHLC faltantes: {missing_cols}")
                return False
            
            # Verificar consistencia OHLC (high >= open,close,low y low <= open,close,high)
            inconsistent_rows = 0
            for _, row in data.iterrows():
                if not (row['low'] <= row['open'] <= row['high'] and 
                       row['low'] <= row['close'] <= row['high']):
                    inconsistent_rows += 1
            
            if inconsistent_rows > 0:
                self._log_warning(f"Filas con inconsistencia OHLC: {inconsistent_rows}")
                if inconsistent_rows > len(data) * 0.1:  # Más del 10% inconsistente
                    self._log_error("Demasiadas inconsistencias OHLC en los datos")
                    return False
            
            # Verificar valores nulos en columnas críticas
            null_counts = data[required_cols].isnull().sum()
            if null_counts.any():
                self._log_warning(f"Valores nulos en columnas OHLC: {null_counts[null_counts > 0].to_dict()}")
            
            self._log_info(f"Validación OHLC: OK ({len(data)} filas)")
            return True
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("ohlc_validation", e)
            return False
    
    def get_ohlc_data(self, symbol: str, timeframe: str, periods: int = 1000, use_cache: bool = True) -> pd.DataFrame:
        """
        Obtiene datos OHLC con cache y validación automática.
        
        Args:
            symbol: Símbolo de trading (ej: 'EURUSD')
            timeframe: Timeframe string ('M5', 'M15', 'H1', 'H4')
            periods: Número de períodos a obtener
            use_cache: Si usar cache o forzar nueva descarga
            
        Returns:
            DataFrame validado con columnas OHLC estándar o DataFrame vacío si error
        """
        # Verificar disponibilidad MT5
        if not self.mt5_available:
            self._log_error("MT5 no está disponible para obtener datos")
            # TRADING-SAFE: Retornar DataFrame vacío con columnas OHLC
            return pd.DataFrame(columns=self.ohlc_columns)
        
        # Generar clave de cache
        cache_key = self._generate_cache_key(symbol, timeframe, periods)
        
        # Intentar obtener del cache
        if use_cache:
            cached_data = self.get_cached_data(cache_key)
            if not cached_data.empty:  # Cambiar de "is not None"
                return cached_data
        
        try:
            # Normalizar timeframe
            mt5_timeframe = self.normalize_timeframe(timeframe)
            
            # Obtener datos de MT5
            self._log_info(f"Obteniendo datos OHLC: {symbol} {timeframe} ({periods} períodos)")
            
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, periods)
            
            if rates is None or len(rates) == 0:
                if self.error_manager:
                    self.error_manager.handle_mt5_error("copy_rates", {
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'periods': periods
                    })
                # TRADING-SAFE: Retornar DataFrame vacío con columnas OHLC
                return pd.DataFrame(columns=self.ohlc_columns)
            
            # Convertir a DataFrame
            df = pd.DataFrame(rates)
            
            # Normalizar columnas
            df['datetime'] = pd.to_datetime(df['time'], unit='s')
            df = df.rename(columns={
                'tick_volume': 'volume',
                'real_volume': 'real_volume'
            })
            
            # Seleccionar columnas OHLC estándar
            available_cols = [col for col in self.ohlc_columns if col in df.columns]
            df = df[available_cols]
            
            # Validar datos
            if not self.validate_ohlc_data(df):
                self._log_error(f"Validación falló para datos {symbol} {timeframe}")
                # TRADING-SAFE: Retornar DataFrame vacío con columnas OHLC
                return pd.DataFrame(columns=self.ohlc_columns)
            
            # Cachear datos si son válidos
            if use_cache:
                self.cache_data(cache_key, df.copy(), ttl_seconds=300)  # 5 minutos TTL
            
            self._log_info(f"Datos OHLC obtenidos exitosamente: {len(df)} filas")
            return df
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("ohlc_fetch", e, {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'periods': periods
                })
            # TRADING-SAFE: Retornar DataFrame vacío con columnas OHLC
            return pd.DataFrame(columns=self.ohlc_columns)
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """
        Calcula Bandas de Bollinger de forma centralizada.
        
        Args:
            data: DataFrame con datos OHLC
            period: Período para la media móvil
            std_dev: Desviaciones estándar para las bandas
            
        Returns:
            DataFrame original + columnas bb_upper, bb_middle, bb_lower
        """
        try:
            if 'close' not in data.columns:
                self._log_error("Columna 'close' requerida para Bollinger Bands")
                return data
            
            # Calcular media móvil
            data['bb_middle'] = data['close'].rolling(window=period).mean()
            
            # Calcular desviación estándar
            std = data['close'].rolling(window=period).std()
            
            # Calcular bandas
            data['bb_upper'] = data['bb_middle'] + (std * std_dev)
            data['bb_lower'] = data['bb_middle'] - (std * std_dev)
            
            self._log_info(f"Bollinger Bands calculadas (período: {period}, std: {std_dev})")
            return data
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("bollinger_calculation", e)
            return data
    
    def calculate_stochastic(self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """
        Calcula Oscilador Estocástico de forma centralizada.
        
        Args:
            data: DataFrame con datos OHLC
            k_period: Período para %K
            d_period: Período para %D (media móvil de %K)
            
        Returns:
            DataFrame original + columnas stoch_k, stoch_d
        """
        try:
            required_cols = ['high', 'low', 'close']
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                self._log_error(f"Columnas requeridas para Estocástico: {missing_cols}")
                return data
            
            # Calcular %K
            lowest_low = data['low'].rolling(window=k_period).min()
            highest_high = data['high'].rolling(window=k_period).max()
            
            data['stoch_k'] = 100 * ((data['close'] - lowest_low) / (highest_high - lowest_low))
            
            # Calcular %D (media móvil de %K)
            data['stoch_d'] = data['stoch_k'].rolling(window=d_period).mean()
            
            self._log_info(f"Estocástico calculado (K: {k_period}, D: {d_period})")
            return data
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("stochastic_calculation", e)
            return data
    
    def get_indicators(self, data: pd.DataFrame, indicators: List[str], **kwargs) -> pd.DataFrame:
        """
        Calcula múltiples indicadores técnicos de forma centralizada.
        
        Args:
            data: DataFrame con datos OHLC
            indicators: Lista de indicadores ['bb', 'stoch', 'ma']
            **kwargs: Parámetros específicos para indicadores
            
        Returns:
            DataFrame original + columnas de indicadores
        """
        result_data = data.copy()
        
        for indicator in indicators:
            if indicator.lower() == 'bb' or indicator.lower() == 'bollinger':
                bb_period = kwargs.get('bb_period', 20)
                bb_std = kwargs.get('bb_std', 2.0)
                result_data = self.calculate_bollinger_bands(result_data, bb_period, bb_std)
                
            elif indicator.lower() == 'stoch' or indicator.lower() == 'stochastic':
                stoch_k = kwargs.get('stoch_k', 14)
                stoch_d = kwargs.get('stoch_d', 3)
                result_data = self.calculate_stochastic(result_data, stoch_k, stoch_d)
                
            else:
                self._log_warning(f"Indicador no reconocido: {indicator}")
        
        return result_data
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del cache.
        
        Returns:
            dict: Estadísticas de hits, misses y ratio
        """
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_ratio = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'total_requests': total_requests,
            'hit_ratio_percent': round(hit_ratio, 2),
            'cached_items': len(self.cache),
            'cache_size_kb': sys.getsizeof(self.cache) / 1024
        }
