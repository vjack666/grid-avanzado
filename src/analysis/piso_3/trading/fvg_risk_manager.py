"""
🛡️ FVG RISK MANAGER - PISO 3 OFICINA TRADING
==============================================

Gestor de Riesgo Específico para Fair Value Gaps
Extiende RiskBotMT5 con funcionalidades FVG avanzadas

FUNCIONALIDADES:
- Herencia completa de RiskBotMT5 para compatibilidad
- Cálculo de lotaje dinámico según calidad FVG
- SL/TP adaptativos basados en tamaño del FVG
- Gestión de confluencias y validación ML
- Múltiples niveles de take profit (R:R 1.5, 2.5, 4.0)

AUTOR: Sistema Trading Grid - Piso 3
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
import MetaTrader5 as mt5

# Configurar imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))

from riskbot_mt5 import RiskBotMT5
from logger_manager import LoggerManager

class FVGRiskManager(RiskBotMT5):
    """
    🛡️ GESTOR DE RIESGO FVG - PISO 3
    Gestión avanzada de riesgo específica para operaciones Fair Value Gap
    """
    
    def __init__(self, symbol='EURUSD'):
        # Inicializar RiskBot base con configuración estándar
        super().__init__(
            risk_target_profit=100,      # Profit objetivo base
            max_profit_target=300,       # Profit máximo antes de cerrar
            risk_percent=2.0,            # Porcentaje de riesgo máximo
            comision_por_lote=7.0        # Comisión por lote
        )
        
        self.symbol = symbol
        self.logger = LoggerManager().get_logger('fvg_risk_manager')
        
        # Configuración específica FVG
        self.fvg_config = {
            'min_quality_score': 6.0,      # Calidad mínima para trading
            'max_positions_fvg': 3,        # Máximo posiciones FVG simultáneas
            'min_confluence_strength': 70,  # Fuerza mínima de confluencia
            'max_daily_fvg_trades': 5,     # Máximo trades FVG por día
            'min_fvg_size_pips': 3,        # Tamaño mínimo FVG en pips
            'max_fvg_size_pips': 50        # Tamaño máximo FVG en pips
        }
        
        # Multiplicadores de lotaje por calidad FVG
        self.quality_multipliers = {
            'EXCEPTIONAL': 1.5,    # Score 9.0+ (Máximo lotaje)
            'HIGH': 1.2,           # Score 7.5-8.9
            'MEDIUM': 1.0,         # Score 6.0-7.4 (Base)
            'LOW': 0.6,            # Score 4.0-5.9
            'POOR': 0.3            # Score < 4.0 (Mínimo)
        }
        
        # Ratios de Risk:Reward para múltiples TP
        self.rr_ratios = {
            'TP1': 1.5,    # Primer take profit
            'TP2': 2.5,    # Segundo take profit  
            'TP3': 4.0     # Tercer take profit
        }
        
        # Estado de posiciones FVG
        self.fvg_positions = {}
        self.daily_fvg_count = 0
        self.last_trade_date = None
        
        # Estadísticas FVG
        self.fvg_stats = {
            'total_fvg_trades': 0,
            'successful_fvg_trades': 0,
            'fvg_profit_total': 0.0,
            'best_fvg_trade': 0.0,
            'worst_fvg_trade': 0.0,
            'avg_fvg_quality': 0.0
        }
        
        self.logger.info("🛡️ FVGRiskManager inicializado para símbolo: %s", symbol)
    
    def evaluate_fvg_trade(self, fvg_analysis: Dict) -> Dict:
        """
        🎯 Evaluar viabilidad y riesgo para trade FVG
        
        Args:
            fvg_analysis: Análisis completo del FVG
            {
                'quality_score': float,      # Score 0-10
                'confluence_strength': float, # Fuerza confluencia 0-100
                'fvg_size_pips': float,      # Tamaño FVG en pips
                'direction': str,            # 'BUY' o 'SELL'
                'ml_confidence': float,      # Confianza ML 0-1
                'session_type': str          # Sesión de mercado
            }
            
        Returns:
            dict: Evaluación completa de riesgo
        """
        try:
            self.logger.info("🎯 Evaluando trade FVG - Quality: %.1f, Confluence: %.1f", 
                           fvg_analysis.get('quality_score', 0), 
                           fvg_analysis.get('confluence_strength', 0))
            
            evaluation = {
                'trade_allowed': False,
                'recommended_lots': 0.0,
                'stop_loss_pips': 0.0,
                'take_profits': {},
                'risk_level': 'VERY_HIGH',
                'max_loss_usd': 0.0,
                'confluence_factor': 0.0,
                'quality_level': 'POOR',
                'reason': '',
                'confidence_score': 0.0
            }
            
            # 1. Verificar estado base del RiskBot
            base_status = self.check_and_act()
            if base_status in ['riesgo', 'objetivo_maximo']:
                evaluation['reason'] = f'RiskBot status: {base_status}'
                return evaluation
            
            # 2. Validar parámetros FVG básicos
            quality_score = fvg_analysis.get('quality_score', 0)
            confluence_strength = fvg_analysis.get('confluence_strength', 0)
            fvg_size_pips = fvg_analysis.get('fvg_size_pips', 0)
            
            if quality_score < self.fvg_config['min_quality_score']:
                evaluation['reason'] = f'Calidad FVG insuficiente: {quality_score:.1f} < {self.fvg_config["min_quality_score"]}'
                return evaluation
            
            if confluence_strength < self.fvg_config['min_confluence_strength']:
                evaluation['reason'] = f'Confluencia débil: {confluence_strength:.1f}% < {self.fvg_config["min_confluence_strength"]}%'
                return evaluation
            
            # 3. Verificar límites de posiciones
            if not self._check_fvg_position_limits():
                evaluation['reason'] = 'Límite de posiciones FVG alcanzado'
                return evaluation
            
            # 4. Verificar límites diarios
            if not self._check_daily_fvg_limits():
                evaluation['reason'] = 'Límite diario de trades FVG alcanzado'
                return evaluation
            
            # 5. Calcular nivel de calidad
            quality_level = self._get_quality_level(quality_score)
            evaluation['quality_level'] = quality_level
            
            # 6. Calcular factor de confluencia
            confluence_factor = self._calculate_confluence_factor(confluence_strength)
            evaluation['confluence_factor'] = confluence_factor
            
            # 7. Calcular lotaje recomendado
            recommended_lots = self._calculate_fvg_lot_size(fvg_analysis, quality_level, confluence_factor)
            evaluation['recommended_lots'] = recommended_lots
            
            # 8. Calcular SL y múltiples TP
            sl_pips, tp_levels = self._calculate_fvg_sl_tp(fvg_analysis)
            evaluation['stop_loss_pips'] = sl_pips
            evaluation['take_profits'] = tp_levels
            
            # 9. Calcular pérdida máxima en USD
            account_balance = self.get_account_balance()
            pip_value = self._get_pip_value(recommended_lots)
            max_loss_usd = sl_pips * pip_value
            evaluation['max_loss_usd'] = max_loss_usd
            
            # 10. Determinar nivel de riesgo final
            risk_level = self._determine_fvg_risk_level(
                quality_score, confluence_strength, max_loss_usd, account_balance
            )
            evaluation['risk_level'] = risk_level
            
            # 11. Calcular score de confianza general
            confidence_score = self._calculate_confidence_score(fvg_analysis, evaluation)
            evaluation['confidence_score'] = confidence_score
            
            # 12. Decisión final
            if (confidence_score >= 0.7 and 
                risk_level in ['LOW', 'MEDIUM'] and
                recommended_lots >= 0.01):
                
                evaluation['trade_allowed'] = True
                evaluation['reason'] = f'Trade FVG aprobado - Confidence: {confidence_score:.2f}, Risk: {risk_level}'
            else:
                evaluation['reason'] = f'Trade rechazado - Confidence: {confidence_score:.2f}, Risk: {risk_level}'
            
            self.logger.info("   Trade permitido: %s", evaluation['trade_allowed'])
            self.logger.info("   Lotaje recomendado: %.3f", evaluation['recommended_lots'])
            self.logger.info("   SL: %.1f pips, Risk: %s", evaluation['stop_loss_pips'], evaluation['risk_level'])
            
            return evaluation
            
        except Exception as e:
            self.logger.error("❌ Error evaluando trade FVG: %s", e)
            return {
                'trade_allowed': False,
                'reason': f'Error en evaluación: {e}',
                'risk_level': 'VERY_HIGH'
            }
    
    def _check_fvg_position_limits(self) -> bool:
        """📊 Verificar límites de posiciones FVG"""
        try:
            # Obtener posiciones abiertas del RiskBot base
            current_positions = self.get_open_positions()
            
            # Contar posiciones FVG específicas
            fvg_position_count = len([pos for pos in current_positions 
                                    if hasattr(pos, 'comment') and 'FVG' in str(pos.comment)])
            
            if fvg_position_count >= self.fvg_config['max_positions_fvg']:
                self.logger.warning("⚠️ Límite de posiciones FVG alcanzado: %d/%d", 
                                  fvg_position_count, self.fvg_config['max_positions_fvg'])
                return False
            
            return True
            
        except Exception as e:
            self.logger.error("❌ Error verificando límites FVG: %s", e)
            return False
    
    def _check_daily_fvg_limits(self) -> bool:
        """📅 Verificar límites diarios de trades FVG"""
        try:
            today = datetime.now().date()
            
            # Reset contador si cambió el día
            if self.last_trade_date != today:
                self.daily_fvg_count = 0
                self.last_trade_date = today
            
            if self.daily_fvg_count >= self.fvg_config['max_daily_fvg_trades']:
                self.logger.warning("⚠️ Límite diario de trades FVG alcanzado: %d/%d", 
                                  self.daily_fvg_count, self.fvg_config['max_daily_fvg_trades'])
                return False
            
            return True
            
        except Exception as e:
            self.logger.error("❌ Error verificando límites diarios: %s", e)
            return True  # Permitir en caso de error
    
    def _get_quality_level(self, quality_score: float) -> str:
        """📊 Determinar nivel de calidad FVG"""
        if quality_score >= 9.0:
            return 'EXCEPTIONAL'
        elif quality_score >= 7.5:
            return 'HIGH'
        elif quality_score >= 6.0:
            return 'MEDIUM'
        elif quality_score >= 4.0:
            return 'LOW'
        else:
            return 'POOR'
    
    def _calculate_confluence_factor(self, confluence_strength: float) -> float:
        """🔢 Calcular factor de confluencia para ajustar riesgo"""
        if confluence_strength >= 90:
            return 1.2  # Boost por confluencia excepcional
        elif confluence_strength >= 80:
            return 1.1
        elif confluence_strength >= 70:
            return 1.0  # Base
        elif confluence_strength >= 60:
            return 0.9
        else:
            return 0.8  # Penalización por confluencia débil
    
    def _calculate_fvg_lot_size(self, fvg_analysis: Dict, quality_level: str, confluence_factor: float) -> float:
        """📏 Calcular tamaño de lote específico para FVG"""
        try:
            # Balance y configuración base
            balance = self.get_account_balance()
            if balance <= 0:
                return 0.0
            
            # Riesgo base (2% del balance por defecto)
            base_risk_usd = balance * (self.risk_percent / 100)
            
            # Multiplicador por calidad FVG
            quality_multiplier = self.quality_multipliers.get(quality_level, 1.0)
            
            # Ajuste por confluencia
            adjusted_risk = base_risk_usd * quality_multiplier * confluence_factor
            
            # Calcular tamaño FVG para SL
            fvg_size_pips = fvg_analysis.get('fvg_size_pips', 10)
            sl_pips = max(fvg_size_pips * 1.2, 8)  # SL = 120% del FVG size, mínimo 8 pips
            
            # Valor por pip para EURUSD (simplificado)
            pip_value_per_lot = 10.0  # $10 por pip para 1 lote estándar
            
            # Calcular lotaje basado en riesgo y SL
            calculated_lots = adjusted_risk / (sl_pips * pip_value_per_lot)
            
            # Aplicar límites del sistema
            final_lots = max(0.01, min(1.0, calculated_lots))
            final_lots = round(final_lots, 2)
            
            self.logger.debug("💰 Cálculo lotaje FVG: Risk=%.2f, Quality=%s(%.2f), Confluence=%.2f -> Lots=%.3f", 
                            adjusted_risk, quality_level, quality_multiplier, confluence_factor, final_lots)
            
            return final_lots
            
        except Exception as e:
            self.logger.error("❌ Error calculando lotaje FVG: %s", e)
            return 0.01  # Lotaje mínimo seguro
    
    def _calculate_fvg_sl_tp(self, fvg_analysis: Dict) -> Tuple[float, Dict]:
        """📐 Calcular SL y múltiples TP basados en FVG"""
        try:
            fvg_size_pips = fvg_analysis.get('fvg_size_pips', 10)
            
            # Stop Loss = 120% del tamaño del FVG (con mínimo de seguridad)
            stop_loss_pips = max(fvg_size_pips * 1.2, 8)
            
            # Múltiples Take Profits basados en R:R ratios
            take_profits = {}
            for tp_name, rr_ratio in self.rr_ratios.items():
                tp_pips = stop_loss_pips * rr_ratio
                take_profits[tp_name] = {
                    'pips': round(tp_pips, 1),
                    'rr_ratio': rr_ratio
                }
            
            self.logger.debug("📐 SL/TP FVG: SL=%.1f pips, TP1=%.1f, TP2=%.1f, TP3=%.1f", 
                            stop_loss_pips, 
                            take_profits['TP1']['pips'],
                            take_profits['TP2']['pips'], 
                            take_profits['TP3']['pips'])
            
            return stop_loss_pips, take_profits
            
        except Exception as e:
            self.logger.error("❌ Error calculando SL/TP: %s", e)
            return 15.0, {'TP1': {'pips': 22.5, 'rr_ratio': 1.5}}  # Valores por defecto
    
    def _determine_fvg_risk_level(self, quality_score: float, confluence_strength: float, 
                                 max_loss_usd: float, account_balance: float) -> str:
        """🎯 Determinar nivel de riesgo para trade FVG"""
        try:
            # Factor por calidad
            if quality_score >= 8.5:
                quality_risk = 'VERY_LOW'
            elif quality_score >= 7.0:
                quality_risk = 'LOW'
            elif quality_score >= 6.0:
                quality_risk = 'MEDIUM'
            else:
                quality_risk = 'HIGH'
            
            # Factor por confluencia
            if confluence_strength >= 85:
                confluence_risk = 'VERY_LOW'
            elif confluence_strength >= 75:
                confluence_risk = 'LOW'
            elif confluence_strength >= 65:
                confluence_risk = 'MEDIUM'
            else:
                confluence_risk = 'HIGH'
            
            # Factor por pérdida máxima (% del balance)
            loss_percent = (max_loss_usd / account_balance) * 100 if account_balance > 0 else 100
            if loss_percent <= 1.0:
                financial_risk = 'VERY_LOW'
            elif loss_percent <= 2.0:
                financial_risk = 'LOW'
            elif loss_percent <= 3.0:
                financial_risk = 'MEDIUM'
            else:
                financial_risk = 'HIGH'
            
            # Combinar factores (usar el más restrictivo)
            risk_levels = ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']
            
            quality_index = risk_levels.index(quality_risk)
            confluence_index = risk_levels.index(confluence_risk)
            financial_index = risk_levels.index(financial_risk)
            
            final_index = max(quality_index, confluence_index, financial_index)
            final_risk = risk_levels[final_index]
            
            self.logger.debug("🎯 Risk factors: Quality=%s, Confluence=%s, Financial=%s -> Final=%s", 
                            quality_risk, confluence_risk, financial_risk, final_risk)
            
            return final_risk
            
        except Exception as e:
            self.logger.error("❌ Error determinando riesgo: %s", e)
            return 'VERY_HIGH'
    
    def _calculate_confidence_score(self, fvg_analysis: Dict, evaluation: Dict) -> float:
        """🎯 Calcular score de confianza general para el trade"""
        try:
            # Factores de confianza (0-1)
            quality_factor = min(fvg_analysis.get('quality_score', 0) / 10, 1.0)
            confluence_factor = min(fvg_analysis.get('confluence_strength', 0) / 100, 1.0)
            ml_factor = fvg_analysis.get('ml_confidence', 0.5)
            
            # Factor de riesgo (invertido)
            risk_factor = {
                'VERY_LOW': 1.0,
                'LOW': 0.8,
                'MEDIUM': 0.6,
                'HIGH': 0.4,
                'VERY_HIGH': 0.2
            }.get(evaluation.get('risk_level', 'VERY_HIGH'), 0.2)
            
            # Pesos para cada factor
            weights = {
                'quality': 0.3,
                'confluence': 0.25,
                'ml': 0.25,
                'risk': 0.2
            }
            
            # Calcular score ponderado
            confidence_score = (
                quality_factor * weights['quality'] +
                confluence_factor * weights['confluence'] +
                ml_factor * weights['ml'] +
                risk_factor * weights['risk']
            )
            
            return round(confidence_score, 3)
            
        except Exception as e:
            self.logger.error("❌ Error calculando confidence score: %s", e)
            return 0.0
    
    def _get_pip_value(self, lot_size: float) -> float:
        """💱 Obtener valor por pip para el lotaje dado"""
        # Para EURUSD, 1 pip = $10 por lote estándar
        return lot_size * 10.0
    
    def register_fvg_trade(self, trade_info: Dict) -> str:
        """
        📝 Registrar nuevo trade FVG ejecutado
        
        Args:
            trade_info: Información del trade ejecutado
            
        Returns:
            str: ID del registro
        """
        try:
            trade_id = f"FVG_{self.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.fvg_positions[trade_id] = {
                'id': trade_id,
                'symbol': self.symbol,
                'trade_info': trade_info,
                'open_time': datetime.now(),
                'status': 'OPEN'
            }
            
            # Actualizar contadores
            self.daily_fvg_count += 1
            self.fvg_stats['total_fvg_trades'] += 1
            
            self.logger.info("📝 Trade FVG registrado: %s", trade_id)
            return trade_id
            
        except Exception as e:
            self.logger.error("❌ Error registrando trade FVG: %s", e)
            return ""
    
    def get_fvg_summary(self) -> Dict:
        """
        📊 Obtener resumen completo del FVG Risk Manager
        
        Returns:
            dict: Resumen completo con métricas
        """
        try:
            # Estado del RiskBot base
            base_status = self.check_and_act()
            total_profit, total_commission, profit_neto, total_lots = self.get_total_profit_and_lots()
            balance = self.get_account_balance()
            
            # Posiciones actuales
            current_positions = self.get_open_positions()
            fvg_positions_count = len([pos for pos in current_positions 
                                     if hasattr(pos, 'comment') and 'FVG' in str(pos.comment)])
            
            # Calcular tasa de éxito FVG
            fvg_success_rate = 0.0
            if self.fvg_stats['total_fvg_trades'] > 0:
                fvg_success_rate = (self.fvg_stats['successful_fvg_trades'] / 
                                  self.fvg_stats['total_fvg_trades']) * 100
            
            summary = {
                'timestamp': datetime.now(),
                'symbol': self.symbol,
                'base_riskbot': {
                    'status': base_status,
                    'balance': balance,
                    'profit_neto': profit_neto,
                    'total_lots': total_lots
                },
                'fvg_specific': {
                    'current_fvg_positions': fvg_positions_count,
                    'max_fvg_positions': self.fvg_config['max_positions_fvg'],
                    'daily_fvg_trades': self.daily_fvg_count,
                    'max_daily_fvg_trades': self.fvg_config['max_daily_fvg_trades'],
                    'fvg_success_rate': fvg_success_rate
                },
                'config': self.fvg_config.copy(),
                'stats': self.fvg_stats.copy()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error("❌ Error obteniendo resumen FVG: %s", e)
            return {'error': str(e)}

# Instancia global del FVG Risk Manager
fvg_risk_manager = None

def get_fvg_risk_manager(symbol: str = 'EURUSD') -> FVGRiskManager:
    """
    🎯 Obtener instancia del FVG Risk Manager
    
    Args:
        symbol: Símbolo para el gestor
        
    Returns:
        FVGRiskManager: Instancia del gestor
    """
    global fvg_risk_manager
    
    if fvg_risk_manager is None or fvg_risk_manager.symbol != symbol:
        fvg_risk_manager = FVGRiskManager(symbol)
    
    return fvg_risk_manager

if __name__ == "__main__":
    # Test básico del FVG Risk Manager
    print("🛡️ Testing FVG Risk Manager...")
    
    # Crear instancia
    fvg_risk = FVGRiskManager('EURUSD')
    
    # Test de evaluación FVG
    test_fvg = {
        'quality_score': 8.2,
        'confluence_strength': 82,
        'fvg_size_pips': 12,
        'direction': 'BUY',
        'ml_confidence': 0.78,
        'session_type': 'LONDON'
    }
    
    evaluation = fvg_risk.evaluate_fvg_trade(test_fvg)
    
    print(f"✅ Evaluación completada:")
    print(f"   Trade permitido: {evaluation.get('trade_allowed', False)}")
    print(f"   Lotaje recomendado: {evaluation.get('recommended_lots', 0):.3f}")
    print(f"   SL: {evaluation.get('stop_loss_pips', 0):.1f} pips")
    print(f"   Nivel de riesgo: {evaluation.get('risk_level', 'UNKNOWN')}")
    print(f"   Razón: {evaluation.get('reason', 'No especificada')}")
    
    # Resumen del gestor
    summary = fvg_risk.get_fvg_summary()
    print(f"\n📊 Resumen FVG Risk Manager:")
    print(f"   Symbol: {summary.get('symbol', 'N/A')}")
    print(f"   Base status: {summary.get('base_riskbot', {}).get('status', 'N/A')}")
    print(f"   Posiciones FVG: {summary.get('fvg_specific', {}).get('current_fvg_positions', 0)}")
    
    print("\n🎯 FVG Risk Manager test completado exitosamente!")
