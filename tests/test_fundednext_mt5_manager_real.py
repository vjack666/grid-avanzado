"""
TEST REAL FUNDEDNEXT MT5 MANAGER - SÓTANO 1
==========================================
Tests reales para el gestor exclusivo de FundedNext MT5 Terminal

PUERTA: PUERTA-S1-FUNDEDNEXT
VERSIÓN: v1.0.0  
FECHA: 2025-08-11
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

# Agregar path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Imports del sistema
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager  
from src.core.error_manager import ErrorManager

# Import del módulo a testear
from src.core.fundednext_mt5_manager import FundedNextMT5Manager


class TestFundedNextMT5ManagerReal:
    """Tests reales para FundedNextMT5Manager"""
    
    @pytest.fixture
    def real_manager(self):
        """Fixture con FundedNextMT5Manager real"""
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger, config)
        
        return FundedNextMT5Manager(
            config=config,
            logger=logger,
            error=error
        )
    
    def test_manager_initialization_real(self, real_manager):
        """Test inicialización real del manager"""
        assert real_manager.component_id == "PUERTA-S1-FUNDEDNEXT"
        assert real_manager.version == "v1.0.0"
        assert real_manager.status == "initialized"
        
        # Verificar configuración
        assert isinstance(real_manager.fundednext_config, dict)
        assert "terminal_path" in real_manager.fundednext_config
        assert "exclusive_mode" in real_manager.fundednext_config
        
        # Verificar métricas iniciales
        assert real_manager.manager_metrics["connection_attempts"] == 0
        assert real_manager.manager_metrics["successful_connections"] == 0
    
    def test_terminal_path_exists(self, real_manager):
        """Test verificar que la ruta de FundedNext existe"""
        terminal_path = real_manager.fundednext_config["terminal_path"]
        
        # El test debe verificar si el terminal existe en el sistema
        if os.path.exists(terminal_path):
            assert True  # Terminal existe
            print(f"✅ FundedNext MT5 Terminal encontrado en: {terminal_path}")
        else:
            pytest.skip(f"FundedNext MT5 Terminal no está instalado en: {terminal_path}")
    
    def test_check_fundednext_terminal_status(self, real_manager):
        """Test verificar estado real del terminal"""
        is_running, pid = real_manager.is_fundednext_terminal_running()
        
        assert isinstance(is_running, bool)
        if is_running:
            assert isinstance(pid, int)
            assert pid > 0
            print(f"✅ FundedNext MT5 Terminal ejecutándose: PID {pid}")
        else:
            assert pid is None
            print("ℹ️ FundedNext MT5 Terminal no está ejecutándose")
    
    def test_check_other_mt5_terminals(self, real_manager):
        """Test verificar otros terminales MT5"""
        other_terminals = real_manager.get_other_mt5_terminals()
        
        assert isinstance(other_terminals, list)
        
        if other_terminals:
            print(f"ℹ️ Encontrados {len(other_terminals)} otros terminales MT5:")
            for terminal in other_terminals:
                print(f"  - {terminal['name']} (PID: {terminal['pid']})")
        else:
            print("✅ No hay otros terminales MT5 ejecutándose")
    
    def test_manager_status_real(self, real_manager):
        """Test obtener estado real del manager"""
        status = real_manager.get_manager_status()
        
        # Verificar estructura del status
        assert "component_id" in status
        assert "version" in status
        assert "terminal_status" in status
        assert "configuration" in status
        assert "metrics" in status
        
        # Verificar datos del terminal
        terminal_status = status["terminal_status"]
        assert "is_running" in terminal_status
        assert "process_id" in terminal_status
        assert "terminal_path" in terminal_status
        
        print(f"📊 Estado del Manager:")
        print(f"  - Terminal ejecutándose: {terminal_status['is_running']}")
        print(f"  - PID: {terminal_status['process_id']}")
        print(f"  - Otros terminales: {status['other_terminals']['count']}")
    
    def test_health_check_real(self, real_manager):
        """Test health check real del sistema"""
        health = real_manager.health_check()
        
        # Verificar estructura del health check
        assert "timestamp" in health
        assert "overall_health" in health
        assert "terminal_running" in health
        assert "configuration_valid" in health
        
        print(f"🏥 Health Check:")
        print(f"  - Salud general: {health['overall_health']}")
        print(f"  - Terminal ejecutándose: {health['terminal_running']}")
        print(f"  - Configuración válida: {health['configuration_valid']}")
        print(f"  - Modo exclusivo: {health.get('exclusive_mode', 'N/A')}")
    
    @pytest.mark.skipif(
        not os.path.exists(r"C:\Program Files\FundedNext MT5 Terminal\terminal64.exe"),
        reason="FundedNext MT5 Terminal no está instalado"
    )
    def test_ensure_terminal_real(self, real_manager):
        """Test asegurar terminal real (solo si está instalado)"""
        # Configurar para no cerrar otros terminales por seguridad
        real_manager.fundednext_config["close_other_terminals"] = False
        real_manager.fundednext_config["auto_open_if_closed"] = False
        
        # Verificar lógica de detección
        result = real_manager.ensure_fundednext_terminal()
        
        # El resultado depende de si el terminal está ejecutándose
        is_running, _ = real_manager.is_fundednext_terminal_running()
        
        if is_running:
            assert result is True
            print("✅ FundedNext MT5 Terminal verificado correctamente")
        else:
            # Si no está ejecutándose y auto_open está deshabilitado
            assert result is False
            print("ℹ️ FundedNext MT5 Terminal no está ejecutándose (auto-apertura deshabilitada)")


class TestFundedNextMT5ManagerIntegration:
    """Tests de integración real con el sistema"""
    
    @pytest.fixture
    def integrated_manager(self):
        """Fixture con manager integrado al sistema"""
        config = ConfigManager()
        logger = LoggerManager()
        error = ErrorManager(logger, config)
        
        return FundedNextMT5Manager(
            config=config,
            logger=logger,
            error=error
        )
    
    def test_integration_with_core_system(self, integrated_manager):
        """Test integración con sistema core"""
        # Verificar integración con LoggerManager
        assert integrated_manager.logger is not None
        assert hasattr(integrated_manager.logger, 'log_info')
        
        # Verificar integración con ErrorManager
        assert integrated_manager.error is not None
        assert hasattr(integrated_manager.error, '_log_error')
        
        # Verificar integración con ConfigManager
        assert integrated_manager.config is not None
    
    def test_real_process_detection(self, integrated_manager):
        """Test detección real de procesos"""
        # Test real de detección de procesos MT5
        other_terminals = integrated_manager.get_other_mt5_terminals()
        
        # Verificar que el método funciona sin errores
        assert isinstance(other_terminals, list)
        
        # Si hay terminales, verificar estructura
        for terminal in other_terminals:
            assert "pid" in terminal
            assert "name" in terminal
            assert "exe" in terminal
            assert isinstance(terminal["pid"], int)
            assert terminal["pid"] > 0
    
    def test_configuration_validation(self, integrated_manager):
        """Test validación real de configuración"""
        config = integrated_manager.fundednext_config
        
        # Verificar configuraciones críticas
        assert config["terminal_path"].endswith("terminal64.exe")
        assert config["terminal_name"] == "FundedNext MT5 Terminal"
        assert config["process_name"] == "terminal64.exe"
        assert isinstance(config["exclusive_mode"], bool)
        assert isinstance(config["auto_open_if_closed"], bool)
        
        # Verificar timeouts razonables
        assert 0 < config["startup_timeout"] <= 120
        assert 0 < config["connection_timeout"] <= 30
        assert config["max_connection_attempts"] >= 1
    
    def test_metrics_tracking(self, integrated_manager):
        """Test seguimiento real de métricas"""
        initial_health_checks = integrated_manager.manager_metrics["health_checks"]
        
        # Ejecutar health check
        health = integrated_manager.health_check()
        
        # Verificar que las métricas se actualizaron
        assert integrated_manager.manager_metrics["health_checks"] == initial_health_checks + 1
        assert health is not None
        assert isinstance(health, dict)


def test_fundednext_manager_import():
    """Test que el módulo se puede importar correctamente"""
    try:
        from src.core.fundednext_mt5_manager import FundedNextMT5Manager
        assert FundedNextMT5Manager is not None
        print("✅ FundedNextMT5Manager importado correctamente")
    except ImportError as e:
        pytest.fail(f"Error importando FundedNextMT5Manager: {e}")


if __name__ == "__main__":
    # Ejecutar tests específicos para desarrollo
    pytest.main([__file__, "-v", "--tb=short", "-s"])
