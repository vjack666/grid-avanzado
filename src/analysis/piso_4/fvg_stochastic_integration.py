"""
🏢 PISO 4 - INTEGRADOR FVG-ESTOCÁSTICO
=====================================

Módulo central que conecta las señales FVG del Piso 3 con el análisis estocástico.
Gestiona la confluencia y timing de entradas.

FLUJO PRINCIPAL:
1. Recibe señales FVG de alta calidad del Piso 3
2. Activa análisis estocástico específico 
3. Evalúa confluencia direccional
4. Calcula timing óptimo de entrada
5. Genera señales combinadas FVG+Estocástico

AUTOR: Sistema Trading Grid - Piso 4
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional, Any

# Configurar imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis" / "piso_3").absolute()))

# Imports del sistema
from logger_manager import LoggerManager
from .stochastic_signal_analyzer import StochasticSignalAnalyzer

class FVGStochasticIntegrator:
    """
    🎯 INTEGRADOR FVG-ESTOCÁSTICO
    Conecta señales FVG con análisis estocástico para entradas precisas
    """
    
    def __init__(self, symbol='EURUSD'):
        self.symbol = symbol
        self.logger = LoggerManager().get_logger('fvg_stochastic_integrator')
        
        # Componentes principales
        self.stochastic_analyzer = StochasticSignalAnalyzer(symbol)
        
        # Estado de integración
        self.active_fvg_signals = []
        self.confluence_history = []
        self.integration_stats = {
            'total_fvg_signals': 0,
            'total_confluences': 0,
            'successful_entries': 0,
            'confluence_rate': 0.0
        }
        
        # Configuración
        self.config = {
            'min_fvg_quality': 7.5,  # Calidad mínima FVG para activar estocástico
            'max_fvg_age_minutes': 60,  # Edad máxima FVG para considerarlo válido
            'min_confluence_strength': 70,  # Fuerza mínima de confluencia para entrada
            'stochastic_timeout_minutes': 15,  # Tiempo máximo espera señal estocástica
        }
    
    def receive_fvg_signal(self, fvg_signal: Dict) -> Dict:
        """
        📡 Recibir y procesar señal FVG del Piso 3
        
        Args:
            fvg_signal: Señal FVG recibida del detector
            
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            self.logger.info(f"📡 Señal FVG recibida: {fvg_signal.get('direction', 'UNKNOWN')}")
            
            # Validar calidad FVG
            if not self._validate_fvg_signal(fvg_signal):
                return {'status': 'rejected', 'reason': 'FVG quality too low'}
            
            # Agregar timestamp si no existe
            if 'timestamp' not in fvg_signal:
                fvg_signal['timestamp'] = datetime.now()
            
            # Activar análisis estocástico
            stochastic_result = self._activate_stochastic_analysis(fvg_signal)
            
            # Evaluar confluencia
            confluence_result = self._evaluate_confluence(fvg_signal, stochastic_result)
            
            # Guardar en historial
            self._update_integration_stats(fvg_signal, confluence_result)
            
            return confluence_result
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando señal FVG: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _validate_fvg_signal(self, fvg_signal: Dict) -> bool:
        """
        ✅ Validar señal FVG para activación estocástica
        
        Args:
            fvg_signal: Señal FVG a validar
            
        Returns:
            bool: True si es válida para activar estocástico
        """
        # Verificar calidad mínima
        quality_score = fvg_signal.get('quality_score', 0)
        if quality_score < self.config['min_fvg_quality']:
            self.logger.info(f"🔴 FVG rechazado: calidad {quality_score} < {self.config['min_fvg_quality']}")
            return False
        
        # Verificar edad del FVG
        if 'timestamp' in fvg_signal:
            age_minutes = (datetime.now() - fvg_signal['timestamp']).total_seconds() / 60
            if age_minutes > self.config['max_fvg_age_minutes']:
                self.logger.info(f"🔴 FVG rechazado: edad {age_minutes:.1f}min > {self.config['max_fvg_age_minutes']}min")
                return False
        
        # Verificar dirección válida
        direction = fvg_signal.get('direction', '').upper()
        if direction not in ['BUY', 'SELL', 'BULLISH', 'BEARISH']:
            self.logger.info(f"🔴 FVG rechazado: dirección inválida '{direction}'")
            return False
        
        self.logger.info(f"✅ FVG validado: calidad {quality_score}, dirección {direction}")
        return True
    
    def _activate_stochastic_analysis(self, fvg_signal: Dict) -> Dict:
        """
        🎯 Activar análisis estocástico específico para FVG
        
        Args:
            fvg_signal: Señal FVG que activa el análisis
            
        Returns:
            dict: Resultado del análisis estocástico
        """
        # Determinar modalidad según dirección FVG
        fvg_direction = fvg_signal.get('direction', '').upper()
        
        # Mapear dirección FVG a modalidad estocástica
        if fvg_direction in ['BUY', 'BULLISH']:
            modalidad = 'BUY'
        elif fvg_direction in ['SELL', 'BEARISH']:
            modalidad = 'SELL'
        else:
            modalidad = 'AMBOS'
        
        self.logger.info(f"🎯 Activando análisis estocástico modo: {modalidad}")
        
        # Ejecutar análisis estocástico
        stochastic_result = self.stochastic_analyzer.analyze_stochastic_for_fvg(
            fvg_signal=fvg_signal,
            modalidad_operacion=modalidad
        )
        
        return stochastic_result
    
    def _evaluate_confluence(self, fvg_signal: Dict, stochastic_result: Dict) -> Dict:
        """
        🔄 Evaluar confluencia entre FVG y Estocástico
        
        Args:
            fvg_signal: Señal FVG
            stochastic_result: Resultado análisis estocástico
            
        Returns:
            dict: Resultado de la evaluación de confluencia
        """
        confluence_result = {
            'status': 'evaluated',
            'fvg_signal': fvg_signal,
            'stochastic_result': stochastic_result,
            'confluence_detected': False,
            'confluence_strength': 0,
            'entry_recommendation': 'WAIT',
            'risk_level': 'HIGH',
            'timestamp': datetime.now()
        }
        
        # Verificar confluencia direccional
        fvg_direction = fvg_signal.get('direction', '').upper()
        stoch_signal = stochastic_result.get('senal_tipo', '')
        
        # Mapear direcciones
        fvg_mapped = self._map_fvg_direction(fvg_direction)
        
        if fvg_mapped == stoch_signal and stochastic_result.get('senal_valida', False):
            confluence_result['confluence_detected'] = True
            
            # Calcular fuerza de confluencia
            strength = self._calculate_confluence_strength(fvg_signal, stochastic_result)
            confluence_result['confluence_strength'] = strength
            
            # Determinar recomendación de entrada
            if strength >= self.config['min_confluence_strength']:
                confluence_result['entry_recommendation'] = fvg_mapped
                confluence_result['risk_level'] = self._calculate_risk_level(strength)
                
                self.logger.info(f"🎯 CONFLUENCIA DETECTADA: {fvg_mapped} - Fuerza: {strength}%")
            else:
                confluence_result['entry_recommendation'] = 'WAIT'
                confluence_result['risk_level'] = 'HIGH'
                
                self.logger.info(f"⚠️ Confluencia débil: {strength}% < {self.config['min_confluence_strength']}%")
        else:
            self.logger.info(f"❌ Sin confluencia: FVG={fvg_direction}, Stoch={stoch_signal}")
        
        return confluence_result
    
    def _map_fvg_direction(self, fvg_direction: str) -> str:
        """🗺️ Mapear dirección FVG a dirección de trading"""
        direction_map = {
            'BULLISH': 'BUY',
            'BUY': 'BUY',
            'BEARISH': 'SELL',
            'SELL': 'SELL'
        }
        return direction_map.get(fvg_direction.upper(), '')
    
    def _calculate_confluence_strength(self, fvg_signal: Dict, stochastic_result: Dict) -> int:
        """
        💪 Calcular fuerza de confluencia
        
        Args:
            fvg_signal: Señal FVG
            stochastic_result: Resultado estocástico
            
        Returns:
            int: Fuerza de confluencia (0-100)
        """
        strength = 0
        
        # Factor 1: Calidad FVG (0-40 puntos)
        fvg_quality = fvg_signal.get('quality_score', 0)
        strength += min(40, int(fvg_quality * 4))
        
        # Factor 2: Intensidad estocástica (0-25 puntos)
        k_value = stochastic_result.get('k', 50)
        if stochastic_result.get('senal_tipo') == 'BUY':
            # Para BUY, mejor si K está más bajo (sobreventa)
            stoch_intensity = max(0, 20 - k_value) if k_value <= 20 else 0
        else:
            # Para SELL, mejor si K está más alto (sobrecompra)
            stoch_intensity = max(0, k_value - 80) if k_value >= 80 else 0
        
        strength += min(25, int(stoch_intensity))
        
        # Factor 3: Vela cerrada (0-15 puntos)
        if stochastic_result.get('vela_cerrada', False):
            strength += 15
        
        # Factor 4: Timing FVG (0-10 puntos)
        fvg_age = self._get_fvg_age_minutes(fvg_signal)
        if fvg_age <= 5:
            strength += 10
        elif fvg_age <= 15:
            strength += 7
        elif fvg_age <= 30:
            strength += 5
        elif fvg_age <= 60:
            strength += 2
        
        # Factor 5: Cruces estocásticos (0-10 puntos)
        if stochastic_result.get('cruce_k_d', False) or stochastic_result.get('cruce_d_k', False):
            strength += 10
        
        return min(100, strength)
    
    def _get_fvg_age_minutes(self, fvg_signal: Dict) -> float:
        """⏰ Obtener edad del FVG en minutos"""
        if 'timestamp' not in fvg_signal:
            return 0
        
        return (datetime.now() - fvg_signal['timestamp']).total_seconds() / 60
    
    def _calculate_risk_level(self, confluence_strength: int) -> str:
        """🎯 Calcular nivel de riesgo basado en fuerza de confluencia"""
        if confluence_strength >= 90:
            return 'VERY_LOW'
        elif confluence_strength >= 80:
            return 'LOW'
        elif confluence_strength >= 70:
            return 'MEDIUM'
        elif confluence_strength >= 60:
            return 'HIGH'
        else:
            return 'VERY_HIGH'
    
    def _update_integration_stats(self, fvg_signal: Dict, confluence_result: Dict):
        """📊 Actualizar estadísticas de integración"""
        self.integration_stats['total_fvg_signals'] += 1
        
        if confluence_result.get('confluence_detected', False):
            self.integration_stats['total_confluences'] += 1
        
        # Calcular tasa de confluencia
        if self.integration_stats['total_fvg_signals'] > 0:
            self.integration_stats['confluence_rate'] = (
                self.integration_stats['total_confluences'] / 
                self.integration_stats['total_fvg_signals'] * 100
            )
        
        # Guardar en historial (mantener últimas 100)
        self.confluence_history.append({
            'timestamp': datetime.now(),
            'fvg_quality': fvg_signal.get('quality_score', 0),
            'confluence_detected': confluence_result.get('confluence_detected', False),
            'confluence_strength': confluence_result.get('confluence_strength', 0),
            'entry_recommendation': confluence_result.get('entry_recommendation', 'WAIT')
        })
        
        # Mantener solo últimas 100 entradas
        if len(self.confluence_history) > 100:
            self.confluence_history = self.confluence_history[-100:]
    
    def get_integration_status(self) -> Dict:
        """
        📈 Obtener estado actual de la integración
        
        Returns:
            dict: Estado y estadísticas de la integración
        """
        return {
            'symbol': self.symbol,
            'stats': self.integration_stats.copy(),
            'active_signals': len(self.active_fvg_signals),
            'last_confluence': self.confluence_history[-1] if self.confluence_history else None,
            'config': self.config.copy(),
            'timestamp': datetime.now()
        }
    
    def get_recent_confluences(self, limit: int = 10) -> List[Dict]:
        """
        📋 Obtener confluencias recientes
        
        Args:
            limit: Número máximo de confluencias a retornar
            
        Returns:
            list: Lista de confluencias recientes
        """
        recent = [item for item in self.confluence_history if item['confluence_detected']]
        return recent[-limit:] if recent else []

