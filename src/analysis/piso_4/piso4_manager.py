"""
🏢 PISO 4 - MANAGER PRINCIPAL
============================

Manager central del Piso 4 que coordina:
- Integración FVG-Estocástico
- Gestión de riesgo y posiciones
- Ejecución de entradas
- Conexión con otros pisos

AUTOR: Sistema Trading Grid - Piso 4
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configurar imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str((project_root / "src" / "core").absolute()))

from logger_manager import LoggerManager
from .fvg_stochastic_integration import FVGStochasticIntegrator
from .stochastic_signal_analyzer import StochasticSignalAnalyzer

class Piso4Manager:
    """
    🏢 MANAGER PRINCIPAL DEL PISO 4
    Coordina todas las operaciones de gestión de riesgo y posiciones
    """
    
    def __init__(self, symbol='EURUSD'):
        self.symbol = symbol
        self.logger = LoggerManager().get_logger('piso4_manager')
        
        # Componentes principales
        self.fvg_stochastic_integrator = None
        self.stochastic_analyzer = None
        
        # Estado del manager
        self.is_initialized = False
        self.is_active = False
        
        # Estadísticas
        self.stats = {
            'signals_processed': 0,
            'confluences_detected': 0,
            'entries_executed': 0,
            'start_time': None
        }
    
    def initialize(self) -> bool:
        """
        🚀 Inicializar Piso 4
        
        Returns:
            bool: True si inicialización exitosa
        """
        try:
            self.logger.info(f"🚀 Inicializando Piso 4 - Gestión de Riesgo y Posiciones")
            
            # Inicializar componentes
            self.fvg_stochastic_integrator = FVGStochasticIntegrator(self.symbol)
            self.stochastic_analyzer = StochasticSignalAnalyzer(self.symbol)
            
            # Actualizar estado
            self.is_initialized = True
            self.is_active = True
            self.stats['start_time'] = datetime.now()
            
            self.logger.info(f"✅ Piso 4 inicializado exitosamente para {self.symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error inicializando Piso 4: {e}")
            self.is_initialized = False
            return False
    
    def process_fvg_from_piso3(self, fvg_signal: Dict) -> Dict:
        """
        📡 Procesar señal FVG recibida del Piso 3
        
        Args:
            fvg_signal: Señal FVG del Piso 3
            
        Returns:
            dict: Resultado del procesamiento
        """
        if not self.is_initialized:
            return {'status': 'error', 'reason': 'Piso 4 not initialized'}
        
        try:
            self.logger.info(f"📡 Procesando señal FVG del Piso 3")
            
            # Procesar con integrador
            result = self.fvg_stochastic_integrator.receive_fvg_signal(fvg_signal)
            
            # Actualizar estadísticas
            self.stats['signals_processed'] += 1
            if result.get('confluence_detected', False):
                self.stats['confluences_detected'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando señal FVG: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_system_status(self) -> Dict:
        """
        📊 Obtener estado completo del Piso 4
        
        Returns:
            dict: Estado del sistema
        """
        status = {
            'piso': 4,
            'name': 'Gestión de Riesgo y Posiciones',
            'symbol': self.symbol,
            'initialized': self.is_initialized,
            'active': self.is_active,
            'timestamp': datetime.now(),
            'stats': self.stats.copy()
        }
        
        if self.is_initialized:
            # Estado del integrador
            integration_status = self.fvg_stochastic_integrator.get_integration_status()
            status['integration'] = integration_status
            
            # Estado del analizador estocástico
            status['stochastic'] = {
                'symbol': self.stochastic_analyzer.symbol,
                'timeframe': self.stochastic_analyzer.timeframe,
                'last_analysis': self.stochastic_analyzer.cache.get('timestamp'),
                'current_k': self.stochastic_analyzer.cache.get('k'),
                'current_d': self.stochastic_analyzer.cache.get('d')
            }
        
        return status
    
    def connect_to_piso3(self):
        """🔗 Conectar con el Piso 3 para recibir señales FVG"""
        try:
            # Importar manager del Piso 3
            sys.path.insert(0, str((Path(__file__).parent.parent / "piso_3").absolute()))
            from piso_3 import get_piso3_manager
            
            piso3_manager = get_piso3_manager()
            if piso3_manager:
                # Registrar callback para señales FVG
                piso3_manager.register_fvg_callback(self.process_fvg_from_piso3)
                self.logger.info("🔗 Conectado exitosamente al Piso 3")
                return True
            else:
                self.logger.warning("⚠️ No se pudo conectar al Piso 3")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error conectando al Piso 3: {e}")
            return False
    
    def stop(self):
        """⏹️ Detener Piso 4"""
        self.logger.info("⏹️ Deteniendo Piso 4")
        self.is_active = False
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """
        📋 Obtener actividad reciente del Piso 4
        
        Args:
            limit: Número máximo de actividades
            
        Returns:
            list: Lista de actividades recientes
        """
        if not self.is_initialized:
            return []
        
        return self.fvg_stochastic_integrator.get_recent_confluences(limit)

# Instancia global del manager
piso4_manager = None

def get_piso4_manager(symbol: str = 'EURUSD'):
    """
    🏢 Obtener manager del Piso 4
    
    Args:
        symbol: Símbolo para el manager
        
    Returns:
        Piso4Manager: Instancia del manager
    """
    global piso4_manager
    
    if piso4_manager is None or piso4_manager.symbol != symbol:
        piso4_manager = Piso4Manager(symbol)
        piso4_manager.initialize()
    
    return piso4_manager

def initialize_piso4(symbol: str = 'EURUSD') -> bool:
    """
    🚀 Inicializar Piso 4
    
    Args:
        symbol: Símbolo para inicializar
        
    Returns:
        bool: True si inicialización exitosa
    """
    manager = get_piso4_manager(symbol)
    return manager.is_initialized
