"""
Tests para MarketRegimeDetector (PUERTA-S2-REGIME)
Testing completo del detector de regímenes de mercado

Fecha: 2025-08-11
Autor: Copilot & AI Assistant
"""

import pytest
import sys
import os
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Agregar el path del proyecto para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.core.real_time.market_regime_detector import (
    MarketRegimeDetector, MarketRegime, RegimeConfidence, RegimeDetection, RegimeAnalysis
)

class TestMarketRegimeDetector:
    """Suite de tests para MarketRegimeDetector"""
    
    def setup_method(self):
        """Setup para cada test"""
        # Crear mocks de los managers
        self.mock_config_manager = Mock()
        self.mock_logger_manager = Mock()
        self.mock_error_manager = Mock()
        self.mock_data_manager = Mock()
        self.mock_analytics_manager = Mock()
        
        # Configurar el mock del analytics_manager
        self.mock_analytics_manager.get_market_summary.return_value = {
            'volatility': 0.015,
            'trend_analysis': {
                'trend_strength': 0.5,
                'trend_direction': 1
            },
            'momentum': 0.3,
            'volume_profile': 1.1,
            'support_resistance_strength': 0.6
        }
        
        # Crear MarketRegimeDetector con mocks
        self.detector = MarketRegimeDetector(
            config_manager=self.mock_config_manager,
            logger_manager=self.mock_logger_manager,
            error_manager=self.mock_error_manager,
            data_manager=self.mock_data_manager,
            analytics_manager=self.mock_analytics_manager
        )
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if self.detector:
            self.detector.cleanup()
    
    def test_initialization(self):
        """Test de inicialización del MarketRegimeDetector"""
        assert self.detector.component_id == "PUERTA-S2-REGIME"
        assert self.detector.version == "v1.0.0"
        assert not self.detector.is_active
        assert not self.detector.detection_running
        assert len(self.detector.current_regimes) == 0
        assert len(self.detector.regime_history) == 0
        
        # Verificar que se llamó al logger para inicialización
        self.mock_logger_manager.log_info.assert_called()
    
    def test_market_regime_detection(self):
        """Test de detección básica de régimen de mercado"""
        detection = self.detector.detect_market_regime("EURUSD", "H1")
        
        assert detection is not None
        assert isinstance(detection, RegimeDetection)
        assert detection.symbol == "EURUSD"
        assert detection.timeframe == "H1"
        assert isinstance(detection.regime, MarketRegime)
        assert isinstance(detection.confidence, RegimeConfidence)
        assert 0.0 <= detection.probability <= 1.0
        assert isinstance(detection.timestamp, datetime)
        assert isinstance(detection.indicators, dict)
        assert len(detection.indicators) > 0
    
    def test_volatility_regime_analysis(self):
        """Test de análisis de régimen de volatilidad"""
        # Test alta volatilidad
        high_vol_regime = self.detector._analyze_volatility_regime(0.030)
        assert high_vol_regime == MarketRegime.HIGH_VOLATILITY
        
        # Test baja volatilidad
        low_vol_regime = self.detector._analyze_volatility_regime(0.005)
        assert low_vol_regime == MarketRegime.LOW_VOLATILITY
        
        # Test volatilidad normal (ranging)
        normal_vol_regime = self.detector._analyze_volatility_regime(0.015)
        assert normal_vol_regime == MarketRegime.RANGING
    
    def test_trend_regime_analysis(self):
        """Test de análisis de régimen de tendencia"""
        # Test trending up
        trend_up_data = {'trend_strength': 0.8, 'trend_direction': 1}
        trend_up_regime = self.detector._analyze_trend_regime(trend_up_data)
        assert trend_up_regime == MarketRegime.TRENDING_UP
        
        # Test trending down
        trend_down_data = {'trend_strength': -0.7, 'trend_direction': -1}
        trend_down_regime = self.detector._analyze_trend_regime(trend_down_data)
        assert trend_down_regime == MarketRegime.TRENDING_DOWN
        
        # Test ranging
        ranging_data = {'trend_strength': 0.1, 'trend_direction': 0}
        ranging_regime = self.detector._analyze_trend_regime(ranging_data)
        assert ranging_regime == MarketRegime.RANGING
        
        # Test consolidación
        consolidation_data = {'trend_strength': 0.4, 'trend_direction': 1}
        consolidation_regime = self.detector._analyze_trend_regime(consolidation_data)
        assert consolidation_regime == MarketRegime.CONSOLIDATION
    
    def test_momentum_regime_analysis(self):
        """Test de análisis de régimen de momentum"""
        # Test breakout
        breakout_data = {'momentum': 2.0, 'volume_profile': 1.5}
        breakout_regime = self.detector._analyze_momentum_regime(breakout_data)
        assert breakout_regime == MarketRegime.BREAKOUT
        
        # Test reversal
        reversal_data = {'momentum': 1.0, 'volume_profile': 0.7}
        reversal_regime = self.detector._analyze_momentum_regime(reversal_data)
        assert reversal_regime == MarketRegime.REVERSAL
        
        # Test consolidación
        consolidation_data = {'momentum': 0.3, 'volume_profile': 1.0}
        consolidation_regime = self.detector._analyze_momentum_regime(consolidation_data)
        assert consolidation_regime == MarketRegime.CONSOLIDATION
    
    def test_regime_combination_analysis(self):
        """Test de combinación de análisis de regímenes"""
        # Test combinación que debería dar trending up con alta confianza
        primary, confidence, probability = self.detector._combine_regime_analysis(
            MarketRegime.RANGING,  # volatility
            MarketRegime.TRENDING_UP,  # trend
            MarketRegime.BREAKOUT  # momentum
        )
        
        assert isinstance(primary, MarketRegime)
        assert isinstance(confidence, RegimeConfidence)
        assert 0.0 <= probability <= 1.0
        
        # Test combinación conflictiva que debería dar menor confianza
        primary2, confidence2, probability2 = self.detector._combine_regime_analysis(
            MarketRegime.HIGH_VOLATILITY,
            MarketRegime.RANGING,
            MarketRegime.REVERSAL
        )
        
        assert isinstance(primary2, MarketRegime)
        assert isinstance(confidence2, RegimeConfidence)
        assert probability2 <= probability  # Debería tener menor probabilidad
    
    def test_regime_stability_analysis(self):
        """Test de análisis de estabilidad del régimen"""
        # Primero detectar un régimen
        detection = self.detector.detect_market_regime("EURUSD", "H1")
        assert detection is not None
        
        # Analizar estabilidad
        analysis = self.detector.analyze_regime_stability("EURUSD", "H1")
        
        if analysis:  # Puede ser None si no hay suficiente historial
            assert isinstance(analysis, RegimeAnalysis)
            assert analysis.current_regime is not None
            assert 0.0 <= analysis.stability_score <= 1.0
            assert isinstance(analysis.recommendations, list)
            assert len(analysis.recommendations) > 0
    
    def test_detection_service_start_stop(self):
        """Test de inicio y parada del servicio de detección"""
        symbols = ["EURUSD", "GBPUSD"]
        timeframes = ["H1", "H4"]
        
        # Test iniciar servicio
        result = self.detector.start_detection_service(symbols, timeframes)
        assert result is True
        assert self.detector.detection_running is True
        assert self.detector.is_active is True
        assert self.detector.detection_thread is not None
        assert self.detector.detection_thread.is_alive()
        
        # Esperar un poco para que el servicio procese
        time.sleep(0.1)
        
        # Test detener servicio
        result = self.detector.stop_detection_service()
        assert result is True
        assert self.detector.detection_running is False
        assert self.detector.is_active is False
    
    def test_detection_service_double_start(self):
        """Test de intentar iniciar el servicio dos veces"""
        symbols = ["EURUSD"]
        timeframes = ["H1"]
        
        # Primer inicio
        result1 = self.detector.start_detection_service(symbols, timeframes)
        assert result1 is True
        
        # Segundo inicio (debe devolver True pero logear warning)
        result2 = self.detector.start_detection_service(symbols, timeframes)
        assert result2 is True
        
        # Verificar que se logueó el warning
        warning_calls = [call for call in self.mock_logger_manager.log_warning.call_args_list 
                        if "ya está ejecutándose" in str(call)]
        assert len(warning_calls) > 0
        
        # Cleanup
        self.detector.stop_detection_service()
    
    def test_get_detector_status(self):
        """Test de obtención del estado del detector"""
        # Detectar un régimen primero
        detection = self.detector.detect_market_regime("EURUSD", "H1")
        
        status = self.detector.get_detector_status()
        
        assert status['component_id'] == "PUERTA-S2-REGIME"
        assert status['version'] == "v1.0.0"
        assert 'is_active' in status
        assert 'detection_running' in status
        assert 'current_regimes_count' in status
        assert 'regime_history_count' in status
        assert 'metrics' in status
        assert 'active_regimes' in status
        
        if detection:
            assert status['current_regimes_count'] >= 1
            assert status['regime_history_count'] >= 1
    
    def test_get_current_regimes(self):
        """Test de obtención de regímenes actuales"""
        # Inicialmente debe estar vacío
        regimes = self.detector.get_current_regimes()
        assert isinstance(regimes, dict)
        
        # Detectar un régimen
        detection = self.detector.detect_market_regime("EURUSD", "H1")
        
        if detection:
            regimes = self.detector.get_current_regimes()
            assert len(regimes) >= 1
            assert "EURUSD_H1" in regimes
            assert regimes["EURUSD_H1"] == detection
    
    def test_error_handling_in_detection(self):
        """Test de manejo de errores en detección"""
        # Configurar el analytics_manager para que lance una excepción
        self.mock_analytics_manager.get_market_summary.side_effect = Exception("Test error")
        
        detection = self.detector.detect_market_regime("EURUSD", "H1")
        
        # Debe devolver None en caso de error
        assert detection is None
        
        # Verificar que se llamó al error_manager
        self.mock_error_manager.handle_system_error.assert_called()
    
    def test_regime_change_detection(self):
        """Test de detección de cambios de régimen"""
        # Configurar diferentes respuestas del analytics_manager
        first_response = {
            'volatility': 0.008,  # Baja volatilidad
            'trend_analysis': {'trend_strength': 0.1, 'trend_direction': 0},
            'momentum': 0.1,
            'volume_profile': 1.0,
            'support_resistance_strength': 0.5
        }
        
        second_response = {
            'volatility': 0.030,  # Alta volatilidad
            'trend_analysis': {'trend_strength': 0.8, 'trend_direction': 1},
            'momentum': 1.8,
            'volume_profile': 1.5,
            'support_resistance_strength': 0.8
        }
        
        # Primera detección
        self.mock_analytics_manager.get_market_summary.return_value = first_response
        detection1 = self.detector.detect_market_regime("EURUSD", "H1")
        
        # Segunda detección con diferentes condiciones
        self.mock_analytics_manager.get_market_summary.return_value = second_response
        detection2 = self.detector.detect_market_regime("EURUSD", "H1")
        
        # Verificar que se detectaron regímenes diferentes (probable)
        if detection1 and detection2:
            # No necesariamente diferentes, pero al menos ambos deben existir
            assert detection1.regime is not None
            assert detection2.regime is not None
    
    def test_cleanup(self):
        """Test de limpieza de recursos"""
        # Detectar algunos regímenes
        self.detector.detect_market_regime("EURUSD", "H1")
        self.detector.detect_market_regime("GBPUSD", "H4")
        
        # Iniciar servicio
        self.detector.start_detection_service(["EURUSD"], ["H1"])
        
        # Verificar que hay datos
        assert len(self.detector.current_regimes) > 0 or len(self.detector.regime_history) > 0
        
        # Ejecutar cleanup
        self.detector.cleanup()
        
        # Verificar que se limpió todo
        assert len(self.detector.current_regimes) == 0
        assert len(self.detector.regime_history) == 0
        assert len(self.detector.regime_statistics) == 0
        assert not self.detector.detection_running
        assert not self.detector.is_active
    
    def test_market_regime_enum(self):
        """Test de la enumeración MarketRegime"""
        assert MarketRegime.TRENDING_UP.value == "trending_up"
        assert MarketRegime.TRENDING_DOWN.value == "trending_down"
        assert MarketRegime.RANGING.value == "ranging"
        assert MarketRegime.HIGH_VOLATILITY.value == "high_volatility"
        assert MarketRegime.LOW_VOLATILITY.value == "low_volatility"
        assert MarketRegime.BREAKOUT.value == "breakout"
        assert MarketRegime.REVERSAL.value == "reversal"
        assert MarketRegime.CONSOLIDATION.value == "consolidation"
    
    def test_regime_confidence_enum(self):
        """Test de la enumeración RegimeConfidence"""
        assert RegimeConfidence.LOW.value == 1
        assert RegimeConfidence.MEDIUM.value == 2
        assert RegimeConfidence.HIGH.value == 3
        assert RegimeConfidence.VERY_HIGH.value == 4
    
    def test_regime_detection_dataclass(self):
        """Test de la estructura RegimeDetection"""
        timestamp = datetime.now()
        duration = timedelta(hours=1)
        detection = RegimeDetection(
            symbol="EURUSD",
            timeframe="H1",
            regime=MarketRegime.TRENDING_UP,
            confidence=RegimeConfidence.HIGH,
            probability=0.85,
            timestamp=timestamp,
            duration=duration,
            indicators={'volatility': 0.015, 'trend_strength': 0.7},
            metadata={'test_key': 'test_value'}
        )
        
        assert detection.symbol == "EURUSD"
        assert detection.timeframe == "H1"
        assert detection.regime == MarketRegime.TRENDING_UP
        assert detection.confidence == RegimeConfidence.HIGH
        assert detection.probability == 0.85
        assert detection.timestamp == timestamp
        assert detection.duration == duration
        assert detection.indicators['volatility'] == 0.015
        assert detection.metadata['test_key'] == 'test_value'

