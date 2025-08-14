"""
🏢 PISO 4 - GESTIÓN DE RIESGO Y POSICIONES
========================================

Este piso integra el análisis estocástico con el sistema FVG para gestión avanzada de entradas.

FLUJO DE TRABAJO:
1. Piso 3 detecta FVGs de calidad alta (≥7.5)
2. Piso 4 activa análisis estocástico específico
3. Estocástico dicta timing exacto de entrada
4. Gestión de riesgo y posiciones integrada

MÓDULOS:
- fvg_stochastic_integration: Integración FVG-Estocástico
- risk_position_manager: Gestión de riesgo y posiciones  
- stochastic_signal_analyzer: Análisis avanzado de señales estocásticas
- entry_execution_manager: Gestión de ejecución de entradas

AUTOR: Sistema Trading Grid
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

# Imports principales
from .stochastic_signal_analyzer import (
    StochasticSignalAnalyzer, 
    get_stochastic_analyzer
)

from .fvg_stochastic_integration import (
    FVGStochasticIntegrator,
    get_fvg_stochastic_integrator
)

from .risk_position_manager import (
    RiskPositionManager,
    get_risk_position_manager
)

from .entry_execution_manager import (
    EntryExecutionManager,
    get_entry_execution_manager
)

from .piso4_manager import (
    Piso4Manager,
    get_piso4_manager
)

__all__ = [
    # Clases principales
    'StochasticSignalAnalyzer',
    'FVGStochasticIntegrator',
    'RiskPositionManager', 
    'EntryExecutionManager',
    'Piso4Manager',
    
    # Funciones de acceso global
    'get_stochastic_analyzer',
    'get_fvg_stochastic_integrator',
    'get_risk_position_manager',
    'get_entry_execution_manager',
    'get_piso4_manager',
    
    # Funciones de utilidad
    'initialize_piso4',
    'get_piso4_status',
    'quick_setup_piso4'
]

def initialize_piso4(symbol: str = 'EURUSD', config: dict = None):
    """
    🏢 Inicializar el Piso 4 completo
    
    Args:
        symbol: Símbolo para configurar todos los gestores
        config: Configuración personalizada (opcional)
        
    Returns:
        Piso4Manager: Gestor principal configurado
    """
    # Obtener gestor principal
    piso4 = get_piso4_manager(symbol)
    
    # Aplicar configuración personalizada si se proporciona
    if config:
        # Aquí se aplicaría la configuración personalizada
        # Por ahora solo retornamos el manager
        pass
    
    return piso4

def get_piso4_status(symbol: str = 'EURUSD'):
    """
    📊 Obtener estado completo del Piso 4
    
    Args:
        symbol: Símbolo para verificar estado
        
    Returns:
        dict: Estado completo del Piso 4
    """
    piso4 = get_piso4_manager(symbol)
    return piso4.get_comprehensive_status()

def quick_setup_piso4(symbol: str = 'EURUSD', 
                      enable_auto_execution: bool = False,
                      risk_per_trade: float = 0.02):
    """
    ⚡ Configuración rápida del Piso 4
    
    Args:
        symbol: Símbolo para configurar
        enable_auto_execution: Habilitar ejecución automática
        risk_per_trade: Riesgo por operación (2% por defecto)
        
    Returns:
        Piso4Manager: Gestor configurado
    """
    config = {
        'auto_execution': enable_auto_execution,
        'risk_per_trade': risk_per_trade,
        'confluence_threshold': 70.0,
        'max_daily_trades': 5
    }
    
    return initialize_piso4(symbol, config)
