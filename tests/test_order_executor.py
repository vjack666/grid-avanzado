"""
TEST ORDEREXECUTOR - PUERTA-PE-EXECUTOR
======================================
Tests para el componente crítico OrderExecutor que conecta
señales del StrategyEngine con ejecución real en MT5.

TESTS INCLUIDOS:
- Inicialización del OrderExecutor
- Validación de señales
- Conversión TradingSignal → OrderRequest  
- Mock execution (sin MT5 real)
- Métricas y estado
- Integration básica

PROTOCOLO: Trading Grid - Piso Ejecutor
FECHA: 2025-08-12
"""

import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

# Añadir path del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Imports del sistema
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager

# Import del OrderExecutor
from src.core.live_trading.order_executor import OrderExecutor, OrderStatus, ExecutedOrder

# Mock de TradingSignal para tests
class MockTradingSignal:
    def __init__(self, symbol="EURUSD", signal_type="BUY", price=1.0850, confidence=0.8, source="test"):
        self.symbol = symbol
        self.signal_type = signal_type
        self.price = price
        self.confidence = confidence
        self.source = source
        self.timestamp = datetime.now()

class TestOrderExecutor:
    """Suite de tests para OrderExecutor"""
    
    @pytest.fixture
    def config_manager(self):
        """ConfigManager mock para tests"""
        return ConfigManager()
    
    @pytest.fixture
    def logger_manager(self):
        """LoggerManager para tests"""
        return LoggerManager()
    
    @pytest.fixture
    def error_manager(self, logger_manager, config_manager):
        """ErrorManager para tests"""
        return ErrorManager(logger_manager=logger_manager, config_manager=config_manager)
    
    @pytest.fixture
    def mock_fundednext_manager(self):
        """Mock del FundedNextMT5Manager"""
        mock_manager = Mock()
        mock_manager.ensure_fundednext_terminal.return_value = True
        mock_manager.connect_to_mt5.return_value = True
        mock_manager.get_connection_status.return_value = "connected"
        return mock_manager
    
    @pytest.fixture
    def order_executor(self, config_manager, logger_manager, error_manager, mock_fundednext_manager):
        """OrderExecutor para tests"""
        return OrderExecutor(
            config_manager=config_manager,
            logger_manager=logger_manager,
            error_manager=error_manager,
            fundednext_manager=mock_fundednext_manager
        )
    
    def test_order_executor_initialization(self, order_executor):
        """Test inicialización del OrderExecutor"""
        assert order_executor.component_id == "PUERTA-PE-EXECUTOR"
        assert order_executor.version == "v1.0.0"
        assert order_executor.is_active == False  # No inicializado aún
        assert order_executor.orders_enabled == True
        assert isinstance(order_executor.execution_metrics, dict)
        assert order_executor.execution_metrics['total_signals_received'] == 0
    
    def test_initialize_executor_success(self, order_executor):
        """Test inicialización exitosa del executor"""
        result = order_executor.initialize_executor()
        
        assert result == True
        assert order_executor.is_active == True
        
        # Verificar que se llamaron los métodos del manager
        order_executor.fundednext_manager.ensure_fundednext_terminal.assert_called_once()
        order_executor.fundednext_manager.connect_to_mt5.assert_called_once()
    
    def test_initialize_executor_failure(self, order_executor):
        """Test fallo en inicialización"""
        # Simular fallo de conexión
        order_executor.fundednext_manager.ensure_fundednext_terminal.return_value = False
        
        result = order_executor.initialize_executor()
        
        assert result == False
        assert order_executor.is_active == False
    
    def test_validate_signal_success(self, order_executor):
        """Test validación exitosa de señal"""
        # Crear señal válida
        signal = MockTradingSignal()
        
        with patch('MetaTrader5.symbol_info') as mock_symbol_info:
            mock_symbol_info.return_value = Mock()  # Symbol info válido
            
            result = order_executor._validate_signal(signal)
            assert result == True
    
    def test_validate_signal_invalid_type(self, order_executor):
        """Test validación con tipo de señal inválido"""
        signal = MockTradingSignal(signal_type="INVALID")
        
        result = order_executor._validate_signal(signal)
        assert result == False
    
    def test_validate_signal_low_confidence(self, order_executor):
        """Test validación con baja confianza"""
        signal = MockTradingSignal(confidence=0.3)  # Baja confianza
        
        with patch('MetaTrader5.symbol_info') as mock_symbol_info:
            mock_symbol_info.return_value = Mock()
            
            result = order_executor._validate_signal(signal)
            assert result == False
    
    def test_convert_signal_to_order_buy(self, order_executor):
        """Test conversión señal BUY a orden"""
        signal = MockTradingSignal(signal_type="BUY", confidence=0.8)
        
        order_request = order_executor._convert_signal_to_order(signal)
        
        assert order_request is not None
        assert order_request.symbol == "EURUSD"
        assert order_request.type == 0  # BUY order type
        assert order_request.price == 1.0850
        assert order_request.volume > 0
        assert "test" in order_request.comment
    
    def test_convert_signal_to_order_sell(self, order_executor):
        """Test conversión señal SELL a orden"""
        signal = MockTradingSignal(signal_type="SELL", confidence=0.9)
        
        order_request = order_executor._convert_signal_to_order(signal)
        
        assert order_request is not None
        assert order_request.symbol == "EURUSD"
        assert order_request.type == 1  # SELL order type
        assert order_request.price == 1.0850
        assert order_request.volume > 0
    
    def test_process_signal_not_active(self, order_executor):
        """Test procesamiento cuando executor no está activo"""
        signal = MockTradingSignal()
        
        # Executor no inicializado (is_active = False)
        result = order_executor.process_signal(signal)
        
        assert result == False
        assert order_executor.execution_metrics['total_signals_received'] == 0
    
    def test_process_signal_orders_disabled(self, order_executor):
        """Test procesamiento con órdenes deshabilitadas"""
        signal = MockTradingSignal()
        
        order_executor.is_active = True
        order_executor.orders_enabled = False
        
        result = order_executor.process_signal(signal)
        
        assert result == False
    
    @patch('MetaTrader5.order_send')
    @patch('MetaTrader5.symbol_info')
    def test_process_signal_success_mock(self, mock_symbol_info, mock_order_send, order_executor):
        """Test procesamiento exitoso con mock de MT5"""
        # Setup mocks
        mock_symbol_info.return_value = Mock()
        mock_result = Mock()
        mock_result.retcode = 10009  # TRADE_RETCODE_DONE
        mock_result.order = 12345
        mock_result.deal = 67890
        mock_result.volume = 0.01
        mock_result.price = 1.0850
        mock_order_send.return_value = mock_result
        
        # Preparar executor
        order_executor.is_active = True
        signal = MockTradingSignal()
        
        # Procesar señal
        result = order_executor.process_signal(signal)
        
        assert result == True
        assert order_executor.execution_metrics['total_signals_received'] == 1
        assert order_executor.execution_metrics['total_orders_executed'] == 1
        assert len(order_executor.executed_orders) == 1
        
        executed_order = order_executor.executed_orders[0]
        assert executed_order.status == OrderStatus.EXECUTED
        assert executed_order.ticket == 67890
    
    def test_get_execution_status(self, order_executor):
        """Test obtener estado del executor"""
        status = order_executor.get_execution_status()
        
        assert isinstance(status, dict)
        assert 'component_id' in status
        assert 'version' in status
        assert 'is_active' in status
        assert 'metrics' in status
        assert status['component_id'] == "PUERTA-PE-EXECUTOR"
        assert status['version'] == "v1.0.0"
    
    def test_enable_disable_orders(self, order_executor):
        """Test habilitar/deshabilitar órdenes"""
        # Inicialmente habilitado
        assert order_executor.orders_enabled == True
        
        # Deshabilitar
        order_executor.enable_orders(False)
        assert order_executor.orders_enabled == False
        
        # Habilitar
        order_executor.enable_orders(True)
        assert order_executor.orders_enabled == True
    
    def test_cleanup(self, order_executor):
        """Test cleanup del executor"""
        order_executor.is_active = True
        order_executor.orders_enabled = True
        
        order_executor.cleanup()
        
        assert order_executor.is_active == False
        assert order_executor.orders_enabled == False
    
    def test_update_success_metrics(self, order_executor):
        """Test actualización de métricas de éxito"""
        executed_order = ExecutedOrder(
            order_id=1,
            ticket=12345,
            symbol="EURUSD",
            type="BUY",
            volume=0.01,
            price=1.0850,
            timestamp=datetime.now(),
            status=OrderStatus.EXECUTED,
            execution_time_ms=150
        )
        
        initial_executed = order_executor.execution_metrics['total_orders_executed']
        
        order_executor._update_success_metrics(executed_order)
        
        assert order_executor.execution_metrics['total_orders_executed'] == initial_executed + 1
        assert order_executor.execution_metrics['avg_execution_time_ms'] > 0
        assert order_executor.last_execution is not None
    
    def test_update_failure_metrics(self, order_executor):
        """Test actualización de métricas de fallo"""
        initial_failed = order_executor.execution_metrics['total_orders_failed']
        
        order_executor._update_failure_metrics()
        
        assert order_executor.execution_metrics['total_orders_failed'] == initial_failed + 1

