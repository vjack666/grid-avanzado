"""
TESTS PARA ADVANCED ANALYZER - SÓTANO 2 DÍA 3
Tests comprehensivos para el sistema de análisis avanzado

PUERTA: PUERTA-S2-ANALYZER
VERSIÓN: v1.0.0  
FECHA: 2025-08-11
"""

import pytest
import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Agregar path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Imports del sistema
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager  
from src.core.error_manager import ErrorManager
from src.core.data_manager import DataManager

# Import del módulo a testear
from src.core.real_time.advanced_analyzer import (
    AdvancedAnalyzer,
    CorrelationAnalysis,
    VolatilityCluster,
    SeasonalPattern,
    MLPrediction,
    MarketMicrostructure,
    ADVANCED_ANALYTICS_AVAILABLE
)


class TestAdvancedAnalyzerStructures:
    """Tests para estructuras de datos del AdvancedAnalyzer"""
    
    def test_correlation_analysis_structure(self):
        """Test estructura CorrelationAnalysis"""
        corr = CorrelationAnalysis()
        
        assert isinstance(corr.correlation_matrix, dict)
        assert isinstance(corr.correlation_strength, dict)
        assert isinstance(corr.correlation_direction, dict)
        assert isinstance(corr.timeframe, str)
        assert isinstance(corr.timestamp, datetime)
    
    def test_correlation_analysis_with_data(self):
        """Test CorrelationAnalysis con datos"""
        corr = CorrelationAnalysis(
            correlation_matrix={"EURUSD": {"GBPUSD": 0.75}},
            correlation_strength={"EURUSD-GBPUSD": "strong"},
            correlation_direction={"EURUSD-GBPUSD": "positive"},
            timeframe="H1"
        )
        
        assert corr.correlation_matrix["EURUSD"]["GBPUSD"] == 0.75
        assert corr.correlation_strength["EURUSD-GBPUSD"] == "strong"
        assert corr.correlation_direction["EURUSD-GBPUSD"] == "positive"
        assert corr.timeframe == "H1"
    
    def test_volatility_cluster_structure(self):
        """Test estructura VolatilityCluster"""
        cluster = VolatilityCluster()
        
        assert isinstance(cluster.cluster_type, str)
        assert isinstance(cluster.start_time, datetime)
        assert cluster.end_time is None
        assert isinstance(cluster.duration_minutes, float)
        assert isinstance(cluster.average_volatility, float)
        assert isinstance(cluster.peak_volatility, float)
        assert isinstance(cluster.cluster_strength, float)
    
    def test_volatility_cluster_with_data(self):
        """Test VolatilityCluster con datos"""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=2)
        
        cluster = VolatilityCluster(
            cluster_type="high",
            start_time=start_time,
            end_time=end_time,
            duration_minutes=120.0,
            average_volatility=0.015,
            peak_volatility=0.025,
            cluster_strength=2.5
        )
        
        assert cluster.cluster_type == "high"
        assert cluster.duration_minutes == 120.0
        assert cluster.average_volatility == 0.015
        assert cluster.peak_volatility == 0.025
        assert cluster.cluster_strength == 2.5
    
    def test_seasonal_pattern_structure(self):
        """Test estructura SeasonalPattern"""
        pattern = SeasonalPattern()
        
        assert isinstance(pattern.pattern_type, str)
        assert isinstance(pattern.pattern_strength, float)
        assert isinstance(pattern.pattern_direction, str)
        assert isinstance(pattern.confidence_level, float)
        assert isinstance(pattern.statistical_significance, float)
        assert isinstance(pattern.pattern_data, dict)
    
    def test_ml_prediction_structure(self):
        """Test estructura MLPrediction"""
        prediction = MLPrediction()
        
        assert isinstance(prediction.prediction_value, float)
        assert isinstance(prediction.confidence_interval, tuple)
        assert isinstance(prediction.model_accuracy, float)
        assert isinstance(prediction.feature_importance, dict)
        assert isinstance(prediction.prediction_horizon, int)
        assert isinstance(prediction.model_type, str)
        assert isinstance(prediction.timestamp, datetime)
    
    def test_market_microstructure_structure(self):
        """Test estructura MarketMicrostructure"""
        micro = MarketMicrostructure()
        
        assert isinstance(micro.bid_ask_spread, float)
        assert isinstance(micro.spread_percentile, float)
        assert isinstance(micro.liquidity_score, float)
        assert isinstance(micro.orderflow_imbalance, float)
        assert isinstance(micro.price_impact, float)
        assert isinstance(micro.market_depth, dict)
        assert isinstance(micro.timestamp, datetime)


