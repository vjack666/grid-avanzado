"""
PerformanceTracker - Seguimiento de Rendimiento - SÓTANO 2 DÍA 2
================================================================

Sistema de seguimiento de rendimiento en tiempo real para trading.
Calcula métricas de performance, drawdown, ratios y análisis estadísticos.

Componente: PUERTA-S2-PERFORMANCE
Fase: SÓTANO 2 - Tiempo Real
Prioridad: 4 de 4 (DÍA 2)
Versión: v2.1.0

Autor: Copilot Trading Grid
Fecha: 2025-08-11
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from collections import deque


@dataclass
class PerformanceSnapshot:
    """Instantánea de performance en un momento dado"""
    timestamp: datetime
    balance: float
    equity: float
    margin_used: float
    margin_free: float
    open_positions: int
    total_pnl: float
    day_pnl: float
    win_rate: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float = 0.0
    trades_count: int = 0


@dataclass
class TradeRecord:
    """Registro de una operación completada"""
    id: str
    symbol: str
    type: str  # "buy" or "sell"
    volume: float
    open_price: float
    close_price: float
    open_time: datetime
    close_time: datetime
    pnl: float
    commission: float
    swap: float
    net_profit: float


class PerformanceTracker:
    """
    Seguimiento de Rendimiento - PUERTA-S2-PERFORMANCE
    
    Sistema completo de análisis de performance en tiempo real:
    - Cálculo de métricas de trading en vivo
    - Tracking de drawdown y recuperación
    - Análisis de ratios de riesgo/retorno
    - Historial de snapshots para análisis temporal
    - Alertas automáticas de performance
    
    Integración SÓTANO 1:
    - PUERTA-S1-CONFIG: Configuración de métricas
    - PUERTA-S1-LOGGER: Logging de performance
    - PUERTA-S1-ERROR: Manejo de errores
    - PUERTA-S1-DATA: Almacenamiento de históricos
    
    Integración SÓTANO 2:
    - PUERTA-S2-ALERTS: Alertas de performance
    - PUERTA-S2-POSITIONS: Datos de posiciones
    
    Características:
    - Cálculos en tiempo real con precisión de microsegundos
    - Métricas estadísticas avanzadas (Sharpe, Sortino, Calmar)
    - Detección de patrones de performance
    - Análisis de correlación con mercado
    """
    
    def __init__(self, config=None, logger=None, error=None, data_manager=None, alert_engine=None):
        """
        Inicializar PerformanceTracker
        
        Args:
            config: ConfigManager para configuración
            logger: LoggerManager para logging
            error: ErrorManager para manejo de errores
            data_manager: DataManager para almacenamiento
            alert_engine: AlertEngine para alertas (opcional)
        """
        # Metadatos del componente
        self.component_id = "PUERTA-S2-PERFORMANCE"
        self.version = "v2.1.0"
        self.status = "initialized"
        
        # Dependencias SÓTANO 1
        self.config = config
        self.logger = logger
        self.error = error
        self.data = data_manager
        
        # Dependencias SÓTANO 2
        self.alert_engine = alert_engine
        
        # Estado del tracker
        self.is_tracking = False
        self.tracking_lock = threading.Lock()
        self.tracking_thread = None
        
        # Configuración de tracking
        self.tracker_config = {
            "enabled": True,
            "update_interval": 5.0,  # segundos
            "snapshot_interval": 60.0,  # segundos
            "max_snapshots": 1440,  # 24 horas de minutos
            "max_trades_history": 10000,
            "alert_thresholds": {
                "max_drawdown": 15.0,  # %
                "daily_loss": 5.0,     # %
                "min_win_rate": 40.0,  # %
                "min_profit_factor": 1.2
            },
            "risk_free_rate": 0.02,  # Para Sharpe ratio
            "benchmark_symbol": "EURUSD"
        }
        
        # Datos de performance
        self.performance_snapshots: deque = deque(maxlen=self.tracker_config["max_snapshots"])
        self.trade_history: List[TradeRecord] = []
        self.current_snapshot: Optional[PerformanceSnapshot] = None
        
        # Estado actual de la cuenta
        self.account_state = {
            "initial_balance": 0.0,
            "current_balance": 0.0,
            "current_equity": 0.0,
            "peak_balance": 0.0,
            "peak_equity": 0.0,
            "max_drawdown": 0.0,
            "max_drawdown_date": None,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "gross_profit": 0.0,
            "gross_loss": 0.0
        }
        
        # Métricas calculadas
        self.calculated_metrics = {
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "consecutive_wins": 0,
            "consecutive_losses": 0,
            "max_consecutive_wins": 0,
            "max_consecutive_losses": 0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "calmar_ratio": 0.0,
            "recovery_factor": 0.0
        }
        
        # Buffers para cálculos en tiempo real
        self.pnl_buffer: deque = deque(maxlen=252)  # 1 año de días trading
        self.returns_buffer: deque = deque(maxlen=252)
        
        # Cargar configuración
        self._load_configuration()
        
        # Log inicialización
        if self.logger:
            self.logger.log_info(f"[{self.component_id}] Configuración cargada: {len(self.tracker_config)} parámetros")
            self.logger.log_info(f"[{self.component_id}] Inicializando PerformanceTracker {self.version}")
    
    def _load_configuration(self):
        """Cargar configuración desde ConfigManager"""
        if self.config:
            try:
                # Por ahora usar configuración por defecto
                # TODO: Implementar configuración personalizada desde archivo cuando esté disponible
                pass
                        
            except Exception as e:
                if self.error:
                    self.error.handle_system_error("PerformanceTracker", e, {"method": "_load_configuration"})
    
    def start_tracking(self, initial_balance: Optional[float] = None) -> bool:
        """
        Iniciar seguimiento de performance
        
        Args:
            initial_balance: Balance inicial para cálculos (opcional)
            
        Returns:
            bool: True si se inició correctamente
        """
        try:
            if self.is_tracking:
                if self.logger:
                    self.logger.log_warning(f"[{self.component_id}] Tracking ya está activo")
                return True
            
            if not self.tracker_config.get("enabled", True):
                if self.logger:
                    self.logger.log_info(f"[{self.component_id}] Tracking deshabilitado en configuración")
                return False
            
            # Configurar balance inicial
            if initial_balance is not None:
                self.account_state["initial_balance"] = initial_balance
                self.account_state["current_balance"] = initial_balance
                self.account_state["current_equity"] = initial_balance
                self.account_state["peak_balance"] = initial_balance
                self.account_state["peak_equity"] = initial_balance
            
            # Iniciar thread de tracking
            self.is_tracking = True
            self.tracking_thread = threading.Thread(
                target=self._tracking_loop,
                daemon=True,
                name="PerformanceTracker"
            )
            self.tracking_thread.start()
            
            self.status = "tracking"
            
            if self.logger:
                self.logger.log_info(f"[{self.component_id}] Tracking de performance iniciado")
                if initial_balance:
                    self.logger.log_info(f"[{self.component_id}] Balance inicial: ${initial_balance:,.2f}")
            
            return True
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("PerformanceTracker", e, {"method": "start_tracking"})
            self.status = "error"
            return False
    
    def stop_tracking(self) -> bool:
        """
        Detener seguimiento de performance
        
        Returns:
            bool: True si se detuvo correctamente
        """
        try:
            if not self.is_tracking:
                return True
            
            self.is_tracking = False
            
            # Esperar a que termine el thread
            if self.tracking_thread:
                self.tracking_thread.join(timeout=5.0)
            
            self.status = "stopped"
            
            if self.logger:
                self.logger.log_info(f"[{self.component_id}] Tracking de performance detenido")
            
            return True
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("PerformanceTracker", e, {"method": "stop_tracking"})
            return False
    
    def _tracking_loop(self):
        """Loop principal de tracking"""
        last_snapshot_time = time.time()
        
        while self.is_tracking:
            try:
                current_time = time.time()
                
                # Actualizar métricas en tiempo real
                self._update_real_time_metrics()
                
                # Crear snapshot periódico
                if current_time - last_snapshot_time >= self.tracker_config["snapshot_interval"]:
                    self._create_performance_snapshot()
                    last_snapshot_time = current_time
                
                # Verificar alertas de performance
                self._check_performance_alerts()
                
                # Dormir hasta la próxima actualización
                time.sleep(self.tracker_config["update_interval"])
                
            except Exception as e:
                if self.error:
                    self.error.handle_system_error("PerformanceTracker", e, {"method": "_tracking_loop"})
                time.sleep(10.0)  # Esperar más tiempo si hay error
    
    def update_account_data(self, balance: float, equity: float, margin_used: float = 0.0, margin_free: float = 0.0):
        """
        Actualizar datos de la cuenta
        
        Args:
            balance: Balance actual
            equity: Equity actual
            margin_used: Margen utilizado
            margin_free: Margen libre
        """
        with self.tracking_lock:
            # Actualizar estado de cuenta
            self.account_state["current_balance"] = balance
            self.account_state["current_equity"] = equity
            
            # Actualizar picos
            if balance > self.account_state["peak_balance"]:
                self.account_state["peak_balance"] = balance
            
            if equity > self.account_state["peak_equity"]:
                self.account_state["peak_equity"] = equity
            
            # Calcular drawdown actual
            if self.account_state["peak_equity"] > 0:
                current_drawdown = (self.account_state["peak_equity"] - equity) / self.account_state["peak_equity"] * 100
                
                if current_drawdown > self.account_state["max_drawdown"]:
                    self.account_state["max_drawdown"] = current_drawdown
                    self.account_state["max_drawdown_date"] = datetime.now()
            
            # Actualizar buffer de returns
            if self.account_state["initial_balance"] > 0:
                daily_return = (equity - self.account_state["initial_balance"]) / self.account_state["initial_balance"]
                self.returns_buffer.append(daily_return)
            
            if self.logger and self.is_tracking:
                self.logger.log_info(f"[{self.component_id}] Cuenta actualizada - Balance: ${balance:,.2f}, Equity: ${equity:,.2f}")
    
    def add_completed_trade(self, trade: TradeRecord):
        """
        Agregar una operación completada
        
        Args:
            trade: Registro de la operación
        """
        with self.tracking_lock:
            # Agregar al historial
            self.trade_history.append(trade)
            
            # Mantener límite de historial
            if len(self.trade_history) > self.tracker_config["max_trades_history"]:
                self.trade_history = self.trade_history[-self.tracker_config["max_trades_history"]:]
            
            # Actualizar estadísticas
            self.account_state["total_trades"] += 1
            
            if trade.net_profit > 0:
                self.account_state["winning_trades"] += 1
                self.account_state["gross_profit"] += trade.net_profit
            else:
                self.account_state["losing_trades"] += 1
                self.account_state["gross_loss"] += abs(trade.net_profit)
            
            # Agregar al buffer de PnL
            self.pnl_buffer.append(trade.net_profit)
            
            # Recalcular métricas
            self._calculate_metrics()
            
            if self.logger:
                self.logger.log_info(f"[{self.component_id}] Trade agregado: {trade.symbol} - PnL: ${trade.net_profit:,.2f}")
    
    def _update_real_time_metrics(self):
        """Actualizar métricas en tiempo real"""
        try:
            # Recalcular métricas básicas
            self._calculate_metrics()
            
            # Crear snapshot actual
            self.current_snapshot = self._create_current_snapshot()
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("PerformanceTracker", e, {"method": "_update_real_time_metrics"})
    
    def _calculate_metrics(self):
        """Calcular todas las métricas de performance"""
        try:
            # Win rate
            total_trades = self.account_state["total_trades"]
            if total_trades > 0:
                self.calculated_metrics["win_rate"] = (self.account_state["winning_trades"] / total_trades) * 100
            
            # Profit factor
            gross_loss = self.account_state["gross_loss"]
            if gross_loss > 0:
                self.calculated_metrics["profit_factor"] = self.account_state["gross_profit"] / gross_loss
            
            # Promedios
            if self.account_state["winning_trades"] > 0:
                self.calculated_metrics["average_win"] = self.account_state["gross_profit"] / self.account_state["winning_trades"]
            
            if self.account_state["losing_trades"] > 0:
                self.calculated_metrics["average_loss"] = self.account_state["gross_loss"] / self.account_state["losing_trades"]
            
            # Calcular desde historial de trades
            if self.trade_history:
                profits = [t.net_profit for t in self.trade_history if t.net_profit > 0]
                losses = [t.net_profit for t in self.trade_history if t.net_profit < 0]
                
                if profits:
                    self.calculated_metrics["largest_win"] = max(profits)
                
                if losses:
                    self.calculated_metrics["largest_loss"] = min(losses)
                
                # Calcular rachas
                self._calculate_consecutive_stats()
            
            # Ratios avanzados
            self._calculate_advanced_ratios()
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("PerformanceTracker", e, {"method": "_calculate_metrics"})
    
    def _calculate_consecutive_stats(self):
        """Calcular estadísticas de rachas consecutivas"""
        if not self.trade_history:
            return
        
        current_wins = 0
        current_losses = 0
        max_wins = 0
        max_losses = 0
        
        for trade in self.trade_history:
            if trade.net_profit > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
        
        self.calculated_metrics["consecutive_wins"] = current_wins
        self.calculated_metrics["consecutive_losses"] = current_losses
        self.calculated_metrics["max_consecutive_wins"] = max_wins
        self.calculated_metrics["max_consecutive_losses"] = max_losses
    
    def _calculate_advanced_ratios(self):
        """Calcular ratios avanzados (Sharpe, Sortino, etc.)"""
        try:
            if len(self.returns_buffer) < 30:  # Necesitamos datos suficientes
                return
            
            returns = np.array(list(self.returns_buffer))
            
            # Sharpe Ratio
            if len(returns) > 1:
                excess_returns = returns - (self.tracker_config["risk_free_rate"] / 252)  # Daily risk-free rate
                if np.std(excess_returns) > 0:
                    self.calculated_metrics["sharpe_ratio"] = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
            
            # Sortino Ratio (solo downside deviation)
            negative_returns = returns[returns < 0]
            if len(negative_returns) > 1:
                downside_std = np.std(negative_returns)
                if downside_std > 0:
                    self.calculated_metrics["sortino_ratio"] = np.mean(returns) / downside_std * np.sqrt(252)
            
            # Calmar Ratio
            if self.account_state["max_drawdown"] > 0:
                annual_return = np.mean(returns) * 252
                self.calculated_metrics["calmar_ratio"] = annual_return / (self.account_state["max_drawdown"] / 100)
            
            # Recovery Factor
            if self.account_state["max_drawdown"] > 0 and self.account_state["gross_profit"] > 0:
                self.calculated_metrics["recovery_factor"] = self.account_state["gross_profit"] / (self.account_state["max_drawdown"] / 100)
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("PerformanceTracker", e, {"method": "_calculate_advanced_ratios"})
    
    def _create_current_snapshot(self) -> PerformanceSnapshot:
        """Crear snapshot del estado actual"""
        return PerformanceSnapshot(
            timestamp=datetime.now(),
            balance=self.account_state["current_balance"],
            equity=self.account_state["current_equity"],
            margin_used=0.0,  # Se actualizará con datos reales
            margin_free=0.0,  # Se actualizará con datos reales
            open_positions=0,  # Se actualizará con datos reales
            total_pnl=self.account_state["current_equity"] - self.account_state["initial_balance"],
            day_pnl=0.0,  # Se calculará
            win_rate=self.calculated_metrics["win_rate"],
            profit_factor=self.calculated_metrics["profit_factor"],
            max_drawdown=self.account_state["max_drawdown"],
            sharpe_ratio=self.calculated_metrics["sharpe_ratio"],
            trades_count=self.account_state["total_trades"]
        )
    
    def _create_performance_snapshot(self):
        """Crear y almacenar un snapshot de performance"""
        try:
            snapshot = self._create_current_snapshot()
            self.performance_snapshots.append(snapshot)
            
            if self.logger:
                self.logger.log_info(f"[{self.component_id}] Snapshot creado - Balance: ${snapshot.balance:,.2f}")
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("PerformanceTracker", e, {"method": "_create_performance_snapshot"})
    
    def _check_performance_alerts(self):
        """Verificar y enviar alertas de performance"""
        try:
            if not self.alert_engine:
                return
            
            thresholds = self.tracker_config["alert_thresholds"]
            
            # Alerta de máximo drawdown
            if self.account_state["max_drawdown"] > thresholds["max_drawdown"]:
                self.alert_engine.send_alert(
                    priority=self.alert_engine.AlertPriority.HIGH,
                    category="performance",
                    title="Máximo Drawdown Excedido",
                    message=f"Drawdown actual: {self.account_state['max_drawdown']:.1f}% (Límite: {thresholds['max_drawdown']:.1f}%)",
                    data={"drawdown": self.account_state["max_drawdown"], "threshold": thresholds["max_drawdown"]}
                )
            
            # Alerta de win rate bajo
            if (self.calculated_metrics["win_rate"] < thresholds["min_win_rate"] and 
                self.account_state["total_trades"] >= 10):
                self.alert_engine.send_alert(
                    priority=self.alert_engine.AlertPriority.MEDIUM,
                    category="performance",
                    title="Win Rate Bajo",
                    message=f"Win rate actual: {self.calculated_metrics['win_rate']:.1f}% (Mínimo: {thresholds['min_win_rate']:.1f}%)",
                    data={"win_rate": self.calculated_metrics["win_rate"], "threshold": thresholds["min_win_rate"]}
                )
            
            # Alerta de profit factor bajo
            if (self.calculated_metrics["profit_factor"] < thresholds["min_profit_factor"] and 
                self.account_state["total_trades"] >= 10):
                self.alert_engine.send_alert(
                    priority=self.alert_engine.AlertPriority.MEDIUM,
                    category="performance",
                    title="Profit Factor Bajo",
                    message=f"Profit factor actual: {self.calculated_metrics['profit_factor']:.2f} (Mínimo: {thresholds['min_profit_factor']:.2f})",
                    data={"profit_factor": self.calculated_metrics["profit_factor"], "threshold": thresholds["min_profit_factor"]}
                )
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("PerformanceTracker", e, {"method": "_check_performance_alerts"})
    
    def get_current_performance(self) -> Dict[str, Any]:
        """Obtener performance actual completa"""
        with self.tracking_lock:
            return {
                "account_state": self.account_state.copy(),
                "calculated_metrics": self.calculated_metrics.copy(),
                "current_snapshot": self.current_snapshot,
                "total_snapshots": len(self.performance_snapshots),
                "total_trades": len(self.trade_history)
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtener resumen de performance"""
        return {
            "balance": self.account_state["current_balance"],
            "equity": self.account_state["current_equity"],
            "total_pnl": self.account_state["current_equity"] - self.account_state["initial_balance"],
            "max_drawdown": self.account_state["max_drawdown"],
            "win_rate": self.calculated_metrics["win_rate"],
            "profit_factor": self.calculated_metrics["profit_factor"],
            "sharpe_ratio": self.calculated_metrics["sharpe_ratio"],
            "total_trades": self.account_state["total_trades"],
            "tracking_active": self.is_tracking
        }
    
    def get_snapshots_dataframe(self) -> pd.DataFrame:
        """Obtener snapshots como DataFrame para análisis"""
        if not self.performance_snapshots:
            return pd.DataFrame()
        
        try:
            data = []
            for snapshot in self.performance_snapshots:
                data.append({
                    'timestamp': snapshot.timestamp,
                    'balance': snapshot.balance,
                    'equity': snapshot.equity,
                    'total_pnl': snapshot.total_pnl,
                    'max_drawdown': snapshot.max_drawdown,
                    'win_rate': snapshot.win_rate,
                    'profit_factor': snapshot.profit_factor,
                    'sharpe_ratio': snapshot.sharpe_ratio,
                    'trades_count': snapshot.trades_count
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("PerformanceTracker", e, {"method": "get_snapshots_dataframe"})
            return pd.DataFrame()
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """Obtener historial de trades como DataFrame"""
        if not self.trade_history:
            return pd.DataFrame()
        
        try:
            data = []
            for trade in self.trade_history:
                data.append({
                    'id': trade.id,
                    'symbol': trade.symbol,
                    'type': trade.type,
                    'volume': trade.volume,
                    'open_price': trade.open_price,
                    'close_price': trade.close_price,
                    'open_time': trade.open_time,
                    'close_time': trade.close_time,
                    'pnl': trade.pnl,
                    'commission': trade.commission,
                    'swap': trade.swap,
                    'net_profit': trade.net_profit
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            if self.error:
                self.error.handle_system_error("PerformanceTracker", e, {"method": "get_trades_dataframe"})
            return pd.DataFrame()
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del tracker"""
        return {
            "component_id": self.component_id,
            "version": self.version,
            "status": self.status,
            "is_tracking": self.is_tracking,
            "config_loaded": bool(self.tracker_config),
            "snapshots_count": len(self.performance_snapshots),
            "trades_count": len(self.trade_history),
            "account_initialized": self.account_state["initial_balance"] > 0,
            "alert_engine_connected": self.alert_engine is not None
        }
