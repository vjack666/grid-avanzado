"""
🏢 CONECTOR CENTRAL DEL EDIFICIO - TRADING GRID
==============================================

Módulo central que conecta todos los pisos del sistema:
- Piso 3: Análisis FVG avanzado
- Piso 4: Gestión de riesgo y posiciones con estocástico

FLUJO PRINCIPAL:
1. Piso 3 detecta FVGs de alta calidad
2. Envía señal al Piso 4 a través del conector
3. Piso 4 activa análisis estocástico
4. Evalúa confluencia FVG-Estocástico
5. Genera recomendaciones de entrada

AUTOR: Sistema Trading Grid
VERSIÓN: 1.0
FECHA: 2025-08-13
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable

# Configurar rutas
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src" / "core"))

from logger_manager import LoggerManager

class TradingGridConnector:
    """
    🏢 CONECTOR CENTRAL DEL EDIFICIO TRADING GRID
    Coordina comunicación entre todos los pisos del sistema
    """
    
    def __init__(self, symbol='EURUSD', test_mode=False):
        self.symbol = symbol
        self.test_mode = test_mode
        self.logger = LoggerManager().get_logger('trading_grid_connector')
        
        # Managers de pisos
        self.piso3_manager = None
        self.piso4_manager = None
        
        # Estado de conexiones
        self.connections = {
            'piso_3': False,
            'piso_4': False
        }
        
        # Callbacks registrados
        self.callbacks = {
            'on_fvg_detected': [],
            'on_confluence_found': [],
            'on_entry_signal': []
        }
        
        # Estadísticas del edificio
        self.building_stats = {
            'total_fvg_signals': 0,
            'total_confluences': 0,
            'total_entries': 0,
            'success_rate': 0.0,
            'start_time': datetime.now()
        }
    
    def initialize_building(self) -> bool:
        """
        🚀 Inicializar todo el edificio Trading Grid
        
        Returns:
            bool: True si inicialización exitosa
        """
        try:
            self.logger.info(f"🏢 Inicializando Edificio Trading Grid para {self.symbol}")
            
            # Inicializar Piso 3
            success_p3 = self._initialize_piso3()
            
            # Inicializar Piso 4
            success_p4 = self._initialize_piso4()
            
            # Conectar pisos
            if success_p3 and success_p4:
                self._connect_pisos()
            
            building_ready = success_p3 and success_p4
            
            if building_ready:
                self.logger.info("✅ Edificio Trading Grid inicializado exitosamente")
                self.logger.info(f"📊 Piso 3: {'✅' if success_p3 else '❌'} | Piso 4: {'✅' if success_p4 else '❌'}")
            else:
                self.logger.warning("⚠️ Edificio parcialmente inicializado")
            
            return building_ready
            
        except Exception as e:
            self.logger.error(f"❌ Error inicializando edificio: {e}")
            return False
    
    def _initialize_piso3(self) -> bool:
        """🏢 Inicializar Piso 3 - Análisis FVG"""
        try:
            # Importar Piso 3
            sys.path.insert(0, str(project_root / "src"))
            
            if self.test_mode:
                # Modo de prueba: crear un mock manager simple
                class MockPiso3Manager:
                    def __init__(self):
                        self.is_initialized = True
                        self.system_status = "TEST_MODE"
                    
                    def get_system_status(self):
                        return {
                            'status': 'TEST_MODE',
                            'initialized': True,
                            'test_mode': True
                        }
                
                self.piso3_manager = MockPiso3Manager()
                self.connections['piso_3'] = True
                self.logger.info("✅ Piso 3 conectado (MODO TEST)")
                return True
            else:
                # Modo producción: cargar manager real
                from src.analysis.piso_3 import get_piso3_manager
                
                self.piso3_manager = get_piso3_manager()
                
                if self.piso3_manager:
                    self.connections['piso_3'] = True
                    self.logger.info("✅ Piso 3 conectado")
                    return True
                else:
                    self.logger.warning("⚠️ Piso 3 no disponible")
                    return False
                
        except Exception as e:
            self.logger.error(f"❌ Error inicializando Piso 3: {e}")
            return False
    
    def _initialize_piso4(self) -> bool:
        """🏢 Inicializar Piso 4 - Gestión de Riesgo"""
        try:
            # Importar Piso 4
            sys.path.insert(0, str(project_root / "src"))
            
            from src.analysis.piso_4 import get_piso4_manager
            
            self.piso4_manager = get_piso4_manager(self.symbol)
            
            if self.piso4_manager and self.piso4_manager.is_initialized:
                self.connections['piso_4'] = True
                self.logger.info("✅ Piso 4 conectado")
                return True
            else:
                self.logger.warning("⚠️ Piso 4 no disponible")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error inicializando Piso 4: {e}")
            return False
    
    def _connect_pisos(self):
        """🔗 Conectar pisos entre sí"""
        try:
            # Registrar callback del Piso 3 para enviar señales al Piso 4
            if self.piso3_manager and self.piso4_manager:
                
                # Callback para señales FVG de alta calidad
                def on_high_quality_fvg(fvg_signal):
                    """Callback para FVGs de alta calidad detectados en Piso 3"""
                    try:
                        quality_score = fvg_signal.get('quality_score', 0)
                        
                        # Solo procesar FVGs de alta calidad (≥7.5)
                        if quality_score >= 7.5:
                            self.logger.info(f"🎯 FVG alta calidad detectado: {quality_score}")
                            
                            # Enviar al Piso 4
                            confluence_result = self.piso4_manager.process_fvg_from_piso3(fvg_signal)
                            
                            # Actualizar estadísticas
                            self.building_stats['total_fvg_signals'] += 1
                            
                            if confluence_result.get('confluence_detected', False):
                                self.building_stats['total_confluences'] += 1
                                
                                # Notificar callbacks de confluencia
                                self._notify_callbacks('on_confluence_found', confluence_result)
                                
                                # Si hay recomendación de entrada
                                if confluence_result.get('entry_recommendation') not in ['WAIT', None]:
                                    self.building_stats['total_entries'] += 1
                                    self._notify_callbacks('on_entry_signal', confluence_result)
                            
                            # Notificar callbacks de FVG
                            self._notify_callbacks('on_fvg_detected', {
                                'fvg_signal': fvg_signal,
                                'confluence_result': confluence_result
                            })
                            
                            return confluence_result
                        
                    except Exception as e:
                        self.logger.error(f"❌ Error procesando FVG en callback: {e}")
                        return None
                
                # Registrar callback en Piso 3 (si tiene método register_callback)
                if hasattr(self.piso3_manager, 'register_fvg_callback'):
                    self.piso3_manager.register_fvg_callback(on_high_quality_fvg)
                    self.logger.info("🔗 Callback FVG registrado en Piso 3")
                
                self.logger.info("🔗 Pisos conectados exitosamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error conectando pisos: {e}")
    
    def _notify_callbacks(self, event_type: str, data: Dict):
        """📢 Notificar callbacks registrados"""
        try:
            for callback in self.callbacks.get(event_type, []):
                callback(data)
        except Exception as e:
            self.logger.error(f"❌ Error notificando callback {event_type}: {e}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """
        📝 Registrar callback para eventos del edificio
        
        Args:
            event_type: Tipo de evento ('on_fvg_detected', 'on_confluence_found', 'on_entry_signal')
            callback: Función callback a registrar
        """
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            self.logger.info(f"📝 Callback registrado para {event_type}")
        else:
            self.logger.warning(f"⚠️ Tipo de evento desconocido: {event_type}")
    
    def get_building_status(self) -> Dict:
        """
        📊 Obtener estado completo del edificio
        
        Returns:
            dict: Estado completo del sistema
        """
        status = {
            'building': 'Trading Grid',
            'symbol': self.symbol,
            'timestamp': datetime.now(),
            'connections': self.connections.copy(),
            'stats': self.building_stats.copy()
        }
        
        # Estado Piso 3
        if self.piso3_manager:
            try:
                status['piso_3'] = self.piso3_manager.get_system_status()
            except:
                status['piso_3'] = {'status': 'error'}
        
        # Estado Piso 4
        if self.piso4_manager:
            try:
                status['piso_4'] = self.piso4_manager.get_system_status()
            except:
                status['piso_4'] = {'status': 'error'}
        
        # Calcular tasa de éxito
        if self.building_stats['total_fvg_signals'] > 0:
            self.building_stats['success_rate'] = (
                self.building_stats['total_confluences'] / 
                self.building_stats['total_fvg_signals'] * 100
            )
        
        return status
    
    def process_manual_fvg(self, fvg_signal: Dict) -> Dict:
        """
        🎯 Procesar FVG manualmente (para testing)
        
        Args:
            fvg_signal: Señal FVG manual
            
        Returns:
            dict: Resultado del procesamiento
        """
        if not self.piso4_manager:
            return {'status': 'error', 'reason': 'Piso 4 not available'}
        
        try:
            self.logger.info("🎯 Procesando FVG manual")
            
            # Agregar timestamp si no existe
            if 'timestamp' not in fvg_signal:
                fvg_signal['timestamp'] = datetime.now()
            
            # Procesar con Piso 4
            result = self.piso4_manager.process_fvg_from_piso3(fvg_signal)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando FVG manual: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def shutdown_building(self):
        """⏹️ Apagar todo el edificio"""
        self.logger.info("⏹️ Apagando Edificio Trading Grid")
        
        if self.piso4_manager:
            self.piso4_manager.stop()
        
        if self.piso3_manager and hasattr(self.piso3_manager, 'stop'):
            self.piso3_manager.stop()
        
        self.logger.info("✅ Edificio apagado")

# Instancia global del conector
trading_grid_connector = None

def get_trading_grid_connector(symbol: str = 'EURUSD', test_mode: bool = False):
    """
    🏢 Obtener conector del edificio Trading Grid
    
    Args:
        symbol: Símbolo para el sistema
        test_mode: Si es True, usa managers mock para pruebas rápidas
        
    Returns:
        TradingGridConnector: Instancia del conector
    """
    global trading_grid_connector
    
    if trading_grid_connector is None or trading_grid_connector.symbol != symbol:
        trading_grid_connector = TradingGridConnector(symbol, test_mode)
        trading_grid_connector.initialize_building()
    
    return trading_grid_connector

def initialize_trading_grid(symbol: str = 'EURUSD') -> bool:
    """
    🚀 Inicializar sistema Trading Grid completo
    
    Args:
        symbol: Símbolo para inicializar
        
    Returns:
        bool: True si inicialización exitosa
    """
    connector = get_trading_grid_connector(symbol)
    return all(connector.connections.values())