class TestAdvancedAnalyzerCore:
    """Tests para funcionalidad core del AdvancedAnalyzer"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Fixture con dependencias mockeadas"""
        config = Mock(spec=ConfigManager)
        logger = Mock(spec=LoggerManager)
        error = Mock(spec=ErrorManager)
        
        # Mock DataManager sin spec para permitir métodos dinámicos
        data_manager = Mock()
        data_manager.get_historical_data.return_value = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=100, freq='h'),
            'open': np.random.randn(100).cumsum() + 1.1000,
            'high': np.random.randn(100).cumsum() + 1.1020,
            'low': np.random.randn(100).cumsum() + 0.9980,
            'close': np.random.randn(100).cumsum() + 1.1000,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        return {
            'config': config,
            'logger': logger,
            'error': error,
            'data_manager': data_manager
        }
    
    def test_advanced_analyzer_initialization(self, mock_dependencies):
        """Test inicialización del AdvancedAnalyzer"""
        analyzer = AdvancedAnalyzer(
            config=mock_dependencies['config'],
            logger=mock_dependencies['logger'],
            error=mock_dependencies['error'],
            data_manager=mock_dependencies['data_manager']
        )
        
        # Verificar metadatos
        assert analyzer.component_id == "PUERTA-S2-ANALYZER"
        assert analyzer.version == "v1.0.0"
        assert analyzer.status == "initialized"
        
        # Verificar dependencias
        assert analyzer.config == mock_dependencies['config']
        assert analyzer.logger == mock_dependencies['logger']
        assert analyzer.error == mock_dependencies['error']
        assert analyzer.data == mock_dependencies['data_manager']
        
        # Verificar estructuras inicializadas
        assert isinstance(analyzer.correlation_history, list)
        assert isinstance(analyzer.volatility_clusters, list)
        assert isinstance(analyzer.seasonal_patterns, dict)
        assert isinstance(analyzer.ml_predictions, list)
        assert isinstance(analyzer.microstructure_data, list)
        
        # Verificar configuración
        assert isinstance(analyzer.analyzer_config, dict)
        assert "enabled" in analyzer.analyzer_config
        assert "analysis_interval_minutes" in analyzer.analyzer_config
        
        # Verificar métricas iniciales
        assert analyzer.analyzer_metrics["total_analyses"] == 0
        assert analyzer.analyzer_metrics["successful_analyses"] == 0
    
    def test_advanced_analyzer_with_optional_components(self, mock_dependencies):
        """Test inicialización con componentes opcionales"""
        mt5_streamer = Mock()
        alert_engine = Mock()
        
        analyzer = AdvancedAnalyzer(
            config=mock_dependencies['config'],
            logger=mock_dependencies['logger'],
            error=mock_dependencies['error'],
            data_manager=mock_dependencies['data_manager'],
            mt5_streamer=mt5_streamer,
            alert_engine=alert_engine
        )
        
        assert analyzer.mt5_streamer == mt5_streamer
        assert analyzer.alert_engine == alert_engine
    
    def test_analyzer_config_initialization(self, mock_dependencies):
        """Test inicialización de configuración"""
        analyzer = AdvancedAnalyzer(
            config=mock_dependencies['config'],
            logger=mock_dependencies['logger'],
            error=mock_dependencies['error'],
            data_manager=mock_dependencies['data_manager']
        )
        
        config = analyzer.analyzer_config
        
        # Verificar configuraciones principales
        assert isinstance(config["enabled"], bool)
        assert isinstance(config["analysis_interval_minutes"], int)
        assert isinstance(config["background_analysis"], bool)
        assert isinstance(config["max_history_size"], int)
        
        # Verificar configuraciones de correlación
        assert "correlation_window_size" in config
        assert "correlation_min_periods" in config
        assert "correlation_significance_level" in config
        
        # Verificar configuraciones de volatilidad
        assert "volatility_window_size" in config
        assert "volatility_cluster_threshold" in config
        
        # Verificar configuraciones ML
        assert "ml_enabled" in config
        assert config["ml_enabled"] == ADVANCED_ANALYTICS_AVAILABLE
    
    def test_ml_models_initialization_when_available(self, mock_dependencies):
        """Test inicialización de modelos ML cuando están disponibles"""
        with patch('src.core.real_time.advanced_analyzer.ADVANCED_ANALYTICS_AVAILABLE', True):
            analyzer = AdvancedAnalyzer(
                config=mock_dependencies['config'],
                logger=mock_dependencies['logger'],
                error=mock_dependencies['error'],
                data_manager=mock_dependencies['data_manager']
            )
            
            if analyzer.analyzer_config["ml_enabled"]:
                assert len(analyzer._ml_models) > 0
                assert len(analyzer._model_scalers) > 0
    
    def test_ml_models_disabled_when_not_available(self, mock_dependencies):
        """Test modelos ML deshabilitados cuando no están disponibles"""
        with patch('src.core.real_time.advanced_analyzer.ADVANCED_ANALYTICS_AVAILABLE', False):
            analyzer = AdvancedAnalyzer(
                config=mock_dependencies['config'],
                logger=mock_dependencies['logger'],
                error=mock_dependencies['error'],
                data_manager=mock_dependencies['data_manager']
            )
            
            assert analyzer.analyzer_config["ml_enabled"] is False
            assert len(analyzer._ml_models) == 0


