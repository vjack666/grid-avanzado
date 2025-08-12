"""
PISO 2 - BACKTEST ENGINE v1.0.0
================================
Sistema de backtesting avanzado con datos reales de MT5

AUTOR: Sistema Modular Trading Grid
FECHA: 2025-08-12
PROTOCOLO: PISO 2 - BACKTEST ENGINE
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import json

# Configurar rutas de imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager


@dataclass
class BacktestConfig:
    """Configuración para backtesting"""
    symbol: str = "EURUSD"
    timeframe: str = "M15"
    start_date: str = "2025-05-20"
    end_date: str = "2025-08-12"
    initial_balance: float = 10000.0
    spread: float = 0.00015  # 1.5 pips
    commission: float = 2.0  # $2 por lote por lado
    strategy_type: str = "GRID_BOLLINGER"
    
    # Parámetros específicos de estrategia
    bollinger_period: int = 20
    bollinger_deviation: float = 2.0
    grid_spacing: float = 0.0025  # 25 pips
    grid_levels: int = 10
    lot_size: float = 0.1
    take_profit: int = 50  # pips
    stop_loss: int = 200   # pips


@dataclass
class BacktestTrade:
    """Estructura para trades del backtest"""
    id: int
    symbol: str
    direction: str  # BUY/SELL
    open_time: datetime
    close_time: Optional[datetime] = None
    open_price: float = 0.0
    close_price: float = 0.0
    volume: float = 0.1
    pnl: float = 0.0
    commission: float = 0.0
    swap: float = 0.0
    net_pnl: float = 0.0
    status: str = "OPEN"  # OPEN/CLOSED/CANCELLED
    signal_source: str = ""
    entry_reason: str = ""
    exit_reason: str = ""


@dataclass
class BacktestResult:
    """Resultado completo del backtest"""
    config: BacktestConfig
    trades: List[BacktestTrade] = field(default_factory=list)
    
    # Métricas de performance
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_profit: float = 0.0
    profit_factor: float = 0.0
    
    max_drawdown: float = 0.0
    max_drawdown_percent: float = 0.0
    max_consecutive_losses: int = 0
    max_consecutive_wins: int = 0
    
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    
    initial_balance: float = 10000.0
    final_balance: float = 10000.0
    
    backtest_start: datetime = field(default_factory=datetime.now)
    backtest_end: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0
    
    # Datos adicionales
    equity_curve: List[float] = field(default_factory=list)
    balance_curve: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)


class HistoricalDataProcessor:
    """PUERTA-P2-DATA: Procesador de datos históricos"""
    
    def __init__(self, config_manager: ConfigManager, logger_manager: LoggerManager, 
                 error_manager: ErrorManager):
        self.config = config_manager
        self.logger = logger_manager
        self.error = error_manager
        self.component_id = "PUERTA-P2-DATA"
        self.version = "v1.0.0"
        
        # Cache de datos
        self._data_cache: Dict[str, pd.DataFrame] = {}
        
    def load_historical_data(self, symbol: str, timeframe: str, 
                           start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
        """Cargar datos históricos desde archivos CSV"""
        try:
            cache_key = f"{symbol}_{timeframe}_{start_date}_{end_date}"
            if cache_key in self._data_cache:
                return self._data_cache[cache_key]
            
            # Buscar archivo más reciente
            # Primero intentar en el directorio del proyecto
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            project_data_dir = os.path.join(project_root, "data")
            
            # Buscar en directorio del proyecto primero
            if os.path.exists(project_data_dir):
                from pathlib import Path
                data_dir = Path(project_data_dir)
                csv_files = list(data_dir.glob(f"**/velas_{symbol}_{timeframe}_*.csv"))
            else:
                # Fallback al ConfigManager
                data_dir = Path(self.config.get_data_dir())
                csv_files = list(data_dir.glob(f"**/velas_{symbol}_{timeframe}_*.csv"))
            
            if not csv_files:
                self.error.handle_system_error(
                    "DATA_NOT_FOUND", 
                    f"No se encontraron datos para {symbol} {timeframe}",
                    {"symbol": symbol, "timeframe": timeframe}
                )
                return None
            
            # Tomar el archivo más reciente
            latest_file = max(csv_files, key=lambda f: f.stat().st_mtime)
            self.logger.log_info(f"Cargando datos desde: {latest_file}")
            
            # Cargar y procesar datos
            df = pd.read_csv(latest_file)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)
            
            # Filtrar por fechas si se especifican
            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]
            
            # Validar datos
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"Faltan columnas requeridas: {required_columns}")
            
            # Cache de datos
            self._data_cache[cache_key] = df
            
            self.logger.log_success(f"Datos cargados: {len(df)} registros de {symbol} {timeframe}")
            
            return df
            
        except Exception as e:
            self.error.handle_system_error(
                "DATA_LOAD_ERROR",
                f"Error cargando datos históricos: {str(e)}",
                {"symbol": symbol, "timeframe": timeframe, "error": str(e)}
            )
            return None
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validar calidad de los datos"""
        try:
            validation = {
                "total_records": len(df),
                "missing_values": df.isnull().sum().to_dict(),
                "duplicate_timestamps": df.index.duplicated().sum(),
                "data_gaps": 0,
                "price_anomalies": 0,
                "quality_score": 0.0
            }
            
            # Detectar gaps en datos
            if len(df) > 1:
                time_diff = df.index.to_series().diff().dropna()
                expected_interval = time_diff.mode()[0] if len(time_diff.mode()) > 0 else timedelta(minutes=15)
                gaps = time_diff[time_diff > expected_interval * 1.5]
                validation["data_gaps"] = len(gaps)
            
            # Detectar anomalías de precio
            price_changes = df['close'].pct_change()
            anomalies = price_changes[abs(price_changes) > 0.05]  # >5% cambio
            validation["price_anomalies"] = len(anomalies)
            
            # Calcular score de calidad
            quality_factors = [
                1.0 - min(1.0, validation["missing_values"].get('close', 0) / len(df)),
                1.0 - min(1.0, validation["duplicate_timestamps"] / len(df)),
                1.0 - min(1.0, validation["data_gaps"] / (len(df) * 0.01)),
                1.0 - min(1.0, validation["price_anomalies"] / (len(df) * 0.01))
            ]
            validation["quality_score"] = sum(quality_factors) / len(quality_factors) * 100
            
            self.logger.log_info(f"Validación de datos completada - Score: {validation['quality_score']:.1f}%")
            
            return validation
            
        except Exception as e:
            self.error.handle_system_error(
                "DATA_VALIDATION_ERROR",
                f"Error validando datos: {str(e)}",
                {"error": str(e)}
            )
            return {"quality_score": 0.0, "error": str(e)}


