"""
Tests para StrategyEngine (PUERTA-S2-STRATEGY)
Testing completo del motor de estrategias adaptativas

Fecha: 2025-08-11
Autor: Copilot & AI Assistant
"""

import pytest
import sys
import os
import time
import threading
from datetime import datetime
from unittest.mock import Mock, patch

# Agregar el path del proyecto para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.core.real_time.strategy_engine import (
    StrategyEngine, StrategyType, SignalStrength, TradingSignal, StrategyConfig
)

class TestStrategyEngine:
    """Suite de tests para StrategyEngine"""
    
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
                'trend_strength': 0.5
            }
        }
        
        # Crear StrategyEngine con mocks
        self.engine = StrategyEngine(
            config_manager=self.mock_config_manager,
            logger_manager=self.mock_logger_manager,
            error_manager=self.mock_error_manager,
            data_manager=self.mock_data_manager,
            analytics_manager=self.mock_analytics_manager
        )
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if self.engine:
            self.engine.cleanup()
    
    def test_initialization(self):
        """Test de inicialización del StrategyEngine"""
        assert self.engine.component_id == "PUERTA-S2-STRATEGY"
        assert self.engine.version == "v1.0.0"
        assert not self.engine.is_active
        assert not self.engine.strategies_running
        assert len(self.engine.strategy_configs) == 0
        assert len(self.engine.active_strategies) == 0
        
        # Verificar que se llamó al logger para inicialización
        self.mock_logger_manager.log_info.assert_called()
    
    def test_strategy_config_initialization(self):
        """Test de inicialización de configuración de estrategia"""
        config = StrategyConfig(
            strategy_type=StrategyType.ADAPTIVE_GRID,
            timeframes=["M15", "H1"],
            symbols=["EURUSD", "GBPUSD"],
            risk_per_trade=0.02,
            max_concurrent_trades=3
        )
        
        result = self.engine.initialize_strategy_config("test_strategy", config)
        
        assert result is True
        assert "test_strategy" in self.engine.strategy_configs
        assert self.engine.strategy_configs["test_strategy"] == config
        assert "test_strategy" in self.engine.active_strategies
        assert not self.engine.active_strategies["test_strategy"]
    
    def test_strategy_start_stop(self):
        """Test de iniciar y detener estrategias"""
        # Configurar estrategia primero
        config = StrategyConfig(
            strategy_type=StrategyType.ADAPTIVE_GRID,
            timeframes=["M15"],
            symbols=["EURUSD"]
        )
        self.engine.initialize_strategy_config("test_strategy", config)
        
        # Test iniciar estrategia
        result = self.engine.start_strategy("test_strategy")
        assert result is True
        assert self.engine.active_strategies["test_strategy"] is True
        assert self.engine.strategy_metrics['active_strategies_count'] == 1
        
        # Test detener estrategia
        result = self.engine.stop_strategy("test_strategy")
        assert result is True
        assert self.engine.active_strategies["test_strategy"] is False
        assert self.engine.strategy_metrics['active_strategies_count'] == 0
    
    def test_strategy_start_nonexistent(self):
        """Test de intentar iniciar estrategia que no existe"""
        result = self.engine.start_strategy("nonexistent_strategy")
        assert result is False
        
        # Verificar que se logueó el warning
        self.mock_logger_manager.log_warning.assert_called()
    
    def test_adaptive_grid_signal_generation(self):
        """Test de generación de señales de grid adaptativo"""
        market_data = {
            'price': 1.0850,
            'volatility': 0.015
        }
        
        signal = self.engine.generate_adaptive_grid_signal("EURUSD", market_data)
        
        assert signal is not None
        assert isinstance(signal, TradingSignal)
        assert signal.symbol == "EURUSD"
        assert signal.timeframe == "M15"
        assert signal.signal_type in ["BUY", "SELL"]
        assert isinstance(signal.strength, SignalStrength)
        assert 0.0 <= signal.confidence <= 1.0
        assert signal.source == "adaptive_grid"
        assert signal.price == 1.0850
        assert 'analytics_used' in signal.metadata
        assert signal.metadata['analytics_used'] is True
    
    def test_dynamic_position_size_calculation(self):
        """Test de cálculo dinámico de tamaño de posición"""
        signal = TradingSignal(
            symbol="EURUSD",
            timeframe="M15",
            signal_type="BUY",
            strength=SignalStrength.STRONG,
            price=1.0850,
            timestamp=datetime.now(),
            confidence=0.8,
            source="test"
        )
        
        account_balance = 10000.0
        position_size = self.engine.calculate_dynamic_position_size(signal, account_balance)
        
        assert position_size > 0
        assert position_size <= account_balance * 0.05  # Máximo 5%
        
        # Test con señal débil
        signal.strength = SignalStrength.WEAK
        signal.confidence = 0.4
        weak_position_size = self.engine.calculate_dynamic_position_size(signal, account_balance)
        
        assert weak_position_size < position_size  # Debe ser menor con señal débil
    
    def test_strategy_service_start_stop(self):
        """Test de inicio y parada del servicio de estrategias"""
        # Test iniciar servicio
        result = self.engine.start_strategy_service()
        assert result is True
        assert self.engine.strategies_running is True
        assert self.engine.is_active is True
        assert self.engine.strategy_thread is not None
        assert self.engine.strategy_thread.is_alive()
        
        # Esperar un poco para que el servicio procese
        time.sleep(0.1)
        
        # Test detener servicio
        result = self.engine.stop_strategy_service()
        assert result is True
        assert self.engine.strategies_running is False
        assert self.engine.is_active is False
    
    def test_strategy_service_double_start(self):
        """Test de intentar iniciar el servicio dos veces"""
        # Primer inicio
        result1 = self.engine.start_strategy_service()
        assert result1 is True
        
        # Segundo inicio (debe devolver True pero logear warning)
        result2 = self.engine.start_strategy_service()
        assert result2 is True
        
        # Verificar que se logueó el warning
        warning_calls = [call for call in self.mock_logger_manager.log_warning.call_args_list 
                        if "ya está ejecutándose" in str(call)]
        assert len(warning_calls) > 0
        
        # Cleanup
        self.engine.stop_strategy_service()
    
    def test_get_strategy_status(self):
        """Test de obtención del estado del motor"""
        # Configurar una estrategia
        config = StrategyConfig(
            strategy_type=StrategyType.ADAPTIVE_GRID,
            timeframes=["M15"],
            symbols=["EURUSD"]
        )
        self.engine.initialize_strategy_config("test_strategy", config)
        self.engine.start_strategy("test_strategy")
        
        status = self.engine.get_strategy_status()
        
        assert status['component_id'] == "PUERTA-S2-STRATEGY"
        assert status['version'] == "v1.0.0"
        assert 'is_active' in status
        assert 'strategies_running' in status
        assert 'active_strategies' in status
        assert 'metrics' in status
        assert status['strategy_configs_count'] == 1
        assert status['active_strategies']['test_strategy'] is True
    
    def test_get_active_signals(self):
        """Test de obtención de señales activas"""
        # Inicialmente debe estar vacío
        signals = self.engine.get_active_signals()
        assert isinstance(signals, dict)
        assert len(signals) == 0
        
        # Agregar una señal activa manualmente para el test
        test_signal = TradingSignal(
            symbol="EURUSD",
            timeframe="M15",
            signal_type="BUY",
            strength=SignalStrength.MODERATE,
            price=1.0850,
            timestamp=datetime.now(),
            confidence=0.7,
            source="test"
        )
        
        self.engine.active_signals["EURUSD_M15"] = test_signal
        
        signals = self.engine.get_active_signals()
        assert len(signals) == 1
        assert "EURUSD_M15" in signals
        assert signals["EURUSD_M15"] == test_signal
    
    def test_error_handling_in_signal_generation(self):
        """Test de manejo de errores en generación de señales"""
        # Configurar el analytics_manager para que lance una excepción
        self.mock_analytics_manager.get_market_summary.side_effect = Exception("Test error")
        
        market_data = {'price': 1.0850}
        signal = self.engine.generate_adaptive_grid_signal("EURUSD", market_data)
        
        # Debe devolver None en caso de error
        assert signal is None
        
        # Verificar que se llamó al error_manager
        self.mock_error_manager.handle_system_error.assert_called()
    
    def test_cleanup(self):
        """Test de limpieza de recursos"""
        # Configurar algunos datos
        config = StrategyConfig(
            strategy_type=StrategyType.ADAPTIVE_GRID,
            timeframes=["M15"],
            symbols=["EURUSD"]
        )
        self.engine.initialize_strategy_config("test_strategy", config)
        self.engine.start_strategy("test_strategy")
        self.engine.start_strategy_service()
        
        # Verificar que hay datos
        assert len(self.engine.strategy_configs) > 0
        assert len(self.engine.active_strategies) > 0
        
        # Ejecutar cleanup
        self.engine.cleanup()
        
        # Verificar que se limpió todo
        assert len(self.engine.strategy_configs) == 0
        assert len(self.engine.active_strategies) == 0
        assert len(self.engine.signal_history) == 0
        assert len(self.engine.active_signals) == 0
        assert not self.engine.strategies_running
        assert not self.engine.is_active
    
    def test_signal_strength_enum(self):
        """Test de la enumeración SignalStrength"""
        assert SignalStrength.WEAK.value == 1
        assert SignalStrength.MODERATE.value == 2
        assert SignalStrength.STRONG.value == 3
        assert SignalStrength.VERY_STRONG.value == 4
    
    def test_strategy_type_enum(self):
        """Test de la enumeración StrategyType"""
        assert StrategyType.ADAPTIVE_GRID.value == "adaptive_grid"
        assert StrategyType.MEAN_REVERSION.value == "mean_reversion"
        assert StrategyType.TREND_FOLLOWING.value == "trend_following"
    
    def test_trading_signal_dataclass(self):
        """Test de la estructura TradingSignal"""
        timestamp = datetime.now()
        signal = TradingSignal(
            symbol="EURUSD",
            timeframe="H1",
            signal_type="BUY",
            strength=SignalStrength.STRONG,
            price=1.0850,
            timestamp=timestamp,
            confidence=0.85,
            source="test",
            metadata={'test_key': 'test_value'}
        )
        
        assert signal.symbol == "EURUSD"
        assert signal.timeframe == "H1"
        assert signal.signal_type == "BUY"
        assert signal.strength == SignalStrength.STRONG
        assert signal.price == 1.0850
        assert signal.timestamp == timestamp
        assert signal.confidence == 0.85
        assert signal.source == "test"
        assert signal.metadata['test_key'] == 'test_value'