class TestAdvancedAnalyzerService:
    """Tests para servicio de análisis del AdvancedAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture con AdvancedAnalyzer"""
        config = Mock(spec=ConfigManager)
        logger = Mock(spec=LoggerManager)
        error = Mock(spec=ErrorManager)
        
        data_manager = Mock()
        data_manager.get_historical_data.return_value = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=100, freq='h'),
            'close': np.random.randn(100).cumsum() + 1.1000
        })
        
        return AdvancedAnalyzer(
            config=config,
            logger=logger,
            error=error,
            data_manager=data_manager
        )
    
    def test_start_analysis_service_success(self, analyzer):
        """Test iniciar servicio de análisis exitosamente"""
        # Habilitar análisis en background
        analyzer.analyzer_config["background_analysis"] = True
        
        result = analyzer.start_analysis_service()
        
        assert result is True
        assert analyzer._is_analyzing is True
        assert analyzer.status == "analyzing"
        assert analyzer._analysis_thread is not None
        assert analyzer._analysis_thread.is_alive()
        
        # Cleanup
        analyzer.stop_analysis_service()
    
    def test_start_analysis_service_disabled(self, analyzer):
        """Test iniciar servicio cuando está deshabilitado"""
        # Deshabilitar análisis en background
        analyzer.analyzer_config["background_analysis"] = False
        
        result = analyzer.start_analysis_service()
        
        assert result is True
        assert analyzer._is_analyzing is False
        assert analyzer._analysis_thread is None
    
    def test_start_analysis_service_already_running(self, analyzer):
        """Test iniciar servicio cuando ya está ejecutándose"""
        analyzer.analyzer_config["background_analysis"] = True
        analyzer._is_analyzing = True
        
        result = analyzer.start_analysis_service()
        
        assert result is True
        # No debe crear nuevo thread
        assert analyzer._analysis_thread is None
    
    def test_stop_analysis_service_success(self, analyzer):
        """Test detener servicio de análisis exitosamente"""
        # Primero iniciar el servicio
        analyzer.analyzer_config["background_analysis"] = True
        analyzer.start_analysis_service()
        
        # Verificar que está ejecutándose
        assert analyzer._is_analyzing is True
        
        # Detener el servicio
        result = analyzer.stop_analysis_service()
        
        assert result is True
        assert analyzer._is_analyzing is False
        assert analyzer.status == "stopped"
    
    def test_stop_analysis_service_not_running(self, analyzer):
        """Test detener servicio cuando no está ejecutándose"""
        assert analyzer._is_analyzing is False
        
        result = analyzer.stop_analysis_service()
        
        assert result is True
        assert analyzer._is_analyzing is False
    
    @patch('time.sleep')
    def test_analysis_service_loop_execution(self, mock_sleep, analyzer):
        """Test ejecución del loop de análisis"""
        analyzer.analyzer_config["analysis_interval_minutes"] = 1  # 1 minuto para test
        
        # Mock para detener después de una iteración
        call_count = 0
        def side_effect(seconds):
            nonlocal call_count
            call_count += 1
            if call_count >= 1:
                analyzer._is_analyzing = False
        
        mock_sleep.side_effect = side_effect
        
        # Ejecutar loop
        analyzer._is_analyzing = True
        analyzer._analysis_service_loop()
        
        # Verificar que se llamó sleep con el intervalo correcto
        assert mock_sleep.call_count >= 1
        mock_sleep.assert_called_with(60)  # 1 minuto en segundos
    
    def test_periodic_analysis_execution(self, analyzer):
        """Test ejecución de análisis periódico"""
        initial_analyses = analyzer.analyzer_metrics["total_analyses"]
        
        # Ejecutar análisis periódico
        analyzer._perform_periodic_analysis()
        
        # Verificar que se incrementaron las métricas
        assert analyzer.analyzer_metrics["total_analyses"] > initial_analyses
        assert analyzer.analyzer_metrics["last_analysis_time"] is not None
        assert analyzer.analyzer_metrics["analysis_time_avg"] > 0
    
    def test_analysis_metrics_update(self, analyzer):
        """Test actualización de métricas de análisis"""
        initial_total = analyzer.analyzer_metrics["total_analyses"]
        initial_successful = analyzer.analyzer_metrics["successful_analyses"]
        
        # Simular análisis exitoso
        analyzer._update_analyzer_metrics(1.5, True)
        
        assert analyzer.analyzer_metrics["total_analyses"] == initial_total + 1
        assert analyzer.analyzer_metrics["successful_analyses"] == initial_successful + 1
        assert analyzer.analyzer_metrics["analysis_time_avg"] > 0
        
        # Simular análisis fallido
        analyzer._update_analyzer_metrics(0.0, False)
        
        assert analyzer.analyzer_metrics["total_analyses"] == initial_total + 2
        assert analyzer.analyzer_metrics["successful_analyses"] == initial_successful + 1


