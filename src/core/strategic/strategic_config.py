"""
🔧 STRATEGIC CONFIGURATION - SÓTANO 3
=====================================

Configuración estratégica centralizada para el FoundationBridge
y componentes SÓTANO 3. Elimina valores hardcodeados y hace
el sistema completamente configurable.

✅ SIN VALORES HARDCODEADOS
🔧 CONFIGURACIÓN CENTRALIZADA
⚙️ VALIDACIÓN AUTOMÁTICA

Fecha: Agosto 12, 2025
Estado: Implementado para eliminar hardcoding
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import os

@dataclass
class StrategicThresholds:
    """Thresholds estratégicos configurables"""
    trend_threshold: float = 0.6
    volatility_threshold: float = 0.7
    signal_threshold: float = 0.5
    confidence_threshold: float = 0.6
    opportunity_threshold: float = 0.5
    risk_threshold: float = 0.5
    
    def validate(self) -> bool:
        """Validar que todos los thresholds estén en rango válido"""
        thresholds = [
            self.trend_threshold,
            self.volatility_threshold, 
            self.signal_threshold,
            self.confidence_threshold,
            self.opportunity_threshold,
            self.risk_threshold
        ]
        return all(0.0 <= t <= 1.0 for t in thresholds)

@dataclass  
class AnalysisWeights:
    """Pesos para cálculos estratégicos"""
    analytics_weight: float = 0.25
    indicators_weight: float = 0.25
    market_data_weight: float = 0.25
    configuration_weight: float = 0.25
    
    # Pesos para análisis de confianza
    base_confidence: float = 0.5
    analytics_confidence_boost: float = 0.2
    indicators_confidence_multiplier: float = 0.1
    max_indicators_boost: float = 0.3
    indicators_divisor: float = 4.0
    
    # Pesos para score de oportunidad
    signal_opportunity_weight: float = 0.6
    confidence_opportunity_weight: float = 0.4
    
    def validate(self) -> bool:
        """Validar que los pesos sumen correctamente donde corresponde"""
        # Los 4 pesos principales deben sumar 1.0
        main_weights_sum = (
            self.analytics_weight + 
            self.indicators_weight + 
            self.market_data_weight + 
            self.configuration_weight
        )
        
        # Los pesos de oportunidad deben sumar 1.0
        opportunity_weights_sum = (
            self.signal_opportunity_weight + 
            self.confidence_opportunity_weight
        )
        
        return (
            abs(main_weights_sum - 1.0) < 0.001 and
            abs(opportunity_weights_sum - 1.0) < 0.001 and
            all(w >= 0.0 for w in [
                self.analytics_weight, self.indicators_weight,
                self.market_data_weight, self.configuration_weight,
                self.base_confidence, self.analytics_confidence_boost,
                self.indicators_confidence_multiplier, self.max_indicators_boost,
                self.indicators_divisor, self.signal_opportunity_weight,
                self.confidence_opportunity_weight
            ])
        )

@dataclass
class OperationalSettings:
    """Configuraciones operacionales"""
    update_interval: float = 5.0  # segundos
    max_retry_attempts: int = 3
    timeout_seconds: float = 30.0
    enable_detailed_logging: bool = True
    enable_performance_monitoring: bool = False
    
    def validate(self) -> bool:
        """Validar configuraciones operacionales"""
        return (
            self.update_interval > 0.0 and
            self.max_retry_attempts > 0 and
            self.timeout_seconds > 0.0
        )

class StrategicConfiguration:
    """
    🔧 Configuración estratégica centralizada para SÓTANO 3
    
    Elimina valores hardcodeados y centraliza toda la configuración
    estratégica en un sistema robusto y validado.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializar configuración estratégica
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.config_path = config_path
        
        # Configuraciones por defecto (NO hardcodeadas en el bridge)
        self.thresholds = StrategicThresholds()
        self.weights = AnalysisWeights()
        self.operations = OperationalSettings()
        
        # Cargar configuración desde archivo si existe
        if config_path and Path(config_path).exists():
            self._load_from_file(config_path)
        elif self._find_default_config():
            self._load_from_file(self._find_default_config())
    
    def _find_default_config(self) -> Optional[str]:
        """Buscar archivo de configuración por defecto"""
        possible_paths = [
            "config/strategic_config.json",
            "strategic_config.json",
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "strategic_config.json")
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        return None
    
    def _load_from_file(self, file_path: str) -> bool:
        """
        Cargar configuración desde archivo JSON
        
        Args:
            file_path: Ruta al archivo de configuración
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Cargar thresholds
            if 'thresholds' in config_data:
                threshold_data = config_data['thresholds']
                self.thresholds = StrategicThresholds(**threshold_data)
            
            # Cargar weights
            if 'weights' in config_data:
                weights_data = config_data['weights']
                self.weights = AnalysisWeights(**weights_data)
            
            # Cargar operations
            if 'operations' in config_data:
                ops_data = config_data['operations']
                self.operations = OperationalSettings(**ops_data)
            
            return self.validate_all()
            
        except Exception as e:
            print(f"Error cargando configuración desde {file_path}: {e}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Guardar configuración a archivo JSON
        
        Args:
            file_path: Ruta donde guardar la configuración
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Crear directorio si no existe
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                'thresholds': {
                    'trend_threshold': self.thresholds.trend_threshold,
                    'volatility_threshold': self.thresholds.volatility_threshold,
                    'signal_threshold': self.thresholds.signal_threshold,
                    'confidence_threshold': self.thresholds.confidence_threshold,
                    'opportunity_threshold': self.thresholds.opportunity_threshold,
                    'risk_threshold': self.thresholds.risk_threshold
                },
                'weights': {
                    'analytics_weight': self.weights.analytics_weight,
                    'indicators_weight': self.weights.indicators_weight,
                    'market_data_weight': self.weights.market_data_weight,
                    'configuration_weight': self.weights.configuration_weight,
                    'base_confidence': self.weights.base_confidence,
                    'analytics_confidence_boost': self.weights.analytics_confidence_boost,
                    'indicators_confidence_multiplier': self.weights.indicators_confidence_multiplier,
                    'max_indicators_boost': self.weights.max_indicators_boost,
                    'indicators_divisor': self.weights.indicators_divisor,
                    'signal_opportunity_weight': self.weights.signal_opportunity_weight,
                    'confidence_opportunity_weight': self.weights.confidence_opportunity_weight
                },
                'operations': {
                    'update_interval': self.operations.update_interval,
                    'max_retry_attempts': self.operations.max_retry_attempts,
                    'timeout_seconds': self.operations.timeout_seconds,
                    'enable_detailed_logging': self.operations.enable_detailed_logging,
                    'enable_performance_monitoring': self.operations.enable_performance_monitoring
                },
                'metadata': {
                    'version': '1.0.0',
                    'created_by': 'Trading Grid System',
                    'description': 'Configuración estratégica SÓTANO 3 - Sin valores hardcodeados'
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error guardando configuración en {file_path}: {e}")
            return False
    
    def validate_all(self) -> bool:
        """
        Validar toda la configuración estratégica
        
        Returns:
            bool: True si toda la configuración es válida
        """
        return (
            self.thresholds.validate() and
            self.weights.validate() and
            self.operations.validate()
        )
    
    def get_legacy_config_dict(self) -> Dict[str, Any]:
        """
        Obtener configuración en formato legacy para compatibilidad
        
        Returns:
            Dict con configuración en formato anterior
        """
        return {
            'trend_threshold': self.thresholds.trend_threshold,
            'volatility_threshold': self.thresholds.volatility_threshold,
            'signal_threshold': self.thresholds.signal_threshold,
            'confidence_threshold': self.thresholds.confidence_threshold,
            'update_interval': self.operations.update_interval
        }
    
    def update_thresholds(self, **kwargs) -> bool:
        """
        Actualizar thresholds estratégicos
        
        Args:
            **kwargs: Pares clave-valor de thresholds a actualizar
            
        Returns:
            bool: True si se actualizaron correctamente
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.thresholds, key):
                    setattr(self.thresholds, key, float(value))
            
            return self.thresholds.validate()
            
        except Exception:
            return False
    
    def update_weights(self, **kwargs) -> bool:
        """
        Actualizar pesos de análisis
        
        Args:
            **kwargs: Pares clave-valor de pesos a actualizar
            
        Returns:
            bool: True si se actualizaron correctamente
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.weights, key):
                    setattr(self.weights, key, float(value))
            
            return self.weights.validate()
            
        except Exception:
            return False
    
    def update_operations(self, **kwargs) -> bool:
        """
        Actualizar configuraciones operacionales
        
        Args:
            **kwargs: Pares clave-valor de configuraciones a actualizar
            
        Returns:
            bool: True si se actualizaron correctamente
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.operations, key):
                    if isinstance(getattr(self.operations, key), bool):
                        setattr(self.operations, key, bool(value))
                    elif isinstance(getattr(self.operations, key), int):
                        setattr(self.operations, key, int(value))
                    else:
                        setattr(self.operations, key, float(value))
            
            return self.operations.validate()
            
        except Exception:
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de toda la configuración
        
        Returns:
            Dict con resumen completo
        """
        return {
            'valid': self.validate_all(),
            'thresholds_valid': self.thresholds.validate(),
            'weights_valid': self.weights.validate(),
            'operations_valid': self.operations.validate(),
            'config_path': self.config_path,
            'thresholds_count': 6,
            'weights_count': 11,
            'operations_count': 5
        }

# Instancia global de configuración (se inicializa una vez)
_strategic_config: Optional[StrategicConfiguration] = None

def get_strategic_config() -> StrategicConfiguration:
    """
    Obtener instancia global de configuración estratégica
    
    Returns:
        StrategicConfiguration: Instancia de configuración
    """
    global _strategic_config
    if _strategic_config is None:
        _strategic_config = StrategicConfiguration()
    return _strategic_config

def reload_strategic_config(config_path: Optional[str] = None) -> StrategicConfiguration:
    """
    Recargar configuración estratégica
    
    Args:
        config_path: Ruta al archivo de configuración (opcional)
        
    Returns:
        StrategicConfiguration: Nueva instancia de configuración
    """
    global _strategic_config
    _strategic_config = StrategicConfiguration(config_path)
    return _strategic_config
