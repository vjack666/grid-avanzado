"""
PISO 2 - BACKTEST ENGINE v1.0.0
===============================
Sistema completo de backtesting con datos reales de MT5

COMPONENTES PRINCIPALES:
- BacktestEngine: Motor principal de backtesting
- BacktestComponents: Analizador, Optimizador, Reporter  
- BacktestManager: Manager integral del PISO 2

AUTOR: Sistema Modular Trading Grid
FECHA: 2025-08-12
PROTOCOLO: PISO 2 - BACKTEST ENGINE
"""

# Imports principales
from .backtest_engine import (
    BacktestConfig,
    BacktestResult, 
    BacktestTrade,
    HistoricalDataProcessor,
    BacktestExecutor
)

from .backtest_components import (
    ResultsAnalyzer,
    ParameterOptimizer,
    BacktestReporter
)

from .backtest_manager import (
    Piso2BacktestManager
)

# Versión del PISO 2
__version__ = "1.0.0"
__protocol__ = "PISO_2_BACKTEST_ENGINE"

# Exports principales
__all__ = [
    # Configuración y resultados
    'BacktestConfig',
    'BacktestResult',
    'BacktestTrade',
    
    # Componentes del motor
    'HistoricalDataProcessor',
    'BacktestExecutor',
    'ResultsAnalyzer', 
    'ParameterOptimizer',
    'BacktestReporter',
    
    # Manager principal
    'Piso2BacktestManager',
    
    # Metadata
    '__version__',
    '__protocol__'
]

# Función de conveniencia para crear el manager
def create_backtest_manager():
    """Crear instancia del manager principal del PISO 2"""
    return Piso2BacktestManager()

# Función para crear configuración rápida
def create_quick_config(symbol: str = "EURUSD", 
                       timeframe: str = "M15",
                       strategy_type: str = "GRID_BOLLINGER",
                       initial_balance: float = 10000.0) -> BacktestConfig:
    """Crear configuración rápida de backtest"""
    return BacktestConfig(
        symbol=symbol,
        timeframe=timeframe,
        strategy_type=strategy_type,
        initial_balance=initial_balance,
        start_date="2025-05-20",
        end_date="2025-08-12"
    )