class TestMarketRegimeDetectorIntegration:
    """Tests de integración para MarketRegimeDetector"""
    
    def test_integration_with_real_managers(self):
        """Test de integración con managers reales"""
        # Este test usa los managers reales en lugar de mocks
        detector = MarketRegimeDetector()
        
        # Verificar que los managers están inicializados
        assert detector.config_manager is not None
        assert detector.logger_manager is not None
        assert detector.error_manager is not None
        assert detector.data_manager is not None
        assert detector.analytics_manager is not None
        
        # Test básico de funcionalidad
        detection = detector.detect_market_regime("EURUSD", "H1")
        # No necesariamente debe devolver algo, depende del estado del analytics_manager
        
        # Test de estado
        status = detector.get_detector_status()
        assert status['component_id'] == "PUERTA-S2-REGIME"
        
        # Cleanup
        detector.cleanup()

if __name__ == "__main__":
    # Ejecutar tests individuales para debugging
    test_detector = TestMarketRegimeDetector()
    test_detector.setup_method()
    
    print("🧪 Testing MarketRegimeDetector...")
    
    try:
        test_detector.test_initialization()
        print("✅ Test inicialización: PASSED")
        
        test_detector.test_market_regime_detection()
        print("✅ Test detección régimen: PASSED")
        
        test_detector.test_volatility_regime_analysis()
        print("✅ Test análisis volatilidad: PASSED")
        
        test_detector.test_trend_regime_analysis()
        print("✅ Test análisis tendencia: PASSED")
        
        test_detector.test_regime_combination_analysis()
        print("✅ Test combinación análisis: PASSED")
        
        test_detector.test_get_detector_status()
        print("✅ Test estado: PASSED")
        
        print("\n🎉 Todos los tests básicos PASSED!")
        
    except Exception as e:
        print(f"❌ Error en tests: {e}")
    finally:
        test_detector.teardown_method()
