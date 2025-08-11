# 🧪 TEMPLATE DE TESTING

**Archivo:** `template_testing.md`  
**Propósito:** Template estandarizado para testing de componentes del sistema trading

---

## 📋 **ESTRUCTURA DE TESTING**

### **🎯 Tipos de Tests Requeridos**
```
Tests por Componente:
├── 🔧 Unit Tests - Funciones individuales
├── 🔗 Integration Tests - Integración con otros componentes
├── ⚡ Performance Tests - Tiempo y memoria
├── 📊 Data Tests - Validación con datos reales MT5
└── 🎯 Regression Tests - No romper funcionalidad existente
```

---

## 🧪 **TEMPLATE TEST UNITARIO**

### **📝 Archivo: `test_[componente].py`**
```python
"""
Tests unitarios para [NombreComponente]
Sistema Trading Grid
Fecha: [DD/MM/AAAA]
"""

import pytest
import pandas as pd
import numpy as np
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Import del componente a testear
from [archivo_componente] import [NombreComponente]

class Test[NombreComponente]:
    """Suite de tests para [NombreComponente]"""
    
    @pytest.fixture
    def componente(self):
        """Fixture del componente con configuración de test"""
        config_test = {
            'parametro1': 'test_value',
            'parametro2': 50,
            'test_mode': True
        }
        return [NombreComponente](config_test)
    
    @pytest.fixture
    def datos_validos(self):
        """Fixture con datos válidos para testing"""
        return pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=100, freq='1min'),
            'open': np.random.uniform(1.1000, 1.1100, 100),
            'high': np.random.uniform(1.1000, 1.1100, 100),
            'low': np.random.uniform(1.1000, 1.1100, 100),
            'close': np.random.uniform(1.1000, 1.1100, 100),
            'volume': np.random.randint(100, 1000, 100)
        })
    
    @pytest.fixture  
    def datos_invalidos(self):
        """Fixture con datos inválidos para testing"""
        return pd.DataFrame({
            'columna_incorrecta': [1, 2, 3]
        })

    # ===== TESTS BÁSICOS =====
    
    def test_inicializacion(self, componente):
        """Test que el componente se inicializa correctamente"""
        assert componente is not None
        assert hasattr(componente, 'config')
        assert hasattr(componente, 'logger')
        assert componente.config['test_mode'] is True
    
    def test_configuracion_default(self):
        """Test configuración por defecto"""
        componente = [NombreComponente]()
        config = componente._get_default_config()
        
        assert isinstance(config, dict)
        assert 'parametro1' in config
        assert 'parametro2' in config
    
    # ===== TESTS FUNCIONALIDAD =====
    
    def test_funcion_principal_datos_validos(self, componente, datos_validos):
        """Test función principal con datos válidos"""
        resultado = componente.funcion_principal(datos_validos)
        
        assert isinstance(resultado, dict)
        assert 'status' in resultado
        assert resultado['status'] == 'success'
        assert 'timestamp' in resultado
        assert 'data_processed' in resultado
        assert resultado['data_processed'] == len(datos_validos)
    
    def test_funcion_principal_datos_vacios(self, componente):
        """Test función principal con DataFrame vacío"""
        datos_vacios = pd.DataFrame()
        
        with pytest.raises(ValueError, match="Los datos no pueden estar vacíos"):
            componente.funcion_principal(datos_vacios)
    
    def test_validacion_datos_invalidos(self, componente, datos_invalidos):
        """Test validación con datos inválidos"""
        with pytest.raises(ValueError, match="Columna requerida"):
            componente.funcion_principal(datos_invalidos)
    
    # ===== TESTS PERFORMANCE =====
    
    def test_performance_tiempo_ejecucion(self, componente, datos_validos):
        """Test que el tiempo de ejecución sea < 5 segundos"""
        start_time = time.time()
        componente.funcion_principal(datos_validos)
        execution_time = time.time() - start_time
        
        assert execution_time < 5.0, f"Ejecución tomó {execution_time:.2f}s (>5s)"
    
    @pytest.mark.performance  
    def test_performance_memoria(self, componente, datos_validos):
        """Test uso de memoria durante ejecución"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memoria_inicial = process.memory_info().rss / 1024 / 1024  # MB
        
        componente.funcion_principal(datos_validos)
        
        memoria_final = process.memory_info().rss / 1024 / 1024  # MB
        incremento_memoria = memoria_final - memoria_inicial
        
        assert incremento_memoria < 100, f"Incremento memoria: {incremento_memoria:.2f}MB"
    
    def test_performance_multiples_ejecuciones(self, componente, datos_validos):
        """Test performance con múltiples ejecuciones"""
        tiempos = []
        
        for _ in range(10):
            start = time.time()
            componente.funcion_principal(datos_validos)
            tiempos.append(time.time() - start)
        
        tiempo_promedio = np.mean(tiempos)
        tiempo_maximo = np.max(tiempos)
        
        assert tiempo_promedio < 3.0, f"Tiempo promedio: {tiempo_promedio:.2f}s"
        assert tiempo_maximo < 5.0, f"Tiempo máximo: {tiempo_maximo:.2f}s"
    
    # ===== TESTS EDGE CASES =====
    
    def test_datos_extremos_pequenos(self, componente):
        """Test con dataset muy pequeño"""
        datos_pequenos = pd.DataFrame({
            'timestamp': [datetime.now()],
            'close': [1.1000]
        })
        
        # Dependiendo del componente, esto puede ser válido o inválido
        # Ajustar según lógica específica
        try:
            resultado = componente.funcion_principal(datos_pequenos)
            assert isinstance(resultado, dict)
        except ValueError as e:
            # Si requiere mínimo de datos, verificar mensaje apropiado
            assert "mínimo" in str(e).lower()
    
    def test_datos_con_nulos(self, componente):
        """Test con datos que contienen NaN"""
        datos_con_nulos = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=10),
            'close': [1.1000, np.nan, 1.1020, np.nan, 1.1040] * 2
        })
        
        # El componente debe manejar NaN apropiadamente
        resultado = componente.funcion_principal(datos_con_nulos)
        assert isinstance(resultado, dict)
    
    # ===== TESTS CONFIGURACIÓN =====
    
    def test_configuracion_personalizada(self):
        """Test con configuración personalizada"""
        config_custom = {
            'parametro1': 'valor_personalizado',
            'parametro2': 999
        }
        
        componente = [NombreComponente](config_custom)
        assert componente.config['parametro1'] == 'valor_personalizado'
        assert componente.config['parametro2'] == 999
    
    # ===== TESTS INTEGRACIÓN =====
    
    @patch('data_logger.DataLogger')
    def test_integracion_data_logger(self, mock_logger, componente, datos_validos):
        """Test integración con DataLogger"""
        componente.funcion_principal(datos_validos)
        
        # Verificar que se llamó al logger
        assert mock_logger.called
        # Verificar métodos específicos según implementación
    
    # ===== TESTS STATUS Y MONITORING =====
    
    def test_get_status(self, componente):
        """Test función get_status"""
        status = componente.get_status()
        
        assert isinstance(status, dict)
        assert 'component' in status
        assert 'status' in status
        assert status['component'] == componente.__class__.__name__
        assert status['status'] == 'active'


# ===== TESTS DE INTEGRACIÓN =====

class TestIntegracion[NombreComponente]:
    """Tests de integración del componente con el sistema"""
    
    def test_integracion_con_main(self):
        """Test integración con controlador principal"""
        # Simular integración con main.py
        pass
    
    def test_integracion_config_global(self):
        """Test integración con config.py global"""
        from config import *
        componente = [NombreComponente]()
        
        # Verificar que usa configuración global apropiadamente
        assert componente.config is not None


# ===== TESTS DE DATOS REALES =====

@pytest.mark.integration
class TestDatosReales[NombreComponente]:
    """Tests con datos reales de MT5"""
    
    @pytest.fixture
    def datos_mt5_reales(self):
        """Fixture con datos reales de MT5 (si están disponibles)"""
        # Cargar datos desde archivo CSV o MT5
        try:
            datos = pd.read_csv('data/2025-08-08/velas_EURUSD_M15_6semanas.csv')
            return datos
        except FileNotFoundError:
            pytest.skip("Datos reales no disponibles")
    
    def test_con_datos_reales_mt5(self, componente, datos_mt5_reales):
        """Test con datos reales de MT5"""
        if datos_mt5_reales is not None:
            resultado = componente.funcion_principal(datos_mt5_reales)
            
            assert resultado['status'] == 'success'
            assert resultado['data_processed'] > 0
    
    def test_precision_con_datos_historicos(self, componente, datos_mt5_reales):
        """Test de precisión con datos históricos"""
        if datos_mt5_reales is not None:
            resultado = componente.funcion_principal(datos_mt5_reales)
            
            # Verificar métricas de precisión específicas del componente
            # Esto depende del tipo de componente (indicador, señales, etc.)
            assert 'precision' in resultado or 'accuracy' in resultado


# ===== CONFIGURACIÓN PYTEST =====

# Marcadores personalizados para organizar tests
pytestmark = [
    pytest.mark.unit,  # Tests unitarios básicos
]

# Configuración de performance tests
def pytest_configure(config):
    """Configuración de pytest"""
    config.addinivalue_line(
        "markers", "performance: marca tests de performance"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración"
    )

# Funciones de utilidad para tests
def crear_datos_ohlc(n_rows=100, symbol="EURUSD"):
    """Utilidad para crear datos OHLC de prueba"""
    base_price = 1.1000
    dates = pd.date_range('2025-01-01', periods=n_rows, freq='1min')
    
    # Generar precios realistas
    returns = np.random.normal(0, 0.0001, n_rows)
    prices = base_price * (1 + returns).cumprod()
    
    return pd.DataFrame({
        'timestamp': dates,
        'symbol': symbol,
        'open': prices,
        'high': prices * (1 + np.abs(np.random.normal(0, 0.0005, n_rows))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.0005, n_rows))),
        'close': prices,
        'volume': np.random.randint(100, 1000, n_rows)
    })

if __name__ == "__main__":
    # Ejecutar tests específicos
    pytest.main([__file__, "-v", "--tb=short"])
```

