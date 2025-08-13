"""
🎯 ENHANCED ORDER EXECUTOR - FVG LIMIT ORDERS
============================================

Versión mejorada del OrderExecutor que utiliza análisis de FVG para 
generar órdenes límite inteligentes en lugar de órdenes de mercado.

NUEVA ESTRATEGIA:
- FVG BULLISH → BUY LIMIT en gap_low (esperar retroceso)
- FVG BEARISH → SELL LIMIT en gap_high (esperar retroceso)
- Stop Loss y Take Profit basados en estructura FVG
- Gestión de tiempo de vida de órdenes límite

INTEGRACIÓN CON:
- FVGDetector para análisis de gaps
- FVGQualityAnalyzer para validación de calidad
- ML Foundation para datos históricos

Autor: Sistema Trading Grid Avanzado
Fecha: Agosto 13, 2025
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Imports del sistema
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager

# Imports de análisis FVG
try:
    from src.analysis.piso_3.deteccion.fvg_detector import FVGDetector, FVGData
    FVG_DETECTOR_AVAILABLE = True
except ImportError:
    FVG_DETECTOR_AVAILABLE = False
    FVGDetector = None
    FVGData = None

try:
    from src.analysis.piso_3.analisis.fvg_quality_analyzer import FVGQualityAnalyzer
    FVG_QUALITY_ANALYZER_AVAILABLE = True
except ImportError:
    FVG_QUALITY_ANALYZER_AVAILABLE = False
    
    # Mock FVGQualityAnalyzer para evitar errores
    class FVGQualityAnalyzer:
        """Mock FVG Quality Analyzer para compatibilidad"""
        def __init__(self, logger=None):
            self.logger = logger
        
        def calculate_quality_score(self, fvg_data: Any, market_context: Dict[str, Any]) -> float:
            """Calcular score de calidad de FVG (mock implementation)"""
            return getattr(fvg_data, 'quality_score', 0.5)
        
        def validate_fvg_entry_conditions(self, fvg_data: Any, market_context: Dict[str, Any]) -> bool:
            """Validar condiciones de entrada para FVG (mock implementation)"""
            return True

try:
    from src.analysis.piso_3.trading import FVGSignalGenerator, SignalType, SignalStrength
    FVG_SIGNAL_GENERATOR_AVAILABLE = True
except ImportError:
    FVG_SIGNAL_GENERATOR_AVAILABLE = False
    FVGSignalGenerator = None
    SignalType = None
    SignalStrength = None

if not (FVG_DETECTOR_AVAILABLE or FVG_QUALITY_ANALYZER_AVAILABLE or FVG_SIGNAL_GENERATOR_AVAILABLE):
    print("⚠️ Import warning FVG modules: Componentes FVG no disponibles, usando análisis básico")

# Import ML Foundation si está disponible
try:
    from src.core.ml_foundation.fvg_database_manager import FVGDatabaseManager
except ImportError:
    FVGDatabaseManager = None

import MetaTrader5 as mt5


class FVGLimitOrderType(Enum):
    """Tipos de órdenes límite basadas en FVG"""
    BUY_LIMIT_FVG_RETRACEMENT = "buy_limit_fvg_retracement"   # Compra en retroceso a FVG bullish
    SELL_LIMIT_FVG_RETRACEMENT = "sell_limit_fvg_retracement" # Venta en retroceso a FVG bearish
    BUY_LIMIT_FVG_BREAKOUT = "buy_limit_fvg_breakout"         # Compra en ruptura de FVG
    SELL_LIMIT_FVG_BREAKOUT = "sell_limit_fvg_breakout"       # Venta en ruptura de FVG


@dataclass
class FVGLimitOrder:
    """Orden límite basada en análisis FVG"""
    symbol: str
    order_type: FVGLimitOrderType
    entry_price: float
    stop_loss: float
    take_profit: float
    volume: float
    fvg_data: FVGData
    quality_score: float
    confidence: float
    expiry_time: datetime
    comment: str = "FVG_Limit_Order"
    magic: int = 987654
    
    # Metadatos de la orden
    creation_time: datetime = None
    mt5_order_id: int = 0
    status: str = "PENDING"
    
    def __post_init__(self):
        if self.creation_time is None:
            self.creation_time = datetime.now()


class EnhancedOrderExecutor:
    """
    🎯 ENHANCED ORDER EXECUTOR CON ANÁLISIS FVG
    
    Ejecutor de órdenes mejorado que utiliza análisis de Fair Value Gaps
    para generar órdenes límite inteligentes en lugar de órdenes de mercado.
    """
    
    def __init__(self, 
                 config_manager: Optional[ConfigManager] = None,
                 logger_manager: Optional[LoggerManager] = None,
                 error_manager: Optional[ErrorManager] = None,
                 fvg_detector: Optional[FVGDetector] = None,
                 fvg_quality_analyzer: Optional[FVGQualityAnalyzer] = None,
                 ml_foundation: Optional[FVGDatabaseManager] = None):
        
        # Managers principales
        self.config = config_manager or ConfigManager()
        self.logger = logger_manager or LoggerManager()
        self.error_manager = error_manager or ErrorManager(self.logger, self.config)
        
        # Analizadores FVG
        self.fvg_detector = fvg_detector or FVGDetector()
        self.fvg_quality_analyzer = fvg_quality_analyzer
        self.ml_foundation = ml_foundation
        
        # Configuración del Enhanced Executor
        self.component_id = "ENHANCED-ORDER-EXECUTOR"
        self.version = "v2.0.0-FVG"
        
        # Estado del sistema
        self.is_active = False
        self.limit_orders_enabled = True
        
        # Tracking de órdenes FVG
        self.active_fvg_orders: Dict[int, FVGLimitOrder] = {}
        self.completed_fvg_orders: List[FVGLimitOrder] = []
        self.expired_fvg_orders: List[FVGLimitOrder] = []
        
        # Configuración específica para órdenes FVG
        self.fvg_order_config = {
            'default_volume': 0.01,
            'max_volume': 0.1,
            'base_expiry_hours': 24,        # Vida base de órdenes límite
            'quality_expiry_multiplier': 2.0, # Multiplicador por calidad
            'min_gap_size_pips': 0.5,      # Gap mínimo para generar orden
            'max_gap_size_pips': 10.0,     # Gap máximo para generar orden
            'risk_reward_ratio': 2.0,      # R:R objetivo
            'max_orders_per_symbol': 3,    # Máximo órdenes simultáneas por símbolo
            'retracement_percentage': 0.618, # % de retroceso para entrada
        }
        
        # Métricas específicas FVG
        self.fvg_metrics = {
            'total_fvg_signals_processed': 0,
            'total_limit_orders_placed': 0,
            'total_limit_orders_filled': 0,
            'total_limit_orders_expired': 0,
            'avg_fill_time_hours': 0.0,
            'success_rate_by_quality': {},
            'best_performing_timeframe': 'UNKNOWN'
        }
        
        self.logger.log_success(f"✅ {self.component_id} {self.version} inicializado")
        self.logger.log_info(f"🎯 Modo: Órdenes límite inteligentes con análisis FVG")
    
    
    def process_fvg_signal(self, fvg_data: FVGData, market_context: Dict = None) -> bool:
        """
        🎯 FUNCIÓN PRINCIPAL: Procesar señal FVG y generar orden límite
        
        Esta función reemplaza el process_signal tradicional y utiliza
        análisis de FVG para crear órdenes límite inteligentes.
        """
        try:
            if not self.is_active or not self.limit_orders_enabled:
                self.logger.log_warning("⚠️ Enhanced Order Executor no está activo")
                return False
            
            self.fvg_metrics['total_fvg_signals_processed'] += 1
            
            self.logger.log_info(f"🎯 Procesando señal FVG: {fvg_data.symbol} {fvg_data.type}")
            
            # 1. Validar FVG
            if not self._validate_fvg_for_trading(fvg_data):
                self.logger.log_warning(f"❌ FVG no válido para trading: {fvg_data.symbol}")
                return False
            
            # 2. Análisis de calidad si está disponible
            quality_score = self._get_fvg_quality_score(fvg_data)
            
            # 3. Verificar límites de órdenes por símbolo
            if not self._check_order_limits(fvg_data.symbol):
                self.logger.log_warning(f"⚠️ Límite de órdenes alcanzado para {fvg_data.symbol}")
                return False
            
            # 4. Calcular parámetros de la orden límite
            order_params = self._calculate_fvg_limit_order_params(fvg_data, quality_score, market_context)
            if not order_params:
                self.logger.log_error(f"❌ Error calculando parámetros de orden: {fvg_data.symbol}")
                return False
            
            # 5. Crear orden límite FVG
            fvg_order = self._create_fvg_limit_order(fvg_data, order_params, quality_score)
            
            # 6. Ejecutar orden límite en MT5
            success = self._place_fvg_limit_order(fvg_order)
            
            if success:
                self.active_fvg_orders[fvg_order.mt5_order_id] = fvg_order
                self.fvg_metrics['total_limit_orders_placed'] += 1
                
                # 7. Almacenar en ML Foundation si está disponible
                self._store_fvg_order_in_ml(fvg_order)
                
                self.logger.log_success(f"✅ Orden límite FVG colocada: {fvg_order.mt5_order_id}")
                return True
            else:
                self.logger.log_error(f"❌ Error colocando orden límite FVG: {fvg_data.symbol}")
                return False
                
        except Exception as e:
            self.error_manager.handle_system_error("EnhancedOrderExecutor", e, {"fvg": fvg_data.symbol})
            return False
    
    
    def _validate_fvg_for_trading(self, fvg_data: FVGData) -> bool:
        """Validar FVG para generar orden de trading"""
        try:
            # Validar gap size en pips
            gap_size_pips = fvg_data.gap_size * 10000  # Convertir a pips
            
            if gap_size_pips < self.fvg_order_config['min_gap_size_pips']:
                self.logger.log_debug(f"Gap muy pequeño: {gap_size_pips:.1f} pips")
                return False
            
            if gap_size_pips > self.fvg_order_config['max_gap_size_pips']:
                self.logger.log_debug(f"Gap muy grande: {gap_size_pips:.1f} pips")
                return False
            
            # Validar que el FVG esté activo
            if fvg_data.status != 'ACTIVE':
                self.logger.log_debug(f"FVG no está activo: {fvg_data.status}")
                return False
            
            # Validar símbolo en MT5
            symbol_info = mt5.symbol_info(fvg_data.symbol)
            if symbol_info is None:
                self.logger.log_error(f"❌ Símbolo no disponible en MT5: {fvg_data.symbol}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error validando FVG: {e}")
            return False
    
    
    def _get_fvg_quality_score(self, fvg_data: FVGData) -> float:
        """Obtener score de calidad del FVG"""
        try:
            if self.fvg_quality_analyzer:
                quality_analysis = self.fvg_quality_analyzer.analyze_fvg_quality(fvg_data)
                return quality_analysis.get('overall_score', 0.5)
            else:
                # Score básico basado en gap size
                gap_size_pips = fvg_data.gap_size * 10000
                if gap_size_pips >= 3.0:
                    return 0.8  # Alta calidad
                elif gap_size_pips >= 1.5:
                    return 0.6  # Calidad media
                else:
                    return 0.4  # Calidad baja
        except Exception as e:
            self.logger.log_error(f"Error obteniendo quality score: {e}")
            return 0.5
    
    
    def _check_order_limits(self, symbol: str) -> bool:
        """Verificar límites de órdenes por símbolo"""
        active_orders_for_symbol = [
            order for order in self.active_fvg_orders.values() 
            if order.symbol == symbol
        ]
        
        max_orders = self.fvg_order_config['max_orders_per_symbol']
        return len(active_orders_for_symbol) < max_orders
    
    
    def _calculate_fvg_limit_order_params(self, fvg_data: FVGData, quality_score: float, market_context: Dict = None) -> Optional[Dict]:
        """
        🧮 CÁLCULO INTELIGENTE DE PARÁMETROS DE ORDEN LÍMITE
        
        Calcula precio de entrada, stop loss, take profit y volumen
        basado en análisis avanzado de FVG.
        """
        try:
            # Obtener precios actuales
            tick = mt5.symbol_info_tick(fvg_data.symbol)
            if not tick:
                return None
            
            current_price = tick.bid if fvg_data.type == 'BEARISH' else tick.ask
            
            # Calcular precio de entrada inteligente
            entry_price = self._calculate_smart_entry_price(fvg_data, current_price, quality_score)
            
            # Calcular stop loss y take profit
            stop_loss = self._calculate_stop_loss(fvg_data, entry_price, quality_score)
            take_profit = self._calculate_take_profit(fvg_data, entry_price, stop_loss, quality_score)
            
            # Calcular volumen ajustado por calidad
            volume = self._calculate_volume_by_quality(quality_score)
            
            # Calcular tiempo de vida de la orden
            expiry_time = self._calculate_order_expiry(quality_score)
            
            # Validar risk-reward ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            risk_reward = reward / risk if risk > 0 else 0
            
            if risk_reward < 1.5:  # R:R mínimo
                self.logger.log_warning(f"⚠️ Risk-Reward ratio bajo: {risk_reward:.2f}")
                return None
            
            return {
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'volume': volume,
                'expiry_time': expiry_time,
                'risk_reward_ratio': risk_reward,
                'current_price': current_price
            }
            
        except Exception as e:
            self.logger.log_error(f"Error calculando parámetros de orden: {e}")
            return None
    
    
    def _calculate_smart_entry_price(self, fvg_data: FVGData, current_price: float, quality_score: float) -> float:
        """
        🎯 CÁLCULO DE PRECIO DE ENTRADA INTELIGENTE
        
        Estrategias de entrada basadas en tipo de FVG:
        - FVG BULLISH: BUY LIMIT en gap_low (retroceso)
        - FVG BEARISH: SELL LIMIT en gap_high (retroceso)
        """
        gap_mid = (fvg_data.gap_high + fvg_data.gap_low) / 2
        retracement_pct = self.fvg_order_config['retracement_percentage']
        
        if fvg_data.type == 'BULLISH':
            # Para FVG bullish, esperamos retroceso hacia gap_low
            # Entry más agresivo si mayor calidad
            entry_adjustment = (1 - quality_score) * 0.2  # 0-20% adjustment
            optimal_entry = fvg_data.gap_low + (fvg_data.gap_size * entry_adjustment)
            
            # Si el precio ya está por debajo del gap, usar precio más conservador
            if current_price < fvg_data.gap_low:
                optimal_entry = min(optimal_entry, gap_mid)
                
        else:  # BEARISH FVG
            # Para FVG bearish, esperamos retroceso hacia gap_high
            entry_adjustment = (1 - quality_score) * 0.2
            optimal_entry = fvg_data.gap_high - (fvg_data.gap_size * entry_adjustment)
            
            # Si el precio ya está por encima del gap, usar precio más conservador
            if current_price > fvg_data.gap_high:
                optimal_entry = max(optimal_entry, gap_mid)
        
        self.logger.log_info(f"📊 Entry calculado: {optimal_entry:.5f} (gap: {fvg_data.gap_low:.5f}-{fvg_data.gap_high:.5f})")
        return optimal_entry
    
    
    def _calculate_stop_loss(self, fvg_data: FVGData, entry_price: float, quality_score: float) -> float:
        """Calcular stop loss basado en estructura FVG"""
        gap_size = fvg_data.gap_size
        
        # Ajustar stop loss por calidad (mayor calidad = stop más lejano)
        sl_multiplier = 1.0 + (quality_score * 0.5)  # 1.0x - 1.5x
        
        if fvg_data.type == 'BULLISH':
            # Stop loss por debajo del gap
            stop_loss = fvg_data.gap_low - (gap_size * sl_multiplier)
        else:
            # Stop loss por encima del gap
            stop_loss = fvg_data.gap_high + (gap_size * sl_multiplier)
        
        return stop_loss
    
    
    def _calculate_take_profit(self, fvg_data: FVGData, entry_price: float, stop_loss: float, quality_score: float) -> float:
        """Calcular take profit basado en risk-reward y calidad FVG"""
        risk = abs(entry_price - stop_loss)
        target_rr = self.fvg_order_config['risk_reward_ratio']
        
        # Ajustar R:R por calidad
        quality_rr_bonus = quality_score * 0.5  # 0-0.5 bonus
        adjusted_rr = target_rr + quality_rr_bonus
        
        reward = risk * adjusted_rr
        
        if fvg_data.type == 'BULLISH':
            take_profit = entry_price + reward
        else:
            take_profit = entry_price - reward
        
        return take_profit
    
    
    def _calculate_volume_by_quality(self, quality_score: float) -> float:
        """Calcular volumen ajustado por calidad del FVG"""
        base_volume = self.fvg_order_config['default_volume']
        max_volume = self.fvg_order_config['max_volume']
        
        # Volumen base + bonus por calidad
        volume_multiplier = 1.0 + (quality_score * 1.0)  # 1.0x - 2.0x
        calculated_volume = base_volume * volume_multiplier
        
        # Limitar volumen máximo
        final_volume = min(calculated_volume, max_volume)
        return round(final_volume, 2)
    
    
    def _calculate_order_expiry(self, quality_score: float) -> datetime:
        """Calcular tiempo de vida de la orden basado en calidad"""
        base_hours = self.fvg_order_config['base_expiry_hours']
        quality_multiplier = self.fvg_order_config['quality_expiry_multiplier']
        
        # Órdenes de mayor calidad duran más tiempo
        expiry_hours = base_hours * (1 + (quality_score * quality_multiplier))
        
        return datetime.now() + timedelta(hours=expiry_hours)
    
    
    def _create_fvg_limit_order(self, fvg_data: FVGData, params: Dict, quality_score: float) -> FVGLimitOrder:
        """Crear objeto FVGLimitOrder"""
        # Determinar tipo de orden
        if fvg_data.type == 'BULLISH':
            order_type = FVGLimitOrderType.BUY_LIMIT_FVG_RETRACEMENT
        else:
            order_type = FVGLimitOrderType.SELL_LIMIT_FVG_RETRACEMENT
        
        # Calcular confianza basada en calidad y R:R
        confidence = (quality_score + min(params['risk_reward_ratio'] / 3.0, 1.0)) / 2
        
        return FVGLimitOrder(
            symbol=fvg_data.symbol,
            order_type=order_type,
            entry_price=params['entry_price'],
            stop_loss=params['stop_loss'],
            take_profit=params['take_profit'],
            volume=params['volume'],
            fvg_data=fvg_data,
            quality_score=quality_score,
            confidence=confidence,
            expiry_time=params['expiry_time'],
            comment=f"FVG_{fvg_data.type}_{fvg_data.timeframe}_{quality_score:.2f}"
        )
    
    
    def _place_fvg_limit_order(self, fvg_order: FVGLimitOrder) -> bool:
        """Colocar orden límite FVG en MT5"""
        try:
            # Determinar tipo de orden MT5
            if fvg_order.order_type == FVGLimitOrderType.BUY_LIMIT_FVG_RETRACEMENT:
                mt5_order_type = mt5.ORDER_TYPE_BUY_LIMIT
            else:
                mt5_order_type = mt5.ORDER_TYPE_SELL_LIMIT
            
            # Crear request MT5
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": fvg_order.symbol,
                "volume": fvg_order.volume,
                "type": mt5_order_type,
                "price": fvg_order.entry_price,
                "sl": fvg_order.stop_loss,
                "tp": fvg_order.take_profit,
                "deviation": 10,
                "magic": fvg_order.magic,
                "comment": fvg_order.comment,
                "type_time": mt5.ORDER_TIME_SPECIFIED,
                "expiration": int(fvg_order.expiry_time.timestamp()),
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            
            self.logger.log_info(f"🚀 Colocando orden límite FVG: {fvg_order.symbol}")
            
            # Ejecutar en MT5
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                fvg_order.mt5_order_id = result.order
                fvg_order.status = "PLACED"
                
                self.logger.log_success(f"✅ Orden límite FVG colocada exitosamente: #{result.order}")
                self.logger.log_info(f"📊 Detalles: {fvg_order.symbol} {fvg_order.volume} lotes @ {fvg_order.entry_price:.5f}")
                self.logger.log_info(f"🛡️ SL: {fvg_order.stop_loss:.5f} | 🎯 TP: {fvg_order.take_profit:.5f}")
                
                return True
            else:
                error_code = result.retcode if result else mt5.last_error()
                self.logger.log_error(f"❌ Error colocando orden límite: {error_code}")
                return False
                
        except Exception as e:
            self.logger.log_error(f"❌ Excepción colocando orden límite: {e}")
            return False
    
    
    def _store_fvg_order_in_ml(self, fvg_order: FVGLimitOrder):
        """Almacenar orden FVG en ML Foundation para análisis futuro"""
        try:
            if self.ml_foundation:
                order_data = {
                    'timestamp_creation': fvg_order.creation_time,
                    'symbol': fvg_order.symbol,
                    'timeframe': fvg_order.fvg_data.timeframe,
                    'gap_type': fvg_order.fvg_data.type,
                    'gap_high': fvg_order.fvg_data.gap_high,
                    'gap_low': fvg_order.fvg_data.gap_low,
                    'gap_size_pips': fvg_order.fvg_data.gap_size * 10000,
                    'quality_score': fvg_order.quality_score,
                    'entry_price': fvg_order.entry_price,
                    'stop_loss': fvg_order.stop_loss,
                    'take_profit': fvg_order.take_profit,
                    'volume': fvg_order.volume,
                    'expiry_time': fvg_order.expiry_time,
                    'mt5_order_id': fvg_order.mt5_order_id,
                    'confidence': fvg_order.confidence,
                    
                    # Datos adicionales para ML
                    'vela1_open': 0.0, 'vela1_high': 0.0, 'vela1_low': 0.0, 'vela1_close': 0.0,
                    'vela2_open': 0.0, 'vela2_high': 0.0, 'vela2_low': 0.0, 'vela2_close': 0.0,
                    'vela3_open': 0.0, 'vela3_high': 0.0, 'vela3_low': 0.0, 'vela3_close': 0.0,
                    'current_price': 0.0,
                    'distance_to_gap': 0.0
                }
                
                fvg_id = self.ml_foundation.insert_fvg(order_data)
                if fvg_id:
                    self.logger.log_success(f"✅ Orden FVG almacenada en ML DB: ID {fvg_id}")
                    
        except Exception as e:
            self.logger.log_error(f"Error almacenando en ML Foundation: {e}")
    
    
    def monitor_active_orders(self):
        """Monitorear órdenes FVG activas para updates de estado"""
        try:
            for order_id, fvg_order in list(self.active_fvg_orders.items()):
                # Verificar estado en MT5
                mt5_orders = mt5.orders_get(ticket=order_id)
                
                if not mt5_orders:  # Orden no encontrada = fue ejecutada o cancelada
                    # Buscar en historial
                    deals = mt5.history_deals_get(ticket=order_id)
                    if deals:
                        # Orden fue ejecutada
                        fvg_order.status = "FILLED"
                        self.completed_fvg_orders.append(fvg_order)
                        self.fvg_metrics['total_limit_orders_filled'] += 1
                        self.logger.log_success(f"✅ Orden FVG ejecutada: #{order_id}")
                    else:
                        # Verificar si expiró
                        if datetime.now() > fvg_order.expiry_time:
                            fvg_order.status = "EXPIRED"
                            self.expired_fvg_orders.append(fvg_order)
                            self.fvg_metrics['total_limit_orders_expired'] += 1
                            self.logger.log_info(f"⏰ Orden FVG expirada: #{order_id}")
                    
                    # Remover de órdenes activas
                    del self.active_fvg_orders[order_id]
                    
        except Exception as e:
            self.logger.log_error(f"Error monitoreando órdenes activas: {e}")
    
    
    def get_fvg_order_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema de órdenes FVG"""
        return {
            'component_id': self.component_id,
            'version': self.version,
            'is_active': self.is_active,
            'limit_orders_enabled': self.limit_orders_enabled,
            'active_orders_count': len(self.active_fvg_orders),
            'completed_orders_count': len(self.completed_fvg_orders),
            'expired_orders_count': len(self.expired_fvg_orders),
            'metrics': self.fvg_metrics.copy(),
            'config': self.fvg_order_config.copy()
        }
    
    
    def enable_fvg_limit_orders(self, enabled: bool = True):
        """Habilitar/deshabilitar órdenes límite FVG"""
        self.limit_orders_enabled = enabled
        status = "habilitadas" if enabled else "deshabilitadas"
        self.logger.log_info(f"🔄 Órdenes límite FVG {status}")
    
    
    def cleanup(self):
        """Cleanup del Enhanced Order Executor"""
        try:
            # Cancelar órdenes activas
            for order_id in list(self.active_fvg_orders.keys()):
                try:
                    cancel_request = {
                        "action": mt5.TRADE_ACTION_REMOVE,
                        "order": order_id
                    }
                    mt5.order_send(cancel_request)
                except:
                    pass  # Continuar aunque falle
            
            self.is_active = False
            self.limit_orders_enabled = False
            self.active_fvg_orders.clear()
            
            self.logger.log_success(f"🧹 {self.component_id} cleanup completado")
            
        except Exception as e:
            self.error_manager.handle_system_error("EnhancedOrderExecutor", e, {"operation": "cleanup"})


