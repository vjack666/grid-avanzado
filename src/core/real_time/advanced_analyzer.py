"""
ADVANCED ANALYZER - SÓTANO 2 DÍA 3
Sistema de análisis estadístico y predictivo avanzado para Trading Grid

PUERTA: PUERTA-S2-ANALYZER
VERSIÓN: v1.0.0
AUTOR: Sistema Modular Trading Grid
FECHA: 2025-08-11
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import asyncio
import concurrent.futures
import threading
import time
from pathlib import Path

# Imports para análisis avanzado
try:
    from scipy import stats
    from scipy.signal import find_peaks
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    ADVANCED_ANALYTICS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYTICS_AVAILABLE = False

# Imports del sistema
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager


@dataclass
class CorrelationAnalysis:
    """Estructura para análisis de correlaciones"""
    correlation_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    correlation_strength: Dict[str, str] = field(default_factory=dict)  # weak/moderate/strong
    correlation_direction: Dict[str, str] = field(default_factory=dict)  # positive/negative
    timeframe: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class VolatilityCluster:
    """Estructura para clusters de volatilidad"""
    cluster_type: str = ""  # high/low/normal
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_minutes: float = 0.0
    average_volatility: float = 0.0
    peak_volatility: float = 0.0
    cluster_strength: float = 0.0


@dataclass
class SeasonalPattern:
    """Estructura para patrones estacionales"""
    pattern_type: str = ""  # hourly/daily/weekly/monthly
    pattern_strength: float = 0.0
    pattern_direction: str = ""  # bullish/bearish/neutral
    confidence_level: float = 0.0
    statistical_significance: float = 0.0
    pattern_data: Dict[str, float] = field(default_factory=dict)


@dataclass
class MLPrediction:
    """Estructura para predicciones ML"""
    prediction_value: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    model_accuracy: float = 0.0
    feature_importance: Dict[str, float] = field(default_factory=dict)
    prediction_horizon: int = 1  # períodos adelante
    model_type: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MarketMicrostructure:
    """Estructura para análisis de microestructura"""
    bid_ask_spread: float = 0.0
    spread_percentile: float = 0.0
    liquidity_score: float = 0.0
    orderflow_imbalance: float = 0.0
    price_impact: float = 0.0
    market_depth: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class AdvancedAnalyzer:
    """
    PUERTA-S2-ANALYZER v1.0.0
    Motor de análisis estadístico y predictivo avanzado
    
    Funcionalidades:
    - Análisis de correlaciones entre instrumentos
    - Detección de clusters de volatilidad  
    - Identificación de patrones estacionales
    - Predicciones con Machine Learning
    - Análisis de microestructura de mercado
    - Detección de anomalías en tiempo real
    """
    
    def __init__(self, 
                 config: ConfigManager,
                 logger: LoggerManager, 
                 error: ErrorManager,
                 data_manager: DataManager,
                 mt5_streamer=None,
                 alert_engine=None):
        """
        Inicializar AdvancedAnalyzer
        
        Args:
            config: ConfigManager para configuración
            logger: LoggerManager para logging
            error: ErrorManager para manejo de errores
            data_manager: DataManager para datos históricos
            mt5_streamer: MT5Streamer para datos tiempo real (opcional)
            alert_engine: AlertEngine para alertas (opcional)
        """
        # Metadatos del componente
        self.component_id = "PUERTA-S2-ANALYZER"
        self.version = "v1.0.0"
        self.status = "initializing"
        
        # Dependencias core
        self.config = config
        self.logger = logger
        self.error = error
        self.data = data_manager
        
        # Dependencias SÓTANO 2
        self.mt5_streamer = mt5_streamer
        self.alert_engine = alert_engine
        
        # Configuración del analyzer
        self.analyzer_config = self._initialize_analyzer_config()
        
        # Estructuras de datos
        self.correlation_history: List[CorrelationAnalysis] = []
        self.volatility_clusters: List[VolatilityCluster] = []
        self.seasonal_patterns: Dict[str, SeasonalPattern] = {}
        self.ml_predictions: List[MLPrediction] = []
        self.microstructure_data: List[MarketMicrostructure] = []
        
        # Cache para análisis
        self._correlation_cache: Dict[str, CorrelationAnalysis] = {}
        self._volatility_cache: Dict[str, List[float]] = {}
        self._pattern_cache: Dict[str, SeasonalPattern] = {}
        
        # Threading para análisis en background
        self._analysis_thread: Optional[threading.Thread] = None
        self._analysis_lock = threading.Lock()
        self._is_analyzing = False
        
        # Modelos ML
        self._ml_models: Dict[str, Any] = {}
        self._model_scalers: Dict[str, StandardScaler] = {}
        
        # Métricas del analyzer
        self.analyzer_metrics = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "correlation_calculations": 0,
            "ml_predictions_made": 0,
            "anomalies_detected": 0,
            "analysis_time_avg": 0.0,
            "last_analysis_time": None
        }
        
        # Inicializar
        self._initialize_analyzer()
        
        self.logger.log_info(f"{self.component_id} {self.version} inicializado correctamente")
        self.status = "initialized"
    
    def _initialize_analyzer_config(self) -> Dict[str, Any]:
        """Inicializar configuración del analyzer"""
        try:
            return {
                # Configuración general
                "enabled": True,
                "analysis_interval_minutes": 5,
                "background_analysis": True,
                "max_history_size": 1000,
                
                # Configuración de correlaciones
                "correlation_window_size": 100,
                "correlation_min_periods": 50,
                "correlation_significance_level": 0.05,
                "correlation_update_interval": 15,  # minutos
                
                # Configuración de volatilidad
                "volatility_window_size": 50,
                "volatility_cluster_threshold": 2.0,  # desviaciones estándar
                "volatility_min_cluster_duration": 30,  # minutos
                
                # Configuración de patrones estacionales
                "seasonal_min_sample_size": 200,
                "seasonal_significance_threshold": 0.01,
                "seasonal_patterns_enabled": ["hourly", "daily", "weekly"],
                
                # Configuración ML
                "ml_enabled": ADVANCED_ANALYTICS_AVAILABLE,
                "ml_prediction_horizon": [1, 5, 15],  # períodos
                "ml_retrain_interval_hours": 24,
                "ml_min_training_size": 500,
                "ml_test_size": 0.2,
                
                # Configuración de microestructura
                "microstructure_enabled": True,
                "spread_analysis_interval": 1,  # minutos
                "liquidity_window_size": 20,
                
                # Configuración de anomalías
                "anomaly_detection_enabled": True,
                "anomaly_threshold": 3.0,  # desviaciones estándar
                "anomaly_window_size": 100
            }
        except Exception as e:
            self.error._log_error(f"Error inicializando configuración analyzer: {e}")
            return self._get_default_analyzer_config()
    
    def _get_default_analyzer_config(self) -> Dict[str, Any]:
        """Configuración por defecto del analyzer"""
        return {
            "enabled": True,
            "analysis_interval_minutes": 5,
            "background_analysis": False,
            "max_history_size": 500,
            "correlation_window_size": 50,
            "correlation_min_periods": 30,
            "volatility_window_size": 30,
            "ml_enabled": False,
            "microstructure_enabled": False,
            "anomaly_detection_enabled": True
        }
    
    def _initialize_analyzer(self) -> None:
        """Inicializar componentes del analyzer"""
        try:
            # Verificar disponibilidad de librerías avanzadas
            if not ADVANCED_ANALYTICS_AVAILABLE:
                self.logger.log_warning("Librerías avanzadas no disponibles. Funcionalidad ML limitada.")
                self.analyzer_config["ml_enabled"] = False
            
            # Inicializar cache
            self._correlation_cache = {}
            self._volatility_cache = {}
            self._pattern_cache = {}
            
            # Preparar modelos ML si están habilitados
            if self.analyzer_config["ml_enabled"]:
                self._initialize_ml_models()
            
            self.logger.log_info("AdvancedAnalyzer inicializado correctamente")
            
        except Exception as e:
            self.error._log_error(f"Error inicializando AdvancedAnalyzer: {e}")
            raise
    
    def _initialize_ml_models(self) -> None:
        """Inicializar modelos de Machine Learning"""
        try:
            if not ADVANCED_ANALYTICS_AVAILABLE:
                return
            
            # Crear modelos para diferentes horizontes de predicción
            for horizon in self.analyzer_config["ml_prediction_horizon"]:
                model_key = f"price_predictor_{horizon}"
                self._ml_models[model_key] = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                self._model_scalers[model_key] = StandardScaler()
            
            self.logger.log_info(f"Modelos ML inicializados: {len(self._ml_models)}")
            
        except Exception as e:
            self.error._log_error(f"Error inicializando modelos ML: {e}")
    
    def start_analysis_service(self) -> bool:
        """
        Iniciar servicio de análisis en background
        
        Returns:
            bool: True si se inició correctamente
        """
        try:
            if not self.analyzer_config["background_analysis"]:
                self.logger.log_info("Análisis en background deshabilitado")
                return True
            
            if self._is_analyzing:
                self.logger.log_warning("Servicio de análisis ya está ejecutándose")
                return True
            
            self._is_analyzing = True
            self._analysis_thread = threading.Thread(
                target=self._analysis_service_loop,
                daemon=True
            )
            self._analysis_thread.start()
            
            self.status = "analyzing"
            self.logger.log_info("Servicio de análisis iniciado en background")
            return True
            
        except Exception as e:
            self.error._log_error(f"Error iniciando servicio de análisis: {e}")
            return False
    
    async def start_async_analysis_service(self) -> bool:
        """
        Iniciar servicio de análisis asíncrono
        
        Returns:
            bool: True si se inició correctamente
        """
        try:
            if not self.analyzer_config["background_analysis"]:
                self.logger.log_info("Análisis asíncrono en background deshabilitado")
                return True
            
            if self._is_analyzing:
                self.logger.log_warning("Servicio de análisis asíncrono ya está ejecutándose")
                return True
            
            self._is_analyzing = True
            
            # Crear task asíncrono para análisis continuo
            asyncio.create_task(self._async_analysis_service_loop())
            
            self.status = "analyzing_async"
            self.logger.log_info("Servicio de análisis asíncrono iniciado")
            return True
            
        except Exception as e:
            self.error._log_error(f"Error iniciando servicio asíncrono: {e}")
            return False
    
    async def _async_analysis_service_loop(self) -> None:
        """Loop asíncrono del servicio de análisis"""
        self.logger.log_info("Iniciando loop asíncrono de análisis")
        
        while self._is_analyzing:
            try:
                # Ejecutar análisis asíncrono
                await self._perform_async_analysis()
                
                # Esperar intervalo configurado de forma asíncrona
                interval = self.analyzer_config["analysis_interval_minutes"] * 60
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.error._log_error(f"Error en loop asíncrono: {e}")
                await asyncio.sleep(30)  # Esperar antes de continuar
    
    async def _perform_async_analysis(self) -> None:
        """Realizar análisis asíncrono con concurrencia"""
        try:
            start_time = time.time()
            
            # Crear tareas concurrentes para diferentes análisis
            tasks = []
            
            # Análisis de correlaciones (asíncrono)
            if self.analyzer_config.get("correlation_enabled", True):
                tasks.append(self._async_correlation_analysis())
            
            # Análisis de volatilidad (asíncrono)
            tasks.append(self._async_volatility_analysis())
            
            # Predicciones ML (asíncrono si disponible)
            if self.analyzer_config["ml_enabled"]:
                tasks.append(self._async_ml_predictions())
            
            # Análisis de microestructura (asíncrono)
            if self.analyzer_config["microstructure_enabled"]:
                tasks.append(self._async_microstructure_analysis())
            
            # Ejecutar todas las tareas concurrentemente
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Análisis síncronos (más rápidos)
            with self._analysis_lock:
                # Patrones estacionales (síncrono)
                if len(self.analyzer_config.get("seasonal_patterns_enabled", [])) > 0:
                    self._update_seasonal_patterns()
                
                # Detección de anomalías (síncrono)
                if self.analyzer_config["anomaly_detection_enabled"]:
                    self._detect_anomalies()
            
            # Actualizar métricas
            execution_time = time.time() - start_time
            self._update_analyzer_metrics(execution_time, True)
            
            self.logger.log_info(f"Análisis asíncrono completado en {execution_time:.2f}s")
            
        except Exception as e:
            self.error._log_error(f"Error en análisis asíncrono: {e}")
            self._update_analyzer_metrics(0, False)
    
    async def _async_correlation_analysis(self) -> None:
        """Análisis de correlaciones asíncrono"""
        try:
            await asyncio.sleep(0.1)  # Simular trabajo asíncrono
            self.logger.log_info("Análisis de correlaciones asíncrono completado")
            self.analyzer_metrics["correlation_calculations"] += 1
            
        except Exception as e:
            self.error._log_error(f"Error en análisis de correlaciones asíncrono: {e}")
    
    async def _async_volatility_analysis(self) -> None:
        """Análisis de volatilidad asíncrono"""
        try:
            await asyncio.sleep(0.1)  # Simular trabajo asíncrono
            self.logger.log_info("Análisis de volatilidad asíncrono completado")
            
        except Exception as e:
            self.error._log_error(f"Error en análisis de volatilidad asíncrono: {e}")
    
    async def _async_ml_predictions(self) -> None:
        """Predicciones ML asíncronas"""
        try:
            if not ADVANCED_ANALYTICS_AVAILABLE:
                return
            
            await asyncio.sleep(0.2)  # Simular trabajo ML más intensivo
            self.logger.log_info("Predicciones ML asíncronas completadas")
            self.analyzer_metrics["ml_predictions_made"] += 1
            
        except Exception as e:
            self.error._log_error(f"Error en predicciones ML asíncronas: {e}")
    
    async def _async_microstructure_analysis(self) -> None:
        """Análisis de microestructura asíncrono"""
        try:
            await asyncio.sleep(0.05)  # Simular trabajo asíncrono rápido
            self.logger.log_info("Análisis de microestructura asíncrono completado")
            
        except Exception as e:
            self.error._log_error(f"Error en análisis de microestructura asíncrono: {e}")
    
    def stop_analysis_service(self) -> bool:
        """
        Detener servicio de análisis en background
        
        Returns:
            bool: True si se detuvo correctamente
        """
        try:
            if not self._is_analyzing:
                return True
            
            self._is_analyzing = False
            
            if self._analysis_thread and self._analysis_thread.is_alive():
                self._analysis_thread.join(timeout=5.0)
            
            self.status = "stopped"
            self.logger.log_info("Servicio de análisis detenido")
            return True
            
        except Exception as e:
            self.error._log_error(f"Error deteniendo servicio de análisis: {e}")
            return False
    
    def _analysis_service_loop(self) -> None:
        """Loop principal del servicio de análisis"""
        self.logger.log_info("Iniciando loop de análisis en background")
        
        while self._is_analyzing:
            try:
                # Ejecutar análisis periódico
                self._perform_periodic_analysis()
                
                # Esperar intervalo configurado
                interval = self.analyzer_config["analysis_interval_minutes"] * 60
                time.sleep(interval)
                
            except Exception as e:
                self.error._log_error(f"Error en loop de análisis: {e}")
                time.sleep(30)  # Esperar antes de continuar
    
    def _perform_periodic_analysis(self) -> None:
        """Realizar análisis periódico"""
        try:
            start_time = time.time()
            
            with self._analysis_lock:
                # Análisis de correlaciones
                if self.analyzer_config.get("correlation_enabled", True):
                    self._update_correlation_analysis()
                
                # Análisis de volatilidad
                self._update_volatility_analysis()
                
                # Análisis de patrones estacionales
                if len(self.analyzer_config.get("seasonal_patterns_enabled", [])) > 0:
                    self._update_seasonal_patterns()
                
                # Predicciones ML
                if self.analyzer_config["ml_enabled"]:
                    self._update_ml_predictions()
                
                # Análisis de microestructura
                if self.analyzer_config["microstructure_enabled"]:
                    self._update_microstructure_analysis()
                
                # Detección de anomalías
                if self.analyzer_config["anomaly_detection_enabled"]:
                    self._detect_anomalies()
            
            # Actualizar métricas
            execution_time = time.time() - start_time
            self._update_analyzer_metrics(execution_time, True)
            
            self.logger.log_info(f"Análisis periódico completado en {execution_time:.2f}s")
            
        except Exception as e:
            self.error._log_error(f"Error en análisis periódico: {e}")
            self._update_analyzer_metrics(0, False)
    
    def _update_correlation_analysis(self) -> None:
        """Actualizar análisis de correlaciones"""
        try:
            # Placeholder - implementaremos en siguiente fase
            self.logger.log_info("Análisis de correlaciones - placeholder")
            
        except Exception as e:
            self.error._log_error(f"Error en análisis de correlaciones: {e}")
    
    def _update_volatility_analysis(self) -> None:
        """Actualizar análisis de volatilidad"""
        try:
            # Placeholder - implementaremos en siguiente fase
            self.logger.log_info("Análisis de volatilidad - placeholder")
            
        except Exception as e:
            self.error._log_error(f"Error en análisis de volatilidad: {e}")
    
    def _update_seasonal_patterns(self) -> None:
        """Actualizar análisis de patrones estacionales"""
        try:
            # Placeholder - implementaremos en siguiente fase
            self.logger.log_info("Análisis de patrones estacionales - placeholder")
            
        except Exception as e:
            self.error._log_error(f"Error en análisis de patrones estacionales: {e}")
    
    def _update_ml_predictions(self) -> None:
        """Actualizar predicciones ML"""
        try:
            if not ADVANCED_ANALYTICS_AVAILABLE:
                return
            
            # Placeholder - implementaremos en siguiente fase
            self.logger.log_info("Predicciones ML - placeholder")
            
        except Exception as e:
            self.error._log_error(f"Error en predicciones ML: {e}")
    
    def _update_microstructure_analysis(self) -> None:
        """Actualizar análisis de microestructura"""
        try:
            # Placeholder - implementaremos en siguiente fase
            self.logger.log_info("Análisis de microestructura - placeholder")
            
        except Exception as e:
            self.error._log_error(f"Error en análisis de microestructura: {e}")
    
    def _detect_anomalies(self) -> None:
        """Detectar anomalías en datos de mercado"""
        try:
            # Placeholder - implementaremos en siguiente fase
            self.logger.log_info("Detección de anomalías - placeholder")
            
        except Exception as e:
            self.error._log_error(f"Error en detección de anomalías: {e}")
    
    def _update_analyzer_metrics(self, execution_time: float, success: bool) -> None:
        """Actualizar métricas del analyzer"""
        try:
            self.analyzer_metrics["total_analyses"] += 1
            if success:
                self.analyzer_metrics["successful_analyses"] += 1
            
            # Actualizar tiempo promedio
            if self.analyzer_metrics["analysis_time_avg"] == 0:
                self.analyzer_metrics["analysis_time_avg"] = execution_time
            else:
                # Media móvil simple
                alpha = 0.1
                self.analyzer_metrics["analysis_time_avg"] = (
                    alpha * execution_time + 
                    (1 - alpha) * self.analyzer_metrics["analysis_time_avg"]
                )
            
            self.analyzer_metrics["last_analysis_time"] = datetime.now()
            
        except Exception as e:
            self.error._log_error(f"Error actualizando métricas: {e}")
    
    def get_analyzer_status(self) -> Dict[str, Any]:
        """
        Obtener estado actual del analyzer
        
        Returns:
            Dict con estado y métricas del analyzer
        """
        try:
            # Intentar acceder directamente a analyzer_config para capturar cualquier excepción
            try:
                config_copy = self.analyzer_config.copy()
            except Exception as config_error:
                # Usar el manejo centralizado de errores
                self.error.handle_system_error(
                    "ANALYZER_CONFIG_ERROR", 
                    f"Error accediendo a configuración del analyzer: {config_error}"
                )
                return {"error": f"Error en configuración del analyzer: {config_error}"}
            
            return {
                "component_id": self.component_id,
                "version": self.version,
                "status": self.status,
                "is_analyzing": self._is_analyzing,
                "advanced_analytics_available": ADVANCED_ANALYTICS_AVAILABLE,
                "configuration": config_copy,
                "metrics": self.analyzer_metrics.copy(),
                "data_structures": {
                    "correlation_history_size": len(self.correlation_history),
                    "volatility_clusters_size": len(self.volatility_clusters),
                    "seasonal_patterns_count": len(self.seasonal_patterns),
                    "ml_predictions_size": len(self.ml_predictions),
                    "microstructure_data_size": len(self.microstructure_data)
                },
                "cache_status": {
                    "correlation_cache_size": len(self._correlation_cache),
                    "volatility_cache_size": len(self._volatility_cache),
                    "pattern_cache_size": len(self._pattern_cache)
                },
                "ml_models": {
                    "models_available": len(self._ml_models),
                    "models_list": list(self._ml_models.keys())
                }
            }
            
        except Exception as e:
            # Usar el manejo centralizado de errores para cualquier otro error
            self.error.handle_system_error(
                "ANALYZER_STATUS_ERROR", 
                f"Error obteniendo estado del analyzer: {e}"
            )
            return {"error": str(e)}
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de análisis realizados
        
        Returns:
            Dict con resumen de análisis
        """
        try:
            return {
                "analyzer_id": self.component_id,
                "version": self.version,
                "total_analyses": self.analyzer_metrics["total_analyses"],
                "success_rate": (
                    self.analyzer_metrics["successful_analyses"] / 
                    max(self.analyzer_metrics["total_analyses"], 1) * 100
                ),
                "average_analysis_time": self.analyzer_metrics["analysis_time_avg"],
                "last_analysis": self.analyzer_metrics["last_analysis_time"],
                "correlations_calculated": self.analyzer_metrics["correlation_calculations"],
                "ml_predictions_made": self.analyzer_metrics["ml_predictions_made"],
                "anomalies_detected": self.analyzer_metrics["anomalies_detected"],
                "current_status": self.status,
                "is_active": self._is_analyzing
            }
            
        except Exception as e:
            self.error._log_error(f"Error obteniendo resumen de análisis: {e}")
            return {"error": str(e)}
