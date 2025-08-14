"""
🎯 PISO 4 - ADVANCED POSITION SIZER
=======================================
Sistema avanzado de cálculo de lotaje optimizado para FVG Trading

Características:
- Cálculo dinámico basado en calidad FVG
- Adaptación por sesión de mercado
- Consideración del estado del ciclo diario
- Risk-reward optimization
- Volatility adjustment
- Account protection

Author: Trading Grid System
Version: 4.0 - Advanced Operations
Date: 2025-08-13
"""

from datetime import datetime, timezone
from typing import Dict, Any

class AdvancedPositionSizer:
    """Sistema avanzado de cálculo de posición optimizado"""
    
    def __init__(self, logger_manager):
        """
        Inicializa el Advanced Position Sizer
        
        Args:
            logger_manager: Instancia del LoggerManager
        """
        self.logger = logger_manager.get_logger('piso_4')
        
        # Configuración base de riesgo
        self.base_risk_pct = 1.0  # 1% base risk per trade
        self.max_position_size = 2.0  # Máximo 2 lotes por trade
        self.min_position_size = 0.01  # Mínimo 0.01 lotes
        
        # Multiplicadores por calidad FVG
        self.quality_multipliers = {
            'PREMIUM': 1.5,    # 150% del lotaje base
            'HIGH': 1.2,       # 120% del lotaje base
            'MEDIUM': 1.0,     # 100% del lotaje base (estándar)
            'LOW': 0.7,        # 70% del lotaje base
            'POOR': 0.5        # 50% del lotaje base
        }
        
        # Multiplicadores por sesión
        self.session_multipliers = {
            'LONDON': 1.3,     # Mayor liquidez y volatilidad
            'NY': 1.2,         # Alta liquidez
            'ASIA': 0.9,       # Menor volatilidad
            'OVERLAP': 1.4,    # Overlaps entre sesiones
            'OFF_HOURS': 0.6   # Fuera de horas principales
        }
        
        # Ajustes por estado del ciclo
        self.cycle_adjustments = {
            'FIRST_TRADE': 1.0,     # Trade inicial normal
            'WINNING_STREAK': 1.1,   # Ligero aumento si va bien
            'LOSING_STREAK': 0.8,    # Reducción si hay pérdidas
            'NEAR_TARGET': 0.7,      # Conservador cerca del target
            'NEAR_LIMIT': 0.5        # Muy conservador cerca del límite
        }
        
        # Configuración de volatilidad
        self.volatility_adjustments = {
            'LOW': 1.2,        # Más lotaje en baja volatilidad
            'NORMAL': 1.0,     # Estándar
            'HIGH': 0.8,       # Menos lotaje en alta volatilidad
            'EXTREME': 0.6     # Muy conservador en volatilidad extrema
        }
        
        self.logger.info("🎯 AdvancedPositionSizer inicializado")
    
    def calculate_position_size(self, 
                              fvg_data: Dict[str, Any],
                              session_data: Dict[str, Any],
                              cycle_data: Dict[str, Any],
                              account_data: Dict[str, Any],
                              market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula el tamaño de posición optimizado
        
        Args:
            fvg_data: Datos del FVG (calidad, tamaño, etc.)
            session_data: Datos de la sesión actual
            cycle_data: Estado del ciclo diario
            account_data: Datos de la cuenta (balance, equity, etc.)
            market_data: Datos de mercado (volatilidad, spread, etc.)
        
        Returns:
            Dict con información del lotaje calculado
        """
        try:
            # 1. Calcular base risk amount
            base_risk_amount = self._calculate_base_risk(account_data)
            
            # 2. Obtener multiplicadores
            quality_mult = self._get_quality_multiplier(fvg_data.get('quality', 'MEDIUM'))
            session_mult = self._get_session_multiplier(session_data)
            cycle_mult = self._get_cycle_multiplier(cycle_data)
            volatility_mult = self._get_volatility_multiplier(market_data)
            
            # 3. Calcular multiplicador total
            total_multiplier = quality_mult * session_mult * cycle_mult * volatility_mult
            
            # 4. Calcular risk amount ajustado
            adjusted_risk_amount = base_risk_amount * total_multiplier
            
            # 5. Calcular posición basada en SL
            stop_loss_pips = self._calculate_stop_loss_pips(fvg_data)
            position_size = self._calculate_lot_size(
                adjusted_risk_amount, 
                stop_loss_pips, 
                market_data
            )
            
            # 6. Aplicar límites de seguridad
            final_position_size = self._apply_safety_limits(
                position_size, 
                account_data, 
                cycle_data
            )
            
            # 7. Preparar resultado
            result = {
                'position_size': final_position_size,
                'risk_amount': adjusted_risk_amount,
                'stop_loss_pips': stop_loss_pips,
                'multipliers': {
                    'quality': quality_mult,
                    'session': session_mult,
                    'cycle': cycle_mult,
                    'volatility': volatility_mult,
                    'total': total_multiplier
                },
                'risk_percentage': (adjusted_risk_amount / account_data['equity']) * 100,
                'expected_sl_amount': final_position_size * stop_loss_pips * market_data.get('pip_value', 10),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.logger.info(f"📊 Position calculada: {final_position_size:.2f} lotes "
                           f"(Risk: {result['risk_percentage']:.2f}%)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando position size: {e}")
            return self._get_emergency_position_size(account_data)
    
    def _calculate_base_risk(self, account_data: Dict[str, Any]) -> float:
        """Calcula el monto base de riesgo"""
        equity = account_data.get('equity', 10000)
        return equity * (self.base_risk_pct / 100)
    
    def _get_quality_multiplier(self, quality: str) -> float:
        """Obtiene multiplicador por calidad FVG"""
        return self.quality_multipliers.get(quality, 1.0)
    
    def _get_session_multiplier(self, session_data: Dict[str, Any]) -> float:
        """Obtiene multiplicador por sesión"""
        session = session_data.get('active_session', 'OFF_HOURS')
        is_overlap = session_data.get('is_overlap', False)
        
        if is_overlap:
            return self.session_multipliers.get('OVERLAP', 1.4)
        
        return self.session_multipliers.get(session, 1.0)
    
    def _get_cycle_multiplier(self, cycle_data: Dict[str, Any]) -> float:
        """Obtiene multiplicador por estado del ciclo"""
        trades_count = cycle_data.get('trades_executed', 0)
        daily_pnl_pct = cycle_data.get('daily_pnl_percentage', 0)
        target_pct = 3.0
        limit_pct = -2.0
        
        # Determinar estado del ciclo
        if trades_count == 0:
            state = 'FIRST_TRADE'
        elif daily_pnl_pct > target_pct * 0.8:  # Cerca del target
            state = 'NEAR_TARGET'
        elif daily_pnl_pct < limit_pct * 0.8:   # Cerca del límite
            state = 'NEAR_LIMIT'
        elif daily_pnl_pct > 0:
            state = 'WINNING_STREAK'
        else:
            state = 'LOSING_STREAK'
        
        return self.cycle_adjustments.get(state, 1.0)
    
    def _get_volatility_multiplier(self, market_data: Dict[str, Any]) -> float:
        """Obtiene multiplicador por volatilidad"""
        volatility = market_data.get('volatility_level', 'NORMAL')
        return self.volatility_adjustments.get(volatility, 1.0)
    
    def _calculate_stop_loss_pips(self, fvg_data: Dict[str, Any]) -> float:
        """Calcula los pips de stop loss basado en el FVG"""
        fvg_size_pips = fvg_data.get('size_pips', 20)
        
        # SL típicamente 1.5x el tamaño del FVG
        sl_pips = fvg_size_pips * 1.5
        
        # Límites mínimos y máximos
        min_sl = 15  # Mínimo 15 pips
        max_sl = 50  # Máximo 50 pips
        
        return max(min_sl, min(sl_pips, max_sl))
    
    def _calculate_lot_size(self, risk_amount: float, sl_pips: float, 
                          market_data: Dict[str, Any]) -> float:
        """Calcula el tamaño de lote basado en risk amount y SL"""
        pip_value = market_data.get('pip_value', 10)  # $10 por pip para 1 lote estándar
        
        if sl_pips <= 0:
            return self.min_position_size
        
        lot_size = risk_amount / (sl_pips * pip_value)
        return lot_size
    
    def _apply_safety_limits(self, position_size: float, 
                           account_data: Dict[str, Any],
                           cycle_data: Dict[str, Any]) -> float:
        """Aplica límites de seguridad"""
        # Límites básicos
        position_size = max(self.min_position_size, 
                          min(position_size, self.max_position_size))
        
        # Límite por margin disponible
        available_margin = account_data.get('free_margin', 10000)
        margin_per_lot = account_data.get('margin_per_lot', 1000)
        max_lots_by_margin = available_margin / margin_per_lot * 0.8  # 80% del margin
        
        position_size = min(position_size, max_lots_by_margin)
        
        # Límite adicional si ya hay trades en el ciclo
        trades_executed = cycle_data.get('trades_executed', 0)
        if trades_executed >= 2:  # Si ya hay 2 trades, ser más conservador
            position_size *= 0.8
        
        return round(position_size, 2)
    
    def _get_emergency_position_size(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Devuelve posición de emergencia en caso de error"""
        return {
            'position_size': self.min_position_size,
            'risk_amount': account_data.get('equity', 10000) * 0.005,  # 0.5% emergency
            'stop_loss_pips': 20,
            'multipliers': {
                'quality': 1.0,
                'session': 1.0,
                'cycle': 1.0,
                'volatility': 1.0,
                'total': 1.0
            },
            'risk_percentage': 0.5,
            'expected_sl_amount': self.min_position_size * 20 * 10,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'emergency_mode': True
        }
    
    def get_position_analysis(self, position_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza una posición calculada para debugging/monitoring
        
        Args:
            position_data: Datos de la posición calculada
            
        Returns:
            Dict con análisis detallado
        """
        multipliers = position_data.get('multipliers', {})
        
        analysis = {
            'size_category': self._categorize_position_size(position_data['position_size']),
            'risk_level': self._categorize_risk_level(position_data['risk_percentage']),
            'dominant_factor': self._get_dominant_factor(multipliers),
            'optimization_score': self._calculate_optimization_score(position_data),
            'recommendations': self._get_recommendations(position_data)
        }
        
        return analysis
    
    def _categorize_position_size(self, size: float) -> str:
        """Categoriza el tamaño de posición"""
        if size <= 0.1:
            return 'MICRO'
        elif size <= 0.5:
            return 'SMALL'
        elif size <= 1.0:
            return 'MEDIUM'
        elif size <= 1.5:
            return 'LARGE'
        else:
            return 'MAXIMUM'
    
    def _categorize_risk_level(self, risk_pct: float) -> str:
        """Categoriza el nivel de riesgo"""
        if risk_pct <= 0.5:
            return 'CONSERVATIVE'
        elif risk_pct <= 1.0:
            return 'MODERATE'
        elif risk_pct <= 1.5:
            return 'AGGRESSIVE'
        else:
            return 'HIGH_RISK'
    
    def _get_dominant_factor(self, multipliers: Dict[str, float]) -> str:
        """Identifica el factor dominante en el cálculo"""
        factors = {k: v for k, v in multipliers.items() if k != 'total'}
        if not factors:
            return 'NONE'
        max_factor = max(factors.keys(), key=lambda k: factors[k])
        return max_factor.upper()
    
    def _calculate_optimization_score(self, position_data: Dict[str, Any]) -> float:
        """Calcula un score de optimización (0-100)"""
        # Factores que indican buena optimización
        risk_pct = position_data['risk_percentage']
        total_mult = position_data['multipliers']['total']
        
        score = 100
        
        # Penalizar riesgo muy alto o muy bajo
        if risk_pct > 2.0 or risk_pct < 0.3:
            score -= 20
        
        # Penalizar multiplicadores extremos
        if total_mult > 2.0 or total_mult < 0.5:
            score -= 15
        
        # Bonus por balance
        if 0.8 <= risk_pct <= 1.5 and 0.8 <= total_mult <= 1.5:
            score += 10
        
        return max(0, min(100, score))
    
    def _get_recommendations(self, position_data: Dict[str, Any]) -> list:
        """Genera recomendaciones basadas en la posición"""
        recommendations = []
        
        risk_pct = position_data['risk_percentage']
        multipliers = position_data['multipliers']
        
        if risk_pct > 1.8:
            recommendations.append("ALTO RIESGO: Considerar reducir multiplicadores")
        
        if risk_pct < 0.4:
            recommendations.append("BAJO RIESGO: Oportunidad perdida de optimización")
        
        if multipliers['quality'] < 0.8:
            recommendations.append("CALIDAD BAJA: Solo trades de alta calidad recomendados")
        
        if multipliers['cycle'] < 0.8:
            recommendations.append("CICLO ADVERSO: Modo conservador activado")
        
        if not recommendations:
            recommendations.append("POSICIÓN OPTIMIZADA: Parámetros dentro de rangos ideales")
        
        return recommendations