class TestAdvancedAnalyzerAsync:
    """Tests para funcionalidad asíncrona del AdvancedAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture con AdvancedAnalyzer para tests asíncronos"""
        config = Mock(spec=ConfigManager)
        logger = Mock(spec=LoggerManager)
        error = Mock(spec=ErrorManager)
        data_manager = Mock()
        
        return AdvancedAnalyzer(
            config=config,
            logger=logger,
            error=error,
            data_manager=data_manager
        )
    
    @pytest.mark.asyncio
    async def test_start_async_analysis_service(self, analyzer):
        """Test iniciar servicio de análisis asíncrono"""
        analyzer.analyzer_config["background_analysis"] = True
        
        result = await analyzer.start_async_analysis_service()
        
        assert result is True
        assert analyzer._is_analyzing is True
        assert analyzer.status == "analyzing_async"
        
        # Cleanup
        analyzer._is_analyzing = False
    
    @pytest.mark.asyncio
    async def test_async_correlation_analysis(self, analyzer):
        """Test análisis de correlaciones asíncrono"""
        initial_count = analyzer.analyzer_metrics["correlation_calculations"]
        
        await analyzer._async_correlation_analysis()
        
        assert analyzer.analyzer_metrics["correlation_calculations"] > initial_count
    
    @pytest.mark.asyncio
    async def test_async_volatility_analysis(self, analyzer):
        """Test análisis de volatilidad asíncrono"""
        # No debería lanzar excepción
        await analyzer._async_volatility_analysis()
        assert True
    
    @pytest.mark.asyncio
    async def test_async_ml_predictions(self, analyzer):
        """Test predicciones ML asíncronas"""
        initial_count = analyzer.analyzer_metrics["ml_predictions_made"]
        
        # Habilitar ML para el test
        analyzer.analyzer_config["ml_enabled"] = True
        
        await analyzer._async_ml_predictions()
        
        # Si ML está disponible, debería incrementar contador
        if analyzer.analyzer_config["ml_enabled"]:
            assert analyzer.analyzer_metrics["ml_predictions_made"] >= initial_count
    
    @pytest.mark.asyncio
    async def test_async_microstructure_analysis(self, analyzer):
        """Test análisis de microestructura asíncrono"""
        # No debería lanzar excepción
        await analyzer._async_microstructure_analysis()
        assert True
    
    @pytest.mark.asyncio
    async def test_perform_async_analysis(self, analyzer):
        """Test análisis asíncrono completo"""
        initial_total = analyzer.analyzer_metrics["total_analyses"]
        
        # Habilitar todos los análisis
        analyzer.analyzer_config["correlation_enabled"] = True
        analyzer.analyzer_config["ml_enabled"] = True
        analyzer.analyzer_config["microstructure_enabled"] = True
        analyzer.analyzer_config["seasonal_patterns_enabled"] = ["hourly"]
        analyzer.analyzer_config["anomaly_detection_enabled"] = True
        
        await analyzer._perform_async_analysis()
        
        # Verificar que se actualizaron las métricas
        assert analyzer.analyzer_metrics["total_analyses"] > initial_total


