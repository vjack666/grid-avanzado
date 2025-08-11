# 🏗️ TEMPLATE PARA NUEVOS COMPONENTES

**Archivo:** `template_componente.md`  
**Propósito:** Template estandarizado para desarrollo de nuevos componentes del sistema trading

---

## 📋 **INFORMACIÓN DEL COMPONENTE**

### **🎯 Datos Básicos**
```markdown
Nombre del Componente: [NombreComponente]
Archivo: [nombre_archivo.py]
Fecha Creación: [DD/MM/AAAA]
Desarrollador: [Nombre]
Versión: v1.0
```

### **📊 Descripción y Propósito**
```markdown
Propósito Principal:
[Descripción en 1-2 líneas de qué hace exactamente este componente]

Funcionalidad Específica:
- [ ] Función 1: [Descripción específica]
- [ ] Función 2: [Descripción específica]  
- [ ] Función 3: [Descripción específica]

Integración con Sistema:
- Componentes que usa: [lista]
- Componentes que lo usan: [lista]
- Datos de entrada: [tipo/formato]
- Datos de salida: [tipo/formato]
```

---

## 🏗️ **ESTRUCTURA DEL CÓDIGO**

### **📝 Template de Archivo Python**
```python
"""
Nombre del Componente - Sistema Trading Grid
Propósito: [Descripción del propósito]
Fecha: [DD/MM/AAAA]
Versión: v1.0
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple
from datetime import datetime

# Imports del sistema
from config import *
from data_logger import DataLogger

class ComponenteNombre:
    """
    Clase principal para [descripción del componente]
    
    Esta clase maneja [funcionalidad específica] dentro del sistema
    de trading automático, proporcionando [beneficio específico].
    
    Attributes:
        logger (logging.Logger): Logger para el componente
        config (dict): Configuración específica del componente
        data_logger (DataLogger): Sistema de logging de datos
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el componente con configuración específica.
        
        Args:
            config (Optional[Dict]): Configuración personalizada
        """
        self.logger = logging.getLogger(f"TradingSystem.{self.__class__.__name__}")
        self.config = config or self._get_default_config()
        self.data_logger = DataLogger()
        
        self.logger.info(f"{self.__class__.__name__} inicializado correctamente")
    
    def _get_default_config(self) -> Dict:
        """
        Retorna configuración por defecto del componente.
        
        Returns:
            Dict: Configuración por defecto
        """
        return {
            'parametro1': 'valor_defecto',
            'parametro2': 100,
            'parametro3': True
        }
    
    def funcion_principal(self, datos: pd.DataFrame) -> Dict:
        """
        Función principal del componente.
        
        Args:
            datos (pd.DataFrame): Datos de entrada con columnas [especificar]
            
        Returns:
            Dict: Resultado del procesamiento con keys [especificar]
            
        Raises:
            ValueError: Si los datos no tienen el formato correcto
            RuntimeError: Si hay error en el procesamiento
        """
        try:
            # Validar datos de entrada
            self._validar_datos(datos)
            
            # Logging del inicio
            self.logger.info(f"Iniciando procesamiento de {len(datos)} registros")
            start_time = datetime.now()
            
            # Procesamiento principal
            resultado = self._procesar_datos(datos)
            
            # Logging del resultado
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Procesamiento completado en {execution_time:.2f}s")
            
            # Log de datos para análisis
            self.data_logger.log_component_execution(
                component=self.__class__.__name__,
                execution_time=execution_time,
                input_size=len(datos),
                result=resultado
            )
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error en {self.__class__.__name__}: {str(e)}")
            raise
    
    def _validar_datos(self, datos: pd.DataFrame) -> None:
        """
        Valida que los datos de entrada tengan el formato correcto.
        
        Args:
            datos (pd.DataFrame): Datos a validar
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        if datos.empty:
            raise ValueError("Los datos no pueden estar vacíos")
        
        columnas_requeridas = ['columna1', 'columna2']  # Especificar columnas
        for columna in columnas_requeridas:
            if columna not in datos.columns:
                raise ValueError(f"Columna requerida '{columna}' no encontrada")
    
    def _procesar_datos(self, datos: pd.DataFrame) -> Dict:
        """
        Lógica principal de procesamiento de datos.
        
        Args:
            datos (pd.DataFrame): Datos validados
            
        Returns:
            Dict: Resultado del procesamiento
        """
        # Implementar lógica específica aquí
        resultado = {
            'status': 'success',
            'timestamp': datetime.now(),
            'data_processed': len(datos),
            'results': {}  # Resultados específicos del componente
        }
        
        return resultado
    
    def get_status(self) -> Dict:
        """
        Retorna estado actual del componente.
        
        Returns:
            Dict: Estado del componente
        """
        return {
            'component': self.__class__.__name__,
            'status': 'active',
            'config': self.config,
            'last_execution': getattr(self, '_last_execution', None)
        }

# Función de utilidad para testing rápido
def test_component():
    """
    Función de testing rápido del componente.
    """
    print(f"Testing {ComponenteNombre.__name__}...")
    
    # Crear datos de prueba
    datos_test = pd.DataFrame({
        'columna1': [1, 2, 3, 4, 5],
        'columna2': [10, 20, 30, 40, 50]
    })
    
    # Instanciar componente
    componente = ComponenteNombre()
    
    # Ejecutar función principal
    resultado = componente.funcion_principal(datos_test)
    
    print(f"Resultado: {resultado}")
    print("Test completado exitosamente!")

if __name__ == "__main__":
    test_component()
```

