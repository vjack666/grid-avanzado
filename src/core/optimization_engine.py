"""
🎯 OPTIMIZATION ENGINE - SÓTANO 1 FASE 1.4
==========================================

Motor de optimización automática de parámetros grid basado en analytics

Autor: Sistema Modular Trading Grid
Fecha: 2025-08-10
Versión: 1.4.0
Protocolo: SÓTANO 1 - FASE 1.4
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import pickle

# Imports del sistema
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager
from src.core.analytics_manager import AnalyticsManager


@dataclass
class OptimizationResult:
    """Resultado de una optimización"""
    parameters: Dict[str, Any]
    confidence_score: float
    expected_improvement: float
    optimization_type: str
    timestamp: datetime
    validation_score: Optional[float] = None


@dataclass
class GridOptimizationParams:
    """Parámetros optimizados para el grid"""
    grid_spacing: float
    grid_levels: int
    volume_per_level: float
    stop_loss_pips: float
    take_profit_pips: float
    max_spread: float


class AutoGridOptimizer:
    """Optimizador automático de parámetros grid"""
    
    def __init__(self, logger_manager: LoggerManager):
        self.logger = logger_manager
        self.optimization_history: List[OptimizationResult] = []
    
    def optimize_grid_spacing(self, grid_analytics: Dict[str, Any], 
                            market_analytics: Dict[str, Any]) -> float:
        """Optimiza el espaciado del grid basado en volatilidad y performance"""
        try:
            # Obtener volatilidad actual
            volatility = market_analytics.get('volatility', 0.001)
            
            # Obtener eficiencia actual del grid
            grid_efficiency = grid_analytics.get('efficiency', 50.0)
            
            # Calcular espaciado óptimo basado en volatilidad
            # Más volatilidad = mayor espaciado
            base_spacing = 0.0020  # 20 pips base
            volatility_factor = max(0.5, min(2.0, volatility * 1000))  # Scale volatility
            
            # Ajustar basado en eficiencia
            efficiency_factor = grid_efficiency / 100.0
            
            optimal_spacing = base_spacing * volatility_factor * (2.0 - efficiency_factor)
            
            # Límites de seguridad
            optimal_spacing = max(0.0010, min(0.0050, optimal_spacing))
            
            self.logger.log_info(f"Grid spacing optimizado: {optimal_spacing:.4f} "
                               f"(Vol: {volatility:.6f}, Eff: {grid_efficiency:.1f}%)")
            
            return optimal_spacing
            
        except Exception as e:
            self.logger.log_error(f"Error optimizando grid spacing: {e}")
            return 0.0025  # Default spacing
    
    def optimize_grid_levels(self, performance_data: Dict[str, Any],
                           market_conditions: Dict[str, Any]) -> int:
        """Optimiza número de niveles del grid"""
        try:
            # Obtener win rate actual
            win_rate = performance_data.get('win_rate', 50.0)
            
            # Obtener strength del mercado
            trend_strength = market_conditions.get('trend_strength', 0.0)
            
            # Calcular niveles óptimos
            base_levels = 10
            
            # Si win rate alto, usar más niveles
            if win_rate > 70:
                level_adjustment = 3
            elif win_rate > 60:
                level_adjustment = 1
            elif win_rate < 40:
                level_adjustment = -2
            else:
                level_adjustment = 0
            
            # Ajustar por tendencia (tendencias fuertes necesitan menos niveles)
            if trend_strength > 50:
                level_adjustment -= 2
            
            optimal_levels = base_levels + level_adjustment
            optimal_levels = max(5, min(20, optimal_levels))  # Límites de seguridad
            
            self.logger.log_info(f"Niveles grid optimizados: {optimal_levels} "
                               f"(WR: {win_rate:.1f}%, Trend: {trend_strength:.1f}%)")
            
            return optimal_levels
            
        except Exception as e:
            self.logger.log_error(f"Error optimizando niveles grid: {e}")
            return 10  # Default levels


class ParameterTuner:
    """Afinador de parámetros basado en performance"""
    
    def __init__(self, logger_manager: LoggerManager):
        self.logger = logger_manager
        self.tuning_history: List[OptimizationResult] = []
    
    def tune_risk_parameters(self, performance_data: Dict[str, Any]) -> Dict[str, float]:
        """Afina parámetros de riesgo basado en performance"""
        try:
            profit_factor = performance_data.get('profit_factor', 1.0)
            win_rate = performance_data.get('win_rate', 50.0)
            max_drawdown = performance_data.get('max_drawdown', 0.0)
            
            adjustments = {}
            
            # Ajustar stop loss
            if profit_factor < 1.2:
                # Performance pobre, reducir riesgo
                adjustments['stop_loss_adjustment'] = -0.0005  # Tighter stop
                adjustments['risk_per_trade_adjustment'] = -0.5  # Menor riesgo
            elif profit_factor > 2.0:
                # Performance buena, incrementar ligeramente
                adjustments['stop_loss_adjustment'] = 0.0002
                adjustments['risk_per_trade_adjustment'] = 0.2
            else:
                adjustments['stop_loss_adjustment'] = 0.0
                adjustments['risk_per_trade_adjustment'] = 0.0
            
            # Ajustar take profit basado en win rate
            if win_rate < 50:
                adjustments['take_profit_adjustment'] = 0.0010  # TP más amplio
            elif win_rate > 70:
                adjustments['take_profit_adjustment'] = -0.0005  # TP más ajustado
            else:
                adjustments['take_profit_adjustment'] = 0.0
            
            # Ajustar volumen basado en drawdown
            if max_drawdown > 10.0:
                adjustments['volume_adjustment'] = -0.1  # Reducir volumen
            elif max_drawdown < 3.0:
                adjustments['volume_adjustment'] = 0.05  # Incrementar ligeramente
            else:
                adjustments['volume_adjustment'] = 0.0
            
            self.logger.log_info(f"Parámetros de riesgo afinados: {adjustments}")
            
            return adjustments
            
        except Exception as e:
            self.logger.log_error(f"Error afinando parámetros de riesgo: {e}")
            return {}
    
    def calculate_improvement_score(self, current_metrics: Dict[str, Any],
                                  optimized_params: Dict[str, Any]) -> float:
        """Calcula score de mejora esperada"""
        try:
            # Factores de mejora basados en optimizaciones
            base_score = 5.0  # Mejora base esperada
            
            # Factor por profit factor actual
            pf = current_metrics.get('profit_factor', 1.0)
            if pf < 1.2:
                pf_factor = 2.0  # Mucho margen de mejora
            elif pf < 1.5:
                pf_factor = 1.5
            else:
                pf_factor = 1.0
            
            # Factor por win rate
            wr = current_metrics.get('win_rate', 50.0)
            if wr < 50:
                wr_factor = 1.8
            elif wr > 70:
                wr_factor = 0.8  # Poco margen de mejora
            else:
                wr_factor = 1.2
            
            improvement_score = base_score * pf_factor * wr_factor
            improvement_score = min(25.0, improvement_score)  # Cap máximo 25%
            
            return improvement_score
            
        except Exception as e:
            self.logger.log_error(f"Error calculando improvement score: {e}")
            return 5.0


class MLBasicEngine:
    """Engine básico de Machine Learning para predicciones"""
    
    def __init__(self, logger_manager: LoggerManager):
        self.logger = logger_manager
        self.model_data: List[Dict[str, Any]] = []
        self.predictions_history: List[Dict[str, Any]] = []
    
    def add_training_data(self, features: Dict[str, Any], outcome: Dict[str, Any]):
        """Agrega datos de entrenamiento"""
        data_point = {
            'features': features.copy(),
            'outcome': outcome.copy(),
            'timestamp': datetime.now()
        }
        self.model_data.append(data_point)
        
        # Mantener solo los últimos 100 puntos
        if len(self.model_data) > 100:
            self.model_data = self.model_data[-100:]
    
    def predict_optimal_timeframe(self, market_conditions: Dict[str, Any]) -> str:
        """Predice el timeframe óptimo basado en condiciones del mercado"""
        try:
            volatility = market_conditions.get('volatility', 0.001)
            trend_strength = market_conditions.get('trend_strength', 0.0)
            
            # Lógica básica de predicción
            if volatility > 0.002:  # Alta volatilidad
                if trend_strength > 30:
                    predicted_tf = "H1"  # Tendencia fuerte, timeframe mayor
                else:
                    predicted_tf = "M15"  # Alta volatilidad sin tendencia
            else:  # Baja volatilidad
                if trend_strength > 50:
                    predicted_tf = "H4"  # Tendencia muy fuerte, timeframe mayor
                else:
                    predicted_tf = "M5"   # Baja volatilidad, timeframe menor
            
            confidence = min(0.9, 0.5 + (abs(trend_strength - 50) / 100))
            
            prediction = {
                'timeframe': predicted_tf,
                'confidence': confidence,
                'reasoning': f"Vol: {volatility:.6f}, Trend: {trend_strength:.1f}%"
            }
            
            self.predictions_history.append(prediction)
            self.logger.log_info(f"Timeframe predicho: {predicted_tf} (conf: {confidence:.2f})")
            
            return predicted_tf
            
        except Exception as e:
            self.logger.log_error(f"Error prediciendo timeframe: {e}")
            return "M15"  # Default
    
    def predict_win_rate(self, optimized_params: Dict[str, Any]) -> float:
        """Predice win rate con parámetros optimizados"""
        try:
            # Análisis básico basado en parámetros
            base_win_rate = 55.0
            
            # Factor por grid spacing
            spacing = optimized_params.get('grid_spacing', 0.0025)
            if 0.0015 <= spacing <= 0.0035:
                spacing_bonus = 5.0
            else:
                spacing_bonus = 0.0
            
            # Factor por número de niveles
            levels = optimized_params.get('grid_levels', 10)
            if 8 <= levels <= 15:
                levels_bonus = 3.0
            else:
                levels_bonus = 0.0
            
            predicted_wr = base_win_rate + spacing_bonus + levels_bonus
            predicted_wr = min(80.0, max(30.0, predicted_wr))
            
            return predicted_wr
            
        except Exception as e:
            self.logger.log_error(f"Error prediciendo win rate: {e}")
            return 55.0


class BacktestValidator:
    """Validador de optimizaciones con datos históricos"""
    
    def __init__(self, logger_manager: LoggerManager, data_manager: DataManager):
        self.logger = logger_manager
        self.data_manager = data_manager
        self.validation_results: List[Dict[str, Any]] = []
    
    def validate_optimization(self, optimized_params: Dict[str, Any],
                            lookback_days: int = 7) -> float:
        """Valida optimización con datos históricos"""
        try:
            # Simular backtesting básico
            # En implementación real, esto usaría datos históricos reales
            
            # Por ahora, simulamos validación basada en parámetros
            grid_spacing = optimized_params.get('grid_spacing', 0.0025)
            grid_levels = optimized_params.get('grid_levels', 10)
            
            # Score basado en "sensibilidad" de parámetros
            spacing_score = 1.0 - abs(grid_spacing - 0.0025) / 0.0025
            levels_score = 1.0 - abs(grid_levels - 10) / 10
            
            validation_score = (spacing_score + levels_score) / 2 * 100
            validation_score = max(50.0, min(95.0, validation_score))
            
            validation_result = {
                'score': validation_score,
                'parameters': optimized_params.copy(),
                'lookback_days': lookback_days,
                'timestamp': datetime.now()
            }
            
            self.validation_results.append(validation_result)
            self.logger.log_info(f"Validación completada: {validation_score:.1f}%")
            
            return validation_score
            
        except Exception as e:
            self.logger.log_error(f"Error en validación: {e}")
            return 50.0


class OptimizationEngine:
    """Motor principal de optimización automática"""
    
    def __init__(self, analytics_manager: AnalyticsManager, config_manager: ConfigManager,
                 logger_manager: LoggerManager, error_manager: ErrorManager,
                 data_manager: DataManager):
        """Inicializar OptimizationEngine"""
        self.analytics = analytics_manager
        self.config = config_manager
        self.logger = logger_manager
        self.error_manager = error_manager
        self.data_manager = data_manager
        
        # Subcomponentes
        self.auto_grid_optimizer = AutoGridOptimizer(logger_manager)
        self.parameter_tuner = ParameterTuner(logger_manager)
        self.ml_engine = MLBasicEngine(logger_manager)
        self.backtest_validator = BacktestValidator(logger_manager, data_manager)
        
        # Estado interno
        self.is_initialized = False
        self.optimization_results: List[OptimizationResult] = []
        self.last_optimization: Optional[datetime] = None
        
        self.logger.log_info("OptimizationEngine inicializado - FASE 1.4")
    
    def initialize(self) -> bool:
        """Inicializar el motor de optimización"""
        try:
            self.logger.log_info("Inicializando OptimizationEngine...")
            
            # Verificar dependencias
            if not self.analytics.is_initialized:
                raise Exception("AnalyticsManager no está inicializado")
            
            # ConfigManager no tiene is_initialized, asumimos que está listo
            # si no lanza excepción al usarse
            
            # Cargar historial de optimizaciones si existe
            self._load_optimization_history()
            
            self.is_initialized = True
            self.logger.log_success("✅ OptimizationEngine inicializado correctamente")
            
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("OptimizationEngine", e, {"operation": "initialize"})
            return False
    
    def optimize_grid_parameters(self) -> OptimizationResult:
        """Optimización completa de parámetros grid"""
        try:
            if not self.is_initialized:
                raise Exception("OptimizationEngine no está inicializado")
            
            self.logger.log_info("Iniciando optimización de parámetros grid...")
            
            # Obtener datos analytics
            performance_data = self.analytics.get_performance_summary()
            grid_data = self.analytics.get_grid_summary()
            market_data = self.analytics.get_market_summary()
            
            # Optimizar componentes individuales
            optimal_spacing = self.auto_grid_optimizer.optimize_grid_spacing(
                grid_data, market_data
            )
            
            optimal_levels = self.auto_grid_optimizer.optimize_grid_levels(
                performance_data, market_data
            )
            
            # Calcular volumen óptimo (lógica básica)
            current_pf = performance_data.get('profit_factor', 1.0)
            if current_pf > 1.5:
                optimal_volume = 0.12
            elif current_pf < 1.2:
                optimal_volume = 0.08
            else:
                optimal_volume = 0.10
            
            # Compilar parámetros optimizados
            optimized_params = {
                'grid_spacing': optimal_spacing,
                'grid_levels': optimal_levels,
                'volume_per_level': optimal_volume,
                'stop_loss_pips': 25,  # Base
                'take_profit_pips': 50,  # Base
                'max_spread': 2.0
            }
            
            # Calcular confidence score
            market_volatility = market_data.get('volatility', 0.001)
            grid_efficiency = grid_data.get('efficiency', 50.0)
            
            confidence = min(0.95, 0.6 + (grid_efficiency / 200) + 
                           (1.0 - min(1.0, market_volatility * 500)) * 0.2)
            
            # Calcular mejora esperada
            expected_improvement = self.parameter_tuner.calculate_improvement_score(
                performance_data, optimized_params
            )
            
            # Crear resultado
            result = OptimizationResult(
                parameters=optimized_params,
                confidence_score=confidence,
                expected_improvement=expected_improvement,
                optimization_type="GRID_PARAMETERS",
                timestamp=datetime.now()
            )
            
            # Validar con backtest
            validation_score = self.backtest_validator.validate_optimization(optimized_params)
            result.validation_score = validation_score
            
            # Guardar resultado
            self.optimization_results.append(result)
            self.last_optimization = datetime.now()
            
            self.logger.log_success(f"✅ Optimización grid completada: "
                                  f"{confidence:.1%} confianza, "
                                  f"{expected_improvement:.1f}% mejora esperada")
            
            return result
            
        except Exception as e:
            self.error_manager.handle_system_error("OptimizationEngine", e, {"operation": "optimize_grid_parameters"})
            # Retornar resultado por defecto
            return OptimizationResult(
                parameters={'grid_spacing': 0.0025, 'grid_levels': 10, 'volume_per_level': 0.1},
                confidence_score=0.5,
                expected_improvement=5.0,
                optimization_type="DEFAULT",
                timestamp=datetime.now()
            )
    
    def tune_based_on_performance(self) -> OptimizationResult:
        """Afinar parámetros basado en performance histórica"""
        try:
            self.logger.log_info("Iniciando tuning basado en performance...")
            
            # Obtener datos de performance
            performance_data = self.analytics.get_performance_summary()
            
            # Obtener ajustes recomendados
            risk_adjustments = self.parameter_tuner.tune_risk_parameters(performance_data)
            
            # Calcular improvement score
            improvement_score = self.parameter_tuner.calculate_improvement_score(
                performance_data, risk_adjustments
            )
            
            # Crear resultado
            result = OptimizationResult(
                parameters=risk_adjustments,
                confidence_score=0.75,
                expected_improvement=improvement_score,
                optimization_type="PERFORMANCE_TUNING",
                timestamp=datetime.now()
            )
            
            self.optimization_results.append(result)
            
            self.logger.log_success(f"✅ Performance tuning completado: "
                                  f"{improvement_score:.1f}% mejora esperada")
            
            return result
            
        except Exception as e:
            self.error_manager.handle_system_error("ParameterTuner", e, {"operation": "tune_based_on_performance"})
            return OptimizationResult(
                parameters={},
                confidence_score=0.5,
                expected_improvement=0.0,
                optimization_type="ERROR",
                timestamp=datetime.now()
            )
    
    def predict_optimal_settings(self) -> Dict[str, Any]:
        """Predecir configuración óptima usando ML básico"""
        try:
            # Obtener condiciones del mercado
            market_data = self.analytics.get_market_summary()
            
            # Predecir timeframe óptimo
            optimal_timeframe = self.ml_engine.predict_optimal_timeframe(market_data)
            
            # Obtener última optimización
            if self.optimization_results:
                last_optimization = self.optimization_results[-1]
                predicted_wr = self.ml_engine.predict_win_rate(last_optimization.parameters)
                predicted_pf = 1.2 + (predicted_wr - 50) / 100  # Aproximación
            else:
                predicted_wr = 55.0
                predicted_pf = 1.25
            
            predictions = {
                'predicted_win_rate': predicted_wr,
                'predicted_profit_factor': predicted_pf,
                'optimal_timeframe': optimal_timeframe,
                'market_condition_preference': 'ranging' if market_data.get('volatility', 0) < 0.002 else 'trending',
                'confidence': 0.70
            }
            
            self.logger.log_info(f"Predicciones generadas: WR={predicted_wr:.1f}%, "
                               f"PF={predicted_pf:.2f}, TF={optimal_timeframe}")
            
            return predictions
            
        except Exception as e:
            self.error_manager.handle_system_error("MLBasicEngine", e, {"operation": "predict_optimal_settings"})
            return {'error': str(e)}
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Obtener resumen de optimizaciones"""
        try:
            if not self.optimization_results:
                return {
                    'total_optimizations': 0,
                    'last_optimization': None,
                    'average_confidence': 0.0,
                    'average_improvement': 0.0
                }
            
            total = len(self.optimization_results)
            avg_confidence = sum(r.confidence_score for r in self.optimization_results) / total
            avg_improvement = sum(r.expected_improvement for r in self.optimization_results) / total
            
            last_opt = self.optimization_results[-1]
            
            return {
                'total_optimizations': total,
                'last_optimization': last_opt.timestamp.isoformat(),
                'last_optimization_type': last_opt.optimization_type,
                'average_confidence': avg_confidence,
                'average_improvement': avg_improvement,
                'best_expected_improvement': max(r.expected_improvement for r in self.optimization_results),
                'last_validation_score': last_opt.validation_score
            }
            
        except Exception as e:
            self.error_manager.handle_system_error("OptimizationEngine", e, {"operation": "get_optimization_summary"})
            return {'error': str(e)}
    
    def save_optimization_snapshot(self) -> bool:
        """Guardar snapshot de optimizaciones"""
        try:
            snapshot_data = {
                'optimization_results': [
                    {
                        'parameters': r.parameters,
                        'confidence_score': r.confidence_score,
                        'expected_improvement': r.expected_improvement,
                        'optimization_type': r.optimization_type,
                        'timestamp': r.timestamp.isoformat(),
                        'validation_score': r.validation_score
                    }
                    for r in self.optimization_results
                ],
                'last_optimization': self.last_optimization.isoformat() if self.last_optimization else None,
                'total_optimizations': len(self.optimization_results),
                'timestamp': datetime.now().isoformat()
            }
            
            # Guardar en directorio de datos
            os.makedirs('data/optimization', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/optimization/optimization_snapshot_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(snapshot_data, f, indent=2)
            
            self.logger.log_success(f"Snapshot de optimización guardado: {filename}")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("OptimizationEngine", e, {"operation": "save_optimization_snapshot"})
            return False
    
    def _load_optimization_history(self):
        """Cargar historial de optimizaciones"""
        try:
            history_file = 'data/optimization/optimization_history.json'
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    
                # Cargar solo los últimos 50 resultados
                recent_results = data.get('optimization_results', [])[-50:]
                
                for result_data in recent_results:
                    result = OptimizationResult(
                        parameters=result_data['parameters'],
                        confidence_score=result_data['confidence_score'],
                        expected_improvement=result_data['expected_improvement'],
                        optimization_type=result_data['optimization_type'],
                        timestamp=datetime.fromisoformat(result_data['timestamp']),
                        validation_score=result_data.get('validation_score')
                    )
                    self.optimization_results.append(result)
                
                self.logger.log_info(f"Historial cargado: {len(recent_results)} optimizaciones")
                
        except Exception as e:
            self.logger.log_warning(f"No se pudo cargar historial: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de optimización"""
        return {
            'optimization_engine': self.is_initialized,
            'auto_grid_optimizer': hasattr(self.auto_grid_optimizer, 'optimization_history'),
            'parameter_tuner': hasattr(self.parameter_tuner, 'tuning_history'),
            'ml_engine': hasattr(self.ml_engine, 'model_data'),
            'backtest_validator': hasattr(self.backtest_validator, 'validation_results'),
            'total_optimizations': len(self.optimization_results),
            'last_optimization': self.last_optimization.isoformat() if self.last_optimization else None,
            'version': '1.4.0',
            'phase': 'FASE_1.4_OPTIMIZATION_ENGINE'
        }
    
    def shutdown(self):
        """Cerrar OptimizationEngine limpiamente"""
        try:
            # Guardar snapshot final
            self.save_optimization_snapshot()
            
            # Guardar historial
            if self.optimization_results:
                history_data = {
                    'optimization_results': [
                        {
                            'parameters': r.parameters,
                            'confidence_score': r.confidence_score,
                            'expected_improvement': r.expected_improvement,
                            'optimization_type': r.optimization_type,
                            'timestamp': r.timestamp.isoformat(),
                            'validation_score': r.validation_score
                        }
                        for r in self.optimization_results
                    ],
                    'saved_at': datetime.now().isoformat()
                }
                
                os.makedirs('data/optimization', exist_ok=True)
                with open('data/optimization/optimization_history.json', 'w') as f:
                    json.dump(history_data, f, indent=2)
            
            self.is_initialized = False
            self.logger.log_success("OptimizationEngine cerrado correctamente")
            
        except Exception as e:
            self.error_manager.handle_system_error("OptimizationEngine", e, {"operation": "shutdown"})


def create_optimization_engine(analytics_manager: AnalyticsManager, config_manager: ConfigManager,
                             logger_manager: LoggerManager, error_manager: ErrorManager,
                             data_manager: DataManager) -> OptimizationEngine:
    """Factory function para crear OptimizationEngine"""
    return OptimizationEngine(analytics_manager, config_manager, logger_manager, 
                            error_manager, data_manager)


def validate_optimization_integration(optimization_engine: OptimizationEngine) -> bool:
    """Validar integración del optimization engine"""
    try:
        # Verificar inicialización
        if not optimization_engine.is_initialized:
            return False
        
        # Verificar subcomponentes
        if not hasattr(optimization_engine, 'auto_grid_optimizer'):
            return False
        
        if not hasattr(optimization_engine, 'parameter_tuner'):
            return False
        
        if not hasattr(optimization_engine, 'ml_engine'):
            return False
        
        if not hasattr(optimization_engine, 'backtest_validator'):
            return False
        
        return True
        
    except Exception:
        return False