class BacktestExecutor:
    """PUERTA-P2-EXECUTOR: Ejecutor de backtests"""
    
    def __init__(self, config_manager: ConfigManager, logger_manager: LoggerManager, 
                 error_manager: ErrorManager, data_processor: HistoricalDataProcessor):
        self.config = config_manager
        self.logger = logger_manager
        self.error = error_manager
        self.data_processor = data_processor
        self.component_id = "PUERTA-P2-EXECUTOR"
        self.version = "v1.0.0"
        
        # Estado del backtest
        self.current_balance: float = 0.0
        self.current_equity: float = 0.0
        self.open_trades: List[BacktestTrade] = []
        self.closed_trades: List[BacktestTrade] = []
        self.trade_counter: int = 0
        
    def run_backtest(self, config: BacktestConfig) -> BacktestResult:
        """Ejecutar backtest completo"""
        try:
            start_time = datetime.now()
            self.logger.log_info(f"Iniciando backtest con {config.strategy_type}")
            
            # Cargar datos históricos
            df = self.data_processor.load_historical_data(
                config.symbol, config.timeframe, 
                config.start_date, config.end_date
            )
            
            if df is None or len(df) == 0:
                raise ValueError("No se pudieron cargar datos históricos")
            
            # Validar calidad de datos
            validation = self.data_processor.validate_data_quality(df)
            if validation["quality_score"] < 70.0:
                self.logger.log_warning(
                    f"Calidad de datos baja: {validation['quality_score']:.1f}%"
                )
            
            # Inicializar estado
            self._initialize_backtest(config)
            
            # Preparar datos con indicadores
            df_with_indicators = self._prepare_data_with_indicators(df, config)
            
            # Ejecutar estrategia bar por bar
            result = self._execute_strategy_backtest(df_with_indicators, config)
            
            # Calcular métricas finales
            self._calculate_final_metrics(result)
            
            # Tiempo de ejecución
            result.execution_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.log_success(
                f"Backtest completado - Trades: {result.total_trades}, "
                f"Win Rate: {result.win_rate:.1f}%, Net P&L: ${result.net_profit:.2f}"
            )
            
            return result
            
        except Exception as e:
            self.error.handle_system_error(
                "BACKTEST_EXECUTION_ERROR",
                f"Error ejecutando backtest: {str(e)}",
                {"config": config.__dict__, "error": str(e)}
            )
            # Retornar resultado vacío en caso de error
            return BacktestResult(config=config)
    
    def _initialize_backtest(self, config: BacktestConfig):
        """Inicializar estado del backtest"""
        self.current_balance = config.initial_balance
        self.current_equity = config.initial_balance
        self.open_trades = []
        self.closed_trades = []
        self.trade_counter = 0
        
    def _prepare_data_with_indicators(self, df: pd.DataFrame, config: BacktestConfig) -> pd.DataFrame:
        """Preparar datos con indicadores necesarios"""
        try:
            df = df.copy()
            
            # Bollinger Bands
            if config.strategy_type == "GRID_BOLLINGER":
                period = config.bollinger_period
                deviation = config.bollinger_deviation
                
                df['sma'] = df['close'].rolling(window=period).mean()
                df['std'] = df['close'].rolling(window=period).std()
                df['bb_upper'] = df['sma'] + (df['std'] * deviation)
                df['bb_lower'] = df['sma'] - (df['std'] * deviation)
                
                # Señales básicas
                df['signal'] = None
                df.loc[df['close'] <= df['bb_lower'], 'signal'] = 'BUY'
                df.loc[df['close'] >= df['bb_upper'], 'signal'] = 'SELL'
            
            return df
            
        except Exception as e:
            self.logger.log_error(f"Error preparando indicadores: {e}")
            return df
    
    def _execute_strategy_backtest(self, df: pd.DataFrame, config: BacktestConfig) -> BacktestResult:
        """Ejecutar estrategia bar por bar"""
        result = BacktestResult(config=config)
        result.backtest_start = df.index[0]
        result.backtest_end = df.index[-1]
        result.initial_balance = config.initial_balance
        
        for i, (timestamp, row) in enumerate(df.iterrows()):
            if i < config.bollinger_period:  # Esperar indicadores válidos
                continue
                
            # Procesar trades abiertos
            self._process_open_trades(row, timestamp, config)
            
            # Buscar nuevas señales
            if not pd.isna(row.get('signal')):
                self._process_signal(row, timestamp, config)
            
            # Actualizar equity curve
            current_equity = self._calculate_current_equity(row['close'])
            result.equity_curve.append(current_equity)
            result.balance_curve.append(self.current_balance)
            result.timestamps.append(timestamp)
        
        # Cerrar trades abiertos al final
        if self.open_trades:
            last_price = df.iloc[-1]['close']
            for trade in self.open_trades:
                self._close_trade(trade, last_price, df.index[-1], "END_OF_DATA")
        
        result.trades = self.closed_trades
        result.final_balance = self.current_balance
        
        return result
    
    def _process_open_trades(self, row: pd.Series, timestamp: datetime, config: BacktestConfig):
        """Procesar trades abiertos para TP/SL"""
        for trade in self.open_trades[:]:  # Copia para modificar durante iteración
            if trade.direction == "BUY":
                # Check Take Profit
                if row['high'] >= trade.open_price + (config.take_profit * 0.0001):
                    self._close_trade(trade, trade.open_price + (config.take_profit * 0.0001), 
                                    timestamp, "TAKE_PROFIT")
                # Check Stop Loss
                elif row['low'] <= trade.open_price - (config.stop_loss * 0.0001):
                    self._close_trade(trade, trade.open_price - (config.stop_loss * 0.0001), 
                                    timestamp, "STOP_LOSS")
                    
            elif trade.direction == "SELL":
                # Check Take Profit
                if row['low'] <= trade.open_price - (config.take_profit * 0.0001):
                    self._close_trade(trade, trade.open_price - (config.take_profit * 0.0001), 
                                    timestamp, "TAKE_PROFIT")
                # Check Stop Loss
                elif row['high'] >= trade.open_price + (config.stop_loss * 0.0001):
                    self._close_trade(trade, trade.open_price + (config.stop_loss * 0.0001), 
                                    timestamp, "STOP_LOSS")
    
    def _process_signal(self, row: pd.Series, timestamp: datetime, config: BacktestConfig):
        """Procesar nueva señal de trading"""
        signal = row['signal']
        
        # Limitar trades concurrentes
        if len(self.open_trades) >= 3:  # Max 3 trades simultáneos
            return
            
        # Crear nuevo trade
        self.trade_counter += 1
        trade = BacktestTrade(
            id=self.trade_counter,
            symbol=config.symbol,
            direction=signal,
            open_time=timestamp,
            open_price=row['close'],
            volume=config.lot_size,
            signal_source=config.strategy_type,
            entry_reason=f"Bollinger Band {signal.lower()}"
        )
        
        # Calcular comisión
        trade.commission = config.commission
        self.current_balance -= trade.commission
        
        self.open_trades.append(trade)
        self.logger.log_info(f"Trade abierto: {signal} {config.symbol} @ {row['close']:.5f}")
    
    def _close_trade(self, trade: BacktestTrade, close_price: float, 
                    close_time: datetime, exit_reason: str):
        """Cerrar trade y calcular P&L"""
        trade.close_time = close_time
        trade.close_price = close_price
        trade.exit_reason = exit_reason
        trade.status = "CLOSED"
        
        # Calcular P&L
        if trade.direction == "BUY":
            trade.pnl = (close_price - trade.open_price) * trade.volume * 100000  # Para EURUSD
        else:  # SELL
            trade.pnl = (trade.open_price - close_price) * trade.volume * 100000
        
        # Comisión de cierre
        trade.commission += 2.0  # Comisión de cierre
        trade.net_pnl = trade.pnl - trade.commission
        
        # Actualizar balance
        self.current_balance += trade.net_pnl
        
        # Mover a trades cerrados
        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        
        self.logger.log_info(
            f"Trade cerrado: {trade.direction} {trade.symbol} "
            f"P&L: ${trade.net_pnl:.2f} ({exit_reason})"
        )
    
    def _calculate_current_equity(self, current_price: float) -> float:
        """Calcular equity actual"""
        floating_pnl = 0.0
        for trade in self.open_trades:
            if trade.direction == "BUY":
                floating_pnl += (current_price - trade.open_price) * trade.volume * 100000
            else:
                floating_pnl += (trade.open_price - current_price) * trade.volume * 100000
        
        return self.current_balance + floating_pnl
    
    def _calculate_final_metrics(self, result: BacktestResult):
        """Calcular métricas finales del backtest"""
        if not result.trades:
            return
        
        # Métricas básicas
        result.total_trades = len(result.trades)
        result.winning_trades = len([t for t in result.trades if t.net_pnl > 0])
        result.losing_trades = result.total_trades - result.winning_trades
        result.win_rate = (result.winning_trades / result.total_trades) * 100 if result.total_trades > 0 else 0
        
        # P&L
        result.gross_profit = sum(t.net_pnl for t in result.trades if t.net_pnl > 0)
        result.gross_loss = abs(sum(t.net_pnl for t in result.trades if t.net_pnl < 0))
        result.net_profit = result.gross_profit - result.gross_loss
        result.profit_factor = result.gross_profit / result.gross_loss if result.gross_loss > 0 else 0
        
        # Drawdown
        if result.equity_curve:
            peak = result.equity_curve[0]
            max_dd = 0
            for equity in result.equity_curve:
                if equity > peak:
                    peak = equity
                dd = peak - equity
                if dd > max_dd:
                    max_dd = dd
            
            result.max_drawdown = max_dd
            result.max_drawdown_percent = (max_dd / peak) * 100 if peak > 0 else 0
        
        # Rachas
        consecutive_wins = 0
        consecutive_losses = 0
        current_win_streak = 0
        current_loss_streak = 0
        
        for trade in result.trades:
            if trade.net_pnl > 0:
                current_win_streak += 1
                current_loss_streak = 0
                consecutive_wins = max(consecutive_wins, current_win_streak)
            else:
                current_loss_streak += 1
                current_win_streak = 0
                consecutive_losses = max(consecutive_losses, current_loss_streak)
        
        result.max_consecutive_wins = consecutive_wins
        result.max_consecutive_losses = consecutive_losses
        
        # Sharpe ratio simplificado
        if result.trades:
            returns = [t.net_pnl for t in result.trades]
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            result.sharpe_ratio = avg_return / std_return if std_return > 0 else 0
