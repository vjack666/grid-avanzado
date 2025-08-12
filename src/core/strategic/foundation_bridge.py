"""
🚪 FOUNDATION BRIDGE - PUERTA-S3-INTEGRATION
============================================

El FoundationBridge es tu "enlace estrategia-bases" - la PUERTA de integración
que conecta las bases (SÓTANO 1) con la inteligencia estratégica (SÓTANO 3).

✨ VISIÓN: "Enlace estrategia-bases"
🎯 PROPÓSITO: Conectar fundamentos con decisiones estratégicas
🔗 INTEGRACIÓN: SÓTANO 1 ↔ SÓTANO 3

Fecha: Agosto 12, 2025
Estado: READY TO IMPLEMENT
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import threading
import logging
from pathlib import Path

# Importaciones centralizadas desde SÓTANO 1
try:
    from ..common_imports import *
    from ..config_manager import ConfigManager
    from ..logger_manager import LoggerManager
    from ..analytics_manager import AnalyticsManager
    from ..data_manager import DataManager
    from ..indicator_manager import IndicatorManager
    from .strategic_config import get_strategic_config, StrategicConfiguration
except ImportError:
    # Fallback para imports directos
    import sys
    current_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(current_dir / "src"))
    
    from core.config_manager import ConfigManager
    from core.logger_manager import LoggerManager
    from core.analytics_manager import AnalyticsManager
    from core.data_manager import DataManager
    from core.indicator_manager import IndicatorManager
    from core.strategic.strategic_config import get_strategic_config, StrategicConfiguration

@dataclass
class StrategicContext:
    """Contexto estratégico para decisiones"""
    market_state: str = "analyzing"
    trend_direction: str = "neutral"
    volatility_level: str = "medium"
    signal_strength: float = 0.0
    confidence_level: float = 0.0
    risk_assessment: str = "medium"
    opportunity_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'market_state': self.market_state,
            'trend_direction': self.trend_direction,
            'volatility_level': self.volatility_level,
            'signal_strength': self.signal_strength,
            'confidence_level': self.confidence_level,
            'risk_assessment': self.risk_assessment,
            'opportunity_score': self.opportunity_score,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class FoundationData:
    """Datos de fundamento desde SÓTANO 1"""
    analytics_data: Dict[str, Any] = field(default_factory=dict)
    indicators_data: Dict[str, Any] = field(default_factory=dict)
    market_data: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_valid(self) -> bool:
        """Verificar si los datos son válidos"""
        return (
            bool(self.analytics_data) and
            bool(self.indicators_data) and
            bool(self.market_data)
        )

class FoundationBridge:
    """
    🚪 FOUNDATION BRIDGE - Tu "enlace estrategia-bases"
    
    Conecta las bases sólidas del SÓTANO 1 con la inteligencia
    estratégica del SÓTANO 3, creando el puente perfecto entre
    fundamentos y decisiones estratégicas.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Inicializar FoundationBridge
        
        Args:
            config_manager: Gestor de configuración del SÓTANO 1
        """
        # Configurar logging
        logger_manager = LoggerManager()
        self.logger = logger_manager.get_logger("FoundationBridge")
        
        # Cargar configuración estratégica (SIN VALORES HARDCODEADOS)
        self.strategic_config = get_strategic_config()
        if not self.strategic_config.validate_all():
            self.logger.warning("⚠️ Configuración estratégica no válida, usando valores por defecto")
        
        # Conectar con SÓTANO 1 (bases)
        self.config_manager = config_manager or ConfigManager()
        
        # Inicializar error manager
        try:
            from ..error_manager import ErrorManager
            self.error_manager = ErrorManager()
        except:
            self.error_manager = None
        
        # Inicializar data manager
        try:
            self.data_manager = DataManager()
        except:
            self.data_manager = None
        
        # Inicializar analytics manager con dependencias
        try:
            if self.error_manager and self.data_manager:
                self.analytics_manager = AnalyticsManager(
                    config_manager=self.config_manager,
                    logger_manager=logger_manager,
                    error_manager=self.error_manager,
                    data_manager=self.data_manager
                )
            else:
                self.analytics_manager = None
        except Exception as e:
            self.logger.warning(f"No se pudo inicializar AnalyticsManager: {e}")
            self.analytics_manager = None
        
        # Inicializar indicator manager
        try:
            self.indicator_manager = IndicatorManager()
        except Exception as e:
            self.logger.warning(f"No se pudo inicializar IndicatorManager: {e}")
            self.indicator_manager = None
        
        # Estado interno
        self._foundation_data: Optional[FoundationData] = None
        self._strategic_context: Optional[StrategicContext] = None
        self._bridge_active = False
        self._lock = threading.Lock()
        
        self.logger.info("🚪 FoundationBridge inicializado - Enlace estrategia-bases activado (SIN hardcoding)")
    
    def activate_bridge(self) -> bool:
        """
        Activar el puente estrategia-bases
        
        Returns:
            bool: True si se activó correctamente
        """
        try:
            with self._lock:
                if self._bridge_active:
                    self.logger.warning("FoundationBridge ya está activo")
                    return True
                
                # Verificar conectividad con SÓTANO 1
                if not self._verify_foundation_connectivity():
                    raise Exception("No se pudo conectar con las bases (SÓTANO 1)")
                
                # Activar el puente
                self._bridge_active = True
                self.logger.info("✅ FoundationBridge activado - Enlace estrategia-bases operativo")
                
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Error activando FoundationBridge: {e}")
            return False
    
    def deactivate_bridge(self) -> bool:
        """
        Desactivar el puente estrategia-bases
        
        Returns:
            bool: True si se desactivó correctamente
        """
        try:
            with self._lock:
                if not self._bridge_active:
                    self.logger.warning("FoundationBridge ya está inactivo")
                    return True
                
                self._bridge_active = False
                self._foundation_data = None
                self._strategic_context = None
                
                self.logger.info("🔒 FoundationBridge desactivado")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Error desactivando FoundationBridge: {e}")
            return False
    
    def extract_foundation_data(self) -> Optional[FoundationData]:
        """
        Extraer datos fundamentales desde SÓTANO 1
        
        Returns:
            FoundationData: Datos de fundamento o None si error
        """
        try:
            if not self._bridge_active:
                raise Exception("FoundationBridge no está activo")
            
            # Extraer datos de analytics
            analytics_data = {}
            try:
                if self.analytics_manager:
                    analytics_data = self.analytics_manager.get_current_analytics()
                if not analytics_data:
                    analytics_data = {'status': 'no_data', 'timestamp': datetime.now().isoformat()}
            except Exception as e:
                self.logger.warning(f"No se pudieron extraer analytics: {e}")
                analytics_data = {'status': 'error', 'error': str(e)}
            
            # Extraer datos de indicadores
            indicators_data = {}
            try:
                if self.indicator_manager:
                    # Obtener indicadores clave
                    indicators = ['sma_20', 'rsi_14', 'bollinger_bands', 'macd']
                    for indicator in indicators:
                        try:
                            value = getattr(self.indicator_manager, f'calculate_{indicator}', lambda x: None)([])
                            indicators_data[indicator] = value
                        except:
                            indicators_data[indicator] = None
                        
                if not any(indicators_data.values()) if indicators_data else True:
                    indicators_data = {'status': 'no_calculations', 'timestamp': datetime.now().isoformat()}
                    
            except Exception as e:
                self.logger.warning(f"No se pudieron extraer indicadores: {e}")
                indicators_data = {'status': 'error', 'error': str(e)}
            
            # Extraer datos de mercado
            market_data = {}
            try:
                if self.data_manager:
                    market_data = self.data_manager.get_current_market_data()
                if not market_data:
                    market_data = {'status': 'no_market_data', 'timestamp': datetime.now().isoformat()}
            except Exception as e:
                self.logger.warning(f"No se pudieron extraer datos de mercado: {e}")
                market_data = {'status': 'error', 'error': str(e)}
            
            # Extraer configuración
            configuration = {}
            try:
                configuration = self.config_manager.get_all_config()
                if not configuration:
                    configuration = {'status': 'no_config', 'timestamp': datetime.now().isoformat()}
            except Exception as e:
                self.logger.warning(f"No se pudo extraer configuración: {e}")
                configuration = {'status': 'error', 'error': str(e)}
            
            # Crear FoundationData
            foundation_data = FoundationData(
                analytics_data=analytics_data,
                indicators_data=indicators_data,
                market_data=market_data,
                configuration=configuration,
                timestamp=datetime.now()
            )
            
            with self._lock:
                self._foundation_data = foundation_data
            
            self.logger.debug("📊 Datos fundamentales extraídos exitosamente")
            return foundation_data
            
        except Exception as e:
            self.logger.error(f"❌ Error extrayendo datos fundamentales: {e}")
            return None
    
    def analyze_strategic_context(self, foundation_data: FoundationData) -> Optional[StrategicContext]:
        """
        Analizar contexto estratégico desde datos fundamentales
        
        Args:
            foundation_data: Datos de fundamento
            
        Returns:
            StrategicContext: Contexto estratégico o None si error
        """
        try:
            if not foundation_data.is_valid():
                self.logger.warning("Datos fundamentales no válidos para análisis estratégico")
                return StrategicContext(
                    market_state="invalid_data",
                    confidence_level=0.0
                )
            
            # Analizar estado del mercado
            market_state = self._analyze_market_state(foundation_data)
            
            # Analizar dirección de tendencia
            trend_direction = self._analyze_trend_direction(foundation_data)
            
            # Analizar nivel de volatilidad
            volatility_level = self._analyze_volatility_level(foundation_data)
            
            # Calcular fuerza de señal
            signal_strength = self._calculate_signal_strength(foundation_data)
            
            # Calcular nivel de confianza
            confidence_level = self._calculate_confidence_level(foundation_data)
            
            # Evaluar riesgo
            risk_assessment = self._assess_risk(foundation_data)
            
            # Calcular score de oportunidad
            opportunity_score = self._calculate_opportunity_score(foundation_data)
            
            # Crear contexto estratégico
            strategic_context = StrategicContext(
                market_state=market_state,
                trend_direction=trend_direction,
                volatility_level=volatility_level,
                signal_strength=signal_strength,
                confidence_level=confidence_level,
                risk_assessment=risk_assessment,
                opportunity_score=opportunity_score,
                timestamp=datetime.now()
            )
            
            with self._lock:
                self._strategic_context = strategic_context
            
            self.logger.debug("🎯 Contexto estratégico analizado exitosamente")
            return strategic_context
            
        except Exception as e:
            self.logger.error(f"❌ Error analizando contexto estratégico: {e}")
            return None
    
    def get_bridge_status(self) -> Dict[str, Any]:
        """
        Obtener estado completo del puente
        
        Returns:
            Dict con estado del bridge
        """
        with self._lock:
            return {
                'bridge_active': self._bridge_active,
                'has_foundation_data': self._foundation_data is not None,
                'has_strategic_context': self._strategic_context is not None,
                'foundation_data_valid': self._foundation_data.is_valid() if self._foundation_data else False,
                'last_update': self._foundation_data.timestamp.isoformat() if self._foundation_data else None,
                'strategic_config': self.strategic_config.get_legacy_config_dict(),
                'config_valid': self.strategic_config.validate_all(),
                'timestamp': datetime.now().isoformat()
            }
    
    def update_strategic_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Actualizar configuración estratégica
        
        Args:
            new_config: Nueva configuración
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Actualizar usando el sistema de configuración centralizado
            updated = False
            
            # Separar tipos de configuración
            threshold_updates = {k: v for k, v in new_config.items() 
                               if k.endswith('_threshold')}
            weight_updates = {k: v for k, v in new_config.items() 
                            if k.endswith('_weight') or k in ['base_confidence', 'analytics_confidence_boost']}
            operation_updates = {k: v for k, v in new_config.items() 
                               if k in ['update_interval', 'max_retry_attempts', 'timeout_seconds']}
            
            # Actualizar por categorías
            if threshold_updates:
                updated |= self.strategic_config.update_thresholds(**threshold_updates)
            
            if weight_updates:
                updated |= self.strategic_config.update_weights(**weight_updates)
                
            if operation_updates:
                updated |= self.strategic_config.update_operations(**operation_updates)
            
            # Actualizar configuraciones individuales no categorizadas
            remaining_config = {k: v for k, v in new_config.items() 
                              if k not in threshold_updates and k not in weight_updates and k not in operation_updates}
            
            for key, value in remaining_config.items():
                # Mapear configuraciones legacy a nuevas
                if key == 'demo_mode':
                    self.strategic_config.update_operations(enable_detailed_logging=bool(value))
                    updated = True
            
            if updated and self.strategic_config.validate_all():
                self.logger.info(f"⚙️ Configuración estratégica actualizada: {new_config}")
                return True
            else:
                self.logger.warning("⚠️ Configuración estratégica no válida después de actualización")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error actualizando configuración estratégica: {e}")
            return False
    
    # Métodos de análisis privados
    def _verify_foundation_connectivity(self) -> bool:
        """Verificar conectividad con SÓTANO 1"""
        try:
            # Verificar config manager
            if not self.config_manager:
                return False
            
            # Al menos config manager debe estar disponible
            connectivity_score = 1  # Config manager está disponible
            
            # Verificar otros componentes (opcionales)
            if self.analytics_manager:
                connectivity_score += 1
            if self.data_manager:
                connectivity_score += 1
            if self.indicator_manager:
                connectivity_score += 1
            
            # Considerar conectado si tenemos al menos config + 1 componente más
            return connectivity_score >= 2
            
        except Exception:
            return False
    
    def _analyze_market_state(self, foundation_data: FoundationData) -> str:
        """Analizar estado del mercado"""
        try:
            # Análisis básico del estado del mercado
            if 'status' in foundation_data.analytics_data:
                if foundation_data.analytics_data['status'] == 'error':
                    return "error"
                elif foundation_data.analytics_data['status'] == 'no_data':
                    return "no_data"
            
            # Estado por defecto basado en disponibilidad de datos
            if foundation_data.is_valid():
                return "analyzing"
            else:
                return "insufficient_data"
                
        except Exception:
            return "unknown"
    
    def _analyze_trend_direction(self, foundation_data: FoundationData) -> str:
        """Analizar dirección de tendencia"""
        try:
            # Análisis básico de tendencia
            indicators = foundation_data.indicators_data
            
            # Verificar SMA para tendencia básica
            if 'sma_20' in indicators and indicators['sma_20'] is not None:
                # Por ahora retornamos neutral, se implementará lógica específica
                return "neutral"
            
            return "neutral"
            
        except Exception:
            return "unknown"
    
    def _analyze_volatility_level(self, foundation_data: FoundationData) -> str:
        """Analizar nivel de volatilidad"""
        try:
            # Análisis básico de volatilidad
            indicators = foundation_data.indicators_data
            
            # Verificar Bollinger Bands para volatilidad
            if 'bollinger_bands' in indicators and indicators['bollinger_bands'] is not None:
                # Por ahora retornamos medium, se implementará lógica específica
                return "medium"
            
            return "medium"
            
        except Exception:
            return "unknown"
    
    def _calculate_signal_strength(self, foundation_data: FoundationData) -> float:
        """Calcular fuerza de señal usando configuración centralizada"""
        try:
            if not foundation_data.is_valid():
                return 0.0
            
            # Usar pesos de configuración en lugar de valores hardcodeados
            weights = self.strategic_config.weights
            score = 0.0
            
            if foundation_data.analytics_data:
                score += weights.analytics_weight
            if foundation_data.indicators_data:
                score += weights.indicators_weight
            if foundation_data.market_data:
                score += weights.market_data_weight
            if foundation_data.configuration:
                score += weights.configuration_weight
            
            return min(score, 1.0)
            
        except Exception:
            return 0.0
    
    def _calculate_confidence_level(self, foundation_data: FoundationData) -> float:
        """Calcular nivel de confianza usando configuración centralizada"""
        try:
            if not foundation_data.is_valid():
                return 0.0
            
            # Usar configuración centralizada en lugar de valores hardcodeados
            weights = self.strategic_config.weights
            confidence = weights.base_confidence
            
            # Ajustar por disponibilidad de analytics
            if 'status' not in foundation_data.analytics_data:
                confidence += weights.analytics_confidence_boost
            
            # Ajustar por disponibilidad de indicadores
            valid_indicators = sum(1 for v in foundation_data.indicators_data.values() if v is not None)
            if valid_indicators > 0:
                indicator_boost = weights.indicators_confidence_multiplier * min(
                    valid_indicators / weights.indicators_divisor, 
                    weights.max_indicators_boost
                )
                confidence += indicator_boost
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.0
    
    def _assess_risk(self, foundation_data: FoundationData) -> str:
        """Evaluar riesgo"""
        try:
            # Evaluación básica de riesgo
            if not foundation_data.is_valid():
                return "high"
            
            # Por ahora retornamos medium como default seguro
            return "medium"
            
        except Exception:
            return "high"
    
    def _calculate_opportunity_score(self, foundation_data: FoundationData) -> float:
        """Calcular score de oportunidad usando configuración centralizada"""
        try:
            if not foundation_data.is_valid():
                return 0.0
            
            # Usar pesos de configuración para combinar métricas
            weights = self.strategic_config.weights
            signal_strength = self._calculate_signal_strength(foundation_data)
            confidence_level = self._calculate_confidence_level(foundation_data)
            
            # Combinar señal y confianza usando pesos configurables
            opportunity = (
                signal_strength * weights.signal_opportunity_weight + 
                confidence_level * weights.confidence_opportunity_weight
            )
            
            return min(opportunity, 1.0)
            
        except Exception:
            return 0.0

# Metadatos del componente
COMPONENT_INFO = {
    'name': 'FoundationBridge',
    'version': '1.0.0',
    'description': 'Enlace estrategia-bases entre SÓTANO 1 y SÓTANO 3',
    'author': 'Trading Grid System',
    'status': 'READY_TO_IMPLEMENT',
    'integration_level': 'PUERTA-S3-INTEGRATION'
}
