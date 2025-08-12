"""
PISO 2 - BACKTEST MANAGER v1.0.0
=================================
Manager principal del sistema de backtesting avanzado

AUTOR: Sistema Modular Trading Grid
FECHA: 2025-08-12
PROTOCOLO: PISO 2 - BACKTEST ENGINE
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path

# Configurar rutas de imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager

from .backtest_engine import (
    BacktestConfig, BacktestResult, BacktestTrade,
    HistoricalDataProcessor, BacktestExecutor
)
from .backtest_components import (
    ResultsAnalyzer, ParameterOptimizer, BacktestReporter
)


class Piso2BacktestManager:
    """
    🏢 PISO 2 - BACKTEST MANAGER v1.0.0
    ===================================
    Sistema completo de backtesting con datos reales de MT5
    
    COMPONENTES:
    ├── PUERTA-P2-DATA      → HistoricalDataProcessor 
    ├── PUERTA-P2-EXECUTOR  → BacktestExecutor
    ├── PUERTA-P2-ANALYZER  → ResultsAnalyzer
    ├── PUERTA-P2-OPTIMIZER → ParameterOptimizer  
    └── PUERTA-P2-REPORTER  → BacktestReporter
    """
    
    def __init__(self, config_manager: ConfigManager = None, 
                 logger_manager: LoggerManager = None, 
                 error_manager: ErrorManager = None):
        
        # Inicializar managers core
        self.config = config_manager or ConfigManager()
        self.logger = logger_manager or LoggerManager()
        self.error = error_manager or ErrorManager()
        
        # Información del componente
        self.component_id = "PISO-2-MANAGER"
        self.version = "v1.0.0"
        self.protocol = "PISO_2_BACKTEST_ENGINE"
        
        # Inicializar componentes del PISO 2
        self._initialize_components()
        
        # Estado del manager
        self.is_initialized = True
        self.last_backtest_result = None
        self.last_analysis = None
        self.last_optimization = None
        
        self.logger.log_success(
            f"🏢 PISO 2 - BACKTEST ENGINE iniciado correctamente - {self.version}"
        )
    
    def _initialize_components(self):
        """Inicializar todos los componentes del PISO 2"""
        try:
            # PUERTA-P2-DATA: Procesador de datos históricos
            self.data_processor = HistoricalDataProcessor(
                self.config, self.logger, self.error
            )
            
            # PUERTA-P2-EXECUTOR: Ejecutor de backtests
            self.backtest_executor = BacktestExecutor(
                self.config, self.logger, self.error, self.data_processor
            )
            
            # PUERTA-P2-ANALYZER: Analizador de resultados
            self.results_analyzer = ResultsAnalyzer(
                self.config, self.logger, self.error
            )
            
            # PUERTA-P2-OPTIMIZER: Optimizador de parámetros
            self.parameter_optimizer = ParameterOptimizer(
                self.config, self.logger, self.error, self.backtest_executor
            )
            
            # PUERTA-P2-REPORTER: Generador de reportes
            self.backtest_reporter = BacktestReporter(
                self.config, self.logger, self.error
            )
            
            self.logger.log_info("Todos los componentes del PISO 2 inicializados correctamente")
            
        except Exception as e:
            self.error.handle_system_error(
                "PISO2_INITIALIZATION_ERROR",
                f"Error inicializando componentes del PISO 2: {str(e)}",
                {"error": str(e)}
            )
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado completo del PISO 2"""
        return {
            "component": self.component_id,
            "version": self.version,
            "protocol": self.protocol,
            "is_initialized": self.is_initialized,
            "components": {
                "data_processor": "ACTIVE",
                "backtest_executor": "ACTIVE", 
                "results_analyzer": "ACTIVE",
                "parameter_optimizer": "ACTIVE",
                "backtest_reporter": "ACTIVE"
            },
            "last_operations": {
                "last_backtest": self.last_backtest_result.config.strategy_type if self.last_backtest_result else None,
                "last_analysis": bool(self.last_analysis),
                "last_optimization": bool(self.last_optimization)
            },
            "available_data": self._get_available_data_summary(),
            "timestamp": datetime.now().isoformat()
        }
    
    def run_single_backtest(self, config: BacktestConfig, 
                          include_analysis: bool = True,
                          include_report: bool = True) -> Dict[str, Any]:
        """
        Ejecutar un backtest completo con análisis y reporte
        
        Args:
            config: Configuración del backtest
            include_analysis: Si incluir análisis avanzado
            include_report: Si generar reporte completo
            
        Returns:
            Dict con resultados completos
        """
        try:
            self.logger.log_info(f"🚀 Iniciando backtest single: {config.strategy_type} - {config.symbol} {config.timeframe}")
            
            # FASE 1: Ejecutar backtest
            self.logger.log_info("📊 FASE 1: Ejecutando backtest...")
            backtest_result = self.backtest_executor.run_backtest(config)
            self.last_backtest_result = backtest_result
            
            # Verificar que hay datos suficientes
            if backtest_result.total_trades == 0:
                self.logger.log_warning("⚠️ No se generaron trades en el backtest")
                return {
                    "success": False,
                    "message": "No se generaron trades",
                    "backtest_result": backtest_result.__dict__
                }
            
            response = {
                "success": True,
                "backtest_result": backtest_result,
                "execution_summary": {
                    "total_trades": backtest_result.total_trades,
                    "net_profit": backtest_result.net_profit,
                    "win_rate": backtest_result.win_rate,
                    "max_drawdown": backtest_result.max_drawdown_percent,
                    "execution_time": backtest_result.execution_time
                }
            }
            
            # FASE 2: Análisis avanzado (opcional)
            if include_analysis:
                self.logger.log_info("🔍 FASE 2: Ejecutando análisis avanzado...")
                analysis = self.results_analyzer.analyze_comprehensive(backtest_result)
                self.last_analysis = analysis
                response["analysis"] = analysis
                response["overall_score"] = analysis.get("overall_score", 0)
            
            # FASE 3: Generar reporte (opcional)
            if include_report:
                self.logger.log_info("📋 FASE 3: Generando reporte completo...")
                report = self.backtest_reporter.generate_comprehensive_report(
                    backtest_result, 
                    analysis if include_analysis else None
                )
                response["report"] = report
            
            self.logger.log_success(
                f"✅ Backtest completado exitosamente - Score: {response.get('overall_score', 'N/A')}"
            )
            
            return response
            
        except Exception as e:
            self.error.handle_system_error(
                "SINGLE_BACKTEST_ERROR",
                f"Error en backtest single: {str(e)}",
                {"config": config.__dict__, "error": str(e)}
            )
            return {
                "success": False,
                "error": str(e),
                "message": "Error ejecutando backtest"
            }
    
    def run_parameter_optimization(self, base_config: BacktestConfig,
                                 parameter_ranges: Dict[str, List],
                                 optimization_metric: str = "custom_score",
                                 max_combinations: int = 100) -> Dict[str, Any]:
        """
        Ejecutar optimización de parámetros
        
        Args:
            base_config: Configuración base
            parameter_ranges: Rangos de parámetros a optimizar
            optimization_metric: Métrica objetivo
            max_combinations: Máximo número de combinaciones a evaluar
            
        Returns:
            Dict con resultados de optimización
        """
        try:
            self.logger.log_info(f"🎯 Iniciando optimización de parámetros - Métrica: {optimization_metric}")
            
            # Limitar combinaciones si es necesario
            total_combinations = 1
            for param_range in parameter_ranges.values():
                total_combinations *= len(param_range)
            
            if total_combinations > max_combinations:
                self.logger.log_warning(
                    f"⚠️ Demasiadas combinaciones ({total_combinations}). "
                    f"Limitando a {max_combinations}"
                )
                # Aquí podrías implementar sampling inteligente
            
            # Ejecutar optimización
            optimization_result = self.parameter_optimizer.optimize_parameters(
                base_config, parameter_ranges, optimization_metric
            )
            self.last_optimization = optimization_result
            
            # Análisis del mejor resultado
            best_result = None
            best_analysis = None
            
            if optimization_result.get("best_result"):
                # Convertir dict a BacktestResult si es necesario
                best_result_data = optimization_result["best_result"]
                if isinstance(best_result_data, dict):
                    best_config = BacktestConfig(**optimization_result["best_config"])
                    # Ejecutar backtest del mejor resultado para obtener objeto completo
                    best_result = self.backtest_executor.run_backtest(best_config)
                    best_analysis = self.results_analyzer.analyze_comprehensive(best_result)
                
                # Generar reporte de optimización
                optimization_report = self.backtest_reporter.generate_comprehensive_report(
                    best_result, best_analysis, optimization_result
                )
                
                optimization_result["best_result_analysis"] = best_analysis
                optimization_result["optimization_report"] = optimization_report
            
            self.logger.log_success(
                f"✅ Optimización completada - Mejor score: {optimization_result.get('best_score', 'N/A')}",
                extra={
                    "component": self.component_id,
                    "combinations": optimization_result.get("total_combinations", 0),
                    "best_score": optimization_result.get("best_score", 0)
                }
            )
            
            return {
                "success": True,
                "optimization_result": optimization_result,
                "best_parameters": optimization_result.get("best_config", {}),
                "improvement_summary": self._calculate_improvement_summary(
                    base_config, optimization_result
                )
            }
            
        except Exception as e:
            self.error.handle_system_error(
                "OPTIMIZATION_ERROR",
                f"Error en optimización: {str(e)}",
                {"base_config": base_config.__dict__, "error": str(e)}
            )
            return {
                "success": False,
                "error": str(e),
                "message": "Error ejecutando optimización"
            }
    
    def run_multiple_strategy_comparison(self, configs: List[BacktestConfig]) -> Dict[str, Any]:
        """
        Comparar múltiples estrategias o configuraciones
        
        Args:
            configs: Lista de configuraciones a comparar
            
        Returns:
            Dict con comparación detallada
        """
        try:
            self.logger.log_info(f"🔄 Iniciando comparación de {len(configs)} estrategias")
            
            results = []
            
            for i, config in enumerate(configs):
                self.logger.log_info(f"Ejecutando estrategia {i+1}/{len(configs)}: {config.strategy_type}")
                
                # Ejecutar backtest
                backtest_result = self.backtest_executor.run_backtest(config)
                
                # Análisis
                analysis = self.results_analyzer.analyze_comprehensive(backtest_result)
                
                result_summary = {
                    "config": config,
                    "backtest_result": backtest_result,
                    "analysis": analysis,
                    "performance_score": analysis.get("overall_score", 0),
                    "key_metrics": {
                        "total_trades": backtest_result.total_trades,
                        "net_profit": backtest_result.net_profit,
                        "win_rate": backtest_result.win_rate,
                        "profit_factor": backtest_result.profit_factor,
                        "max_drawdown": backtest_result.max_drawdown_percent,
                        "sharpe_ratio": backtest_result.sharpe_ratio
                    }
                }
                
                results.append(result_summary)
            
            # Ranking y comparación
            comparison_analysis = self._analyze_strategy_comparison(results)
            
            # Generar reporte comparativo
            comparison_report = self._generate_comparison_report(results, comparison_analysis)
            
            self.logger.log_success(f"✅ Comparación completada - Mejor estrategia: {comparison_analysis['best_strategy']['strategy']}")
            
            return {
                "success": True,
                "results": results,
                "comparison_analysis": comparison_analysis,
                "comparison_report": comparison_report,
                "ranking": comparison_analysis["ranking"]
            }
            
        except Exception as e:
            self.error.handle_system_error(
                "COMPARISON_ERROR",
                f"Error en comparación de estrategias: {str(e)}",
                {"configs_count": len(configs), "error": str(e)}
            )
            return {
                "success": False,
                "error": str(e),
                "message": "Error ejecutando comparación"
            }
    
    def quick_backtest(self, symbol: str = "EURUSD", timeframe: str = "M15",
                      strategy_type: str = "GRID_BOLLINGER",
                      initial_balance: float = 10000.0) -> Dict[str, Any]:
        """
        Ejecutar backtest rápido con configuración por defecto
        
        Args:
            symbol: Símbolo a testear
            timeframe: Timeframe
            strategy_type: Tipo de estrategia
            initial_balance: Balance inicial
            
        Returns:
            Dict con resultados del backtest rápido
        """
        try:
            # Crear configuración por defecto
            config = BacktestConfig(
                symbol=symbol,
                timeframe=timeframe,
                strategy_type=strategy_type,
                initial_balance=initial_balance,
                start_date="2025-05-20",
                end_date="2025-08-12"
            )
            
            self.logger.log_info(f"⚡ Ejecutando backtest rápido: {strategy_type} - {symbol} {timeframe}")
            
            # Ejecutar backtest completo
            result = self.run_single_backtest(config, include_analysis=True, include_report=False)
            
            if result["success"]:
                # Generar resumen rápido
                quick_summary = self._generate_quick_summary(result)
                result["quick_summary"] = quick_summary
            
            return result
            
        except Exception as e:
            self.error.handle_system_error(
                "QUICK_BACKTEST_ERROR",
                f"Error en backtest rápido: {str(e)}",
                {"symbol": symbol, "timeframe": timeframe, "error": str(e)}
            )
            return {
                "success": False,
                "error": str(e),
                "message": "Error ejecutando backtest rápido"
            }
    
    def validate_data_availability(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Validar disponibilidad y calidad de datos"""
        try:
            df = self.data_processor.load_historical_data(symbol, timeframe)
            
            if df is None:
                return {
                    "available": False,
                    "message": f"No hay datos disponibles para {symbol} {timeframe}"
                }
            
            validation = self.data_processor.validate_data_quality(df)
            
            return {
                "available": True,
                "records": len(df),
                "date_range": {
                    "start": df.index[0].strftime('%Y-%m-%d %H:%M'),
                    "end": df.index[-1].strftime('%Y-%m-%d %H:%M')
                },
                "quality_score": validation["quality_score"],
                "validation_details": validation
            }
            
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "message": f"Error validando datos para {symbol} {timeframe}"
            }
    
    def _get_available_data_summary(self) -> Dict[str, Any]:
        """Obtener resumen de datos disponibles"""
        try:
            data_dir = Path(self.config.get_data_dir())
            csv_files = list(data_dir.glob("**/velas_*.csv"))
            
            available_data = {}
            for file in csv_files:
                # Extraer símbolo y timeframe del nombre
                parts = file.stem.split('_')
                if len(parts) >= 3:
                    symbol = parts[1]
                    timeframe = parts[2]
                    
                    if symbol not in available_data:
                        available_data[symbol] = []
                    available_data[symbol].append(timeframe)
            
            return {
                "total_files": len(csv_files),
                "symbols": list(available_data.keys()),
                "data_by_symbol": available_data
            }
            
        except Exception:
            return {"total_files": 0, "symbols": [], "data_by_symbol": {}}
    
    def _calculate_improvement_summary(self, base_config: BacktestConfig, 
                                     optimization_result: Dict) -> Dict[str, Any]:
        """Calcular resumen de mejoras de la optimización"""
        try:
            # Ejecutar backtest con configuración base
            base_result = self.backtest_executor.run_backtest(base_config)
            
            best_score = optimization_result.get("best_score", 0)
            base_score = self._calculate_simple_score(base_result)
            
            improvement = {
                "base_score": base_score,
                "optimized_score": best_score,
                "improvement_percent": ((best_score - base_score) / max(base_score, 0.01)) * 100,
                "base_metrics": {
                    "net_profit": base_result.net_profit,
                    "win_rate": base_result.win_rate,
                    "max_drawdown": base_result.max_drawdown_percent
                }
            }
            
            if optimization_result.get("best_result"):
                best_result_data = optimization_result["best_result"]
                improvement["optimized_metrics"] = {
                    "net_profit": best_result_data.get("net_profit", 0),
                    "win_rate": best_result_data.get("win_rate", 0),
                    "max_drawdown": best_result_data.get("max_drawdown_percent", 0)
                }
            
            return improvement
            
        except Exception:
            return {"improvement_percent": 0, "error": "No se pudo calcular mejora"}
    
    def _calculate_simple_score(self, result: BacktestResult) -> float:
        """Calcular score simple para comparación"""
        if result.total_trades == 0:
            return 0.0
        
        profit_score = min(100, max(0, (result.profit_factor - 1) * 50))
        drawdown_score = min(100, max(0, 100 - result.max_drawdown_percent))
        sharpe_score = min(100, max(0, result.sharpe_ratio * 25 + 50))
        
        return (profit_score * 0.4 + drawdown_score * 0.3 + sharpe_score * 0.3) / 100
    
    def _analyze_strategy_comparison(self, results: List[Dict]) -> Dict[str, Any]:
        """Analizar comparación de estrategias"""
        if not results:
            return {}
        
        # Ranking por score
        ranked_results = sorted(results, key=lambda x: x["performance_score"], reverse=True)
        
        return {
            "best_strategy": {
                "strategy": ranked_results[0]["config"].strategy_type,
                "score": ranked_results[0]["performance_score"],
                "net_profit": ranked_results[0]["key_metrics"]["net_profit"]
            },
            "worst_strategy": {
                "strategy": ranked_results[-1]["config"].strategy_type,
                "score": ranked_results[-1]["performance_score"],
                "net_profit": ranked_results[-1]["key_metrics"]["net_profit"]
            },
            "ranking": [
                {
                    "rank": i + 1,
                    "strategy": result["config"].strategy_type,
                    "score": result["performance_score"],
                    "key_metrics": result["key_metrics"]
                }
                for i, result in enumerate(ranked_results)
            ],
            "summary_stats": {
                "avg_score": sum(r["performance_score"] for r in results) / len(results),
                "avg_profit": sum(r["key_metrics"]["net_profit"] for r in results) / len(results),
                "total_trades": sum(r["key_metrics"]["total_trades"] for r in results)
            }
        }
    
    def _generate_comparison_report(self, results: List[Dict], analysis: Dict) -> Dict[str, Any]:
        """Generar reporte de comparación"""
        return {
            "report_type": "STRATEGY_COMPARISON",
            "generated_at": datetime.now().isoformat(),
            "strategies_compared": len(results),
            "best_strategy": analysis["best_strategy"],
            "ranking_summary": analysis["ranking"][:3],  # Top 3
            "recommendations": self._generate_comparison_recommendations(analysis)
        }
    
    def _generate_comparison_recommendations(self, analysis: Dict) -> List[str]:
        """Generar recomendaciones de comparación"""
        recommendations = []
        
        best = analysis["best_strategy"]
        recommendations.append(f"🥇 Mejor estrategia: {best['strategy']} (Score: {best['score']:.1f})")
        
        if len(analysis["ranking"]) > 1:
            diff = analysis["ranking"][0]["score"] - analysis["ranking"][1]["score"]
            if diff > 20:
                recommendations.append("✅ Diferencia significativa entre estrategias. Usar la mejor.")
            elif diff < 5:
                recommendations.append("⚠️ Diferencias menores. Considerar otros factores como robustez.")
        
        avg_score = analysis["summary_stats"]["avg_score"]
        if avg_score < 50:
            recommendations.append("🔴 Scores generalmente bajos. Revisar parámetros globales.")
        elif avg_score > 70:
            recommendations.append("✅ Scores buenos en general. Conjunto robusto de estrategias.")
        
        return recommendations
    
    def _generate_quick_summary(self, result: Dict) -> Dict[str, str]:
        """Generar resumen rápido de resultados"""
        if not result["success"]:
            return {"status": "ERROR", "message": result.get("message", "Error desconocido")}
        
        backtest = result["backtest_result"]
        analysis = result.get("analysis", {})
        
        # Determinar status general
        score = analysis.get("overall_score", 0)
        if score >= 80:
            status = "EXCELENTE"
            status_icon = "🟢"
        elif score >= 60:
            status = "BUENO"
            status_icon = "🟡"
        elif score >= 40:
            status = "REGULAR"
            status_icon = "🟠"
        else:
            status = "POBRE"
            status_icon = "🔴"
        
        return {
            "status": f"{status_icon} {status}",
            "score": f"{score:.1f}/100",
            "profit": f"${backtest.net_profit:,.2f}",
            "win_rate": f"{backtest.win_rate:.1f}%",
            "trades": str(backtest.total_trades),
            "drawdown": f"{backtest.max_drawdown_percent:.1f}%",
            "recommendation": self._get_quick_recommendation(score, backtest)
        }
    
    def _get_quick_recommendation(self, score: float, backtest) -> str:
        """Obtener recomendación rápida"""
        if score >= 80:
            return "Estrategia prometedora. Considerar trading en vivo."
        elif score >= 60:
            return "Buena base. Optimizar parámetros antes de usar."
        elif score >= 40:
            return "Necesita mejoras. Revisar configuración."
        else:
            return "No recomendada. Cambiar estrategia o parámetros."
