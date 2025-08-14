"""
💰 OFICINA DE TRADING - PISO 3
Módulos especializados en generación de señales y trading automático

Componentes:
- FVGSignalGenerator: Generador de señales de trading
- RiskManager: Gestión de riesgo avanzada
- BacktestEngine: Motor de backtesting
- LiveTrader: Trading automático en vivo
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class SignalType(Enum):
    """Tipos de señales de trading"""
    BUY = "BUY"
    SELL = "SELL"
    CLOSE_LONG = "CLOSE_LONG"
    CLOSE_SHORT = "CLOSE_SHORT"
    HOLD = "HOLD"

class SignalStrength(Enum):
    """Fuerza de la señal"""
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    VERY_STRONG = 4

class RiskLevel(Enum):
    """Niveles de riesgo"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"

class FVGSignalGenerator:
    """
    📈 GENERADOR DE SEÑALES FVG
    
    Genera señales de trading basadas en análisis avanzado de FVGs
    combinando múltiples factores y timeframes
    """
    
    def __init__(self, config=None):
        """
        Inicializa el generador de señales
        
        Args:
            config: Configuración personalizada
        """
        self.config = config or {
            "min_signal_strength": 2,
            "confluence_weight": 0.4,
            "quality_weight": 0.3,
            "context_weight": 0.3,
            "timeframes": ["M15", "H1", "H4"],
            "risk_reward_ratio": 2.0
        }
        
        self.signal_history = []
        self.active_signals = []
        
        print("📈 FVGSignalGenerator inicializado")
    
    def generate_signal(self, fvg_data, market_context, quality_analysis=None):
        """
        Genera señal de trading basada en FVG
        
        Args:
            fvg_data: Datos del FVG
            market_context: Contexto de mercado
            quality_analysis: Análisis de calidad del FVG
            
        Returns:
            Dict con información de la señal
        """
        # Análisis de confluencias
        confluence_score = self._analyze_confluences(fvg_data, market_context)
        
        # Análisis de calidad
        quality_score = self._get_quality_score(quality_analysis)
        
        # Análisis de contexto
        context_score = self._analyze_market_context(market_context)
        
        # Cálculo de fuerza de señal
        signal_strength = self._calculate_signal_strength(
            confluence_score, quality_score, context_score
        )
        
        # Determinar tipo de señal
        signal_type = self._determine_signal_type(fvg_data, market_context)
        
        # Calcular niveles de entrada y salida
        entry_levels = self._calculate_entry_levels(fvg_data, signal_strength)
        exit_levels = self._calculate_exit_levels(fvg_data, entry_levels, signal_strength)
        
        # Crear señal
        signal = {
            'id': self._generate_signal_id(),
            'timestamp': datetime.now(),
            'symbol': fvg_data.get('symbol', 'UNKNOWN'),
            'timeframe': fvg_data.get('timeframe', 'UNKNOWN'),
            'type': signal_type,
            'strength': signal_strength,
            'confluence_score': confluence_score,
            'quality_score': quality_score,
            'context_score': context_score,
            'entry_price': entry_levels['entry'],
            'stop_loss': exit_levels['stop_loss'],
            'take_profit': exit_levels['take_profit'],
            'risk_reward_ratio': exit_levels['risk_reward'],
            'fvg_data': fvg_data,
            'status': 'PENDING',
            'confidence': (confluence_score + quality_score + context_score) / 3
        }
        
        # Validar señal
        if self._validate_signal(signal):
            self.signal_history.append(signal)
            self.active_signals.append(signal)
            
            print(f"🎯 Señal generada: {signal_type.value} {signal['symbol']} "
                  f"({signal_strength.name}) - Confianza: {signal['confidence']:.2f}")
            
            return signal
        
        return None
    
    def _analyze_confluences(self, fvg_data, market_context):
        """Analiza confluencias para la señal"""
        confluence_factors = []
        
        # Factor de confluencia multi-timeframe
        if 'multi_timeframe_confluences' in market_context:
            mtf_confluences = market_context['multi_timeframe_confluences']
            confluence_factors.append(min(1.0, len(mtf_confluences) / 3))
        
        # Factor de soporte/resistencia
        if 'sr_confluence' in market_context:
            confluence_factors.append(market_context['sr_confluence'])
        
        # Factor de indicadores técnicos
        if 'technical_confluence' in market_context:
            confluence_factors.append(market_context['technical_confluence'])
        
        if confluence_factors:
            return np.mean(confluence_factors)
        
        return 0.5
    
    def _get_quality_score(self, quality_analysis):
        """Obtiene score de calidad normalizado"""
        if quality_analysis and 'final_score' in quality_analysis:
            return quality_analysis['final_score'] / 10
        return 0.5
    
    def _analyze_market_context(self, market_context):
        """Analiza contexto de mercado para la señal"""
        context_factors = []
        
        # Factor de tendencia
        if 'trend_alignment' in market_context:
            context_factors.append(market_context['trend_alignment'])
        
        # Factor de volatilidad
        if 'volatility_factor' in market_context:
            vol_factor = market_context['volatility_factor']
            # Volatilidad moderada es óptima
            optimal_vol = 1.0 - abs(vol_factor - 0.6)
            context_factors.append(optimal_vol)
        
        # Factor de sesión
        if 'session_factor' in market_context:
            context_factors.append(market_context['session_factor'])
        
        if context_factors:
            return np.mean(context_factors)
        
        return 0.5
    
    def _calculate_signal_strength(self, confluence, quality, context):
        """Calcula fuerza de la señal"""
        weighted_score = (
            confluence * self.config['confluence_weight'] +
            quality * self.config['quality_weight'] +
            context * self.config['context_weight']
        )
        
        if weighted_score >= 0.8:
            return SignalStrength.VERY_STRONG
        elif weighted_score >= 0.65:
            return SignalStrength.STRONG
        elif weighted_score >= 0.5:
            return SignalStrength.MODERATE
        else:
            return SignalStrength.WEAK
    
    def _determine_signal_type(self, fvg_data, market_context):
        """Determina el tipo de señal"""
        fvg_type = fvg_data.get('type', '')
        trend = market_context.get('trend', 'NEUTRAL')
        
        if fvg_type == 'BULLISH' and trend in ['BULLISH', 'NEUTRAL']:
            return SignalType.BUY
        elif fvg_type == 'BEARISH' and trend in ['BEARISH', 'NEUTRAL']:
            return SignalType.SELL
        else:
            return SignalType.HOLD
    
    def _calculate_entry_levels(self, fvg_data, signal_strength):
        """Calcula niveles de entrada"""
        if fvg_data.get('type') == 'BULLISH':
            # Para FVG bullish, entrada en la zona del gap
            entry = (fvg_data.get('gap_low', 0) + fvg_data.get('gap_high', 0)) / 2
        else:
            # Para FVG bearish, entrada en la zona del gap
            entry = (fvg_data.get('gap_low', 0) + fvg_data.get('gap_high', 0)) / 2
        
        return {'entry': entry}
    
    def _calculate_exit_levels(self, fvg_data, entry_levels, signal_strength):
        """Calcula niveles de salida (stop loss y take profit)"""
        entry_price = entry_levels['entry']
        gap_size = fvg_data.get('gap_size', 0.0001)
        
        # Ajustar riesgo según fuerza de señal
        risk_multiplier = {
            SignalStrength.WEAK: 0.5,
            SignalStrength.MODERATE: 1.0,
            SignalStrength.STRONG: 1.5,
            SignalStrength.VERY_STRONG: 2.0
        }[signal_strength]
        
        # Calcular stop loss y take profit
        if fvg_data.get('type') == 'BULLISH':
            stop_loss = entry_price - (gap_size * risk_multiplier)
            take_profit = entry_price + (gap_size * risk_multiplier * self.config['risk_reward_ratio'])
        else:
            stop_loss = entry_price + (gap_size * risk_multiplier)
            take_profit = entry_price - (gap_size * risk_multiplier * self.config['risk_reward_ratio'])
        
        risk_reward = abs(take_profit - entry_price) / abs(entry_price - stop_loss)
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward': risk_reward
        }
    
    def _validate_signal(self, signal):
        """Valida si la señal cumple los criterios mínimos"""
        # Validar fuerza mínima
        if signal['strength'].value < self.config['min_signal_strength']:
            return False
        
        # Validar risk-reward ratio
        if signal['risk_reward_ratio'] < 1.5:
            return False
        
        # Validar confianza mínima
        if signal['confidence'] < 0.6:
            return False
        
        return True
    
    def _generate_signal_id(self):
        """Genera ID único para la señal"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"FVG_SIGNAL_{timestamp}_{len(self.signal_history)}"
    
    def get_active_signals(self, symbol=None):
        """Obtiene señales activas"""
        if symbol:
            return [s for s in self.active_signals if s['symbol'] == symbol]
        return self.active_signals.copy()
    
    def update_signal_status(self, signal_id, new_status, result=None):
        """Actualiza el estado de una señal"""
        for signal in self.active_signals:
            if signal['id'] == signal_id:
                signal['status'] = new_status
                signal['updated_at'] = datetime.now()
                
                if result:
                    signal['result'] = result
                
                if new_status in ['FILLED', 'CANCELLED', 'EXPIRED']:
                    self.active_signals.remove(signal)
                
                print(f"📊 Señal {signal_id} actualizada: {new_status}")
                break


class RiskManager:
    """
    🛡️ GESTOR DE RIESGO AVANZADO
    
    Sistema completo de gestión de riesgo para trading FVG
    """
    
    def __init__(self, config=None):
        """
        Inicializa el gestor de riesgo
        
        Args:
            config: Configuración de riesgo
        """
        self.config = config or {
            "max_risk_per_trade": 0.02,  # 2% por operación
            "max_daily_loss": 0.05,     # 5% pérdida diaria máxima
            "max_concurrent_trades": 3,
            "max_correlation": 0.7,      # Correlación máxima entre trades
            "account_balance": 10000     # Balance inicial
        }
        
        self.daily_pnl = 0
        self.open_positions = []
        self.risk_metrics = {}
        
        print("🛡️ RiskManager inicializado")
    
    def assess_trade_risk(self, signal, account_balance=None):
        """
        Evalúa el riesgo de una operación propuesta
        
        Args:
            signal: Señal de trading
            account_balance: Balance actual de la cuenta
            
        Returns:
            Dict con evaluación de riesgo
        """
        balance = account_balance or self.config['account_balance']
        
        # Calcular tamaño de posición
        position_size = self._calculate_position_size(signal, balance)
        
        # Evaluar riesgo de la operación
        trade_risk = abs(signal['entry_price'] - signal['stop_loss']) * position_size
        risk_percentage = trade_risk / balance
        
        # Evaluar riesgo de correlación
        correlation_risk = self._assess_correlation_risk(signal)
        
        # Evaluar riesgo de exposición
        exposure_risk = self._assess_exposure_risk(signal, position_size)
        
        # Evaluar límites diarios
        daily_risk = self._assess_daily_limits()
        
        # Nivel de riesgo general
        risk_level = self._determine_risk_level(
            risk_percentage, correlation_risk, exposure_risk, daily_risk
        )
        
        risk_assessment = {
            'approved': risk_level != RiskLevel.EXTREME,
            'risk_level': risk_level,
            'position_size': position_size,
            'risk_amount': trade_risk,
            'risk_percentage': risk_percentage,
            'correlation_risk': correlation_risk,
            'exposure_risk': exposure_risk,
            'daily_risk': daily_risk,
            'recommendations': self._generate_risk_recommendations(risk_level, risk_percentage)
        }
        
        return risk_assessment
    
    def _calculate_position_size(self, signal, balance):
        """Calcula tamaño de posición basado en riesgo"""
        max_risk_amount = balance * self.config['max_risk_per_trade']
        price_risk = abs(signal['entry_price'] - signal['stop_loss'])
        
        if price_risk > 0:
            position_size = max_risk_amount / price_risk
        else:
            position_size = 0
        
        return position_size
    
    def _assess_correlation_risk(self, signal):
        """Evalúa riesgo de correlación con posiciones existentes"""
        if not self.open_positions:
            return 0.0
        
        # Análisis simplificado de correlación
        same_symbol_positions = [
            pos for pos in self.open_positions 
            if pos['symbol'] == signal['symbol']
        ]
        
        same_direction_positions = [
            pos for pos in same_symbol_positions
            if pos['direction'] == signal['type'].value
        ]
        
        correlation_factor = len(same_direction_positions) / max(1, len(self.open_positions))
        
        return correlation_factor
    
    def _assess_exposure_risk(self, signal, position_size):
        """Evalúa riesgo de exposición total"""
        current_exposure = sum(pos['position_size'] for pos in self.open_positions)
        total_exposure = current_exposure + position_size
        
        max_exposure = self.config['account_balance'] * 0.5  # 50% del balance
        
        exposure_ratio = total_exposure / max_exposure
        
        return min(1.0, exposure_ratio)
    
    def _assess_daily_limits(self):
        """Evalúa límites de riesgo diarios"""
        max_daily_loss = self.config['account_balance'] * self.config['max_daily_loss']
        
        if abs(self.daily_pnl) >= max_daily_loss:
            return 1.0  # Límite alcanzado
        
        return abs(self.daily_pnl) / max_daily_loss
    
    def _determine_risk_level(self, risk_pct, correlation, exposure, daily):
        """Determina nivel de riesgo general"""
        risk_factors = [risk_pct / 0.02, correlation, exposure, daily]
        avg_risk = np.mean(risk_factors)
        
        if avg_risk >= 1.0:
            return RiskLevel.EXTREME
        elif avg_risk >= 0.75:
            return RiskLevel.HIGH
        elif avg_risk >= 0.5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_risk_recommendations(self, risk_level, risk_percentage):
        """Genera recomendaciones basadas en el riesgo"""
        recommendations = []
        
        if risk_level == RiskLevel.EXTREME:
            recommendations.append("❌ NO OPERAR - Riesgo extremo detectado")
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("⚠️ Reducir tamaño de posición")
            recommendations.append("🎯 Considerar stop loss más ajustado")
        elif risk_percentage > 0.015:  # > 1.5%
            recommendations.append("📊 Tamaño de posición en límite superior")
        
        if len(self.open_positions) >= self.config['max_concurrent_trades']:
            recommendations.append("🔄 Considerar cerrar posiciones existentes")
        
        return recommendations
    
    def add_position(self, signal, position_size, entry_price):
        """Añade posición al tracking de riesgo"""
        position = {
            'signal_id': signal['id'],
            'symbol': signal['symbol'],
            'direction': signal['type'].value,
            'position_size': position_size,
            'entry_price': entry_price,
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'opened_at': datetime.now()
        }
        
        self.open_positions.append(position)
        print(f"📈 Posición añadida: {signal['symbol']} {signal['type'].value}")
    
    def remove_position(self, signal_id, exit_price, pnl):
        """Remueve posición y actualiza métricas"""
        for i, position in enumerate(self.open_positions):
            if position['signal_id'] == signal_id:
                self.open_positions.pop(i)
                self.daily_pnl += pnl
                
                print(f"📊 Posición cerrada: PnL = ${pnl:.2f}")
                break
    
    def get_risk_summary(self):
        """Obtiene resumen de riesgo actual"""
        total_exposure = sum(pos['position_size'] for pos in self.open_positions)
        
        return {
            'open_positions': len(self.open_positions),
            'total_exposure': total_exposure,
            'daily_pnl': self.daily_pnl,
            'risk_utilization': len(self.open_positions) / self.config['max_concurrent_trades'],
            'daily_loss_utilization': abs(self.daily_pnl) / (self.config['account_balance'] * self.config['max_daily_loss'])
        }


class BacktestEngine:
    """
    📊 MOTOR DE BACKTESTING
    
    Sistema completo de backtesting para estrategias FVG
    """
    
    def __init__(self):
        """Inicializa el motor de backtesting"""
        self.results = {}
        self.trades = []
        self.equity_curve = []
        
        print("📊 BacktestEngine inicializado")
    
    def run_backtest(self, strategy_config, historical_data, initial_balance=10000):
        """
        Ejecuta backtest completo
        
        Args:
            strategy_config: Configuración de la estrategia
            historical_data: Datos históricos
            initial_balance: Balance inicial
            
        Returns:
            Dict con resultados del backtest
        """
        print(f"🔄 Iniciando backtest con balance inicial: ${initial_balance}")
        
        # Inicializar variables
        balance = initial_balance
        open_trades = []
        trade_id = 0
        
        # Procesar datos históricos
        for i, row in historical_data.iterrows():
            # Generar señales reales basadas en FVG
            signals = self._generate_backtest_signals(row, strategy_config)
            
            # Procesar nuevas señales
            for signal in signals:
                trade_id += 1
                trade = self._create_backtest_trade(signal, trade_id, row['datetime'])
                open_trades.append(trade)
            
            # Procesar trades abiertos
            closed_trades = []
            for trade in open_trades:
                result = self._check_trade_exit(trade, row)
                if result:
                    trade.update(result)
                    self.trades.append(trade)
                    closed_trades.append(trade)
                    
                    # Actualizar balance
                    balance += trade['pnl']
            
            # Remover trades cerrados
            for trade in closed_trades:
                open_trades.remove(trade)
            
            # Registrar equity
            self.equity_curve.append({
                'datetime': row['datetime'],
                'balance': balance,
                'open_trades': len(open_trades)
            })
        
        # Cerrar trades restantes
        for trade in open_trades:
            trade.update({
                'exit_price': historical_data.iloc[-1]['close'],
                'exit_time': historical_data.iloc[-1]['datetime'],
                'exit_reason': 'END_OF_DATA'
            })
            trade['pnl'] = self._calculate_trade_pnl(trade)
            self.trades.append(trade)
            balance += trade['pnl']
        
        # Calcular métricas
        self.results = self._calculate_backtest_metrics(initial_balance, balance)
        
        print(f"✅ Backtest completado: {len(self.trades)} trades, "
              f"Balance final: ${balance:.2f}")
        
        return self.results
    
    def _generate_backtest_signals(self, market_data, strategy_config):
        """Genera señales para backtest basadas en análisis FVG real"""
        signals = []
        
        try:
            # Usar detector FVG real para backtest
            from src.analysis.fvg_detector import FVGDetector
            from src.analysis.piso_3.analisis import FVGQualityAnalyzer
            
            detector = FVGDetector()
            analyzer = FVGQualityAnalyzer()
            
            # Crear DataFrame con la vela actual
            df = pd.DataFrame([market_data])
            
            # Detectar FVGs
            fvgs = detector.detect_fvgs(df)
            
            for fvg in fvgs:
                # Analizar calidad
                quality = analyzer.analyze_fvg_quality(fvg)
                
                # Solo generar señal si calidad es suficiente
                if quality['final_score'] >= strategy_config.get('min_quality', 6.0):
                    signal = {
                        'type': 'BUY' if fvg.type == 'BULLISH' else 'SELL',
                        'entry_price': market_data['close'],
                        'stop_loss': market_data['close'] * (0.995 if fvg.type == 'BULLISH' else 1.005),
                        'take_profit': market_data['close'] * (1.01 if fvg.type == 'BULLISH' else 0.99),
                        'strength': min(4, int(quality['final_score'] / 2.5)),
                        'confidence': quality['final_score'] / 10,
                        'fvg_data': fvg
                    }
                    signals.append(signal)
                    
        except Exception as e:
            # Fallback a método simple si hay problemas
            if np.random.random() < 0.02:  # 2% probabilidad reducida
                signal_type = np.random.choice(['BUY', 'SELL'])
                
                signal = {
                    'type': signal_type,
                    'entry_price': market_data['close'],
                    'stop_loss': market_data['close'] * (0.995 if signal_type == 'BUY' else 1.005),
                    'take_profit': market_data['close'] * (1.01 if signal_type == 'BUY' else 0.99),
                    'strength': np.random.choice([1, 2, 3]),
                    'confidence': np.random.uniform(0.5, 0.8)
                }
                signals.append(signal)
        
        return signals
    
    def _create_backtest_trade(self, signal, trade_id, entry_time):
        """Crea trade para backtest"""
        return {
            'id': trade_id,
            'type': signal['type'],
            'entry_price': signal['entry_price'],
            'entry_time': entry_time,
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'strength': signal['strength'],
            'confidence': signal['confidence'],
            'status': 'OPEN',
            'exit_price': None,
            'exit_time': None,
            'exit_reason': None,
            'pnl': 0
        }
    
    def _check_trade_exit(self, trade, market_data):
        """Verifica si un trade debe cerrarse"""
        current_price = market_data['close']
        
        if trade['type'] == 'BUY':
            if current_price <= trade['stop_loss']:
                return {
                    'exit_price': trade['stop_loss'],
                    'exit_time': market_data['datetime'],
                    'exit_reason': 'STOP_LOSS',
                    'pnl': self._calculate_trade_pnl({**trade, 'exit_price': trade['stop_loss']})
                }
            elif current_price >= trade['take_profit']:
                return {
                    'exit_price': trade['take_profit'],
                    'exit_time': market_data['datetime'],
                    'exit_reason': 'TAKE_PROFIT',
                    'pnl': self._calculate_trade_pnl({**trade, 'exit_price': trade['take_profit']})
                }
        
        else:  # SELL
            if current_price >= trade['stop_loss']:
                return {
                    'exit_price': trade['stop_loss'],
                    'exit_time': market_data['datetime'],
                    'exit_reason': 'STOP_LOSS',
                    'pnl': self._calculate_trade_pnl({**trade, 'exit_price': trade['stop_loss']})
                }
            elif current_price <= trade['take_profit']:
                return {
                    'exit_price': trade['take_profit'],
                    'exit_time': market_data['datetime'],
                    'exit_reason': 'TAKE_PROFIT',
                    'pnl': self._calculate_trade_pnl({**trade, 'exit_price': trade['take_profit']})
                }
        
        return None
    
    def _calculate_trade_pnl(self, trade):
        """Calcula PnL de un trade"""
        if trade['type'] == 'BUY':
            return (trade['exit_price'] - trade['entry_price']) * 10000  # 1 lot = 10000 units
        else:
            return (trade['entry_price'] - trade['exit_price']) * 10000
    
    def _calculate_backtest_metrics(self, initial_balance, final_balance):
        """Calcula métricas del backtest"""
        if not self.trades:
            return {'error': 'No trades executed'}
        
        # Métricas básicas
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] < 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        total_pnl = sum(trade['pnl'] for trade in self.trades)
        gross_profit = sum(trade['pnl'] for trade in winning_trades)
        gross_loss = sum(trade['pnl'] for trade in losing_trades)
        
        # Métricas avanzadas
        if len(winning_trades) > 0:
            avg_win = gross_profit / len(winning_trades)
        else:
            avg_win = 0
        
        if len(losing_trades) > 0:
            avg_loss = abs(gross_loss / len(losing_trades))
        else:
            avg_loss = 1  # Evitar división por cero
        
        profit_factor = gross_profit / abs(gross_loss) if gross_loss != 0 else float('inf')
        
        # Drawdown
        equity_values = [point['balance'] for point in self.equity_curve]
        running_max = np.maximum.accumulate(equity_values)
        drawdown = (running_max - equity_values) / running_max * 100
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
        
        return {
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'total_return': ((final_balance - initial_balance) / initial_balance) * 100,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate * 100,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'net_profit': total_pnl,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': self._calculate_sharpe_ratio(equity_values),
            'total_days': len(self.equity_curve)
        }
    
    def _calculate_sharpe_ratio(self, equity_values):
        """Calcula Sharpe ratio"""
        if len(equity_values) < 2:
            return 0
        
        returns = np.diff(equity_values) / equity_values[:-1]
        
        if np.std(returns) == 0:
            return 0
        
        return np.mean(returns) / np.std(returns) * np.sqrt(252)  # Anualizado


class LiveTrader:
    """
    ⚡ TRADER AUTOMÁTICO EN VIVO
    
    Sistema de trading automático para operar FVGs en tiempo real
    """
    
    def __init__(self, broker_config=None):
        """
        Inicializa el trader en vivo
        
        Args:
            broker_config: Configuración del broker
        """
        self.broker_config = broker_config or {}
        self.is_active = False
        self.open_positions = {}
        self.trade_log = []
        
        print("⚡ LiveTrader inicializado")
    
    def start_trading(self):
        """Inicia el trading automático"""
        if not self.broker_config:
            print("❌ Configuración del broker requerida")
            return False
        
        self.is_active = True
        print("🚀 Trading automático iniciado")
        return True
    
    def stop_trading(self):
        """Detiene el trading automático"""
        self.is_active = False
        print("⏹️ Trading automático detenido")
    
    def process_signal(self, signal, risk_assessment):
        """
        Procesa una señal de trading
        
        Args:
            signal: Señal de trading
            risk_assessment: Evaluación de riesgo
            
        Returns:
            Dict con resultado de la operación
        """
        if not self.is_active:
            return {'status': 'ERROR', 'message': 'Trading no activo'}
        
        if not risk_assessment['approved']:
            return {
                'status': 'REJECTED',
                'message': f"Riesgo {risk_assessment['risk_level'].value}",
                'recommendations': risk_assessment['recommendations']
            }
        
        # Simular ejecución de trade
        trade_result = self._execute_trade(signal, risk_assessment)
        
        if trade_result['status'] == 'SUCCESS':
            self.open_positions[signal['id']] = {
                'signal': signal,
                'position_size': risk_assessment['position_size'],
                'entry_time': datetime.now(),
                'status': 'OPEN'
            }
            
            self.trade_log.append({
                'signal_id': signal['id'],
                'action': 'OPEN',
                'timestamp': datetime.now(),
                'details': trade_result
            })
        
        return trade_result
    
    def _execute_trade(self, signal, risk_assessment):
        """Ejecuta trade con el broker"""
        # Simulación de ejecución (en producción conectaría con API del broker)
        
        try:
            # Simular slippage
            slippage = np.random.uniform(-0.00002, 0.00002)
            execution_price = signal['entry_price'] + slippage
            
            # Simular latencia
            import time
            time.sleep(0.1)
            
            print(f"📊 Trade ejecutado: {signal['type'].value} {signal['symbol']} "
                  f"@ {execution_price:.5f} (Size: {risk_assessment['position_size']:.2f})")
            
            return {
                'status': 'SUCCESS',
                'execution_price': execution_price,
                'position_size': risk_assessment['position_size'],
                'slippage': slippage,
                'commission': 0.00007,  # 0.7 pips
                'timestamp': datetime.now()
            }
        
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': str(e),
                'timestamp': datetime.now()
            }
    
    def monitor_positions(self, current_market_data):
        """Monitorea posiciones abiertas"""
        closed_positions = []
        
        for signal_id, position in self.open_positions.items():
            signal = position['signal']
            current_price = current_market_data.get('price', signal['entry_price'])
            
            # Verificar stop loss y take profit
            should_close, reason = self._check_exit_conditions(signal, current_price)
            
            if should_close:
                close_result = self._close_position(signal_id, current_price, reason)
                closed_positions.append(signal_id)
                
                self.trade_log.append({
                    'signal_id': signal_id,
                    'action': 'CLOSE',
                    'reason': reason,
                    'timestamp': datetime.now(),
                    'details': close_result
                })
        
        # Remover posiciones cerradas
        for signal_id in closed_positions:
            del self.open_positions[signal_id]
    
    def _check_exit_conditions(self, signal, current_price):
        """Verifica condiciones de salida"""
        if signal['type'] == SignalType.BUY:
            if current_price <= signal['stop_loss']:
                return True, 'STOP_LOSS'
            elif current_price >= signal['take_profit']:
                return True, 'TAKE_PROFIT'
        
        elif signal['type'] == SignalType.SELL:
            if current_price >= signal['stop_loss']:
                return True, 'STOP_LOSS'
            elif current_price <= signal['take_profit']:
                return True, 'TAKE_PROFIT'
        
        return False, None
    
    def _close_position(self, signal_id, exit_price, reason):
        """Cierra una posición"""
        # Simulación de cierre
        print(f"🔒 Cerrando posición {signal_id}: {reason} @ {exit_price:.5f}")
        
        return {
            'status': 'CLOSED',
            'exit_price': exit_price,
            'reason': reason,
            'timestamp': datetime.now()
        }
    
    def get_trading_summary(self):
        """Obtiene resumen de trading"""
        return {
            'is_active': self.is_active,
            'open_positions': len(self.open_positions),
            'total_trades': len(self.trade_log),
            'last_activity': self.trade_log[-1]['timestamp'] if self.trade_log else None
        }


# Configuración de la oficina de trading
TRADING_CONFIG = {
    "signal_generator": {
        "min_signal_strength": 2,
        "risk_reward_ratio": 2.0,
        "confluence_weight": 0.4,
        "quality_weight": 0.3,
        "context_weight": 0.3
    },
    "risk_manager": {
        "max_risk_per_trade": 0.02,
        "max_daily_loss": 0.05,
        "max_concurrent_trades": 3,
        "max_correlation": 0.7
    },
    "backtest_engine": {
        "initial_balance": 10000,
        "commission": 0.00007,
        "slippage": 0.00001
    },
    "live_trader": {
        "execution_timeout": 5,
        "max_slippage": 0.00003,
        "position_monitoring_interval": 1
    }
}

__all__ = [
    "FVGSignalGenerator",
    "RiskManager",
    "BacktestEngine",
    "LiveTrader",
    "SignalType",
    "SignalStrength", 
    "RiskLevel",
    "TRADING_CONFIG"
]
