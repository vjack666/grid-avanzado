"""
PUERTA-S2-STRATEGY: StrategyEngine v1.0.0
Sistema de Estrategias Adaptativas Inteligentes

Este módulo implementa un motor de estrategias que se adapta automáticamente
a las condiciones del mercado utilizando el sistema centralizado de SÓTANO 1.

Integración con SÓTANO 1:
- ConfigManager: Configuración centralizada
- LoggerManager: Logging unificado  
- ErrorManager: Manejo de errores centralizado
- DataManager: Gestión de datos históricos
- AnalyticsManager: Motor de análisis técnico

Protocolo: Trading Grid SÓTANO 1 + SÓTANO 2
Autor: Copilot & AI Assistant  
Fecha: 2025-08-11
"""

import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

# Imports del sistema SÓTANO 1 (protocolo centralizado)
from ..config_manager import ConfigManager
from ..logger_manager import LoggerManager
from ..error_manager import ErrorManager
from ..data_manager import DataManager
from ..analytics_manager import AnalyticsManager

class StrategyType(Enum):
    """Tipos de estrategia disponibles"""
    ADAPTIVE_GRID = "adaptive_grid"
    MEAN_REVERSION = "mean_reversion"
    TREND_FOLLOWING = "trend_following"

class SignalStrength(Enum):
    """Fuerza de la señal"""
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4

@dataclass
class TradingSignal:
    """Señal de trading con metadatos"""
    symbol: str
    timeframe: str
    signal_type: str  # BUY, SELL, CLOSE
    strength: SignalStrength
    price: float
    timestamp: datetime
    confidence: float  # 0.0 - 1.0
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategyConfig:
    """Configuración de estrategia"""
    strategy_type: StrategyType
    timeframes: List[str]
    symbols: List[str]
    risk_per_trade: float = 0.02
    max_concurrent_trades: int = 5
    min_signal_strength: SignalStrength = SignalStrength.MODERATE

