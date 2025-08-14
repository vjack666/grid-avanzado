"""
INTERFACES - Trading Grid v2.0.0
================================
Módulo de interfaces para el sistema Trading Grid.

Contiene abstracciones e interfaces para:
- Conectores de trading
- Gestores de datos
- Sistemas de análisis
- APIs externas

Arquitectura:
- BaseConnector: Interfaz base para conectores
- DataInterface: Interfaz para gestores de datos
- AnalysisInterface: Interfaz para sistemas de análisis
- APIInterface: Interfaz para APIs externas

Autor: GitHub Copilot
Fecha: Agosto 2025
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd

__version__ = "2.0.0"
__author__ = "GitHub Copilot"

# Interfaces base del sistema
class BaseConnector(ABC):
    """Interfaz base para conectores de trading"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establecer conexión"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Cerrar conexión"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Verificar estado de conexión"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """Obtener información de cuenta"""
        pass

class DataInterface(ABC):
    """Interfaz para gestores de datos"""
    
    @abstractmethod
    def load_data(self, symbol: str, timeframe: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Cargar datos históricos"""
        pass
    
    @abstractmethod
    def save_data(self, data: pd.DataFrame, symbol: str, timeframe: str) -> bool:
        """Guardar datos"""
        pass
    
    @abstractmethod
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validar calidad de datos"""
        pass

class AnalysisInterface(ABC):
    """Interfaz para sistemas de análisis"""
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar análisis"""
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generar señales de trading"""
        pass
    
    @abstractmethod
    def validate_signals(self, signals: List[Dict[str, Any]]) -> bool:
        """Validar señales generadas"""
        pass

class APIInterface(ABC):
    """Interfaz para APIs externas"""
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Autenticar con API"""
        pass
    
    @abstractmethod
    def fetch_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener datos de API"""
        pass
    
    @abstractmethod
    def handle_error(self, error: Exception) -> None:
        """Manejar errores de API"""
        pass

class BacktestInterface(ABC):
    """Interfaz para sistemas de backtest"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializar backtest"""
        pass
    
    @abstractmethod
    def run(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Ejecutar backtest"""
        pass
    
    @abstractmethod
    def get_results(self) -> Dict[str, Any]:
        """Obtener resultados"""
        pass

class RiskManagerInterface(ABC):
    """Interfaz para gestores de riesgo"""
    
    @abstractmethod
    def calculate_position_size(self, capital: float, risk_percent: float, stop_loss: float) -> float:
        """Calcular tamaño de posición"""
        pass
    
    @abstractmethod
    def validate_trade(self, trade_request: Dict[str, Any]) -> bool:
        """Validar operación"""
        pass
    
    @abstractmethod
    def monitor_risk(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Monitorear riesgo"""
        pass

# Exports del módulo
__all__ = [
    "BaseConnector",
    "DataInterface", 
    "AnalysisInterface",
    "APIInterface",
    "BacktestInterface",
    "RiskManagerInterface"
]