# Factory function para crear Enhanced Order Executor
def create_enhanced_order_executor(config_manager=None, logger_manager=None, error_manager=None):
    """Factory para crear Enhanced Order Executor con componentes FVG"""
    try:
        # Crear analizadores FVG
        fvg_detector = FVGDetector()
        
        try:
            fvg_quality_analyzer = FVGQualityAnalyzer()
        except:
            fvg_quality_analyzer = None
        
        # Crear ML Foundation si está disponible
        ml_foundation = None
        if FVGDatabaseManager:
            try:
                ml_foundation = FVGDatabaseManager()
            except:
                pass
        
        # Crear Enhanced Order Executor
        executor = EnhancedOrderExecutor(
            config_manager=config_manager,
            logger_manager=logger_manager,
            error_manager=error_manager,
            fvg_detector=fvg_detector,
            fvg_quality_analyzer=fvg_quality_analyzer,
            ml_foundation=ml_foundation
        )
        
        return executor
        
    except Exception as e:
        print(f"❌ Error creando Enhanced Order Executor: {e}")
        return None


# Demo
def demo_enhanced_order_executor():
    """Demo del Enhanced Order Executor"""
    print("🎯 DEMO ENHANCED ORDER EXECUTOR - FVG LIMIT ORDERS")
    print("=" * 60)
    
    try:
        executor = create_enhanced_order_executor()
        
        if executor:
            executor.is_active = True
            print("✅ Enhanced Order Executor creado exitosamente")
            
            status = executor.get_fvg_order_status()
            print(f"📊 Estado: Activo={status['is_active']}")
            print(f"📊 Órdenes límite: {status['limit_orders_enabled']}")
            print(f"📊 Config: {status['config']}")
            
            print("💡 Listo para procesar señales FVG y generar órdenes límite inteligentes")
            
            executor.cleanup()
        else:
            print("❌ Error creando Enhanced Order Executor")
            
    except Exception as e:
        print(f"❌ Error en demo: {e}")


if __name__ == "__main__":
    demo_enhanced_order_executor()
