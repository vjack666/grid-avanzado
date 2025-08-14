"""
🧪 TEST SIMPLE - ADVANCED POSITION SIZER
========================================
Script de testing simplificado sin dependencias complejas
"""

from datetime import datetime, timezone

class MockLogger:
    """Mock del Logger para testing"""
    def info(self, msg): print(f"ℹ️ {msg}")
    def error(self, msg): print(f"❌ {msg}")
    def warning(self, msg): print(f"⚠️ {msg}")

class MockLoggerManager:
    """Mock del LoggerManager para testing"""
    def get_logger(self, name): return MockLogger()

class AdvancedPositionSizer:
    """Sistema avanzado de cálculo de posición optimizado"""
    
    def __init__(self, logger_manager):
        self.logger = logger_manager.get_logger('piso_4')
        
        # Configuración base de riesgo
        self.base_risk_pct = 1.0
        self.max_position_size = 2.0
        self.min_position_size = 0.01
        
        # Multiplicadores por calidad FVG
        self.quality_multipliers = {
            'PREMIUM': 1.5, 'HIGH': 1.2, 'MEDIUM': 1.0, 'LOW': 0.7, 'POOR': 0.5
        }
        
        # Multiplicadores por sesión
        self.session_multipliers = {
            'LONDON': 1.3, 'NY': 1.2, 'ASIA': 0.9, 'OVERLAP': 1.4, 'OFF_HOURS': 0.6
        }
        
        # Ajustes por estado del ciclo
        self.cycle_adjustments = {
            'FIRST_TRADE': 1.0, 'WINNING_STREAK': 1.1, 'LOSING_STREAK': 0.8,
            'NEAR_TARGET': 0.7, 'NEAR_LIMIT': 0.5
        }
        
        # Configuración de volatilidad
        self.volatility_adjustments = {
            'LOW': 1.2, 'NORMAL': 1.0, 'HIGH': 0.8, 'EXTREME': 0.6
        }
        
        self.logger.info("🎯 AdvancedPositionSizer inicializado")
    
    def calculate_position_size(self, fvg_data, session_data, cycle_data, account_data, market_data):
        """Calcula el tamaño de posición optimizado"""
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
            position_size = self._calculate_lot_size(adjusted_risk_amount, stop_loss_pips, market_data)
            
            # 6. Aplicar límites de seguridad
            final_position_size = self._apply_safety_limits(position_size, account_data, cycle_data)
            
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
            
            self.logger.info(f"📊 Position calculada: {final_position_size:.2f} lotes (Risk: {result['risk_percentage']:.2f}%)")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error calculando position size: {e}")
            return self._get_emergency_position_size(account_data)
    
    def _calculate_base_risk(self, account_data):
        equity = account_data.get('equity', 10000)
        return equity * (self.base_risk_pct / 100)
    
    def _get_quality_multiplier(self, quality):
        return self.quality_multipliers.get(quality, 1.0)
    
    def _get_session_multiplier(self, session_data):
        session = session_data.get('active_session', 'OFF_HOURS')
        is_overlap = session_data.get('is_overlap', False)
        
        if is_overlap:
            return self.session_multipliers.get('OVERLAP', 1.4)
        return self.session_multipliers.get(session, 1.0)
    
    def _get_cycle_multiplier(self, cycle_data):
        trades_count = cycle_data.get('trades_executed', 0)
        daily_pnl_pct = cycle_data.get('daily_pnl_percentage', 0)
        
        if trades_count == 0:
            state = 'FIRST_TRADE'
        elif daily_pnl_pct > 2.4:  # Cerca del target 3%
            state = 'NEAR_TARGET'
        elif daily_pnl_pct < -1.6:   # Cerca del límite -2%
            state = 'NEAR_LIMIT'
        elif daily_pnl_pct > 0:
            state = 'WINNING_STREAK'
        else:
            state = 'LOSING_STREAK'
        
        return self.cycle_adjustments.get(state, 1.0)
    
    def _get_volatility_multiplier(self, market_data):
        volatility = market_data.get('volatility_level', 'NORMAL')
        return self.volatility_adjustments.get(volatility, 1.0)
    
    def _calculate_stop_loss_pips(self, fvg_data):
        fvg_size_pips = fvg_data.get('size_pips', 20)
        sl_pips = fvg_size_pips * 1.5
        return max(15, min(sl_pips, 50))  # Entre 15 y 50 pips
    
    def _calculate_lot_size(self, risk_amount, sl_pips, market_data):
        pip_value = market_data.get('pip_value', 10)
        if sl_pips <= 0:
            return self.min_position_size
        return risk_amount / (sl_pips * pip_value)
    
    def _apply_safety_limits(self, position_size, account_data, cycle_data):
        # Límites básicos
        position_size = max(self.min_position_size, min(position_size, self.max_position_size))
        
        # Límite por margin disponible
        available_margin = account_data.get('free_margin', 10000)
        margin_per_lot = account_data.get('margin_per_lot', 1000)
        max_lots_by_margin = available_margin / margin_per_lot * 0.8
        
        position_size = min(position_size, max_lots_by_margin)
        
        # Límite adicional si ya hay trades en el ciclo
        trades_executed = cycle_data.get('trades_executed', 0)
        if trades_executed >= 2:
            position_size *= 0.8
        
        return round(position_size, 2)
    
    def _get_emergency_position_size(self, account_data):
        return {
            'position_size': self.min_position_size,
            'risk_amount': account_data.get('equity', 10000) * 0.005,
            'stop_loss_pips': 20,
            'multipliers': {'quality': 1.0, 'session': 1.0, 'cycle': 1.0, 'volatility': 1.0, 'total': 1.0},
            'risk_percentage': 0.5,
            'expected_sl_amount': self.min_position_size * 20 * 10,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'emergency_mode': True
        }
    
    def get_position_analysis(self, position_data):
        """Analiza una posición calculada"""
        size = position_data['position_size']
        risk_pct = position_data['risk_percentage']
        multipliers = position_data.get('multipliers', {})
        
        # Categorizar tamaño
        if size <= 0.1: size_cat = 'MICRO'
        elif size <= 0.5: size_cat = 'SMALL'
        elif size <= 1.0: size_cat = 'MEDIUM'
        elif size <= 1.5: size_cat = 'LARGE'
        else: size_cat = 'MAXIMUM'
        
        # Categorizar riesgo
        if risk_pct <= 0.5: risk_cat = 'CONSERVATIVE'
        elif risk_pct <= 1.0: risk_cat = 'MODERATE'
        elif risk_pct <= 1.5: risk_cat = 'AGGRESSIVE'
        else: risk_cat = 'HIGH_RISK'
        
        # Factor dominante
        factors = {k: v for k, v in multipliers.items() if k != 'total'}
        if factors:
            dominant_factor = max(factors.keys(), key=lambda k: factors[k]).upper()
        else:
            dominant_factor = 'NONE'
        
        # Score de optimización
        score = 100
        if risk_pct > 2.0 or risk_pct < 0.3: score -= 20
        total_mult = multipliers.get('total', 1.0)
        if total_mult > 2.0 or total_mult < 0.5: score -= 15
        if 0.8 <= risk_pct <= 1.5 and 0.8 <= total_mult <= 1.5: score += 10
        score = max(0, min(100, score))
        
        # Recomendaciones
        recommendations = []
        if risk_pct > 1.8: recommendations.append("ALTO RIESGO: Considerar reducir multiplicadores")
        if risk_pct < 0.4: recommendations.append("BAJO RIESGO: Oportunidad perdida de optimización")
        if multipliers.get('quality', 1.0) < 0.8: recommendations.append("CALIDAD BAJA: Solo trades de alta calidad recomendados")
        if multipliers.get('cycle', 1.0) < 0.8: recommendations.append("CICLO ADVERSO: Modo conservador activado")
        if not recommendations: recommendations.append("POSICIÓN OPTIMIZADA: Parámetros dentro de rangos ideales")
        
        return {
            'size_category': size_cat,
            'risk_level': risk_cat,
            'dominant_factor': dominant_factor,
            'optimization_score': score,
            'recommendations': recommendations
        }