class StrategyEngine:
    """
    PUERTA-S2-STRATEGY: Motor de Estrategias Adaptativas
    
    Integrado con el sistema centralizado de SÓTANO 1 siguiendo protocolos establecidos.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None,
                 logger_manager: Optional[LoggerManager] = None,
                 error_manager: Optional[ErrorManager] = None,
                 data_manager: Optional[DataManager] = None,
                 analytics_manager: Optional[AnalyticsManager] = None):
        
        # Managers principales (protocolo SÓTANO 1)
        self.config_manager = config_manager or ConfigManager()
        self.logger_manager = logger_manager or LoggerManager()
        self.error_manager = error_manager or ErrorManager(
            logger_manager=self.logger_manager, 
            config_manager=self.config_manager
        )
        self.data_manager = data_manager or DataManager()
        self.analytics_manager = analytics_manager or AnalyticsManager(
            config_manager=self.config_manager,
            logger_manager=self.logger_manager,
            error_manager=self.error_manager,
            data_manager=self.data_manager
        )
        
        # Configuración del componente
        self.component_id = "PUERTA-S2-STRATEGY"
        self.version = "v1.0.0"
        
        # Estado del motor
        self.is_active = False
        self.strategies_running = False
        self.last_update = None
        
        # Configuraciones y datos
        self.strategy_configs: Dict[str, StrategyConfig] = {}
        self.active_strategies: Dict[str, bool] = {}
        self.signal_history: List[TradingSignal] = []
        self.active_signals: Dict[str, TradingSignal] = {}
        
        # Métricas
        self.strategy_metrics = {
            'total_signals_generated': 0,
            'successful_signals': 0,
            'active_strategies_count': 0,
            'signals_per_hour': 0.0,
            'avg_signal_strength': 0.0
        }
        
        # Threading
        self.strategy_thread = None
        self.strategy_lock = threading.Lock()
        
        # Log de inicialización
        self.logger_manager.log_info(f"✅ {self.component_id} {self.version} inicializado correctamente")
    
    def initialize_strategy_config(self, strategy_name: str, config: StrategyConfig) -> bool:
        """Inicializar configuración de estrategia"""
        try:
            with self.strategy_lock:
                self.strategy_configs[strategy_name] = config
                self.active_strategies[strategy_name] = False
                
            self.logger_manager.log_info(f"✅ Estrategia '{strategy_name}' configurada: {config.strategy_type.value}")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"strategy_name": strategy_name})
            return False
    
    def start_strategy(self, strategy_name: str) -> bool:
        """Iniciar una estrategia específica"""
        try:
            if strategy_name not in self.strategy_configs:
                self.logger_manager.log_warning(f"❌ Estrategia '{strategy_name}' no encontrada")
                return False
            
            with self.strategy_lock:
                if self.active_strategies.get(strategy_name, False):
                    self.logger_manager.log_warning(f"⚠️ Estrategia '{strategy_name}' ya está activa")
                    return True
                
                self.active_strategies[strategy_name] = True
                self.strategy_metrics['active_strategies_count'] += 1
            
            self.logger_manager.log_info(f"🚀 Estrategia '{strategy_name}' iniciada")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"strategy_name": strategy_name})
            return False
    
    def stop_strategy(self, strategy_name: str) -> bool:
        """Detener una estrategia específica"""
        try:
            with self.strategy_lock:
                if strategy_name in self.active_strategies and self.active_strategies[strategy_name]:
                    self.active_strategies[strategy_name] = False
                    self.strategy_metrics['active_strategies_count'] = max(0, 
                        self.strategy_metrics['active_strategies_count'] - 1)
            
            self.logger_manager.log_info(f"⏹️ Estrategia '{strategy_name}' detenida")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"strategy_name": strategy_name})
            return False
    
    def generate_adaptive_grid_signal(self, symbol: str, market_data: Dict[str, Any]) -> Optional[TradingSignal]:
        """Generar señal de grid adaptativo usando datos del AnalyticsManager"""
        try:
            # Usar el AnalyticsManager para obtener métricas del mercado
            market_summary = self.analytics_manager.get_market_summary()
            
            # Obtener volatilidad y tendencia del AnalyticsManager
            volatility = market_summary.get('volatility', 0.015)
            trend_analysis = market_summary.get('trend_analysis', {})
            trend_strength = trend_analysis.get('trend_strength', 0.0) if trend_analysis else 0.0
            price = market_data.get('price', 0.0)
            
            # Calcular spacing del grid basado en volatilidad
            base_spacing = 0.0010  # 10 pips
            adaptive_spacing = base_spacing * (1 + volatility * 10)
            
            # Determinar dirección basada en tendencia
            if abs(trend_strength) < 0.3:  # Mercado ranging
                signal_type = "BUY" if price % (adaptive_spacing * 2) < adaptive_spacing else "SELL"
                strength = SignalStrength.MODERATE
                confidence = 0.6
            else:  # Mercado trending
                signal_type = "BUY" if trend_strength > 0 else "SELL"
                strength = SignalStrength.STRONG if abs(trend_strength) > 0.7 else SignalStrength.MODERATE
                confidence = min(0.9, 0.5 + abs(trend_strength))
            
            return TradingSignal(
                symbol=symbol,
                timeframe="M15",
                signal_type=signal_type,
                strength=strength,
                price=price,
                timestamp=datetime.now(),
                confidence=confidence,
                source="adaptive_grid",
                metadata={
                    'adaptive_spacing': adaptive_spacing,
                    'volatility': volatility,
                    'trend_strength': trend_strength,
                    'analytics_used': True
                }
            )
            
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"symbol": symbol})
            return None
    
    def calculate_dynamic_position_size(self, signal: TradingSignal, account_balance: float) -> float:
        """Calcular tamaño de posición dinámico"""
        try:
            base_risk = 0.02  # 2% base
            
            # Ajustar riesgo por fuerza de señal
            strength_multiplier = {
                SignalStrength.WEAK: 0.7,
                SignalStrength.MODERATE: 1.0,
                SignalStrength.STRONG: 1.3,
                SignalStrength.VERY_STRONG: 1.6
            }
            
            # Calcular riesgo ajustado
            adjusted_risk = (base_risk * 
                           strength_multiplier.get(signal.strength, 1.0) *
                           signal.confidence)
            
            # Limitar el riesgo máximo
            adjusted_risk = min(adjusted_risk, 0.05)  # Máximo 5%
            
            position_size = account_balance * adjusted_risk
            
            self.logger_manager.log_info(f"📊 Posición calculada: ${position_size:.2f} "
                                       f"(Risk: {adjusted_risk:.1%})")
            
            return position_size
            
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"signal": signal.symbol})
            return account_balance * 0.01  # Fallback 1%
    
    def start_strategy_service(self) -> bool:
        """Iniciar el servicio de estrategias"""
        try:
            if self.strategies_running:
                self.logger_manager.log_warning("⚠️ Servicio de estrategias ya está ejecutándose")
                return True
            
            self.strategies_running = True
            self.is_active = True
            
            # Iniciar thread de estrategias
            self.strategy_thread = threading.Thread(target=self._strategy_service_loop, daemon=True)
            self.strategy_thread.start()
            
            self.logger_manager.log_info("🚀 Servicio de estrategias iniciado")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"operation": "start_service"})
            self.strategies_running = False
            return False
    
    def stop_strategy_service(self) -> bool:
        """Detener el servicio de estrategias"""
        try:
            self.strategies_running = False
            self.is_active = False
            
            if self.strategy_thread and self.strategy_thread.is_alive():
                self.strategy_thread.join(timeout=5.0)
            
            self.logger_manager.log_info("⏹️ Servicio de estrategias detenido")
            return True
            
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"operation": "stop_service"})
            return False
    
    def _strategy_service_loop(self):
        """Loop principal del servicio de estrategias"""
        try:
            while self.strategies_running:
                try:
                    # Actualizar métricas
                    self._update_strategy_metrics()
                    
                    # Procesar estrategias activas
                    self._process_active_strategies()
                    
                    # Actualizar timestamp
                    self.last_update = datetime.now()
                    
                    # Pausa entre ciclos
                    time.sleep(1.0)
                    
                except Exception as e:
                    self.error_manager.handle_system_error("StrategyEngine", e, {"location": "service_loop"})
                    time.sleep(5.0)
                    
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"location": "service_loop_critical"})
            self.strategies_running = False
    
    def _update_strategy_metrics(self):
        """Actualizar métricas del motor de estrategias"""
        try:
            with self.strategy_lock:
                # Calcular señales por hora
                if len(self.signal_history) > 1:
                    time_span = (self.signal_history[-1].timestamp - self.signal_history[0].timestamp).total_seconds() / 3600
                    self.strategy_metrics['signals_per_hour'] = len(self.signal_history) / max(1, time_span)
                
                # Fuerza promedio de señales
                if self.signal_history:
                    avg_strength = sum(s.strength.value for s in self.signal_history) / len(self.signal_history)
                    self.strategy_metrics['avg_signal_strength'] = avg_strength
                
                # Actualizar conteo de estrategias activas
                self.strategy_metrics['active_strategies_count'] = sum(1 for active in self.active_strategies.values() if active)
            
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"location": "update_metrics"})
    
    def _process_active_strategies(self):
        """Procesar estrategias activas"""
        try:
            for strategy_name, is_active in self.active_strategies.items():
                if is_active and strategy_name in self.strategy_configs:
                    config = self.strategy_configs[strategy_name]
                    
                    # Procesar cada símbolo de la estrategia
                    for symbol in config.symbols:
                        # Datos simulados para prueba (en producción vendría del DataManager)
                        mock_data = {
                            'price': 1.0850 + np.random.normal(0, 0.001),
                            'volatility': 0.015 + np.random.normal(0, 0.005)
                        }
                        
                        # Generar señal según tipo de estrategia
                        signal = None
                        if config.strategy_type == StrategyType.ADAPTIVE_GRID:
                            signal = self.generate_adaptive_grid_signal(symbol, mock_data)
                        
                        # Procesar señal si existe y es suficientemente fuerte
                        if signal and signal.strength.value >= config.min_signal_strength.value:
                            with self.strategy_lock:
                                self.signal_history.append(signal)
                                self.active_signals[f"{symbol}_{signal.timeframe}"] = signal
                                self.strategy_metrics['total_signals_generated'] += 1
                            
                            self.logger_manager.log_info(f"🎯 Señal: {symbol} {signal.signal_type} "
                                                       f"({signal.strength.name}, {signal.confidence:.1%})")
                        
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"location": "process_strategies"})
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """Obtener estado completo del motor de estrategias"""
        try:
            with self.strategy_lock:
                status = {
                    'component_id': self.component_id,
                    'version': self.version,
                    'is_active': self.is_active,
                    'strategies_running': self.strategies_running,
                    'last_update': self.last_update.isoformat() if self.last_update else None,
                    'active_strategies': dict(self.active_strategies),
                    'strategy_configs_count': len(self.strategy_configs),
                    'active_signals_count': len(self.active_signals),
                    'signal_history_count': len(self.signal_history),
                    'metrics': dict(self.strategy_metrics)
                }
            
            return status
            
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"location": "get_status"})
            return {'error': str(e)}
    
    def get_active_signals(self) -> Dict[str, TradingSignal]:
        """Obtener señales activas"""
        try:
            with self.strategy_lock:
                return dict(self.active_signals)
                
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"location": "get_signals"})
            return {}
    
    def cleanup(self):
        """Limpieza de recursos"""
        try:
            self.stop_strategy_service()
            
            with self.strategy_lock:
                self.strategy_configs.clear()
                self.active_strategies.clear()
                self.signal_history.clear()
                self.active_signals.clear()
            
            self.logger_manager.log_info(f"🧹 {self.component_id} limpieza completada")
            
        except Exception as e:
            self.error_manager.handle_system_error("StrategyEngine", e, {"location": "cleanup"})

if __name__ == "__main__":
    # Demo básico del StrategyEngine
    print("🎯 STRATEGY ENGINE - PUERTA-S2-STRATEGY")
    print("=" * 50)
    
    try:
        # Inicializar usando el protocolo SÓTANO 1
        engine = StrategyEngine()
        
        # Configurar estrategia adaptativa
        config = StrategyConfig(
            strategy_type=StrategyType.ADAPTIVE_GRID,
            timeframes=["M15", "H1"],
            symbols=["EURUSD", "GBPUSD"],
            risk_per_trade=0.02,
            max_concurrent_trades=3
        )
        
        engine.initialize_strategy_config("adaptive_grid_1", config)
        engine.start_strategy("adaptive_grid_1")
        
        # Iniciar servicio
        engine.start_strategy_service()
        
        # Simular funcionamiento
        print("🚀 Motor de estrategias iniciado...")
        time.sleep(5)
        
        # Mostrar estado
        status = engine.get_strategy_status()
        print(f"\n📊 Estado: {status['metrics']['active_strategies_count']} estrategias activas")
        print(f"🎯 Señales generadas: {status['metrics']['total_signals_generated']}")
        
        # Cleanup
        engine.cleanup()
        print("\n✅ Demo completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