---

## ⚡ **CHECKLIST DE TESTING**

### **✅ Tests Obligatorios**
- [ ] **Test inicialización** - Constructor y configuración
- [ ] **Test función principal** - Casos válidos e inválidos  
- [ ] **Test validación datos** - Entrada correcta/incorrecta
- [ ] **Test performance** - < 5 segundos y memoria
- [ ] **Test edge cases** - Casos límite y extremos
- [ ] **Test configuración** - Default y personalizada
- [ ] **Test integración** - Con otros componentes

### **📊 Coverage Objetivo**
- **Líneas de código:** > 80% coverage
- **Funciones:** 100% funciones testeadas
- **Branches:** > 70% branch coverage
- **Edge cases:** Casos principales cubiertos

### **🎯 Métricas de Calidad**
- **Tests passing:** 100% tests deben pasar
- **Tiempo total:** < 30 segundos suite completa
- **Memoria máxima:** < 200 MB durante tests
- **Flaky tests:** 0 tests intermitentes

---

## 🔧 **COMANDOS DE TESTING**

### **🧪 Ejecutar Tests**
```bash
# Tests específicos del componente
pytest test_componente.py -v

# Tests con coverage
pytest test_componente.py --cov=componente --cov-report=html

# Solo tests rápidos (sin integration)
pytest test_componente.py -m "not integration" 

# Solo performance tests
pytest test_componente.py -m performance

# Tests en paralelo
pytest test_componente.py -n auto
```

