    
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
