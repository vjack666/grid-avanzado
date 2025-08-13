"""
🎯 CONFIG MANAGER - TRADING GRID v2.0
====================================

Gestión centralizada de configuración y rutas del sistema.
Elimina redundancia de 4 definiciones duplicadas de directorios.

Autor: GitHub Copilot
Fecha: Agosto 10, 2025
Protocolo: TRADING GRID v2.0
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class ConfigManager:
    """
    Gestión centralizada de configuración para Trading Grid.
    
    Esta clase centraliza todas las rutas y configuraciones que previamente
    estaban duplicadas en main.py, trading_schedule.py y otros archivos.
    """

    def __init__(self):
        """Inicializar ConfigManager con estado de inicialización"""
        # Configuración base - centralizada desde config.py
        self._user_dir = os.path.expanduser("~")
        self._safe_data_dir = os.path.join(self._user_dir, "Documents", "GRID SCALP")
        
        # Estado de inicialización para compatibilidad con AnalyticsManager
        self.is_initialized = True
        
        # Asegurar que los directorios existan
        self.ensure_directories()
    
    def get_safe_data_dir(self) -> str:
        """
        Directorio principal de datos de usuario.
        
        Returns:
            str: Ruta al directorio seguro de datos (ej: C:/Users/usuario/Documents/GRID SCALP)
        """
        return self._safe_data_dir
    
    def get_logs_dir(self) -> str:
        """
        Directorio para archivos de log.
        
        Returns:
            str: Ruta al directorio de logs
        """
        return os.path.join(self._safe_data_dir, "logs")
    
    def get_data_dir(self) -> str:
        """
        Directorio para datos históricos y velas.
        
        Returns:
            str: Ruta al directorio de datos
        """
        return os.path.join(self._safe_data_dir, "data")
    
    def get_backup_dir(self) -> str:
        """
        Directorio para backups del sistema.
        
        Returns:
            str: Ruta al directorio de backups
        """
        return os.path.join(self._safe_data_dir, "backup")
    
    def get_parametros_path(self) -> str:
        """
        Ruta al archivo de parámetros de usuario.
        
        Returns:
            str: Ruta completa al archivo parametros_usuario.json
        """
        return os.path.join(self._safe_data_dir, "parametros_usuario.json")
    
    def get_config_path(self) -> str:
        """
        Ruta al archivo de configuración global del sistema.
        
        Returns:
            str: Ruta completa al archivo config_sistema.json
        """
        return os.path.join(self._safe_data_dir, "config_sistema.json")
    
    def get_modalidad_path(self) -> str:
        """
        Ruta al archivo de modalidad actual.
        
        Returns:
            str: Ruta completa al archivo modalidad_actual.json
        """
        return os.path.join(self._safe_data_dir, "modalidad_actual.json")
    
    def get_log_operaciones_path(self) -> str:
        """
        Ruta al archivo CSV de log de operaciones.
        
        Returns:
            str: Ruta completa al archivo log_operaciones.csv
        """
        return os.path.join(self.get_logs_dir(), "log_operaciones.csv")
    
    def get_all_paths(self) -> dict:
        """
        Diccionario con todas las rutas del sistema.
        
        Returns:
            dict: Diccionario con todas las rutas organizadas por categoría
        """
        return {
            # Directorios principales
            'safe_data_dir': self.get_safe_data_dir(),
            'logs_dir': self.get_logs_dir(),
            'data_dir': self.get_data_dir(),
            'backup_dir': self.get_backup_dir(),
            
            # Archivos de configuración
            'parametros_path': self.get_parametros_path(),
            'config_path': self.get_config_path(),
            'modalidad_path': self.get_modalidad_path(),
            
            # Archivos de logging
            'log_operaciones_path': self.get_log_operaciones_path(),
        }
    
    def ensure_directories(self) -> bool:
        """
        Crea todos los directorios necesarios si no existen.
        
        Returns:
            bool: True si todos los directorios fueron creados/existen, False en caso de error
        """
        try:
            paths = self.get_all_paths()
            
            # Crear directorios principales
            directories = [
                paths['safe_data_dir'],
                paths['logs_dir'], 
                paths['data_dir'],
                paths['backup_dir']
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
            
            # Crear directorios padre para archivos
            file_paths = [
                paths['parametros_path'],
                paths['config_path'],
                paths['modalidad_path'],
                paths['log_operaciones_path']
            ]
            
            for file_path in file_paths:
                parent_dir = os.path.dirname(file_path)
                os.makedirs(parent_dir, exist_ok=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creando directorios: {e}")
            return False
    
    def get_trading_config(self) -> Dict[str, Any]:
        """
        Carga la configuración completa desde trading_config.json
        
        Returns:
            dict: Configuración completa del sistema
        """
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     "config", "trading_config.json")
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Configuración por defecto si no existe el archivo
                return self._get_default_config()
                
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return self._get_default_config()
    
    def get_symbols(self) -> List[str]:
        """Obtiene la lista de símbolos desde configuración"""
        config = self.get_trading_config()
        return config.get('trading', {}).get('default_symbols', ['EURUSD'])
    
    def get_primary_symbol(self) -> str:
        """Obtiene el símbolo principal desde configuración"""
        config = self.get_trading_config()
        return config.get('trading', {}).get('primary_symbol', 'EURUSD')
    
    def get_timeframes(self) -> List[str]:
        """Obtiene la lista de timeframes desde configuración"""
        config = self.get_trading_config()
        return config.get('trading', {}).get('timeframes', ['M5', 'M15', 'H1'])
    
    def get_default_timeframe(self) -> str:
        """Obtiene el timeframe por defecto desde configuración"""
        config = self.get_trading_config()
        return config.get('trading', {}).get('default_timeframe', 'H1')
    
    def get_fvg_config(self) -> Dict[str, Any]:
        """Obtiene la configuración FVG completa"""
        config = self.get_trading_config()
        return config.get('fvg', {})
    
    def get_order_execution_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de ejecución de órdenes"""
        config = self.get_trading_config()
        return config.get('order_execution', {})
    
    def get_alerts_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de alertas"""
        config = self.get_trading_config()
        return config.get('alerts', {})
    
    def get_system_config(self) -> Dict[str, Any]:
        """Obtiene la configuración del sistema"""
        config = self.get_trading_config()
        return config.get('system', {})
    
    def get_sessions_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de sesiones de mercado"""
        config = self.get_trading_config()
        return config.get('sessions', {})
    
    def get_current_session(self) -> str:
        """
        Detecta la sesión actual basada en la hora UTC
        
        Returns:
            str: Nombre de la sesión actual
        """
        from datetime import datetime
        
        now = datetime.utcnow()
        current_hour = now.hour
        
        sessions = self.get_sessions_config()
        
        for session_name, session_info in sessions.items():
            start_hour = int(session_info['start'].split(':')[0])
            end_hour = int(session_info['end'].split(':')[0])
            
            if start_hour <= end_hour:
                # Sesión normal (no cruza medianoche)
                if start_hour <= current_hour < end_hour:
                    return session_name.upper()
            else:
                # Sesión que cruza medianoche
                if current_hour >= start_hour or current_hour < end_hour:
                    return session_name.upper()
        
        return 'UNKNOWN'
    
    def get_market_trend_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de tendencias de mercado"""
        config = self.get_trading_config()
        return config.get('market_trends', {})
    
    def detect_market_trend(self, trend_value: float) -> str:
        """
        Detecta la tendencia del mercado basada en un valor numérico
        
        Args:
            trend_value: Valor numérico de tendencia (-1.0 a 1.0)
            
        Returns:
            str: 'BULLISH', 'BEARISH', o 'NEUTRAL'
        """
        trend_config = self.get_market_trend_config()
        
        bullish_threshold = trend_config.get('bullish_threshold', 0.7)
        bearish_threshold = trend_config.get('bearish_threshold', -0.7)
        
        if trend_value >= bullish_threshold:
            return 'BULLISH'
        elif trend_value <= bearish_threshold:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def is_environment_production(self) -> bool:
        """Verifica si el sistema está en modo producción"""
        config = self.get_system_config()
        return config.get('environment', 'development') == 'production'
    
    def is_debug_mode(self) -> bool:
        """Verifica si el modo debug está activado"""
        config = self.get_system_config()
        return config.get('debug_mode', True)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto si no se encuentra el archivo JSON"""
        return {
            'trading': {
                'default_symbols': ['EURUSD'],
                'primary_symbol': 'EURUSD',
                'timeframes': ['M5', 'M15', 'H1'],
                'default_timeframe': 'H1'
            },
            'system': {
                'environment': 'development',
                'debug_mode': True,
                'version': '2.0.0'
            },
            'fvg': {
                'detection': {
                    'min_gap_size': 0.0001,
                    'max_gap_size': 0.005
                }
            }
        }
    
    def validate_paths() -> dict:
        """
        Valida que todas las rutas sean accesibles.
        
        Returns:
            dict: Diccionario con el estado de validación de cada ruta
        """
        paths = self.get_all_paths()
        validation = {}
        
        for name, path in paths.items():
            try:
                if name.endswith('_dir'):
                    # Validar directorios
                    validation[name] = {
                        'path': path,
                        'exists': os.path.exists(path),
                        'writable': os.access(os.path.dirname(path), os.W_OK) if os.path.exists(os.path.dirname(path)) else False,
                        'type': 'directory'
                    }
                else:
                    # Validar archivos
                    parent_dir = os.path.dirname(path)
                    validation[name] = {
                        'path': path,
                        'exists': os.path.exists(path),
                        'parent_exists': os.path.exists(parent_dir),
                        'parent_writable': os.access(parent_dir, os.W_OK) if os.path.exists(parent_dir) else False,
                        'type': 'file'
                    }
                    
            except Exception as e:
                validation[name] = {
                    'path': path,
                    'error': str(e),
                    'valid': False
                }
        
        return validation
    
    def get_system_info(self) -> dict:
        """
        Información del sistema de configuración.
        
        Returns:
            dict: Información sobre el estado del ConfigManager
        """
        return {
            'version': '1.0',
            'created': '2025-08-10',
            'purpose': 'Centralización de configuración Trading Grid',
            'replaces': [
                'main.py - definiciones locales de safe_data_dir',
                'trading_schedule.py - definiciones locales de safe_data_dir', 
                'Múltiples definiciones de user_dir'
            ],
            'total_paths': len(self.get_all_paths()),
            'directories_managed': 4,
            'files_managed': 4
        }


# 🧪 Auto-test del ConfigManager
if __name__ == "__main__":
    print("🧪 Testing ConfigManager...")
    
    # Test 1: Obtener rutas
    paths = self.get_all_paths()
    print(f"✅ {len(paths)} rutas configuradas")
    
    # Test 2: Crear directorios
    success = ConfigManager.ensure_directories()
    print(f"✅ Directorios creados: {success}")
    
    # Test 3: Validar rutas
    validation = ConfigManager.validate_paths()
    valid_count = sum(1 for v in validation.values() if v.get('exists', False) or v.get('parent_exists', False))
    print(f"✅ Rutas válidas: {valid_count}/{len(validation)}")
    
    # Test 4: Info del sistema
    info = self.get_system_info()
    print(f"✅ ConfigManager v{info['version']} operativo")
    
    print("🎉 ConfigManager testing completado!")