---

## 🧪 **CHECKLIST DE DESARROLLO**

### **✅ Implementación**
- [ ] **Clase principal creada** con docstring completo
- [ ] **Constructor implementado** con manejo de configuración
- [ ] **Función principal** con validación de entrada y logging
- [ ] **Funciones auxiliares** con documentación específica
- [ ] **Manejo de errores** robusto con logging apropiado
- [ ] **Type hints** en todas las funciones
- [ ] **Configuración por defecto** implementada

### **📊 Integración**
- [ ] **Imports del sistema** correctos (config, data_logger)
- [ ] **Logging estructurado** implementado
- [ ] **Interfaz estándar** siguiendo convenciones del sistema
- [ ] **Compatibilidad** con otros componentes verificada

### **🧪 Testing**
- [ ] **Función de test** implementada en el archivo
- [ ] **Test unitario** específico creado
- [ ] **Test con datos reales** validado
- [ ] **Test de performance** < 5 segundos
- [ ] **Test de errores** y edge cases

### **📝 Documentación**
- [ ] **Docstrings** completos en todas las funciones
- [ ] **Comentarios** en lógica compleja
- [ ] **README** del componente actualizado
- [ ] **Bitácora** actualizada con implementación

---

## ⚡ **OPTIMIZACIÓN Y PERFORMANCE**

### **🎯 Objetivos de Performance**
```
Tiempo de Ejecución: < [X] segundos
Uso de Memoria: < [X] MB
Throughput: > [X] operaciones/segundo
Precisión: > [X]% (si aplica)
```

### **🔧 Checklist de Optimización**
- [ ] **Vectorización NumPy/Pandas** donde sea posible
- [ ] **Cache de resultados** para cálculos repetitivos
- [ ] **Lazy loading** de datos pesados
- [ ] **Validación mínima** en loops críticos
- [ ] **Memory profiling** realizado

---

## 📊 **TESTING ESPECÍFICO**

### **🧪 Test Cases Mínimos**
```python
def test_casos_minimos():
    """Tests básicos que debe pasar el componente"""
    
    # Test 1: Datos válidos básicos
    datos_validos = crear_datos_test_validos()
    resultado = componente.funcion_principal(datos_validos)
    assert resultado['status'] == 'success'
    
    # Test 2: Datos vacíos (debe fallar)
    datos_vacios = pd.DataFrame()
    with pytest.raises(ValueError):
        componente.funcion_principal(datos_vacios)
    
    # Test 3: Performance bajo umbral
    start = time.time()
    componente.funcion_principal(datos_validos)
    execution_time = time.time() - start
    assert execution_time < 5.0  # Menos de 5 segundos
    
    # Test 4: Configuración personalizada
    config_custom = {'parametro1': 'valor_custom'}
    componente_custom = ComponenteNombre(config_custom)
    assert componente_custom.config['parametro1'] == 'valor_custom'
```

---

## 📝 **DOCUMENTACIÓN POST-IMPLEMENTACIÓN**

### **✅ Actualizar Después de Completar**
1. **Bitácora Diaria:** Agregar entrada con detalles de implementación
2. **Estado del Sistema:** Actualizar componentes operativos
3. **Plan de Trabajo:** Marcar tarea como completada
4. **Documentación Arquitectura:** Actualizar integraciones

### **📊 Métricas a Documentar**
- Tiempo de desarrollo: [X] horas
- Performance final: [X] segundos
- Test coverage: [X]%
- Líneas de código: [X]
- Complejidad: [X]/10

---

*Template v1.0 - Última actualización: Agosto 10, 2025*