class TestAdvancedAnalyzerStatus:
    """Tests para estado y métricas del AdvancedAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture con AdvancedAnalyzer"""
        config = Mock(spec=ConfigManager)
        logger = Mock(spec=LoggerManager)
        error = Mock(spec=ErrorManager)
        data_manager = Mock(spec=DataManager)
        
        return AdvancedAnalyzer(
            config=config,
            logger=logger,
            error=error,
            data_manager=data_manager
        )
    
    def test_get_analyzer_status_complete(self, analyzer):
        """Test obtener estado completo del analyzer"""
        status = analyzer.get_analyzer_status()
        
        # Verificar metadatos
        assert status["component_id"] == "PUERTA-S2-ANALYZER"
        assert status["version"] == "v1.0.0"
        assert status["status"] == "initialized"
        assert "is_analyzing" in status
        assert "advanced_analytics_available" in status
        
        # Verificar configuración
        assert "configuration" in status
        assert isinstance(status["configuration"], dict)
        
        # Verificar métricas
        assert "metrics" in status
        assert isinstance(status["metrics"], dict)
        assert "total_analyses" in status["metrics"]
        
        # Verificar estructuras de datos
        assert "data_structures" in status
        data_structures = status["data_structures"]
        assert "correlation_history_size" in data_structures
        assert "volatility_clusters_size" in data_structures
        assert "seasonal_patterns_count" in data_structures
        assert "ml_predictions_size" in data_structures
        assert "microstructure_data_size" in data_structures
        
        # Verificar cache
        assert "cache_status" in status
        cache_status = status["cache_status"]
        assert "correlation_cache_size" in cache_status
        assert "volatility_cache_size" in cache_status
        assert "pattern_cache_size" in cache_status
        
        # Verificar modelos ML
        assert "ml_models" in status
        ml_models = status["ml_models"]
        assert "models_available" in ml_models
        assert "models_list" in ml_models
    
    def test_get_analysis_summary_complete(self, analyzer):
        """Test obtener resumen completo de análisis"""
        # Simular algunas métricas
        analyzer.analyzer_metrics["total_analyses"] = 10
        analyzer.analyzer_metrics["successful_analyses"] = 8
        analyzer.analyzer_metrics["analysis_time_avg"] = 2.5
        analyzer.analyzer_metrics["correlation_calculations"] = 5
        analyzer.analyzer_metrics["ml_predictions_made"] = 3
        analyzer.analyzer_metrics["anomalies_detected"] = 1
        
        summary = analyzer.get_analysis_summary()
        
        # Verificar metadatos
        assert summary["analyzer_id"] == "PUERTA-S2-ANALYZER"
        assert summary["version"] == "v1.0.0"
        
        # Verificar métricas calculadas
        assert summary["total_analyses"] == 10
        assert summary["success_rate"] == 80.0  # 8/10 * 100
        assert summary["average_analysis_time"] == 2.5
        
        # Verificar contadores específicos
        assert summary["correlations_calculated"] == 5
        assert summary["ml_predictions_made"] == 3
        assert summary["anomalies_detected"] == 1
        
        # Verificar estado
        assert "current_status" in summary
        assert "is_active" in summary
    
    def test_get_status_with_error_handling(self, analyzer):
        """Test manejo de errores en obtención de estado"""
        # Simular error en get_analyzer_status
        with patch.object(analyzer, 'analyzer_config', side_effect=Exception("Test error")):
            status = analyzer.get_analyzer_status()
            assert "error" in status
            assert "Test error" in status["error"]
    
    def test_get_summary_with_zero_analyses(self, analyzer):
        """Test resumen con cero análisis realizados"""
        summary = analyzer.get_analysis_summary()
        
        # Verificar que no hay división por cero
        assert summary["total_analyses"] == 0
        assert summary["success_rate"] == 0.0  # Debe manejar división por cero
        assert summary["average_analysis_time"] == 0.0


def test_advanced_analytics_availability():
    """Test disponibilidad de librerías de análisis avanzado"""
    # Solo verificar que la variable está definida
    assert isinstance(ADVANCED_ANALYTICS_AVAILABLE, bool)
    
    # Si está disponible, verificar que las librerías se pueden importar
    if ADVANCED_ANALYTICS_AVAILABLE:
        try:
            from scipy import stats
            from sklearn.ensemble import RandomForestRegressor
            assert True  # Importación exitosa
        except ImportError:
            pytest.fail("ADVANCED_ANALYTICS_AVAILABLE es True pero las librerías no están disponibles")


if __name__ == "__main__":
    # Ejecutar tests específicos para desarrollo
    pytest.main([__file__, "-v", "--tb=short"])