# Test de integración básica
class TestOrderExecutorIntegration:
    """Tests de integración del OrderExecutor"""
    
    def test_full_signal_processing_flow(self):
        """Test del flujo completo de procesamiento"""
        print("🧪 Test integración OrderExecutor")
        
        # Crear components reales (sin MT5)
        config_manager = ConfigManager()
        logger_manager = LoggerManager()
        error_manager = ErrorManager(logger_manager, config_manager)
        
        # Mock del FundedNext manager
        mock_fundednext = Mock()
        mock_fundednext.ensure_fundednext_terminal.return_value = True
        mock_fundednext.connect_to_mt5.return_value = True
        mock_fundednext.get_connection_status.return_value = "connected"
        
        # Crear executor
        executor = OrderExecutor(
            config_manager=config_manager,
            logger_manager=logger_manager,
            error_manager=error_manager,
            fundednext_manager=mock_fundednext
        )
        
        # Test inicialización
        assert executor.initialize_executor() == True
        assert executor.is_active == True
        
        # Test estado
        status = executor.get_execution_status()
        assert status['is_active'] == True
        assert status['orders_enabled'] == True
        
        # Test cleanup
        executor.cleanup()
        assert executor.is_active == False
        
        print("✅ Test integración completado")

if __name__ == "__main__":
    # Ejecutar tests básicos
    print("🧪 EJECUTANDO TESTS ORDEREXECUTOR")
    print("=" * 40)
    
    # Test de integración
    test_integration = TestOrderExecutorIntegration()
    test_integration.test_full_signal_processing_flow()
    
    print("\n✅ Tests básicos completados")
    print("💡 Para tests completos ejecutar: pytest test_order_executor.py -v")
