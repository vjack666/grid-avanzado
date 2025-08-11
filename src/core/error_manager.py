"""
🎯 ERROR MANAGER - TRADING GRID v2.0
====================================

Sistema de manejo de errores centralizado para Trading Grid.
Unifica todo el error handling disperso en una interfaz consistente.

Autor: GitHub Copilot
Fecha: Agosto 10, 2025
Protocolo: TRADING GRID v2.0
Fase: 3 de 6
"""

import sys
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import pandas as pd

# Imports para MT5
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

class ErrorManager:
    """
    Sistema de manejo de errores centralizado para Trading Grid.
    
    Centraliza 5 tipos de error handling:
    1. Errores MT5 - Manejo específico de MetaTrader5
    2. Errores de datos - Validación y manejo de DataFrames
    3. Errores de trading - Operaciones de trading fallidas
    4. Errores de sistema - Fallos generales del sistema
    5. Validaciones - Checks de salud y consistencia
    """
    
    def __init__(self, logger_manager=None, config_manager=None):
        """
        Inicializa el ErrorManager.
        
        Args:
            logger_manager: Instancia de LoggerManager de FASE 2
            config_manager: Instancia de ConfigManager de FASE 1
        """
        self.logger = logger_manager
        self.config = config_manager
        
        # Contadores de errores por tipo
        self.error_counts = {
            'mt5': 0,
            'data': 0,
            'trading': 0,
            'system': 0,
            'validation': 0
        }
        
        # Estado del sistema
        self.system_health = {
            'mt5_connection': False,
            'data_quality': True,
            'trading_status': True,
            'system_status': True
        }
        
        # Configuración de reintentos
        self.retry_config = {
            'mt5_connection': 3,
            'data_fetch': 2,
            'trading_operation': 1,
            'system_operation': 2
        }
    
    def _log_error(self, message: str, error_type: str = "ERROR"):
        """Helper para logging de errores."""
        if self.logger:
            self.logger.log_error(f"[{error_type}] {message}")
        else:
            print(f"ERROR [{error_type}]: {message}")
    
    def _log_warning(self, message: str):
        """Helper para logging de warnings."""
        if self.logger:
            self.logger.log_warning(message)
        else:
            print(f"WARNING: {message}")
    
    def _log_info(self, message: str):
        """Helper para logging de info."""
        if self.logger:
            self.logger.log_info(message)
        else:
            print(f"INFO: {message}")
    
    def handle_mt5_error(self, operation: str, context: Dict[str, Any] = None) -> bool:
        """
        Maneja errores específicos de MetaTrader5.
        
        Args:
            operation: Operación que falló (ej: "initialize", "copy_rates")
            context: Contexto adicional del error
            
        Returns:
            bool: True si el error fue manejado, False si es crítico
        """
        if not MT5_AVAILABLE:
            self._log_error("MetaTrader5 no está disponible", "MT5")
            return False
        
        # Obtener información del error MT5
        error_code, error_msg = mt5.last_error()
        
        # Incrementar contador
        self.error_counts['mt5'] += 1
        
        # Contexto del error
        error_context = {
            'operation': operation,
            'error_code': error_code,
            'error_message': error_msg,
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            error_context.update(context)
        
        # Log del error
        self._log_error(f"MT5 Error en {operation}: [{error_code}] {error_msg}", "MT5")
        
        # Actualizar estado del sistema
        if operation == "initialize":
            self.system_health['mt5_connection'] = False
        
        # Manejo específico por tipo de error
        if error_code == 1:  # Generic error
            self._log_warning("Error genérico de MT5, reintentando...")
            return True
        elif error_code == 4024:  # No connection
            self._log_error("Sin conexión a MT5", "MT5")
            self.system_health['mt5_connection'] = False
            return False
        elif error_code == 4756:  # Invalid symbol
            self._log_error(f"Símbolo inválido en {operation}", "MT5")
            return False
        else:
            # Error no reconocido, pero manejable
            self._log_warning(f"Error MT5 no reconocido: {error_code}")
            return True
    
    def handle_data_error(self, data_type: str, error: Exception, context: Dict[str, Any] = None) -> bool:
        """
        Maneja errores de validación y procesamiento de datos.
        
        Args:
            data_type: Tipo de dato que falló (ej: "OHLC", "indicators")
            error: Excepción capturada
            context: Contexto adicional
            
        Returns:
            bool: True si el error fue manejado, False si es crítico
        """
        # Incrementar contador
        self.error_counts['data'] += 1
        
        # Contexto del error
        error_context = {
            'data_type': data_type,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            error_context.update(context)
        
        # Log del error
        self._log_error(f"Error de datos en {data_type}: {str(error)}", "DATA")
        
        # Actualizar estado del sistema
        self.system_health['data_quality'] = False
        
        # Manejo específico por tipo de error
        if isinstance(error, pd.errors.EmptyDataError):
            self._log_warning("DataFrame vacío detectado")
            return True
        elif isinstance(error, KeyError):
            self._log_error(f"Columna faltante en datos: {str(error)}", "DATA")
            return False
        elif isinstance(error, ValueError):
            self._log_warning(f"Valor inválido en datos: {str(error)}")
            return True
        else:
            # Error no reconocido
            self._log_error(f"Error de datos no reconocido: {type(error).__name__}", "DATA")
            return False
    
    def handle_trading_error(self, operation: str, error: Exception, context: Dict[str, Any] = None) -> bool:
        """
        Maneja errores de operaciones de trading.
        
        Args:
            operation: Operación de trading que falló
            error: Excepción capturada
            context: Contexto adicional
            
        Returns:
            bool: True si el error fue manejado, False si es crítico
        """
        # Incrementar contador
        self.error_counts['trading'] += 1
        
        # Contexto del error
        error_context = {
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            error_context.update(context)
        
        # Log del error
        self._log_error(f"Error de trading en {operation}: {str(error)}", "TRADING")
        
        # Actualizar estado del sistema
        self.system_health['trading_status'] = False
        
        # Todos los errores de trading son críticos por defecto
        return False
    
    def handle_system_error(self, component: str, error: Exception, context: Dict[str, Any] = None) -> bool:
        """
        Maneja errores generales del sistema.
        
        Args:
            component: Componente que falló
            error: Excepción capturada
            context: Contexto adicional
            
        Returns:
            bool: True si el error fue manejado, False si es crítico
        """
        # Incrementar contador
        self.error_counts['system'] += 1
        
        # Contexto del error
        error_context = {
            'component': component,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            error_context.update(context)
        
        # Log del error
        self._log_error(f"Error de sistema en {component}: {str(error)}", "SYSTEM")
        
        # Actualizar estado del sistema
        self.system_health['system_status'] = False
        
        # Manejo específico por tipo de error
        if isinstance(error, ImportError):
            self._log_error(f"Dependencia faltante en {component}: {str(error)}", "SYSTEM")
            return False
        elif isinstance(error, FileNotFoundError):
            self._log_warning(f"Archivo no encontrado en {component}: {str(error)}")
            return True
        elif isinstance(error, PermissionError):
            self._log_error(f"Permisos insuficientes en {component}: {str(error)}", "SYSTEM")
            return False
        else:
            # Error general del sistema
            self._log_warning(f"Error general en {component}: {type(error).__name__}")
            return True
    
    def validate_mt5_connection(self) -> bool:
        """
        Valida la conexión con MetaTrader5.
        
        Returns:
            bool: True si la conexión es válida
        """
        if not MT5_AVAILABLE:
            self._log_error("MetaTrader5 no está disponible para validación", "VALIDATION")
            return False
        
        try:
            # Intentar inicializar MT5
            if not mt5.initialize():
                self.handle_mt5_error("validate_connection")
                return False
            
            # Verificar información de cuenta
            account_info = mt5.account_info()
            if account_info is None:
                self._log_error("No se pudo obtener información de cuenta MT5", "VALIDATION")
                return False
            
            # Verificar información de terminal
            terminal_info = mt5.terminal_info()
            if terminal_info is None:
                self._log_error("No se pudo obtener información de terminal MT5", "VALIDATION")
                return False
            
            # Validación exitosa
            self.system_health['mt5_connection'] = True
            self._log_info("Validación MT5: Conexión OK")
            return True
            
        except Exception as e:
            self.handle_system_error("mt5_validation", e)
            return False
    
    def validate_market_data(self, data: pd.DataFrame, required_columns: list = None) -> bool:
        """
        Valida datos de mercado.
        
        Args:
            data: DataFrame con datos de mercado
            required_columns: Columnas requeridas
            
        Returns:
            bool: True si los datos son válidos
        """
        try:
            # Verificar que sea DataFrame
            if not isinstance(data, pd.DataFrame):
                self._log_error("Los datos no son un DataFrame válido", "VALIDATION")
                return False
            
            # Verificar que no esté vacío
            if data.empty:
                self._log_error("DataFrame de datos está vacío", "VALIDATION")
                return False
            
            # Verificar columnas requeridas
            if required_columns:
                missing_columns = [col for col in required_columns if col not in data.columns]
                if missing_columns:
                    self._log_error(f"Columnas faltantes: {missing_columns}", "VALIDATION")
                    return False
            
            # Verificar valores nulos críticos
            if required_columns:
                for col in required_columns:
                    if data[col].isnull().any():
                        self._log_warning(f"Valores nulos encontrados en columna: {col}")
            
            # Validación exitosa
            self.system_health['data_quality'] = True
            self._log_info(f"Validación de datos: OK ({len(data)} filas)")
            return True
            
        except Exception as e:
            self.handle_data_error("validation", e)
            return False
    
    def validate_system_health(self) -> Dict[str, bool]:
        """
        Realiza un health check completo del sistema.
        
        Returns:
            dict: Estado de cada componente del sistema
        """
        self._log_info("Iniciando validación de salud del sistema...")
        
        # Validar MT5
        mt5_ok = self.validate_mt5_connection()
        
        # Resetear contadores para nueva validación
        health_status = {
            'mt5_connection': mt5_ok,
            'system_responsive': True,
            'error_rate_acceptable': True,
            'overall_status': True
        }
        
        # Verificar tasa de errores
        total_errors = sum(self.error_counts.values())
        if total_errors > 10:  # Umbral de errores
            health_status['error_rate_acceptable'] = False
            self._log_warning(f"Tasa de errores alta: {total_errors} errores totales")
        
        # Estado general
        health_status['overall_status'] = all([
            health_status['mt5_connection'],
            health_status['system_responsive'],
            health_status['error_rate_acceptable']
        ])
        
        # Actualizar estado interno
        self.system_health.update(health_status)
        
        # Log de resultado
        if health_status['overall_status']:
            self._log_info("Health check: Sistema OK")
        else:
            self._log_warning("Health check: Sistema con problemas")
        
        return health_status
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Obtiene resumen de errores del sistema.
        
        Returns:
            dict: Resumen de errores y estado
        """
        return {
            'error_counts': self.error_counts.copy(),
            'system_health': self.system_health.copy(),
            'total_errors': sum(self.error_counts.values()),
            'timestamp': datetime.now().isoformat()
        }
