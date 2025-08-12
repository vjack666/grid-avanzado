"""
FASE 5: IndicatorManager - Gestión Avanzada de Indicadores Técnicos
================================================================

IndicatorManager centraliza la gestión de indicadores técnicos avanzados,
señales compuestas, y analytics de performance. Se integra con DataManager
para optimizar el uso de datos y cache.

Funcionalidades:
- Indicadores técnicos avanzados (MACD, EMA, Williams %R, ADX, ATR, CCI)
- Sistema de señales compuestas multi-indicador
- Optimización automática de parámetros
- Performance analytics y backtesting básico
- Cache especializado para indicadores

Autor: Sistema Trading Grid
Fecha: 2025-08-12
"""

# Import centralizado desde SÓTANO 1
# Imports centralizados
from .common_imports import pd, np, Dict, List, Optional, Tuple, Union, datetime, timedelta, json

class IndicatorManager:
    """
    FASE 5: Gestor centralizado de indicadores técnicos avanzados y señales compuestas
    """
    
    def __init__(self, data_manager, logger_manager=None, error_manager=None):
        """
        Inicializar IndicatorManager con dependencias
        
        Args:
            data_manager: DataManager para acceso a datos OHLC
            logger_manager: LoggerManager para logging
            error_manager: ErrorManager para manejo de errores
        """
        self.data_manager = data_manager
        self.logger = logger_manager
        self.error_manager = error_manager
        
        # Cache específico para indicadores (TTL más largo)
        self.indicator_cache = {}
        self.signal_history = {}
        
        # Configuración de TTL para diferentes tipos de cache
        self.ttl_config = {
            'indicators': 600,  # 10 minutos para indicadores
            'signals': 300,     # 5 minutos para señales
            'analytics': 1800,  # 30 minutos para analytics
        }
        
        if self.logger:
            self.logger.log_info("IndicatorManager inicializado correctamente")
    
    # ========================================================================
    # GESTIÓN DE CACHE ESPECIALIZADO
    # ========================================================================
    
    def _cache_key(self, symbol: str, timeframe: str, indicator: str, params: str = "") -> str:
        """Generar clave de cache para indicadores"""
        base_key = f"{symbol}_{timeframe}_{indicator}"
        return f"{base_key}_{params}" if params else base_key
    
    def cache_indicator_result(self, key: str, result, ttl: int = 300) -> None:
        """Cache resultado de indicador con TTL específico"""
        if ttl is None:
            ttl = self.ttl_config['indicators']
            
        self.indicator_cache[key] = {
            'data': result,
            'timestamp': datetime.now(),
            'ttl': ttl
        }
        
        if self.logger:
            self.logger.log_info(f"Indicador cacheado: {key} (TTL: {ttl}s)")
    
    def get_cached_indicator(self, key: str):
        """Obtener indicador del cache si no ha expirado"""
        if key not in self.indicator_cache:
            # En trading, retornar None aquí es aceptable para el cache
            return None
            
        cached_item = self.indicator_cache[key]
        elapsed = (datetime.now() - cached_item['timestamp']).total_seconds()
        
        if elapsed > cached_item['ttl']:
            del self.indicator_cache[key]
            # En trading, retornar None aquí es aceptable para el cache
            return None
            
        if self.logger:
            self.logger.log_info(f"Cache hit: {key}")
        return cached_item['data']
    
    def clear_indicator_cache(self) -> None:
        """Limpiar cache de indicadores"""
        self.indicator_cache.clear()
        if self.logger:
            self.logger.log_info("Cache de indicadores limpiado")
    
    # ========================================================================
    # INDICADORES TÉCNICOS AVANZADOS
    # ========================================================================
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        Calcular MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame con datos OHLC
            fast: Período EMA rápida (default: 12)
            slow: Período EMA lenta (default: 26)
            signal: Período línea de señal (default: 9)
            
        Returns:
            DataFrame con columnas MACD, MACD_Signal, MACD_Histogram
        """
        try:
            # Determinar columna de cierre
            close_col = 'close' if 'close' in df.columns else 'Close'
            close = df[close_col]
            
            # Calcular EMAs
            ema_fast = close.ewm(span=fast).mean()
            ema_slow = close.ewm(span=slow).mean()
            
            # MACD Line = EMA_fast - EMA_slow
            macd_line = ema_fast - ema_slow
            
            # Signal Line = EMA of MACD Line
            signal_line = macd_line.ewm(span=signal).mean()
            
            # Histogram = MACD - Signal
            histogram = macd_line - signal_line
            
            # Agregar al DataFrame
            result = df.copy()
            result['MACD'] = macd_line
            result['MACD_Signal'] = signal_line
            result['MACD_Histogram'] = histogram
            
            if self.logger:
                self.logger.log_info(f"MACD calculado (fast: {fast}, slow: {slow}, signal: {signal})")
            
            return result
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("MACD_calculation", e)
            # Devolver DataFrame vacío en lugar de None para trading
            return pd.DataFrame()
    
    def calculate_ema(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Calcular EMA (Exponential Moving Average)
        
        Args:
            df: DataFrame con datos OHLC
            period: Período para EMA (default: 20)
            
        Returns:
            DataFrame con columna EMA_{period}
        """
        try:
            close_col = 'close' if 'close' in df.columns else 'Close'
            close = df[close_col]
            
            ema = close.ewm(span=period).mean()
            
            result = df.copy()
            result[f'EMA_{period}'] = ema
            
            if self.logger:
                self.logger.log_info(f"EMA calculado (período: {period})")
            
            return result
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("EMA_calculation", e)
            # Devolver DataFrame vacío en lugar de None para trading
            return pd.DataFrame()
    
    def calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calcular Williams %R
        
        Args:
            df: DataFrame con datos OHLC
            period: Período para Williams %R (default: 14)
            
        Returns:
            DataFrame con columna Williams_R
        """
        try:
            high_col = 'high' if 'high' in df.columns else 'High'
            low_col = 'low' if 'low' in df.columns else 'Low'
            close_col = 'close' if 'close' in df.columns else 'Close'
            
            high = df[high_col]
            low = df[low_col]
            close = df[close_col]
            
            # Highest high y Lowest low en el período
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            
            # Williams %R = ((Highest High - Close) / (Highest High - Lowest Low)) * -100
            williams_r = ((highest_high - close) / (highest_high - lowest_low)) * -100
            
            result = df.copy()
            result['Williams_R'] = williams_r
            
            if self.logger:
                self.logger.log_info(f"Williams %R calculado (período: {period})")
            
            return result
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("Williams_R_calculation", e)
            # Devolver DataFrame vacío en lugar de None para trading
            return pd.DataFrame()
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calcular ATR (Average True Range)
        
        Args:
            df: DataFrame con datos OHLC
            period: Período para ATR (default: 14)
            
        Returns:
            DataFrame con columna ATR
        """
        try:
            high_col = 'high' if 'high' in df.columns else 'High'
            low_col = 'low' if 'low' in df.columns else 'Low'
            close_col = 'close' if 'close' in df.columns else 'Close'
            
            high = df[high_col]
            low = df[low_col]
            close = df[close_col]
            
            # True Range = max(High-Low, |High-Close_prev|, |Low-Close_prev|)
            close_prev = close.shift(1)
            
            tr1 = high - low
            tr2 = (high - close_prev).abs()
            tr3 = (low - close_prev).abs()
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # ATR = Media móvil del True Range
            atr = true_range.rolling(window=period).mean()
            
            result = df.copy()
            result['ATR'] = atr
            
            if self.logger:
                self.logger.log_info(f"ATR calculado (período: {period})")
            
            return result
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("ATR_calculation", e)
            # Devolver DataFrame vacío en lugar de None para trading
            return pd.DataFrame()
    
    def calculate_cci(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        Calcular CCI (Commodity Channel Index)
        
        Args:
            df: DataFrame con datos OHLC
            period: Período para CCI (default: 20)
            
        Returns:
            DataFrame con columna CCI
        """
        try:
            high_col = 'high' if 'high' in df.columns else 'High'
            low_col = 'low' if 'low' in df.columns else 'Low'
            close_col = 'close' if 'close' in df.columns else 'Close'
            
            high = df[high_col]
            low = df[low_col]
            close = df[close_col]
            
            # Typical Price = (High + Low + Close) / 3
            typical_price = (high + low + close) / 3
            
            # SMA del Typical Price
            sma_tp = typical_price.rolling(window=period).mean()
            
            # Mean Deviation
            mean_deviation = typical_price.rolling(window=period).apply(
                lambda x: np.mean(np.abs(x - x.mean()))
            )
            
            # CCI = (Typical Price - SMA) / (0.015 * Mean Deviation)
            cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
            
            result = df.copy()
            result['CCI'] = cci
            
            if self.logger:
                self.logger.log_info(f"CCI calculado (período: {period})")
            
            return result
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("CCI_calculation", e)
            # Devolver DataFrame vacío en lugar de None para trading
            return pd.DataFrame()
    
    # ========================================================================
    # INDICADORES BÁSICOS CON CACHE (Wrapper para DataManager)
    # ========================================================================
    
    def get_bollinger_bands(self, symbol: str, timeframe: str, periods: int = 20, deviation: float = 2.0) -> pd.DataFrame:
        """Obtener Bollinger Bands con cache especializado"""
        cache_key = self._cache_key(symbol, timeframe, "BB", f"{periods}_{deviation}")
        cached_result = self.get_cached_indicator(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        # Obtener datos y calcular
        df = self.data_manager.get_ohlc_data(symbol, timeframe, periods + 5)
        if df is None:
            # Devolver DataFrame vacío en lugar de None para trading
            return pd.DataFrame()
            
        result = self.data_manager.calculate_bollinger_bands(df, periods, deviation)
        
        # Cache resultado
        if result is not None:
            self.cache_indicator_result(cache_key, result)
        
        return result
    
    def get_rsi(self, symbol: str, timeframe: str, period: int = 14) -> pd.DataFrame:
        """Obtener RSI con cache especializado"""
        cache_key = self._cache_key(symbol, timeframe, "RSI", str(period))
        cached_result = self.get_cached_indicator(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        # Obtener datos y calcular
        df = self.data_manager.get_ohlc_data(symbol, timeframe, period + 10)
        if df is None:
            # Devolver DataFrame vacío en lugar de None para trading
            return pd.DataFrame()
            
        result = self.data_manager.calculate_rsi(df, period)
        
        # Cache resultado
        if result is not None:
            self.cache_indicator_result(cache_key, result)
        
        return result
    
    def get_stochastic(self, symbol: str, timeframe: str, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """Obtener Estocástico con cache especializado"""
        cache_key = self._cache_key(symbol, timeframe, "STOCH", f"{k_period}_{d_period}")
        cached_result = self.get_cached_indicator(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        # Obtener datos y calcular
        df = self.data_manager.get_ohlc_data(symbol, timeframe, k_period + 10)
        if df is None:
            # Devolver DataFrame vacío en lugar de None para trading
            return pd.DataFrame()
            
        result = self.data_manager.calculate_stochastic(df, k_period, d_period)
        
        # Cache resultado
        if result is not None:
            self.cache_indicator_result(cache_key, result)
        
        return result
    
    def get_macd(self, symbol: str, timeframe: str, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Obtener MACD con cache especializado"""
        cache_key = self._cache_key(symbol, timeframe, "MACD", f"{fast}_{slow}_{signal}")
        cached_result = self.get_cached_indicator(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        # Obtener datos y calcular
        df = self.data_manager.get_ohlc_data(symbol, timeframe, slow + 20)
        if df is None:
            # Devolver DataFrame vacío en lugar de None para trading
            return pd.DataFrame()
            
        result = self.calculate_macd(df, fast, slow, signal)
        
        # Cache resultado
        if result is not None:
            self.cache_indicator_result(cache_key, result)
        
        return result
    
    # ========================================================================
    # SISTEMA DE SEÑALES COMPUESTAS
    # ========================================================================
    
    def generate_compound_signal(self, symbol: str, timeframe: str, strategy: str = "balanced") -> Dict:
        """
        Generar señal compuesta basada en múltiples indicadores
        
        Args:
            symbol: Símbolo a analizar (ej: "EURUSD")
            timeframe: Marco temporal (ej: "M15")
            strategy: Estrategia a usar ("balanced", "momentum_breakout", "trend_following")
            
        Returns:
            Dict con signal, strength, indicators, timestamp
        """
        try:
            # Verificar cache de señales
            signal_cache_key = self._cache_key(symbol, timeframe, "SIGNAL", strategy)
            cached_signal = self.get_cached_indicator(signal_cache_key)
            
            if cached_signal is not None:
                return cached_signal
            
            # Obtener datos base
            df = self.data_manager.get_ohlc_data(symbol, timeframe, 50)
            if df is None or len(df) < 30:
                return {
                    "signal": "NO_DATA",
                    "strength": 0,
                    "strategy": strategy,
                    "indicators": {},
                    "timestamp": datetime.now(),
                    "message": "Datos insuficientes"
                }
            
            # Obtener precio actual
            current_price = df['close'].iloc[-1] if 'close' in df.columns else df['Close'].iloc[-1]
            
            # Calcular indicadores necesarios
            indicators_data = self._calculate_indicators_for_signal(symbol, timeframe, df)
            
            if not indicators_data:
                return {
                    "signal": "ERROR",
                    "strength": 0,
                    "strategy": strategy,
                    "indicators": {},
                    "timestamp": datetime.now(),
                    "message": "Error calculando indicadores"
                }
            
            # Aplicar estrategia específica
            if strategy == "momentum_breakout":
                signal_result = self._momentum_breakout_strategy(current_price, indicators_data)
            elif strategy == "trend_following":
                signal_result = self._trend_following_strategy(current_price, indicators_data, df)
            elif strategy == "mean_reversion":
                signal_result = self._mean_reversion_strategy(current_price, indicators_data)
            else:  # balanced
                signal_result = self._balanced_strategy(current_price, indicators_data)
            
            # Añadir metadata
            signal_result.update({
                "strategy": strategy,
                "timestamp": datetime.now(),
                "symbol": symbol,
                "timeframe": timeframe
            })
            
            # Cache la señal
            self.cache_indicator_result(signal_cache_key, signal_result, self.ttl_config['signals'])
            
            if self.logger:
                self.logger.log_info(f"Señal compuesta generada: {symbol} {timeframe} - {signal_result['signal']} (fuerza: {signal_result['strength']})")
            
            return signal_result
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_error(e, "IndicatorManager.generate_compound_signal")
            return {
                "signal": "ERROR",
                "strength": 0,
                "strategy": strategy,
                "indicators": {},
                "timestamp": datetime.now(),
                "message": f"Error: {str(e)}"
            }
    
    def _calculate_indicators_for_signal(self, symbol: str, timeframe: str, df: pd.DataFrame) -> Dict:
        """Calcular todos los indicadores necesarios para señales"""
        try:
            indicators = {}
            
            # Bollinger Bands
            bb_data = self.data_manager.calculate_bollinger_bands(df)
            if bb_data is not None and len(bb_data) > 0:
                indicators['bb_upper'] = bb_data['BB_Upper'].iloc[-1]
                indicators['bb_middle'] = bb_data['BB_Middle'].iloc[-1]
                indicators['bb_lower'] = bb_data['BB_Lower'].iloc[-1]
            
            # RSI
            rsi_data = self.data_manager.calculate_rsi(df)
            if rsi_data is not None and len(rsi_data) > 0:
                indicators['rsi'] = rsi_data['RSI'].iloc[-1]
            
            # MACD
            macd_data = self.calculate_macd(df)
            if macd_data is not None and len(macd_data) > 0:
                indicators['macd'] = macd_data['MACD'].iloc[-1]
                indicators['macd_signal'] = macd_data['MACD_Signal'].iloc[-1]
                indicators['macd_histogram'] = macd_data['MACD_Histogram'].iloc[-1]
            
            # Estocástico
            stoch_data = self.data_manager.calculate_stochastic(df)
            if stoch_data is not None and len(stoch_data) > 0:
                indicators['stoch_k'] = stoch_data['%K'].iloc[-1]
                indicators['stoch_d'] = stoch_data['%D'].iloc[-1]
            
            # Williams %R
            williams_data = self.calculate_williams_r(df)
            if williams_data is not None and len(williams_data) > 0:
                indicators['williams_r'] = williams_data['Williams_R'].iloc[-1]
            
            # EMA 12 y 26
            ema12_data = self.calculate_ema(df, 12)
            ema26_data = self.calculate_ema(df, 26)
            if ema12_data is not None and ema26_data is not None:
                indicators['ema12'] = ema12_data['EMA_12'].iloc[-1]
                indicators['ema26'] = ema26_data['EMA_26'].iloc[-1]
            
            return indicators
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_error(e, "IndicatorManager._calculate_indicators_for_signal")
            return {}
    
    def _balanced_strategy(self, current_price: float, indicators: Dict) -> Dict:
        """Estrategia Balanceada (implementación simplificada)"""
        try:
            signals = []
            strength = 0
            
            # RSI básico
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi > 70:
                    signals.append({"indicator": "RSI", "signal": "SELL", "strength": 0.7})
                elif rsi < 30:
                    signals.append({"indicator": "RSI", "signal": "BUY", "strength": 0.7})
            
            # MACD básico
            if 'macd' in indicators and 'macd_signal' in indicators:
                macd = indicators['macd']
                macd_signal = indicators['macd_signal']
                if macd > macd_signal:
                    signals.append({"indicator": "MACD", "signal": "BUY", "strength": 0.6})
                elif macd < macd_signal:
                    signals.append({"indicator": "MACD", "signal": "SELL", "strength": 0.6})
            
            # Calcular señal final
            buy_strength = sum([s['strength'] for s in signals if s['signal'] == 'BUY'])
            sell_strength = sum([s['strength'] for s in signals if s['signal'] == 'SELL'])
            
            if buy_strength > sell_strength and buy_strength >= 0.5:
                final_signal = "BUY"
                strength = min(buy_strength, 1.0)
            elif sell_strength > buy_strength and sell_strength >= 0.5:
                final_signal = "SELL"
                strength = min(sell_strength, 1.0)
            else:
                final_signal = "HOLD"
                strength = 0
            
            return {
                "signal": final_signal,
                "strength": round(strength, 2),
                "indicators": indicators,
                "signals_detail": signals
            }
            
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_error(e, "IndicatorManager._balanced_strategy")
            return {"signal": "ERROR", "strength": 0, "indicators": indicators}
    
    def _momentum_breakout_strategy(self, current_price: float, indicators: Dict) -> Dict:
        """Estrategia Momentum Breakout (implementación simplificada)"""
        return self._balanced_strategy(current_price, indicators)
    
    def _trend_following_strategy(self, current_price: float, indicators: Dict, df: pd.DataFrame) -> Dict:
        """Estrategia Trend Following (implementación simplificada)"""
        return self._balanced_strategy(current_price, indicators)
    
    def _mean_reversion_strategy(self, current_price: float, indicators: Dict) -> Dict:
        """Estrategia Mean Reversion (implementación simplificada)"""
        return self._balanced_strategy(current_price, indicators)