### **📊 Análisis de Resultados**
```bash
# Reporte detallado
pytest test_componente.py --tb=long --capture=no

# Benchmark de performance  
pytest test_componente.py --benchmark-only

# Profiling de memoria
pytest test_componente.py --memray
```

---

## 📝 **DOCUMENTACIÓN POST-TESTING**

### **✅ Actualizar Después de Testing**
1. **Bitácora:** Registrar resultados de tests
2. **Métricas:** Documentar coverage y performance
3. **Problemas:** Registrar bugs encontrados
4. **Mejoras:** Identificar optimizaciones

### **📊 Template Reporte Testing**
```markdown
## 🧪 REPORTE TESTING - [ComponenteNombre]

### Resultados:
- Tests ejecutados: [X]/[Total]
- Tests pasando: [X]/[Total] ([X]%)
- Coverage: [X]%
- Tiempo total: [X]s

### Performance:
- Tiempo promedio: [X]s
- Memoria máxima: [X]MB
- Throughput: [X] ops/s

### Issues encontrados:
- [ ] Issue 1: [Descripción]
- [ ] Issue 2: [Descripción]

### Próximos pasos:
- [ ] Optimización 1
- [ ] Fix bug 1
```

---

*Template Testing v1.0 - Última actualización: Agosto 10, 2025*
