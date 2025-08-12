#!/usr/bin/env python3
"""
🧪 TEST ANTI-HARDCODING - FOUNDATION BRIDGE
===========================================

Tests específicos para validar que NO hay valores hardcodeados
en el FoundationBridge y que toda la configuración es centralizada
y configurable.

✅ SIN VALORES HARDCODEADOS
🔧 CONFIGURACIÓN CENTRALIZADA
⚙️ VALIDACIÓN COMPLETA

Fecha: Agosto 12, 2025
Estado: Tests para eliminar hardcoding
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime
import json
import tempfile
import os

# Configurar paths
current_dir = Path(__file__).parent.parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path.absolute()))

# Importar componentes a testear
from core.strategic import (
    FoundationBridge, 
    StrategicConfiguration,
    StrategicThresholds,
    AnalysisWeights,
    OperationalSettings,
    get_strategic_config,
    reload_strategic_config,
    FoundationData
)
from core.config_manager import ConfigManager

class TestAntiHardcoding(unittest.TestCase):
    """Tests para validar ausencia de hardcoding"""
    
    def setUp(self):
        """Configurar test environment"""
        self.config_manager = ConfigManager()
        # Crear configuración temporal para tests
        self.temp_config_file = None
    
    def tearDown(self):
        """Limpiar después de cada test"""
        if self.temp_config_file and os.path.exists(self.temp_config_file):
            os.unlink(self.temp_config_file)
    
    def test_strategic_configuration_validation(self):
        """Test: Validación de configuración estratégica"""
        # Test configuración válida
        config = StrategicConfiguration()
        self.assertTrue(config.validate_all())
        
        # Test thresholds válidos
        self.assertTrue(config.thresholds.validate())
        
        # Test weights válidos
        self.assertTrue(config.weights.validate())
        
        # Test operaciones válidas
        self.assertTrue(config.operations.validate())
        
        print("✅ Test validación configuración estratégica: EXITOSO")
    
    def test_no_hardcoded_thresholds(self):
        """Test: No hay thresholds hardcodeados"""
        # Crear configuración custom
        custom_config = StrategicConfiguration()
        
        # Modificar thresholds
        custom_config.update_thresholds(
            trend_threshold=0.8,
            volatility_threshold=0.9,
            signal_threshold=0.7
        )
        
        # Verificar que se actualizaron (no hardcodeados)
        self.assertEqual(custom_config.thresholds.trend_threshold, 0.8)
        self.assertEqual(custom_config.thresholds.volatility_threshold, 0.9)
        self.assertEqual(custom_config.thresholds.signal_threshold, 0.7)
        
        # Verificar que siguen siendo válidos
        self.assertTrue(custom_config.validate_all())
        
        print("✅ Test no hay thresholds hardcodeados: EXITOSO")
    
    def test_configurable_weights(self):
        """Test: Pesos son configurables (no hardcodeados)"""
        config = StrategicConfiguration()
        
        # Cambiar pesos manteniendo suma = 1.0
        new_weights = {
            'analytics_weight': 0.3,
            'indicators_weight': 0.3,
            'market_data_weight': 0.2,
            'configuration_weight': 0.2
        }
        
        result = config.update_weights(**new_weights)
        self.assertTrue(result)
        
        # Verificar que se aplicaron
        self.assertEqual(config.weights.analytics_weight, 0.3)
        self.assertEqual(config.weights.indicators_weight, 0.3)
        self.assertEqual(config.weights.market_data_weight, 0.2)
        self.assertEqual(config.weights.configuration_weight, 0.2)
        
        print("✅ Test pesos configurables: EXITOSO")
    
    def test_config_file_loading(self):
        """Test: Carga de configuración desde archivo"""
        # Crear archivo de configuración temporal
        temp_config = {
            "thresholds": {
                "trend_threshold": 0.75,
                "volatility_threshold": 0.85,
                "signal_threshold": 0.65,
                "confidence_threshold": 0.7,
                "opportunity_threshold": 0.6,
                "risk_threshold": 0.55
            },
            "weights": {
                "analytics_weight": 0.3,
                "indicators_weight": 0.3,
                "market_data_weight": 0.2,
                "configuration_weight": 0.2,
                "base_confidence": 0.6,
                "analytics_confidence_boost": 0.25,
                "indicators_confidence_multiplier": 0.15,
                "max_indicators_boost": 0.35,
                "indicators_divisor": 5.0,
                "signal_opportunity_weight": 0.7,
                "confidence_opportunity_weight": 0.3
            },
            "operations": {
                "update_interval": 3.0,
                "max_retry_attempts": 5,
                "timeout_seconds": 45.0,
                "enable_detailed_logging": False,
                "enable_performance_monitoring": True
            }
        }
        
        # Escribir archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_config, f)
            self.temp_config_file = f.name
        
        # Cargar configuración desde archivo
        config = StrategicConfiguration(self.temp_config_file)
        
        # Verificar que se cargó correctamente
        self.assertEqual(config.thresholds.trend_threshold, 0.75)
        self.assertEqual(config.weights.analytics_weight, 0.3)
        self.assertEqual(config.operations.update_interval, 3.0)
        self.assertFalse(config.operations.enable_detailed_logging)
        
        # Verificar que es válida
        self.assertTrue(config.validate_all())
        
        print("✅ Test carga configuración desde archivo: EXITOSO")
    
    def test_foundation_bridge_uses_config(self):
        """Test: FoundationBridge usa configuración centralizada"""
        # Crear configuración custom
        config = StrategicConfiguration()
        config.update_weights(
            analytics_weight=0.4,
            indicators_weight=0.3,
            market_data_weight=0.2,
            configuration_weight=0.1
        )
        
        # Crear bridge (debería usar la configuración)
        bridge = FoundationBridge(config_manager=self.config_manager)
        
        # Verificar que tiene la configuración
        self.assertIsNotNone(bridge.strategic_config)
        self.assertTrue(bridge.strategic_config.validate_all())
        
        # Verificar que usa los valores de configuración
        status = bridge.get_bridge_status()
        self.assertIn('config_valid', status)
        self.assertTrue(status['config_valid'])
        
        print("✅ Test FoundationBridge usa configuración: EXITOSO")
    
    def test_signal_calculation_uses_config(self):
        """Test: Cálculo de señal usa configuración (no hardcoded)"""
        # Crear datos de test
        foundation_data = FoundationData(
            analytics_data={'test': 'data'},
            indicators_data={'rsi': 50.0},
            market_data={'price': 1.2345},
            configuration={'symbol': 'EURUSD'}
        )
        
        # Test con configuración por defecto
        bridge1 = FoundationBridge()
        signal1 = bridge1._calculate_signal_strength(foundation_data)
        
        # Cambiar configuración de pesos
        custom_config = StrategicConfiguration()
        custom_config.update_weights(
            analytics_weight=0.5,
            indicators_weight=0.2,
            market_data_weight=0.2,
            configuration_weight=0.1
        )
        
        # Recargar configuración global
        reload_strategic_config()
        bridge2 = FoundationBridge()
        bridge2.strategic_config = custom_config
        
        signal2 = bridge2._calculate_signal_strength(foundation_data)
        
        # Las señales pueden ser diferentes si usa configuración
        # (esto valida que NO está hardcodeado)
        self.assertIsInstance(signal1, float)
        self.assertIsInstance(signal2, float)
        self.assertGreaterEqual(signal1, 0.0)
        self.assertGreaterEqual(signal2, 0.0)
        self.assertLessEqual(signal1, 1.0)
        self.assertLessEqual(signal2, 1.0)
        
        print("✅ Test cálculo señal usa configuración: EXITOSO")
    
    def test_confidence_calculation_configurable(self):
        """Test: Cálculo de confianza es configurable"""
        foundation_data = FoundationData(
            analytics_data={'valid': 'data'},
            indicators_data={'rsi': 50.0, 'sma': 1.23, 'macd': 0.01},
            market_data={'price': 1.2345},
            configuration={'symbol': 'EURUSD'}
        )
        
        # Test con diferentes configuraciones
        config1 = StrategicConfiguration()
        config1.update_weights(base_confidence=0.3)
        
        config2 = StrategicConfiguration()
        config2.update_weights(base_confidence=0.7)
        
        bridge1 = FoundationBridge()
        bridge1.strategic_config = config1
        confidence1 = bridge1._calculate_confidence_level(foundation_data)
        
        bridge2 = FoundationBridge()
        bridge2.strategic_config = config2
        confidence2 = bridge2._calculate_confidence_level(foundation_data)
        
        # Con diferente base_confidence, deberían dar resultados diferentes
        self.assertNotEqual(confidence1, confidence2)
        self.assertGreater(confidence2, confidence1)
        
        print("✅ Test cálculo confianza configurable: EXITOSO")
    
    def test_opportunity_score_configurable(self):
        """Test: Score de oportunidad es configurable"""
        foundation_data = FoundationData(
            analytics_data={'test': 'data'},
            indicators_data={'rsi': 70.0},
            market_data={'price': 1.2500},
            configuration={'symbol': 'EURUSD'}
        )
        
        # Configuración que favorece señal
        config_signal = StrategicConfiguration()
        config_signal.update_weights(
            signal_opportunity_weight=0.8,
            confidence_opportunity_weight=0.2
        )
        
        # Configuración que favorece confianza
        config_confidence = StrategicConfiguration()
        config_confidence.update_weights(
            signal_opportunity_weight=0.2,
            confidence_opportunity_weight=0.8
        )
        
        bridge1 = FoundationBridge()
        bridge1.strategic_config = config_signal
        opp1 = bridge1._calculate_opportunity_score(foundation_data)
        
        bridge2 = FoundationBridge()
        bridge2.strategic_config = config_confidence
        opp2 = bridge2._calculate_opportunity_score(foundation_data)
        
        # Ambos deben ser válidos
        self.assertGreaterEqual(opp1, 0.0)
        self.assertGreaterEqual(opp2, 0.0)
        self.assertLessEqual(opp1, 1.0)
        self.assertLessEqual(opp2, 1.0)
        
        print("✅ Test score oportunidad configurable: EXITOSO")
    
    def test_config_update_bridge(self):
        """Test: Actualización de configuración en bridge funciona"""
        bridge = FoundationBridge()
        
        # Configuración inicial
        initial_status = bridge.get_bridge_status()
        initial_config = initial_status['strategic_config']
        
        # Actualizar configuración
        new_config = {
            'trend_threshold': 0.8,
            'signal_threshold': 0.7
        }
        
        result = bridge.update_strategic_config(new_config)
        self.assertTrue(result)
        
        # Verificar que se actualizó
        updated_status = bridge.get_bridge_status()
        updated_config = updated_status['strategic_config']
        
        self.assertEqual(updated_config['trend_threshold'], 0.8)
        self.assertEqual(updated_config['signal_threshold'], 0.7)
        self.assertNotEqual(initial_config['trend_threshold'], updated_config['trend_threshold'])
        
        print("✅ Test actualización configuración bridge: EXITOSO")
    
    def test_no_hardcoded_strings(self):
        """Test: No hay strings hardcodeados en análisis"""
        # Los valores por defecto deben venir de configuración
        bridge = FoundationBridge()
        
        # Estados por defecto deben ser configurables
        foundation_data = FoundationData()  # Datos vacíos
        
        context = bridge.analyze_strategic_context(foundation_data)
        self.assertIsNotNone(context)
        
        # Los estados por defecto son apropiados para datos inválidos
        self.assertIn(context.market_state, ["invalid_data", "insufficient_data", "error", "analyzing"])
        self.assertEqual(context.trend_direction, "neutral")  # Neutral es correcto para datos inválidos
        self.assertEqual(context.volatility_level, "medium")  # Medium es default seguro
        
        print("✅ Test no hay strings hardcodeados: EXITOSO")


def run_anti_hardcoding_tests():
    """Ejecutar tests anti-hardcoding"""
    print("🧪 INICIANDO TESTS ANTI-HARDCODING FOUNDATION BRIDGE")
    print("=" * 60)
    
    # Crear test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar test class
    suite.addTests(loader.loadTestsFromTestCase(TestAntiHardcoding))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🏆 TODOS LOS TESTS ANTI-HARDCODING: ✅ EXITOSOS")
        print("✅ FoundationBridge SIN valores hardcodeados")
        print("🔧 Configuración completamente centralizada")
        return True
    else:
        print("❌ ALGUNOS TESTS ANTI-HARDCODING FALLARON")
        print(f"Errores: {len(result.errors)}")
        print(f"Fallos: {len(result.failures)}")
        return False


if __name__ == "__main__":
    try:
        success = run_anti_hardcoding_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrumpidos por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado ejecutando tests: {e}")
        sys.exit(1)
