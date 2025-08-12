#!/usr/bin/env python3
"""
🧪 TEST FOUNDATION BRIDGE - PUERTA-S3-INTEGRATION
================================================

Tests unitarios para validar el FoundationBridge - tu "enlace estrategia-bases"
que conecta SÓTANO 1 (bases) con SÓTANO 3 (estratégico).

✨ TU VISIÓN: "Enlace estrategia-bases"
🚪 PUERTA: PUERTA-S3-INTEGRATION  
🎯 PROPÓSITO: Validar conectividad y funcionalidad

Fecha: Agosto 12, 2025
Estado: Implementado y listo para validación
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Configurar paths
current_dir = Path(__file__).parent.parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path.absolute()))

# Importar componentes a testear
from core.strategic import FoundationBridge, StrategicContext, FoundationData
from core.config_manager import ConfigManager

class TestFoundationBridge(unittest.TestCase):
    """Tests para FoundationBridge - Tu enlace estrategia-bases"""
    
    def setUp(self):
        """Configurar test environment"""
        self.config_manager = ConfigManager()
        self.bridge = FoundationBridge(config_manager=self.config_manager)
    
    def tearDown(self):
        """Limpiar después de cada test"""
        if self.bridge._bridge_active:
            self.bridge.deactivate_bridge()
    
    def test_foundation_bridge_initialization(self):
        """Test: FoundationBridge se inicializa correctamente"""
        # Verificar que se inicializó
        self.assertIsNotNone(self.bridge)
        self.assertIsNotNone(self.bridge.config_manager)
        self.assertIsNotNone(self.bridge.logger)
        
        # Verificar estado inicial
        self.assertFalse(self.bridge._bridge_active)
        self.assertIsNone(self.bridge._foundation_data)
        self.assertIsNone(self.bridge._strategic_context)
        
        # Verificar configuración estratégica
        self.assertIsNotNone(self.bridge.strategic_config)
        self.assertTrue(self.bridge.strategic_config.validate_all())
        
        print("✅ Test inicialización FoundationBridge: EXITOSO")
    
    def test_bridge_activation_deactivation(self):
        """Test: Activación y desactivación del puente"""
        # Test activación
        result = self.bridge.activate_bridge()
        self.assertTrue(result)
        self.assertTrue(self.bridge._bridge_active)
        
        # Test desactivación
        result = self.bridge.deactivate_bridge()
        self.assertTrue(result)
        self.assertFalse(self.bridge._bridge_active)
        
        print("✅ Test activación/desactivación: EXITOSO")
    
    def test_bridge_status(self):
        """Test: Estado del puente"""
        # Estado inicial
        status = self.bridge.get_bridge_status()
        self.assertIsInstance(status, dict)
        self.assertIn('bridge_active', status)
        self.assertIn('strategic_config', status)
        self.assertFalse(status['bridge_active'])
        
        # Estado después de activación
        self.bridge.activate_bridge()
        status = self.bridge.get_bridge_status()
        self.assertTrue(status['bridge_active'])
        
        print("✅ Test estado del puente: EXITOSO")
    
    def test_strategic_config_update(self):
        """Test: Actualización de configuración estratégica"""
        new_config = {
            'trend_threshold': 0.8,
            'signal_threshold': 0.7
        }
        
        result = self.bridge.update_strategic_config(new_config)
        self.assertTrue(result)
        
        # Verificar que se actualizó
        status = self.bridge.get_bridge_status()
        config = status['strategic_config']
        self.assertEqual(config['trend_threshold'], 0.8)
        self.assertEqual(config['signal_threshold'], 0.7)
        
        print("✅ Test actualización configuración: EXITOSO")
    
    def test_foundation_data_extraction(self):
        """Test: Extracción de datos fundamentales"""
        # Activar bridge
        self.bridge.activate_bridge()
        
        # Extraer datos
        foundation_data = self.bridge.extract_foundation_data()
        
        # Verificar datos
        self.assertIsNotNone(foundation_data)
        self.assertIsInstance(foundation_data, FoundationData)
        self.assertIsInstance(foundation_data.analytics_data, dict)
        self.assertIsInstance(foundation_data.indicators_data, dict)
        self.assertIsInstance(foundation_data.market_data, dict)
        self.assertIsInstance(foundation_data.configuration, dict)
        self.assertIsInstance(foundation_data.timestamp, datetime)
        
        print("✅ Test extracción datos fundamentales: EXITOSO")
    
    def test_strategic_context_analysis(self):
        """Test: Análisis de contexto estratégico"""
        # Crear datos de prueba
        foundation_data = FoundationData(
            analytics_data={'test': 'data'},
            indicators_data={'rsi': 50.0, 'sma_20': 1.2345},
            market_data={'price': 1.2345, 'volume': 1000},
            configuration={'symbol': 'EURUSD'},
            timestamp=datetime.now()
        )
        
        # Analizar contexto
        strategic_context = self.bridge.analyze_strategic_context(foundation_data)
        
        # Verificar contexto
        self.assertIsNotNone(strategic_context)
        self.assertIsInstance(strategic_context, StrategicContext)
        self.assertIsInstance(strategic_context.market_state, str)
        self.assertIsInstance(strategic_context.trend_direction, str)
        self.assertIsInstance(strategic_context.volatility_level, str)
        self.assertIsInstance(strategic_context.signal_strength, float)
        self.assertIsInstance(strategic_context.confidence_level, float)
        self.assertIsInstance(strategic_context.risk_assessment, str)
        self.assertIsInstance(strategic_context.opportunity_score, float)
        
        # Verificar rangos
        self.assertGreaterEqual(strategic_context.signal_strength, 0.0)
        self.assertLessEqual(strategic_context.signal_strength, 1.0)
        self.assertGreaterEqual(strategic_context.confidence_level, 0.0)
        self.assertLessEqual(strategic_context.confidence_level, 1.0)
        self.assertGreaterEqual(strategic_context.opportunity_score, 0.0)
        self.assertLessEqual(strategic_context.opportunity_score, 1.0)
        
        print("✅ Test análisis contexto estratégico: EXITOSO")
    
    def test_foundation_data_validation(self):
        """Test: Validación de datos fundamentales"""
        # Datos válidos
        valid_data = FoundationData(
            analytics_data={'test': 'data'},
            indicators_data={'rsi': 50.0},
            market_data={'price': 1.2345},
            configuration={'symbol': 'EURUSD'}
        )
        self.assertTrue(valid_data.is_valid())
        
        # Datos inválidos (vacíos)
        invalid_data = FoundationData()
        self.assertFalse(invalid_data.is_valid())
        
        # Datos parcialmente válidos
        partial_data = FoundationData(
            analytics_data={'test': 'data'},
            indicators_data={},
            market_data={},
            configuration={}
        )
        self.assertFalse(partial_data.is_valid())
        
        print("✅ Test validación datos fundamentales: EXITOSO")
    
    def test_strategic_context_serialization(self):
        """Test: Serialización de contexto estratégico"""
        context = StrategicContext(
            market_state="analyzing",
            trend_direction="bullish",
            volatility_level="medium",
            signal_strength=0.75,
            confidence_level=0.85,
            risk_assessment="low",
            opportunity_score=0.80,
            timestamp=datetime.now()
        )
        
        # Serializar a dict
        context_dict = context.to_dict()
        
        # Verificar serialización
        self.assertIsInstance(context_dict, dict)
        self.assertEqual(context_dict['market_state'], 'analyzing')
        self.assertEqual(context_dict['trend_direction'], 'bullish')
        self.assertEqual(context_dict['signal_strength'], 0.75)
        self.assertIn('timestamp', context_dict)
        
        print("✅ Test serialización contexto: EXITOSO")
    
    def test_bridge_error_handling(self):
        """Test: Manejo de errores del puente"""
        # Test activación múltiple
        self.bridge.activate_bridge()
        result = self.bridge.activate_bridge()  # Segunda activación
        self.assertTrue(result)  # Debe manejar gracefully
        
        # Test desactivación múltiple
        self.bridge.deactivate_bridge()
        result = self.bridge.deactivate_bridge()  # Segunda desactivación
        self.assertTrue(result)  # Debe manejar gracefully
        
        # Test extracción sin activación
        result = self.bridge.deactivate_bridge()
        foundation_data = self.bridge.extract_foundation_data()
        self.assertIsNone(foundation_data)  # Debe retornar None
        
        print("✅ Test manejo de errores: EXITOSO")
    
    def test_integration_sotano_1_3(self):
        """Test: Integración completa SÓTANO 1 ↔ SÓTANO 3"""
        # Activar puente
        self.assertTrue(self.bridge.activate_bridge())
        
        # Flujo completo: extracción → análisis
        foundation_data = self.bridge.extract_foundation_data()
        self.assertIsNotNone(foundation_data)
        
        strategic_context = self.bridge.analyze_strategic_context(foundation_data)
        self.assertIsNotNone(strategic_context)
        
        # Verificar que el bridge mantuvo estado
        status = self.bridge.get_bridge_status()
        self.assertTrue(status['bridge_active'])
        self.assertTrue(status['has_foundation_data'])
        self.assertTrue(status['has_strategic_context'])
        
        print("✅ Test integración SÓTANO 1 ↔ SÓTANO 3: EXITOSO")


class TestStrategicContext(unittest.TestCase):
    """Tests para StrategicContext"""
    
    def test_strategic_context_creation(self):
        """Test: Creación de contexto estratégico"""
        context = StrategicContext()
        
        # Verificar valores por defecto
        self.assertEqual(context.market_state, "analyzing")
        self.assertEqual(context.trend_direction, "neutral")
        self.assertEqual(context.volatility_level, "medium")
        self.assertEqual(context.signal_strength, 0.0)
        self.assertEqual(context.confidence_level, 0.0)
        self.assertEqual(context.risk_assessment, "medium")
        self.assertEqual(context.opportunity_score, 0.0)
        self.assertIsInstance(context.timestamp, datetime)
        
        print("✅ Test creación StrategicContext: EXITOSO")
    
    def test_strategic_context_custom_values(self):
        """Test: Contexto estratégico con valores personalizados"""
        custom_time = datetime.now()
        context = StrategicContext(
            market_state="trending",
            trend_direction="bullish",
            volatility_level="high",
            signal_strength=0.8,
            confidence_level=0.9,
            risk_assessment="low",
            opportunity_score=0.85,
            timestamp=custom_time
        )
        
        # Verificar valores personalizados
        self.assertEqual(context.market_state, "trending")
        self.assertEqual(context.trend_direction, "bullish")
        self.assertEqual(context.volatility_level, "high")
        self.assertEqual(context.signal_strength, 0.8)
        self.assertEqual(context.confidence_level, 0.9)
        self.assertEqual(context.risk_assessment, "low")
        self.assertEqual(context.opportunity_score, 0.85)
        self.assertEqual(context.timestamp, custom_time)
        
        print("✅ Test StrategicContext personalizado: EXITOSO")


class TestFoundationData(unittest.TestCase):
    """Tests para FoundationData"""
    
    def test_foundation_data_creation(self):
        """Test: Creación de datos de fundamento"""
        data = FoundationData()
        
        # Verificar valores por defecto
        self.assertIsInstance(data.analytics_data, dict)
        self.assertIsInstance(data.indicators_data, dict)
        self.assertIsInstance(data.market_data, dict)
        self.assertIsInstance(data.configuration, dict)
        self.assertIsInstance(data.timestamp, datetime)
        
        # Datos vacíos no son válidos
        self.assertFalse(data.is_valid())
        
        print("✅ Test creación FoundationData: EXITOSO")
    
    def test_foundation_data_validation_logic(self):
        """Test: Lógica de validación de FoundationData"""
        # Caso 1: Todos los datos presentes = válido
        data1 = FoundationData(
            analytics_data={'key': 'value'},
            indicators_data={'rsi': 50},
            market_data={'price': 1.23},
            configuration={'symbol': 'EURUSD'}
        )
        self.assertTrue(data1.is_valid())
        
        # Caso 2: Un campo vacío = inválido
        data2 = FoundationData(
            analytics_data={},  # Vacío
            indicators_data={'rsi': 50},
            market_data={'price': 1.23},
            configuration={'symbol': 'EURUSD'}
        )
        self.assertFalse(data2.is_valid())
        
        # Caso 3: Múltiples campos vacíos = inválido
        data3 = FoundationData(
            analytics_data={},
            indicators_data={},
            market_data={'price': 1.23},
            configuration={'symbol': 'EURUSD'}
        )
        self.assertFalse(data3.is_valid())
        
        print("✅ Test validación FoundationData: EXITOSO")


def run_test_suite():
    """Ejecutar suite completa de tests"""
    print("🧪 INICIANDO TESTS FOUNDATION BRIDGE - ENLACE ESTRATEGIA-BASES")
    print("=" * 70)
    
    # Crear test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFoundationBridge))
    suite.addTests(loader.loadTestsFromTestCase(TestStrategicContext))
    suite.addTests(loader.loadTestsFromTestCase(TestFoundationData))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen de resultados
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🏆 TODOS LOS TESTS FOUNDATION BRIDGE: ✅ EXITOSOS")
        print("🔮 Tu 'enlace estrategia-bases' está completamente validado")
        return True
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print(f"Errores: {len(result.errors)}")
        print(f"Fallos: {len(result.failures)}")
        return False


if __name__ == "__main__":
    try:
        success = run_test_suite()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrumpidos por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado ejecutando tests: {e}")
        sys.exit(1)
