"""
ANALYTICS MANAGER - SÓTANO 1
Sistema avanzado de análisis y métricas para Trading Grid

FASE: 1.1 - Arquitectura Core
AUTOR: Sistema Modular Trading Grid
FECHA: 2025-08-10
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path

from .config_manager import ConfigManager
from .logger_manager import LoggerManager
from .error_manager import ErrorManager
from .data_manager import DataManager


@dataclass
class PerformanceMetrics:
    """Estructura de datos para métricas de rendimiento"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_profit: float = 0.0
    total_loss: float = 0.0
    net_profit: float = 0.0
    profit_factor: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    trades_per_day: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GridMetrics:
    """Estructura de datos para métricas del grid"""
    active_levels: int = 0
    completed_cycles: int = 0
    grid_efficiency: float = 0.0
    level_hit_rate: float = 0.0
    average_cycle_time: float = 0.0
    grid_spread: float = 0.0
    level_distribution: Dict[str, int] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MarketMetrics:
    """Estructura de datos para métricas del mercado"""
    volatility: float = 0.0
    trend_strength: float = 0.0
    support_resistance_strength: float = 0.0
    market_efficiency: float = 0.0
    correlation_with_grid: float = 0.0
    bollinger_width: float = 0.0
    rsi_average: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class MarketAnalytics:
    """Módulo de análisis de condiciones del mercado"""
    
    def __init__(self, config_manager: ConfigManager, logger_manager: LoggerManager, data_manager):
        self.config = config_manager
        self.logger = logger_manager
        self.data_manager = data_manager
        self.market_history: List[MarketMetrics] = []
        self.current_market_metrics = MarketMetrics()
        self.stochastic_signals = []  # Historial de señales estocásticas
        self.market_conditions = {}  # Condiciones actuales del mercado
        
    def update_stochastic_signal(self, signal_data: Dict[str, Any]) -> None:
        """Actualiza señal estocástica para apertura de primera orden"""
        try:
            # Extraer datos de la señal estocástica
            k_value = signal_data.get('k', 0)
            d_value = signal_data.get('d', 0)
            signal_type = signal_data.get('senal_tipo', None)
            signal_valid = signal_data.get('senal_valida', False)
            oversold = signal_data.get('sobreventa', False)
            overbought = signal_data.get('sobrecompra', False)
            
            # Registrar señal en historial
            signal_record = {
                'timestamp': datetime.now(),
                'k_value': k_value,
                'd_value': d_value,
                'signal_type': signal_type,
                'signal_valid': signal_valid,
                'oversold': oversold,
                'overbought': overbought,
                'cross_occurred': signal_data.get('cruce_k_d', False)
            }
            
            self.stochastic_signals.append(signal_record)
            
            # Mantener solo las últimas 100 señales
            if len(self.stochastic_signals) > 100:
                self.stochastic_signals.pop(0)
            
            # Actualizar métricas del mercado
            self.current_market_metrics.rsi_average = (k_value + d_value) / 2
            
            # Actualizar condiciones del mercado
            self.market_conditions.update({
                'stochastic_k': k_value,
                'stochastic_d': d_value,
                'market_phase': self._determine_market_phase(k_value, d_value),
                'signal_strength': self._calculate_signal_strength(signal_data),
                'last_signal_type': signal_type if signal_valid else None
            })
            
            self.logger.log_info(f"Señal estocástica actualizada: K={k_value:.2f}, D={d_value:.2f}, Señal={signal_type}")
            
        except Exception as e:
            self.logger.log_error(f"Error actualizando señal estocástica: {e}")
    
    def update_volatility_analysis(self, symbol: str = "EURUSD", timeframe: str = "M15") -> None:
        """Actualiza análisis de volatilidad del mercado"""
        try:
            # Obtener datos OHLC recientes
            df_ohlc = self.data_manager.get_ohlc_data(symbol, timeframe, 20)
            if df_ohlc is None or len(df_ohlc) < 10:
                return
            
            # Calcular volatilidad (ATR simplificado)
            highs = df_ohlc['high']
            lows = df_ohlc['low']
            closes = df_ohlc['close']
            
            # True Range
            tr1 = highs - lows
            tr2 = abs(highs - closes.shift(1))
            tr3 = abs(lows - closes.shift(1))
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Average True Range
            atr = true_range.rolling(window=14).mean()
            current_volatility = atr.iloc[-1] if not atr.empty else 0
            
            # Actualizar métricas
            self.current_market_metrics.volatility = current_volatility
            
            # Determinar nivel de volatilidad
            volatility_percentile = self._calculate_volatility_percentile(atr)
            
            self.market_conditions.update({
                'volatility_level': current_volatility,
                'volatility_percentile': volatility_percentile,
                'volatility_classification': self._classify_volatility(volatility_percentile)
            })
            
            self.logger.log_info(f"Volatilidad actualizada: {current_volatility:.5f} ({volatility_percentile:.1f}%)")
            
        except Exception as e:
            self.logger.log_error(f"Error calculando volatilidad: {e}")
    
    def update_trend_analysis(self, symbol: str = "EURUSD", timeframe: str = "M15") -> None:
        """Actualiza análisis de tendencia del mercado"""
        try:
            # Obtener datos para análisis de tendencia
            df_ohlc = self.data_manager.get_ohlc_data(symbol, timeframe, 50)
            if df_ohlc is None or len(df_ohlc) < 20:
                return
            
            closes = df_ohlc['close']
            
            # Calcular medias móviles simples
            sma_fast = closes.rolling(window=10).mean()
            sma_slow = closes.rolling(window=20).mean()
            
            # Determinar tendencia
            current_price = closes.iloc[-1]
            sma_fast_current = sma_fast.iloc[-1]
            sma_slow_current = sma_slow.iloc[-1]
            
            # Clasificar tendencia
            if sma_fast_current > sma_slow_current and current_price > sma_fast_current:
                trend = "UPTREND"
                trend_strength = min(((sma_fast_current - sma_slow_current) / sma_slow_current) * 100, 100)
            elif sma_fast_current < sma_slow_current and current_price < sma_fast_current:
                trend = "DOWNTREND"  
                trend_strength = min(((sma_slow_current - sma_fast_current) / sma_slow_current) * 100, 100)
            else:
                trend = "SIDEWAYS"
                trend_strength = 0
            
            # Actualizar métricas
            self.current_market_metrics.trend_strength = abs(trend_strength)
            
            self.market_conditions.update({
                'trend_direction': trend,
                'trend_strength': abs(trend_strength),
                'sma_fast': sma_fast_current,
                'sma_slow': sma_slow_current,
                'price_position': self._determine_price_position(current_price, sma_fast_current, sma_slow_current)
            })
            
            self.logger.log_info(f"Tendencia actualizada: {trend} (Fuerza: {trend_strength:.2f}%)")
            
        except Exception as e:
            self.logger.log_error(f"Error calculando tendencia: {e}")
    
    def update_grid_correlation(self, grid_efficiency: float, grid_hit_rate: float) -> None:
        """Actualiza correlación entre condiciones del mercado y eficiencia del grid"""
        try:
            # Calcular correlación simple entre volatilidad y eficiencia del grid
            if self.current_market_metrics.volatility > 0:
                # Correlación inversa: mayor volatilidad, menor eficiencia esperada del grid
                volatility_factor = 1 / (1 + self.current_market_metrics.volatility * 10000)
                correlation = grid_efficiency * volatility_factor
            else:
                correlation = grid_efficiency
            
            self.current_market_metrics.correlation_with_grid = correlation
            
            # Determinar eficiencia esperada del mercado para grid trading
            market_efficiency = self._calculate_market_efficiency(grid_hit_rate)
            self.current_market_metrics.market_efficiency = market_efficiency
            
            self.market_conditions.update({
                'grid_correlation': correlation,
                'market_efficiency_for_grid': market_efficiency,
                'optimal_for_grid': market_efficiency > 70  # Umbral de eficiencia
            })
            
            self.logger.log_info(f"Correlación grid actualizada: {correlation:.2f}% (Eficiencia: {market_efficiency:.2f}%)")
            
        except Exception as e:
            self.logger.log_error(f"Error calculando correlación con grid: {e}")
    
    def _determine_market_phase(self, k_value: float, d_value: float) -> str:
        """Determina la fase del mercado basada en estocástico"""
        if k_value < 20 and d_value < 20:
            return "OVERSOLD"
        elif k_value > 80 and d_value > 80:
            return "OVERBOUGHT"
        elif 20 <= k_value <= 80 and 20 <= d_value <= 80:
            return "NEUTRAL"
        else:
            return "TRANSITION"
    
    def _calculate_signal_strength(self, signal_data: Dict[str, Any]) -> float:
        """Calcula la fuerza de la señal estocástica"""
        try:
            k_value = signal_data.get('k', 50)
            d_value = signal_data.get('d', 50)
            
            # Fuerza basada en la distancia a las zonas extremas
            if k_value < 20 or k_value > 80:
                distance_from_neutral = abs(k_value - 50)
                strength = min(distance_from_neutral * 2, 100)
            else:
                strength = 0
            
            return strength
            
        except Exception:
            return 0
    
    def _calculate_volatility_percentile(self, atr_series) -> float:
        """Calcula el percentil de la volatilidad actual"""
        try:
            if len(atr_series) < 10:
                return 50.0
            
            current_atr = atr_series.iloc[-1]
            historical_atr = atr_series.dropna()
            
            if len(historical_atr) == 0:
                return 50.0
            
            percentile = (historical_atr < current_atr).sum() / len(historical_atr) * 100
            return percentile
            
        except Exception:
            return 50.0
    
    def _classify_volatility(self, percentile: float) -> str:
        """Clasifica el nivel de volatilidad"""
        if percentile < 25:
            return "LOW"
        elif percentile < 75:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _determine_price_position(self, price: float, sma_fast: float, sma_slow: float) -> str:
        """Determina la posición del precio respecto a las medias"""
        if price > sma_fast > sma_slow:
            return "ABOVE_ALL"
        elif price < sma_fast < sma_slow:
            return "BELOW_ALL"
        elif sma_slow < price < sma_fast:
            return "BETWEEN_UP"
        elif sma_fast < price < sma_slow:
            return "BETWEEN_DOWN"
        else:
            return "MIXED"
    
    def _calculate_market_efficiency(self, grid_hit_rate: float) -> float:
        """Calcula la eficiencia del mercado para grid trading"""
        try:
            # Combinar múltiples factores
            volatility_factor = 50 if self.current_market_metrics.volatility == 0 else min(
                100 / (1 + self.current_market_metrics.volatility * 5000), 100
            )
            
            trend_factor = max(100 - self.current_market_metrics.trend_strength, 20)
            hit_rate_factor = grid_hit_rate if grid_hit_rate > 0 else 50
            
            # Promedio ponderado
            efficiency = (volatility_factor * 0.4 + trend_factor * 0.3 + hit_rate_factor * 0.3)
            return min(efficiency, 100)
            
        except Exception:
            return 50.0
    
    def get_current_market_metrics(self) -> MarketMetrics:
        """Retorna métricas actuales del mercado"""
        return self.current_market_metrics
    
    def get_stochastic_summary(self) -> Dict[str, Any]:
        """Retorna resumen de señales estocásticas"""
        try:
            if not self.stochastic_signals:
                return {"message": "No hay señales estocásticas registradas"}
            
            recent_signals = self.stochastic_signals[-10:]  # Últimas 10 señales
            
            # Estadísticas
            buy_signals = len([s for s in recent_signals if s['signal_type'] == 'BUY' and s['signal_valid']])
            sell_signals = len([s for s in recent_signals if s['signal_type'] == 'SELL' and s['signal_valid']])
            
            return {
                "total_recent_signals": len(recent_signals),
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "last_signal": recent_signals[-1] if recent_signals else None,
                "market_phase": self.market_conditions.get('market_phase', 'UNKNOWN'),
                "signal_strength": self.market_conditions.get('signal_strength', 0),
                "stochastic_k": self.market_conditions.get('stochastic_k', 0),
                "stochastic_d": self.market_conditions.get('stochastic_d', 0)
            }
            
        except Exception as e:
            self.logger.log_error(f"Error generando resumen estocástico: {e}")
            return {"error": str(e)}
    
    def get_market_conditions_report(self) -> Dict[str, Any]:
        """Retorna reporte completo de condiciones del mercado"""
        try:
            return {
                "volatility": {
                    "level": self.market_conditions.get('volatility_level', 0),
                    "percentile": self.market_conditions.get('volatility_percentile', 50),
                    "classification": self.market_conditions.get('volatility_classification', 'UNKNOWN')
                },
                "trend": {
                    "direction": self.market_conditions.get('trend_direction', 'UNKNOWN'),
                    "strength": self.market_conditions.get('trend_strength', 0),
                    "price_position": self.market_conditions.get('price_position', 'UNKNOWN')
                },
                "stochastic": {
                    "k_value": self.market_conditions.get('stochastic_k', 0),
                    "d_value": self.market_conditions.get('stochastic_d', 0),
                    "market_phase": self.market_conditions.get('market_phase', 'UNKNOWN'),
                    "last_signal": self.market_conditions.get('last_signal_type', None)
                },
                "grid_optimization": {
                    "correlation": self.market_conditions.get('grid_correlation', 0),
                    "market_efficiency": self.market_conditions.get('market_efficiency_for_grid', 50),
                    "optimal_conditions": self.market_conditions.get('optimal_for_grid', False)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.log_error(f"Error generando reporte de mercado: {e}")
            return {"error": str(e)}
    
    def save_market_snapshot(self) -> None:
        """Guarda snapshot de métricas del mercado"""
        try:
            snapshot = MarketMetrics(
                volatility=self.current_market_metrics.volatility,
                trend_strength=self.current_market_metrics.trend_strength,
                support_resistance_strength=self.current_market_metrics.support_resistance_strength,
                market_efficiency=self.current_market_metrics.market_efficiency,
                correlation_with_grid=self.current_market_metrics.correlation_with_grid,
                bollinger_width=self.current_market_metrics.bollinger_width,
                rsi_average=self.current_market_metrics.rsi_average,
                timestamp=datetime.now()
            )
            
            self.market_history.append(snapshot)
            self.logger.log_success("Snapshot de mercado guardado")
            
        except Exception as e:
            self.logger.log_error(f"Error guardando snapshot de mercado: {e}")


class GridAnalytics:
    """Módulo de análisis específico para grid trading"""
    
    def __init__(self, config_manager: ConfigManager, logger_manager: LoggerManager):
        self.config = config_manager
        self.logger = logger_manager
        self.grid_history: List[GridMetrics] = []
        self.current_grid_metrics = GridMetrics()
        self.active_levels = {}  # nivel -> información del nivel
        self.completed_cycles = []
        self.level_performance = {}  # tracking por nivel
        
    def update_grid_level(self, level: float, action: str, price: float, volume: float = 0.0) -> None:
        """Actualiza información de un nivel del grid"""
        try:
            level_key = f"{level:.5f}"
            
            if action == "ACTIVATE":
                self.active_levels[level_key] = {
                    'level': level,
                    'activated_at': datetime.now(),
                    'price': price,
                    'volume': volume,
                    'hits': 0
                }
                self.current_grid_metrics.active_levels += 1
                
            elif action == "HIT":
                if level_key in self.active_levels:
                    self.active_levels[level_key]['hits'] += 1
                    self.active_levels[level_key]['last_hit'] = datetime.now()
                
                # Actualizar performance por nivel
                if level_key not in self.level_performance:
                    self.level_performance[level_key] = {'hits': 0, 'volume': 0.0}
                self.level_performance[level_key]['hits'] += 1
                self.level_performance[level_key]['volume'] += volume
                
            elif action == "DEACTIVATE":
                if level_key in self.active_levels:
                    level_info = self.active_levels.pop(level_key)
                    self.current_grid_metrics.active_levels -= 1
                    
                    # Registrar ciclo completado
                    if level_info.get('hits', 0) > 0:
                        cycle_time = (datetime.now() - level_info['activated_at']).total_seconds()
                        self.completed_cycles.append({
                            'level': level,
                            'duration': cycle_time,
                            'hits': level_info['hits'],
                            'completed_at': datetime.now()
                        })
                        self.current_grid_metrics.completed_cycles += 1
            
            self._calculate_grid_metrics()
            self.logger.log_info(f"Grid level {action}: {level:.5f} @ {price:.5f}")
            
        except Exception as e:
            self.logger.log_error(f"Error actualizando grid level: {e}")
    
    def _calculate_grid_metrics(self) -> None:
        """Calcula métricas derivadas del grid"""
        try:
            if self.completed_cycles:
                total_duration = sum(cycle['duration'] for cycle in self.completed_cycles)
                self.current_grid_metrics.average_cycle_time = total_duration / len(self.completed_cycles)
            
            # Calcular eficiencia del grid
            total_hits = sum(perf['hits'] for perf in self.level_performance.values())
            if total_hits > 0 and self.current_grid_metrics.active_levels > 0:
                self.current_grid_metrics.level_hit_rate = (
                    total_hits / (self.current_grid_metrics.active_levels + len(self.completed_cycles)) * 100
                )
            
            # Calcular spread del grid
            if len(self.active_levels) >= 2:
                levels = [float(level) for level in self.active_levels.keys()]
                self.current_grid_metrics.grid_spread = max(levels) - min(levels)
            
            # Distribución de niveles
            self.current_grid_metrics.level_distribution = {
                'buy_levels': len([l for l in self.active_levels.values() if l.get('type') == 'BUY']),
                'sell_levels': len([l for l in self.active_levels.values() if l.get('type') == 'SELL']),
                'total_levels': len(self.active_levels)
            }
            
            # Calcular eficiencia general
            if self.current_grid_metrics.completed_cycles > 0:
                self.current_grid_metrics.grid_efficiency = (
                    self.current_grid_metrics.completed_cycles / 
                    (self.current_grid_metrics.active_levels + self.current_grid_metrics.completed_cycles) * 100
                )
                
        except Exception as e:
            self.logger.log_error(f"Error calculando métricas del grid: {e}")
    
    def get_current_grid_metrics(self) -> GridMetrics:
        """Retorna métricas actuales del grid"""
        return self.current_grid_metrics
    
    def get_level_performance_report(self) -> Dict[str, Any]:
        """Retorna reporte detallado de performance por nivel"""
        try:
            if not self.level_performance:
                return {"message": "No hay datos de niveles disponibles"}
            
            # Top 5 niveles más activos
            top_levels = sorted(
                self.level_performance.items(),
                key=lambda x: x[1]['hits'],
                reverse=True
            )[:5]
            
            return {
                "total_levels_tracked": len(self.level_performance),
                "total_hits": sum(perf['hits'] for perf in self.level_performance.values()),
                "total_volume": sum(perf['volume'] for perf in self.level_performance.values()),
                "top_performing_levels": [
                    {
                        "level": level,
                        "hits": data['hits'],
                        "volume": round(data['volume'], 2)
                    }
                    for level, data in top_levels
                ],
                "average_hits_per_level": round(
                    sum(perf['hits'] for perf in self.level_performance.values()) / len(self.level_performance),
                    2
                )
            }
            
        except Exception as e:
            self.logger.log_error(f"Error generando reporte de niveles: {e}")
            return {"error": str(e)}
    
    def save_grid_snapshot(self) -> None:
        """Guarda snapshot de métricas del grid"""
        try:
            snapshot = GridMetrics(
                active_levels=self.current_grid_metrics.active_levels,
                completed_cycles=self.current_grid_metrics.completed_cycles,
                grid_efficiency=self.current_grid_metrics.grid_efficiency,
                level_hit_rate=self.current_grid_metrics.level_hit_rate,
                average_cycle_time=self.current_grid_metrics.average_cycle_time,
                grid_spread=self.current_grid_metrics.grid_spread,
                level_distribution=self.current_grid_metrics.level_distribution.copy(),
                timestamp=datetime.now()
            )
            
            self.grid_history.append(snapshot)
            self.logger.log_success("Snapshot de grid guardado")
            
        except Exception as e:
            self.logger.log_error(f"Error guardando snapshot de grid: {e}")


class PerformanceTracker:
    """Módulo de seguimiento de rendimiento del sistema"""
    
    def __init__(self, config_manager: ConfigManager, logger_manager: LoggerManager):
        self.config = config_manager
        self.logger = logger_manager
        self.metrics_history: List[PerformanceMetrics] = []
        self.current_metrics = PerformanceMetrics()
        
    def update_trade_metrics(self, trade_result: Dict[str, Any]) -> None:
        """Actualiza métricas con resultado de un trade"""
        try:
            profit = trade_result.get('profit', 0)
            
            self.current_metrics.total_trades += 1
            
            if profit > 0:
                self.current_metrics.winning_trades += 1
                self.current_metrics.total_profit += profit
            else:
                self.current_metrics.losing_trades += 1
                self.current_metrics.total_loss += abs(profit)
            
            self._calculate_derived_metrics()
            self.logger.log_info(f"Métricas actualizadas - Trades: {self.current_metrics.total_trades}")
            
        except Exception as e:
            self.logger.log_error(f"Error actualizando métricas de trade: {e}")
    
    def _calculate_derived_metrics(self) -> None:
        """Calcula métricas derivadas"""
        try:
            if self.current_metrics.total_trades > 0:
                self.current_metrics.win_rate = (
                    self.current_metrics.winning_trades / self.current_metrics.total_trades * 100
                )
            
            self.current_metrics.net_profit = (
                self.current_metrics.total_profit - self.current_metrics.total_loss
            )
            
            if self.current_metrics.total_loss > 0:
                self.current_metrics.profit_factor = (
                    self.current_metrics.total_profit / self.current_metrics.total_loss
                )
            
            if self.current_metrics.winning_trades > 0:
                self.current_metrics.average_win = (
                    self.current_metrics.total_profit / self.current_metrics.winning_trades
                )
            
            if self.current_metrics.losing_trades > 0:
                self.current_metrics.average_loss = (
                    self.current_metrics.total_loss / self.current_metrics.losing_trades
                )
                
        except Exception as e:
            self.logger.log_error(f"Error calculando métricas derivadas: {e}")
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Retorna métricas actuales"""
        return self.current_metrics
    
    def save_snapshot(self) -> None:
        """Guarda snapshot de métricas actuales"""
        try:
            snapshot = PerformanceMetrics(
                total_trades=self.current_metrics.total_trades,
                winning_trades=self.current_metrics.winning_trades,
                losing_trades=self.current_metrics.losing_trades,
                win_rate=self.current_metrics.win_rate,
                total_profit=self.current_metrics.total_profit,
                total_loss=self.current_metrics.total_loss,
                net_profit=self.current_metrics.net_profit,
                profit_factor=self.current_metrics.profit_factor,
                average_win=self.current_metrics.average_win,
                average_loss=self.current_metrics.average_loss,
                max_drawdown=self.current_metrics.max_drawdown,
                sharpe_ratio=self.current_metrics.sharpe_ratio,
                trades_per_day=self.current_metrics.trades_per_day,
                timestamp=datetime.now()
            )
            
            self.metrics_history.append(snapshot)
            self.logger.log_success("Snapshot de métricas guardado")
            
        except Exception as e:
            self.logger.log_error(f"Error guardando snapshot: {e}")


class AnalyticsManager:
    """Manager principal de análisis y métricas avanzadas"""
    
    def __init__(self, config_manager: ConfigManager, logger_manager: LoggerManager, 
                 error_manager: ErrorManager, data_manager: DataManager):
        """
        Inicializa el Analytics Manager
        
        Args:
            config_manager: Manager de configuración
            logger_manager: Manager de logging
            error_manager: Manager de errores
            data_manager: Manager de datos
        """
        self.config = config_manager
        self.logger = logger_manager
        self.error_manager = error_manager
        self.data_manager = data_manager
        
        # Inicializar submódulos
        self.performance_tracker = PerformanceTracker(config_manager, logger_manager)
        self.grid_analytics = GridAnalytics(config_manager, logger_manager)
        self.market_analytics = MarketAnalytics(config_manager, logger_manager, data_manager)
        
        # Estado interno
        self.is_initialized = False
        self.analytics_active = False
        
        self.logger.log_info("AnalyticsManager inicializado - FASE 1.3")
    
    def initialize(self) -> bool:
        """Inicializa el sistema de analytics"""
        try:
            self.logger.log_info("Inicializando AnalyticsManager...")
            
            # Validar dependencias
            if not self._validate_dependencies():
                raise Exception("Dependencias no válidas")
            
            # Configurar directorio de analytics
            analytics_dir = Path("analytics")
            analytics_dir.mkdir(exist_ok=True)
            
            self.is_initialized = True
            self.analytics_active = True
            
            self.logger.log_success("✅ AnalyticsManager inicializado correctamente")
            return True
            
        except Exception as e:
            error_msg = f"Error inicializando AnalyticsManager: {e}"
            self.logger.log_error(error_msg)
            self.error_manager.handle_system_error("AnalyticsManager", e)
            return False
    
    def _validate_dependencies(self) -> bool:
        """Valida que las dependencias estén disponibles"""
        try:
            required_managers = [self.config, self.data_manager, self.error_manager]
            
            for manager in required_managers:
                if not hasattr(manager, 'is_initialized') or not manager.is_initialized:
                    self.logger.log_warning(f"Manager no inicializado: {type(manager).__name__}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error validando dependencias: {e}")
            return False
    
    def update_trade_performance(self, trade_data: Dict[str, Any]) -> None:
        """Actualiza métricas de rendimiento con datos de trade"""
        try:
            if not self.analytics_active:
                return
            
            self.performance_tracker.update_trade_metrics(trade_data)
            self.logger.log_info("Métricas de trade actualizadas")
            
        except Exception as e:
            error_msg = f"Error actualizando performance: {e}"
            self.logger.log_error(error_msg)
            self.error_manager.handle_system_error("PerformanceUpdate", e)
    
    def update_stochastic_signal(self, signal_data: Dict[str, Any]) -> None:
        """Actualiza señal estocástica para análisis de mercado"""
        try:
            if not self.analytics_active:
                return
            
            self.market_analytics.update_stochastic_signal(signal_data)
            
            # Actualizar análisis adicionales
            self.market_analytics.update_volatility_analysis()
            self.market_analytics.update_trend_analysis()
            
            self.logger.log_info("Señal estocástica y análisis de mercado actualizados")
            
        except Exception as e:
            error_msg = f"Error actualizando señal estocástica: {e}"
            self.logger.log_error(error_msg)
            self.error_manager.handle_system_error("StochasticSignalUpdate", e)
    
    def update_market_grid_correlation(self, grid_efficiency: float, grid_hit_rate: float) -> None:
        """Actualiza correlación entre mercado y grid"""
        try:
            if not self.analytics_active:
                return
            
            self.market_analytics.update_grid_correlation(grid_efficiency, grid_hit_rate)
            self.logger.log_info("Correlación mercado-grid actualizada")
            
        except Exception as e:
            error_msg = f"Error actualizando correlación: {e}"
            self.logger.log_error(error_msg)
            self.error_manager.handle_system_error("CorrelationUpdate", e)
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Retorna resumen de análisis del mercado"""
        try:
            if not self.analytics_active:
                return {"error": "Analytics no activo"}
            
            metrics = self.market_analytics.get_current_market_metrics()
            
            return {
                "volatility": round(metrics.volatility, 6),
                "trend_strength": round(metrics.trend_strength, 2),
                "market_efficiency": round(metrics.market_efficiency, 2),
                "correlation_with_grid": round(metrics.correlation_with_grid, 2),
                "rsi_average": round(metrics.rsi_average, 2),
                "timestamp": metrics.timestamp.isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error obteniendo resumen de mercado: {e}"
            self.logger.log_error(error_msg)
            return {"error": error_msg}
    
    def get_stochastic_report(self) -> Dict[str, Any]:
        """Retorna reporte de señales estocásticas"""
        try:
            if not self.analytics_active:
                return {"error": "Analytics no activo"}
            
            return self.market_analytics.get_stochastic_summary()
            
        except Exception as e:
            error_msg = f"Error obteniendo reporte estocástico: {e}"
            self.logger.log_error(error_msg)
            return {"error": error_msg}
    
    def get_market_conditions_report(self) -> Dict[str, Any]:
        """Retorna reporte completo de condiciones del mercado"""
        try:
            if not self.analytics_active:
                return {"error": "Analytics no activo"}
            
            return self.market_analytics.get_market_conditions_report()
            
        except Exception as e:
            error_msg = f"Error obteniendo condiciones de mercado: {e}"
            self.logger.log_error(error_msg)
            return {"error": error_msg}
    
    def update_grid_level(self, level: float, action: str, price: float, volume: float = 0.0) -> None:
        """Actualiza información de un nivel del grid"""
        try:
            if not self.analytics_active:
                return
            
            self.grid_analytics.update_grid_level(level, action, price, volume)
            self.logger.log_info(f"Grid level actualizado: {action} @ {level:.5f}")
            
        except Exception as e:
            error_msg = f"Error actualizando grid level: {e}"
            self.logger.log_error(error_msg)
            self.error_manager.handle_system_error("GridLevelUpdate", e)
    
    def get_grid_summary(self) -> Dict[str, Any]:
        """Retorna resumen de métricas del grid"""
        try:
            if not self.analytics_active:
                return {"error": "Analytics no activo"}
            
            metrics = self.grid_analytics.get_current_grid_metrics()
            
            return {
                "active_levels": metrics.active_levels,
                "completed_cycles": metrics.completed_cycles,
                "grid_efficiency": round(metrics.grid_efficiency, 2),
                "level_hit_rate": round(metrics.level_hit_rate, 2),
                "average_cycle_time": round(metrics.average_cycle_time, 2),
                "grid_spread": round(metrics.grid_spread, 5),
                "level_distribution": metrics.level_distribution,
                "timestamp": metrics.timestamp.isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error obteniendo resumen de grid: {e}"
            self.logger.log_error(error_msg)
            return {"error": error_msg}
    
    def get_level_performance_report(self) -> Dict[str, Any]:
        """Retorna reporte detallado de performance por nivel"""
        try:
            if not self.analytics_active:
                return {"error": "Analytics no activo"}
            
            return self.grid_analytics.get_level_performance_report()
            
        except Exception as e:
            error_msg = f"Error obteniendo reporte de niveles: {e}"
            self.logger.log_error(error_msg)
            return {"error": error_msg}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumen de rendimiento actual"""
        try:
            if not self.analytics_active:
                return {"error": "Analytics no activo"}
            
            metrics = self.performance_tracker.get_current_metrics()
            
            return {
                "total_trades": metrics.total_trades,
                "win_rate": round(metrics.win_rate, 2),
                "net_profit": round(metrics.net_profit, 4),
                "profit_factor": round(metrics.profit_factor, 2),
                "average_win": round(metrics.average_win, 4),
                "average_loss": round(metrics.average_loss, 4),
                "timestamp": metrics.timestamp.isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error obteniendo resumen: {e}"
            self.logger.log_error(error_msg)
            return {"error": error_msg}
    
    def save_analytics_snapshot(self) -> bool:
        """Guarda snapshot completo de analytics"""
        try:
            if not self.analytics_active:
                return False
            
            # Guardar snapshots de todos los submódulos
            self.performance_tracker.save_snapshot()
            self.grid_analytics.save_grid_snapshot()
            self.market_analytics.save_market_snapshot()
            
            self.logger.log_success("Snapshot completo de analytics guardado")
            return True
            
        except Exception as e:
            error_msg = f"Error guardando snapshot: {e}"
            self.logger.log_error(error_msg)
            self.error_manager.handle_system_error("SnapshotSave", e)
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna estado del sistema de analytics"""
        return {
            "initialized": self.is_initialized,
            "active": self.analytics_active,
            "performance_tracker": self.performance_tracker is not None,
            "grid_analytics": self.grid_analytics is not None,
            "market_analytics": self.market_analytics is not None,
            "version": "1.3.0",
            "phase": "FASE_1.3_MARKET_ANALYTICS"
        }
    
    def shutdown(self) -> None:
        """Cierra el sistema de analytics limpiamente"""
        try:
            if self.analytics_active:
                self.save_analytics_snapshot()
            
            self.analytics_active = False
            self.logger.log_success("AnalyticsManager cerrado correctamente")
            
        except Exception as e:
            self.logger.log_error(f"Error en shutdown: {e}")


# Funciones de utilidad para integración
def create_analytics_manager(config_manager: ConfigManager, logger_manager: LoggerManager,
                           error_manager: ErrorManager, data_manager: DataManager) -> AnalyticsManager:
    """Factory function para crear AnalyticsManager"""
    return AnalyticsManager(config_manager, logger_manager, error_manager, data_manager)


def validate_analytics_integration(analytics_manager: AnalyticsManager) -> bool:
    """Valida que el analytics manager esté correctamente integrado"""
    try:
        status = analytics_manager.get_system_status()
        return status.get("initialized", False) and status.get("active", False)
    except Exception:
        return False
