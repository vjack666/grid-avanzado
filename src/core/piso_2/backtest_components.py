"""
PISO 2 - BACKTEST ENGINE v1.0.0 - PARTE 2
==========================================
Componentes adicionales: Analyzer, Optimizer y Reporter

AUTOR: Sistema Modular Trading Grid
FECHA: 2025-08-12
PROTOCOLO: PISO 2 - BACKTEST ENGINE
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from .backtest_engine import BacktestResult, BacktestConfig, BacktestTrade


class ResultsAnalyzer:
    """PUERTA-P2-ANALYZER: Analizador avanzado de resultados"""
    
    def __init__(self, config_manager, logger_manager, error_manager):
        self.config = config_manager
        self.logger = logger_manager
        self.error = error_manager
        self.component_id = "PUERTA-P2-ANALYZER"
        self.version = "v1.0.0"
    
    def analyze_comprehensive(self, result: BacktestResult) -> Dict[str, Any]:
        """Análisis comprehensivo de resultados"""
        try:
            analysis = {
                "performance_metrics": self._analyze_performance(result),
                "risk_metrics": self._analyze_risk(result),
                "trade_analysis": self._analyze_trades(result),
                "temporal_analysis": self._analyze_temporal_patterns(result),
                "distribution_analysis": self._analyze_pnl_distribution(result),
                "efficiency_metrics": self._analyze_efficiency(result),
                "market_conditions": self._analyze_market_conditions(result)
            }
            
            # Score general del backtest
            analysis["overall_score"] = self._calculate_overall_score(analysis)
            analysis["analysis_timestamp"] = datetime.now().isoformat()
            
            self.logger.log_success(f"Análisis completado - Score: {analysis['overall_score']:.1f}/100")
            
            return analysis
            
        except Exception as e:
            self.error.handle_system_error(
                "ANALYSIS_ERROR",
                f"Error en análisis de resultados: {str(e)}",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    def _analyze_performance(self, result: BacktestResult) -> Dict[str, float]:
        """Análisis de performance"""
        return {
            "total_return": ((result.final_balance - result.initial_balance) / result.initial_balance) * 100,
            "cagr": self._calculate_cagr(result),
            "win_rate": result.win_rate,
            "profit_factor": result.profit_factor,
            "sharpe_ratio": result.sharpe_ratio,
            "sortino_ratio": self._calculate_sortino_ratio(result),
            "calmar_ratio": self._calculate_calmar_ratio(result),
            "avg_win": result.gross_profit / result.winning_trades if result.winning_trades > 0 else 0,
            "avg_loss": result.gross_loss / result.losing_trades if result.losing_trades > 0 else 0,
            "expectancy": self._calculate_expectancy(result)
        }
    
    def _analyze_risk(self, result: BacktestResult) -> Dict[str, float]:
        """Análisis de riesgo"""
        return {
            "max_drawdown": result.max_drawdown,
            "max_drawdown_percent": result.max_drawdown_percent,
            "var_95": self._calculate_var(result, 0.95),
            "var_99": self._calculate_var(result, 0.99),
            "volatility": self._calculate_volatility(result),
            "downside_deviation": self._calculate_downside_deviation(result),
            "ulcer_index": self._calculate_ulcer_index(result),
            "recovery_factor": self._calculate_recovery_factor(result)
        }
    
    def _analyze_trades(self, result: BacktestResult) -> Dict[str, Any]:
        """Análisis de trades"""
        if not result.trades:
            return {}
        
        pnls = [t.net_pnl for t in result.trades]
        holding_times = [(t.close_time - t.open_time).total_seconds() / 3600 
                        for t in result.trades if t.close_time]
        
        return {
            "total_trades": result.total_trades,
            "winning_trades": result.winning_trades,
            "losing_trades": result.losing_trades,
            "max_consecutive_wins": result.max_consecutive_wins,
            "max_consecutive_losses": result.max_consecutive_losses,
            "largest_win": max(pnls) if pnls else 0,
            "largest_loss": min(pnls) if pnls else 0,
            "avg_holding_time": np.mean(holding_times) if holding_times else 0,
            "median_holding_time": np.median(holding_times) if holding_times else 0,
            "trades_per_day": self._calculate_trades_per_day(result),
            "win_loss_ratio": (result.gross_profit / result.winning_trades) / (result.gross_loss / result.losing_trades) 
                            if result.losing_trades > 0 and result.winning_trades > 0 else 0
        }
    
    def _analyze_temporal_patterns(self, result: BacktestResult) -> Dict[str, Any]:
        """Análisis de patrones temporales"""
        if not result.trades:
            return {}
        
        # Análisis por hora del día
        hourly_pnl = {}
        for trade in result.trades:
            hour = trade.open_time.hour
            if hour not in hourly_pnl:
                hourly_pnl[hour] = []
            hourly_pnl[hour].append(trade.net_pnl)
        
        # Análisis por día de la semana
        daily_pnl = {}
        for trade in result.trades:
            day = trade.open_time.weekday()  # 0=Monday, 6=Sunday
            if day not in daily_pnl:
                daily_pnl[day] = []
            daily_pnl[day].append(trade.net_pnl)
        
        return {
            "best_hour": max(hourly_pnl.items(), key=lambda x: sum(x[1]))[0] if hourly_pnl else None,
            "worst_hour": min(hourly_pnl.items(), key=lambda x: sum(x[1]))[0] if hourly_pnl else None,
            "best_day": max(daily_pnl.items(), key=lambda x: sum(x[1]))[0] if daily_pnl else None,
            "worst_day": min(daily_pnl.items(), key=lambda x: sum(x[1]))[0] if daily_pnl else None,
            "hourly_distribution": {str(k): sum(v) for k, v in hourly_pnl.items()},
            "daily_distribution": {str(k): sum(v) for k, v in daily_pnl.items()}
        }
    
    def _analyze_pnl_distribution(self, result: BacktestResult) -> Dict[str, float]:
        """Análisis de distribución de P&L"""
        if not result.trades:
            return {}
        
        pnls = [t.net_pnl for t in result.trades]
        
        return {
            "mean": np.mean(pnls),
            "median": np.median(pnls),
            "std": np.std(pnls),
            "skewness": self._calculate_skewness(pnls),
            "kurtosis": self._calculate_kurtosis(pnls),
            "q25": np.percentile(pnls, 25),
            "q75": np.percentile(pnls, 75),
            "iqr": np.percentile(pnls, 75) - np.percentile(pnls, 25)
        }
    
    def _analyze_efficiency(self, result: BacktestResult) -> Dict[str, float]:
        """Análisis de eficiencia"""
        if not result.equity_curve or len(result.equity_curve) < 2:
            return {}
        
        # Calcular retornos diarios
        returns = []
        for i in range(1, len(result.equity_curve)):
            ret = (result.equity_curve[i] - result.equity_curve[i-1]) / result.equity_curve[i-1]
            returns.append(ret)
        
        return {
            "information_ratio": np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0,
            "sterling_ratio": self._calculate_sterling_ratio(result),
            "burke_ratio": self._calculate_burke_ratio(result),
            "tail_ratio": self._calculate_tail_ratio(returns) if returns else 0,
            "gain_to_pain_ratio": self._calculate_gain_to_pain_ratio(returns) if returns else 0
        }
    
    def _analyze_market_conditions(self, result: BacktestResult) -> Dict[str, Any]:
        """Análisis de condiciones de mercado durante el backtest"""
        return {
            "backtest_period_days": (result.backtest_end - result.backtest_start).days,
            "market_exposure": len([t for t in result.trades if t.status == "CLOSED"]) / 
                             max(1, (result.backtest_end - result.backtest_start).days) * 100,
            "avg_trades_per_week": result.total_trades / max(1, (result.backtest_end - result.backtest_start).days / 7),
            "strategy_type": result.config.strategy_type
        }
    
    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> float:
        """Calcular score general del backtest (0-100)"""
        try:
            performance = analysis.get("performance_metrics", {})
            risk = analysis.get("risk_metrics", {})
            
            # Componentes del score
            components = {
                "profit_factor": min(100, max(0, (performance.get("profit_factor", 0) - 1) * 50)),
                "win_rate": min(100, max(0, performance.get("win_rate", 0))),
                "sharpe_ratio": min(100, max(0, performance.get("sharpe_ratio", 0) * 25 + 50)),
                "drawdown": min(100, max(0, 100 - risk.get("max_drawdown_percent", 100))),
                "expectancy": min(100, max(0, performance.get("expectancy", 0) * 10 + 50))
            }
            
            # Pesos
            weights = {
                "profit_factor": 0.25,
                "win_rate": 0.20,
                "sharpe_ratio": 0.25,
                "drawdown": 0.20,
                "expectancy": 0.10
            }
            
            score = sum(components[k] * weights[k] for k in components.keys())
            return max(0, min(100, score))
            
        except Exception:
            return 0.0
    
    # Métodos auxiliares para cálculos
    def _calculate_cagr(self, result: BacktestResult) -> float:
        """Calcular CAGR (Compound Annual Growth Rate)"""
        if result.initial_balance <= 0:
            return 0.0
        
        years = (result.backtest_end - result.backtest_start).days / 365.25
        if years <= 0:
            return 0.0
        
        return ((result.final_balance / result.initial_balance) ** (1/years) - 1) * 100
    
    def _calculate_sortino_ratio(self, result: BacktestResult) -> float:
        """Calcular Sortino Ratio"""
        if not result.trades:
            return 0.0
        
        returns = [t.net_pnl for t in result.trades]
        downside_returns = [r for r in returns if r < 0]
        
        if len(downside_returns) == 0:
            return float('inf') if np.mean(returns) > 0 else 0
        
        downside_std = np.std(downside_returns)
        return np.mean(returns) / downside_std if downside_std > 0 else 0
    
    def _calculate_calmar_ratio(self, result: BacktestResult) -> float:
        """Calcular Calmar Ratio"""
        cagr = self._calculate_cagr(result)
        max_dd = result.max_drawdown_percent
        return cagr / max_dd if max_dd > 0 else 0
    
    def _calculate_expectancy(self, result: BacktestResult) -> float:
        """Calcular expectancy por trade"""
        if result.total_trades == 0:
            return 0.0
        
        avg_win = result.gross_profit / result.winning_trades if result.winning_trades > 0 else 0
        avg_loss = result.gross_loss / result.losing_trades if result.losing_trades > 0 else 0
        win_rate = result.win_rate / 100
        
        return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    
    def _calculate_var(self, result: BacktestResult, confidence: float) -> float:
        """Calcular Value at Risk"""
        if not result.trades:
            return 0.0
        
        returns = [t.net_pnl for t in result.trades]
        return np.percentile(returns, (1 - confidence) * 100)
    
    def _calculate_volatility(self, result: BacktestResult) -> float:
        """Calcular volatilidad de equity curve"""
        if len(result.equity_curve) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(result.equity_curve)):
            ret = (result.equity_curve[i] - result.equity_curve[i-1]) / result.equity_curve[i-1]
            returns.append(ret)
        
        return np.std(returns) * 100
    
    def _calculate_downside_deviation(self, result: BacktestResult) -> float:
        """Calcular downside deviation"""
        if len(result.equity_curve) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(result.equity_curve)):
            ret = (result.equity_curve[i] - result.equity_curve[i-1]) / result.equity_curve[i-1]
            returns.append(ret)
        
        downside_returns = [r for r in returns if r < 0]
        return np.std(downside_returns) * 100 if downside_returns else 0
    
    def _calculate_ulcer_index(self, result: BacktestResult) -> float:
        """Calcular Ulcer Index"""
        if not result.equity_curve:
            return 0.0
        
        drawdowns = []
        peak = result.equity_curve[0]
        
        for equity in result.equity_curve:
            if equity > peak:
                peak = equity
            dd_percent = ((peak - equity) / peak) * 100 if peak > 0 else 0
            drawdowns.append(dd_percent ** 2)
        
        return np.sqrt(np.mean(drawdowns)) if drawdowns else 0
    
    def _calculate_recovery_factor(self, result: BacktestResult) -> float:
        """Calcular Recovery Factor"""
        if result.max_drawdown == 0:
            return float('inf') if result.net_profit > 0 else 0
        
        return result.net_profit / result.max_drawdown
    
    def _calculate_trades_per_day(self, result: BacktestResult) -> float:
        """Calcular trades por día"""
        days = (result.backtest_end - result.backtest_start).days
        return result.total_trades / max(1, days)
    
    def _calculate_skewness(self, data: List[float]) -> float:
        """Calcular skewness"""
        if len(data) < 3:
            return 0.0
        
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        
        skew = np.mean([(x - mean) ** 3 for x in data]) / (std ** 3)
        return skew
    
    def _calculate_kurtosis(self, data: List[float]) -> float:
        """Calcular kurtosis"""
        if len(data) < 4:
            return 0.0
        
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        
        kurt = np.mean([(x - mean) ** 4 for x in data]) / (std ** 4) - 3
        return kurt
    
    def _calculate_sterling_ratio(self, result: BacktestResult) -> float:
        """Calcular Sterling Ratio"""
        if result.max_drawdown_percent == 0:
            return float('inf') if result.net_profit > 0 else 0
        
        return self._calculate_cagr(result) / result.max_drawdown_percent
    
    def _calculate_burke_ratio(self, result: BacktestResult) -> float:
        """Calcular Burke Ratio"""
        if not result.equity_curve:
            return 0.0
        
        drawdowns = []
        peak = result.equity_curve[0]
        
        for equity in result.equity_curve:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0
            if dd > 0:
                drawdowns.append(dd)
        
        if not drawdowns:
            return float('inf') if result.net_profit > 0 else 0
        
        burke_denominator = np.sqrt(np.sum([dd ** 2 for dd in drawdowns]))
        return self._calculate_cagr(result) / (burke_denominator * 100) if burke_denominator > 0 else 0
    
    def _calculate_tail_ratio(self, returns: List[float]) -> float:
        """Calcular Tail Ratio"""
        if len(returns) < 20:
            return 0.0
        
        top_5_percent = np.percentile(returns, 95)
        bottom_5_percent = np.percentile(returns, 5)
        
        return abs(top_5_percent / bottom_5_percent) if bottom_5_percent != 0 else 0
    
    def _calculate_gain_to_pain_ratio(self, returns: List[float]) -> float:
        """Calcular Gain to Pain Ratio"""
        if not returns:
            return 0.0
        
        gains = sum([r for r in returns if r > 0])
        pains = abs(sum([r for r in returns if r < 0]))
        
        return gains / pains if pains > 0 else float('inf') if gains > 0 else 0


class ParameterOptimizer:
    """PUERTA-P2-OPTIMIZER: Optimizador de parámetros"""
    
    def __init__(self, config_manager, logger_manager, error_manager, backtest_executor):
        self.config = config_manager
        self.logger = logger_manager
        self.error = error_manager
        self.backtest_executor = backtest_executor
        self.component_id = "PUERTA-P2-OPTIMIZER"
        self.version = "v1.0.0"
    
    def optimize_parameters(self, base_config: BacktestConfig, 
                          parameter_ranges: Dict[str, List], 
                          optimization_metric: str = "sharpe_ratio") -> Dict[str, Any]:
        """Optimizar parámetros usando grid search"""
        try:
            self.logger.log_info(f"Iniciando optimización de parámetros - Métrica: {optimization_metric}")
            
            # Generar combinaciones de parámetros
            parameter_combinations = self._generate_parameter_combinations(parameter_ranges)
            
            results = []
            best_score = float('-inf')
            best_config = None
            best_result = None
            
            total_combinations = len(parameter_combinations)
            self.logger.log_info(f"Evaluando {total_combinations} combinaciones de parámetros")
            
            for i, params in enumerate(parameter_combinations):
                if i % 10 == 0:  # Log progreso cada 10 combinaciones
                    self.logger.log_info(f"Progreso: {i}/{total_combinations} ({i/total_combinations*100:.1f}%)")
                
                # Crear configuración con nuevos parámetros
                test_config = self._create_config_with_params(base_config, params)
                
                # Ejecutar backtest
                backtest_result = self.backtest_executor.run_backtest(test_config)
                
                # Calcular métrica objetivo
                score = self._calculate_optimization_score(backtest_result, optimization_metric)
                
                # Guardar resultado
                result_data = {
                    "parameters": params,
                    "score": score,
                    "net_profit": backtest_result.net_profit,
                    "win_rate": backtest_result.win_rate,
                    "max_drawdown": backtest_result.max_drawdown_percent,
                    "profit_factor": backtest_result.profit_factor,
                    "total_trades": backtest_result.total_trades
                }
                results.append(result_data)
                
                # Actualizar mejor resultado
                if score > best_score:
                    best_score = score
                    best_config = test_config
                    best_result = backtest_result
            
            # Analizar resultados
            optimization_analysis = self._analyze_optimization_results(results, parameter_ranges)
            
            optimization_summary = {
                "best_config": best_config.__dict__ if best_config else None,
                "best_result": best_result.__dict__ if best_result else None,
                "best_score": best_score,
                "optimization_metric": optimization_metric,
                "total_combinations": total_combinations,
                "results": results,
                "analysis": optimization_analysis,
                "optimization_timestamp": datetime.now().isoformat()
            }
            
            self.logger.log_success(f"Optimización completada - Mejor score: {best_score:.4f}")
            
            return optimization_summary
            
        except Exception as e:
            self.error.handle_system_error(
                "OPTIMIZATION_ERROR",
                f"Error en optimización de parámetros: {str(e)}",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    def _generate_parameter_combinations(self, parameter_ranges: Dict[str, List]) -> List[Dict]:
        """Generar todas las combinaciones de parámetros"""
        import itertools
        
        keys = list(parameter_ranges.keys())
        values = list(parameter_ranges.values())
        
        combinations = []
        for combination in itertools.product(*values):
            combinations.append(dict(zip(keys, combination)))
        
        return combinations
    
    def _create_config_with_params(self, base_config: BacktestConfig, params: Dict) -> BacktestConfig:
        """Crear nueva configuración con parámetros específicos"""
        # Copiar configuración base
        new_config = BacktestConfig(**base_config.__dict__)
        
        # Aplicar nuevos parámetros
        for param_name, param_value in params.items():
            if hasattr(new_config, param_name):
                setattr(new_config, param_name, param_value)
        
        return new_config
    
    def _calculate_optimization_score(self, result: BacktestResult, metric: str) -> float:
        """Calcular score para optimización"""
        if metric == "sharpe_ratio":
            return result.sharpe_ratio
        elif metric == "profit_factor":
            return result.profit_factor
        elif metric == "net_profit":
            return result.net_profit
        elif metric == "win_rate":
            return result.win_rate
        elif metric == "calmar_ratio":
            cagr = self._calculate_cagr(result)
            return cagr / result.max_drawdown_percent if result.max_drawdown_percent > 0 else 0
        elif metric == "custom_score":
            # Score personalizado que combina múltiples métricas
            profit_score = min(100, max(0, (result.profit_factor - 1) * 50))
            drawdown_score = min(100, max(0, 100 - result.max_drawdown_percent))
            sharpe_score = min(100, max(0, result.sharpe_ratio * 25 + 50))
            return (profit_score * 0.4 + drawdown_score * 0.3 + sharpe_score * 0.3) / 100
        else:
            return result.net_profit  # Default
    
    def _calculate_cagr(self, result: BacktestResult) -> float:
        """Calcular CAGR"""
        if result.initial_balance <= 0:
            return 0.0
        
        years = (result.backtest_end - result.backtest_start).days / 365.25
        if years <= 0:
            return 0.0
        
        return ((result.final_balance / result.initial_balance) ** (1/years) - 1) * 100
    
    def _analyze_optimization_results(self, results: List[Dict], parameter_ranges: Dict) -> Dict:
        """Analizar resultados de optimización"""
        if not results:
            return {}
        
        # Estadísticas generales
        scores = [r["score"] for r in results]
        
        analysis = {
            "score_statistics": {
                "mean": np.mean(scores),
                "median": np.median(scores),
                "std": np.std(scores),
                "min": min(scores),
                "max": max(scores),
                "q25": np.percentile(scores, 25),
                "q75": np.percentile(scores, 75)
            },
            "parameter_sensitivity": {},
            "top_10_results": sorted(results, key=lambda x: x["score"], reverse=True)[:10]
        }
        
        # Análisis de sensibilidad por parámetro
        for param_name in parameter_ranges.keys():
            param_scores = {}
            for result in results:
                param_value = result["parameters"][param_name]
                if param_value not in param_scores:
                    param_scores[param_value] = []
                param_scores[param_value].append(result["score"])
            
            # Calcular estadísticas por valor de parámetro
            param_stats = {}
            for value, scores_list in param_scores.items():
                param_stats[str(value)] = {
                    "mean_score": np.mean(scores_list),
                    "median_score": np.median(scores_list),
                    "count": len(scores_list)
                }
            
            analysis["parameter_sensitivity"][param_name] = param_stats
        
        return analysis


class BacktestReporter:
    """PUERTA-P2-REPORTER: Generador de reportes"""
    
    def __init__(self, config_manager, logger_manager, error_manager):
        self.config = config_manager
        self.logger = logger_manager
        self.error = error_manager
        self.component_id = "PUERTA-P2-REPORTER"
        self.version = "v1.0.0"
    
    def generate_comprehensive_report(self, result: BacktestResult, 
                                    analysis: Dict[str, Any] = None,
                                    optimization_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generar reporte comprehensivo"""
        try:
            report = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "component": self.component_id,
                    "version": self.version,
                    "report_type": "COMPREHENSIVE_BACKTEST"
                },
                "executive_summary": self._generate_executive_summary(result, analysis),
                "backtest_configuration": result.config.__dict__,
                "performance_summary": self._generate_performance_summary(result),
                "trade_analysis": self._generate_trade_analysis(result),
                "risk_analysis": self._generate_risk_analysis(result, analysis),
                "charts_data": self._prepare_charts_data(result),
                "recommendations": self._generate_recommendations(result, analysis),
                "detailed_trades": [trade.__dict__ for trade in result.trades[:100]]  # Limitar a 100 trades
            }
            
            if optimization_data:
                report["optimization_analysis"] = optimization_data
            
            # Guardar reporte
            self._save_report(report, result.config.symbol, result.config.strategy_type)
            
            self.logger.log_success(f"Reporte generado - {result.total_trades} trades analizados")
            
            return report
            
        except Exception as e:
            self.error.handle_system_error(
                "REPORT_GENERATION_ERROR",
                f"Error generando reporte: {str(e)}",
                {"error": str(e)}
            )
            return {"error": str(e)}
    
    def _generate_executive_summary(self, result: BacktestResult, analysis: Dict = None) -> Dict:
        """Generar resumen ejecutivo"""
        return {
            "strategy": result.config.strategy_type,
            "symbol": result.config.symbol,
            "timeframe": result.config.timeframe,
            "period": f"{result.backtest_start.strftime('%Y-%m-%d')} to {result.backtest_end.strftime('%Y-%m-%d')}",
            "total_return": f"{((result.final_balance - result.initial_balance) / result.initial_balance * 100):.2f}%",
            "net_profit": f"${result.net_profit:.2f}",
            "total_trades": result.total_trades,
            "win_rate": f"{result.win_rate:.1f}%",
            "profit_factor": f"{result.profit_factor:.2f}",
            "max_drawdown": f"{result.max_drawdown_percent:.2f}%",
            "sharpe_ratio": f"{result.sharpe_ratio:.2f}",
            "overall_score": f"{analysis.get('overall_score', 0):.1f}/100" if analysis else "N/A"
        }
    
    def _generate_performance_summary(self, result: BacktestResult) -> Dict:
        """Generar resumen de performance"""
        return {
            "returns": {
                "initial_balance": f"${result.initial_balance:,.2f}",
                "final_balance": f"${result.final_balance:,.2f}",
                "net_profit": f"${result.net_profit:,.2f}",
                "gross_profit": f"${result.gross_profit:,.2f}",
                "gross_loss": f"${result.gross_loss:,.2f}",
                "total_return_percent": f"{((result.final_balance - result.initial_balance) / result.initial_balance * 100):.2f}%"
            },
            "ratios": {
                "profit_factor": f"{result.profit_factor:.2f}",
                "sharpe_ratio": f"{result.sharpe_ratio:.2f}",
                "win_rate": f"{result.win_rate:.1f}%",
                "avg_win": f"${(result.gross_profit / max(1, result.winning_trades)):,.2f}",
                "avg_loss": f"${(result.gross_loss / max(1, result.losing_trades)):,.2f}"
            }
        }
    
    def _generate_trade_analysis(self, result: BacktestResult) -> Dict:
        """Generar análisis de trades"""
        return {
            "trade_counts": {
                "total_trades": result.total_trades,
                "winning_trades": result.winning_trades,
                "losing_trades": result.losing_trades,
                "max_consecutive_wins": result.max_consecutive_wins,
                "max_consecutive_losses": result.max_consecutive_losses
            },
            "trade_details": {
                "largest_win": f"${max([t.net_pnl for t in result.trades]) if result.trades else 0:.2f}",
                "largest_loss": f"${min([t.net_pnl for t in result.trades]) if result.trades else 0:.2f}",
                "avg_trade_pnl": f"${(result.net_profit / max(1, result.total_trades)):.2f}",
                "trades_per_day": f"{result.total_trades / max(1, (result.backtest_end - result.backtest_start).days):.1f}"
            }
        }
    
    def _generate_risk_analysis(self, result: BacktestResult, analysis: Dict = None) -> Dict:
        """Generar análisis de riesgo"""
        risk_data = {
            "drawdown": {
                "max_drawdown": f"${result.max_drawdown:.2f}",
                "max_drawdown_percent": f"{result.max_drawdown_percent:.2f}%"
            }
        }
        
        if analysis and "risk_metrics" in analysis:
            risk_metrics = analysis["risk_metrics"]
            risk_data["advanced_metrics"] = {
                "var_95": f"${risk_metrics.get('var_95', 0):.2f}",
                "volatility": f"{risk_metrics.get('volatility', 0):.2f}%",
                "ulcer_index": f"{risk_metrics.get('ulcer_index', 0):.2f}",
                "recovery_factor": f"{risk_metrics.get('recovery_factor', 0):.2f}"
            }
        
        return risk_data
    
    def _prepare_charts_data(self, result: BacktestResult) -> Dict:
        """Preparar datos para gráficos"""
        charts_data = {}
        
        # Equity curve
        if result.equity_curve and result.timestamps:
            charts_data["equity_curve"] = {
                "timestamps": [ts.isoformat() for ts in result.timestamps],
                "equity": result.equity_curve,
                "balance": result.balance_curve
            }
        
        # Distribución de P&L
        if result.trades:
            pnls = [t.net_pnl for t in result.trades]
            charts_data["pnl_distribution"] = {
                "pnls": pnls,
                "bins": 20
            }
        
        # Trades por día de la semana
        if result.trades:
            daily_trades = {i: 0 for i in range(7)}  # 0=Monday, 6=Sunday
            for trade in result.trades:
                day = trade.open_time.weekday()
                daily_trades[day] += 1
            
            charts_data["trades_by_weekday"] = {
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "counts": [daily_trades[i] for i in range(7)]
            }
        
        return charts_data
    
    def _generate_recommendations(self, result: BacktestResult, analysis: Dict = None) -> List[str]:
        """Generar recomendaciones basadas en resultados"""
        recommendations = []
        
        # Recomendaciones basadas en win rate
        if result.win_rate < 40:
            recommendations.append("⚠️ Win rate bajo (<40%). Considerar ajustar criterios de entrada o salida.")
        elif result.win_rate > 70:
            recommendations.append("✅ Win rate excelente (>70%). Estrategia muestra buena precisión.")
        
        # Recomendaciones basadas en profit factor
        if result.profit_factor < 1.2:
            recommendations.append("⚠️ Profit factor bajo (<1.2). Revisar gestión de riesgo y tamaño de posiciones.")
        elif result.profit_factor > 2.0:
            recommendations.append("✅ Profit factor excelente (>2.0). Estrategia muestra buena eficiencia.")
        
        # Recomendaciones basadas en drawdown
        if result.max_drawdown_percent > 20:
            recommendations.append("🔴 Drawdown máximo alto (>20%). Implementar mejor gestión de riesgo.")
        elif result.max_drawdown_percent < 10:
            recommendations.append("✅ Drawdown máximo controlado (<10%). Buen control de riesgo.")
        
        # Recomendaciones basadas en número de trades
        if result.total_trades < 30:
            recommendations.append("ℹ️ Pocos trades para muestra estadística (<30). Considerar período más largo.")
        elif result.total_trades > 500:
            recommendations.append("✅ Muestra estadística robusta (>500 trades).")
        
        # Recomendaciones basadas en Sharpe ratio
        if result.sharpe_ratio < 0.5:
            recommendations.append("⚠️ Sharpe ratio bajo (<0.5). Revisar relación riesgo-retorno.")
        elif result.sharpe_ratio > 1.5:
            recommendations.append("✅ Sharpe ratio excelente (>1.5). Buena relación riesgo-retorno.")
        
        if not recommendations:
            recommendations.append("📊 Estrategia muestra performance balanceada. Continuar monitoreo.")
        
        return recommendations
    
    def _save_report(self, report: Dict, symbol: str, strategy: str):
        """Guardar reporte en archivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_report_{symbol}_{strategy}_{timestamp}.json"
            
            reports_dir = Path(self.config.get_project_root()) / "analytics" / "backtest_reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = reports_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.log_info(f"Reporte guardado: {filepath}")
            
        except Exception as e:
            self.logger.log_error(f"Error guardando reporte: {e}")