class TestStrategyEngineIntegration:
    """Tests de integración para StrategyEngine"""
    
    def test_integration_with_real_managers(self):
        """Test de integración con managers reales"""
        # Este test usa los managers reales en lugar de mocks
        engine = StrategyEngine()
        
        # Verificar que los managers están inicializados
        assert engine.config_manager is not None
        assert engine.logger_manager is not None
        assert engine.error_manager is not None
        assert engine.data_manager is not None
        assert engine.analytics_manager is not None
        
        # Test básico de funcionalidad
        config = StrategyConfig(
            strategy_type=StrategyType.ADAPTIVE_GRID,
            timeframes=["M15"],
            symbols=["EURUSD"]
        )
        
        result = engine.initialize_strategy_config("integration_test", config)
        assert result is True
        
        result = engine.start_strategy("integration_test")
        assert result is True
        
        # Cleanup
        engine.cleanup()

if __name__ == "__main__":
    # Ejecutar tests individuales para debugging
    test_engine = TestStrategyEngine()
    test_engine.setup_method()
    
    print("🧪 Testing StrategyEngine...")
    
    try:
        test_engine.test_initialization()
        print("✅ Test inicialización: PASSED")
        
        test_engine.test_strategy_config_initialization()
        print("✅ Test configuración: PASSED")
        
        test_engine.test_adaptive_grid_signal_generation()
        print("✅ Test generación señales: PASSED")
        
        test_engine.test_dynamic_position_size_calculation()
        print("✅ Test cálculo posición: PASSED")
        
        test_engine.test_get_strategy_status()
        print("✅ Test estado: PASSED")
        
        print("\n🎉 Todos los tests básicos PASSED!")
        
    except Exception as e:
        print(f"❌ Error en tests: {e}")
    finally:
        test_engine.teardown_method()