# Instancia global del integrador
fvg_stochastic_integrator = FVGStochasticIntegrator()

def process_fvg_signal(fvg_signal: Dict, symbol: str = 'EURUSD') -> Dict:
    """
    🎯 Función principal para procesar señales FVG
    
    Args:
        fvg_signal: Señal FVG del Piso 3
        symbol: Símbolo a procesar
        
    Returns:
        dict: Resultado del procesamiento
    """
    global fvg_stochastic_integrator
    
    # Actualizar símbolo si es diferente
    if fvg_stochastic_integrator.symbol != symbol:
        fvg_stochastic_integrator = FVGStochasticIntegrator(symbol)
    
    return fvg_stochastic_integrator.receive_fvg_signal(fvg_signal)

def get_integration_status(symbol: str = 'EURUSD') -> Dict:
    """
    📊 Obtener estado de la integración
    
    Args:
        symbol: Símbolo a consultar
        
    Returns:
        dict: Estado actual de la integración
    """
    global fvg_stochastic_integrator
    
    if fvg_stochastic_integrator.symbol != symbol:
        fvg_stochastic_integrator = FVGStochasticIntegrator(symbol)
    
    return fvg_stochastic_integrator.get_integration_status()

def get_fvg_stochastic_integrator(symbol: str = 'EURUSD'):
    """
    🤝 Obtener instancia del integrador FVG-Estocástico
    
    Args:
        symbol: Símbolo para el integrador
        
    Returns:
        FVGStochasticIntegrator: Instancia del integrador
    """
    global fvg_stochastic_integrator
    
    if fvg_stochastic_integrator is None or fvg_stochastic_integrator.symbol != symbol:
        fvg_stochastic_integrator = FVGStochasticIntegrator(symbol)
    
    return fvg_stochastic_integrator