def test_advanced_position_sizer():
    """Test del AdvancedPositionSizer con múltiples escenarios"""
    
    print("🎯 TESTING ADVANCED POSITION SIZER")
    print("=" * 50)
    
    logger_manager = MockLoggerManager()
    sizer = AdvancedPositionSizer(logger_manager)
    
    # ESCENARIO 1: Trade de alta calidad en Londres
    print("\n📊 ESCENARIO 1: FVG Premium en Londres")
    print("-" * 40)
    
    fvg_data = {'quality': 'PREMIUM', 'size_pips': 30}
    session_data = {'active_session': 'LONDON', 'is_overlap': False}
    cycle_data = {'trades_executed': 0, 'daily_pnl_percentage': 0}
    account_data = {'equity': 10000, 'free_margin': 8000, 'margin_per_lot': 1000}
    market_data = {'volatility_level': 'NORMAL', 'pip_value': 10}
    
    result1 = sizer.calculate_position_size(fvg_data, session_data, cycle_data, account_data, market_data)
    
    print(f"Position Size: {result1['position_size']:.2f} lotes")
    print(f"Risk Amount: ${result1['risk_amount']:.2f}")
    print(f"Risk %: {result1['risk_percentage']:.2f}%")
    print(f"Stop Loss: {result1['stop_loss_pips']:.1f} pips")
    print(f"Total Multiplier: {result1['multipliers']['total']:.2f}")
    
    analysis1 = sizer.get_position_analysis(result1)
    print(f"Categoría: {analysis1['size_category']}")
    print(f"Nivel Riesgo: {analysis1['risk_level']}")
    print(f"Factor Dominante: {analysis1['dominant_factor']}")
    print(f"Score: {analysis1['optimization_score']}/100")
    
    # ESCENARIO 2: Trade de baja calidad fuera de horas
    print("\n📊 ESCENARIO 2: FVG Pobre fuera de horas")
    print("-" * 40)
    
    fvg_data2 = {'quality': 'POOR', 'size_pips': 15}
    session_data2 = {'active_session': 'OFF_HOURS', 'is_overlap': False}
    cycle_data2 = {'trades_executed': 0, 'daily_pnl_percentage': 0}
    
    result2 = sizer.calculate_position_size(fvg_data2, session_data2, cycle_data2, account_data, market_data)
    
    print(f"Position Size: {result2['position_size']:.2f} lotes")
    print(f"Risk %: {result2['risk_percentage']:.2f}%")
    print(f"Total Multiplier: {result2['multipliers']['total']:.2f}")
    
    # ESCENARIO 3: Tercer trade del día cerca del límite
    print("\n📊 ESCENARIO 3: 3er trade cerca del límite")
    print("-" * 40)
    
    fvg_data3 = {'quality': 'HIGH', 'size_pips': 25}
    session_data3 = {'active_session': 'NY', 'is_overlap': False}
    cycle_data3 = {'trades_executed': 2, 'daily_pnl_percentage': -1.5}
    
    result3 = sizer.calculate_position_size(fvg_data3, session_data3, cycle_data3, account_data, market_data)
    
    print(f"Position Size: {result3['position_size']:.2f} lotes")
    print(f"Risk %: {result3['risk_percentage']:.2f}%")
    print(f"Total Multiplier: {result3['multipliers']['total']:.2f}")
    
    analysis3 = sizer.get_position_analysis(result3)
    print(f"Recomendaciones: {analysis3['recommendations']}")
    
    # ESCENARIO 4: Overlap de sesiones con alta volatilidad
    print("\n📊 ESCENARIO 4: Overlap + Alta volatilidad")
    print("-" * 40)
    
    fvg_data4 = {'quality': 'HIGH', 'size_pips': 35}
    session_data4 = {'active_session': 'LONDON', 'is_overlap': True}
    cycle_data4 = {'trades_executed': 1, 'daily_pnl_percentage': 1.2}
    market_data4 = {'volatility_level': 'HIGH', 'pip_value': 10}
    
    result4 = sizer.calculate_position_size(fvg_data4, session_data4, cycle_data4, account_data, market_data4)
    
    print(f"Position Size: {result4['position_size']:.2f} lotes")
    print(f"Risk %: {result4['risk_percentage']:.2f}%")
    print(f"Multiplicadores:")
    for key, value in result4['multipliers'].items():
        if key != 'total':
            print(f"  {key.capitalize()}: {value:.2f}")
    print(f"  Total: {result4['multipliers']['total']:.2f}")
    
    # RESUMEN COMPARATIVO
    print("\n📈 RESUMEN COMPARATIVO")
    print("=" * 50)
    
    scenarios = [
        ("Premium Londres", result1),
        ("Pobre Off-Hours", result2),
        ("3er trade límite", result3),
        ("Overlap volátil", result4)
    ]
    
    print(f"{'Escenario':<18} {'Lotes':<8} {'Risk%':<8} {'Mult':<8}")
    print("-" * 50)
    
    for name, result in scenarios:
        print(f"{name:<18} {result['position_size']:<8.2f} "
              f"{result['risk_percentage']:<8.2f} "
              f"{result['multipliers']['total']:<8.2f}")
    
    print("\n✅ Testing del AdvancedPositionSizer completado")
    
    # Validaciones
    assert result1['position_size'] > result2['position_size'], "Premium debe ser > Pobre"
    assert result3['position_size'] < result1['position_size'], "3er trade debe ser conservador"
    assert all(r['risk_percentage'] <= 2.5 for _, r in scenarios), "Risk nunca debe exceder 2.5%"
    
    print("🎯 Todas las validaciones pasaron correctamente")

if __name__ == "__main__":
    test_advanced_position_sizer()
    print(f"\n🎯 ADVANCED POSITION SIZER - TESTING COMPLETADO")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
