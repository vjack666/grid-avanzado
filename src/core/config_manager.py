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

class ConfigManager:
    """
    Gestión centralizada de configuración para Trading Grid.
    
    Esta clase centraliza todas las rutas y configuraciones que previamente
    estaban duplicadas en main.py, trading_schedule.py y otros archivos.
    """
    
    # Configuración base - centralizada desde config.py
    _user_dir = os.path.expanduser("~")
    _safe_data_dir = os.path.join(_user_dir, "Documents", "GRID SCALP")
    
    @staticmethod
    def get_safe_data_dir() -> str:
        """
        Directorio principal de datos de usuario.
        
        Returns:
            str: Ruta al directorio seguro de datos (ej: C:/Users/usuario/Documents/GRID SCALP)
        """
        return ConfigManager._safe_data_dir
    
    @staticmethod
    def get_logs_dir() -> str:
        """
        Directorio para archivos de log.
        
        Returns:
            str: Ruta al directorio de logs
        """
        return os.path.join(ConfigManager._safe_data_dir, "logs")
    
    @staticmethod
    def get_data_dir() -> str:
        """
        Directorio para datos históricos y velas.
        
        Returns:
            str: Ruta al directorio de datos
        """
        return os.path.join(ConfigManager._safe_data_dir, "data")
    
    @staticmethod
    def get_backup_dir() -> str:
        """
        Directorio para backups del sistema.
        
        Returns:
            str: Ruta al directorio de backups
        """
        return os.path.join(ConfigManager._safe_data_dir, "backup")
    
    @staticmethod
    def get_parametros_path() -> str:
        """
        Ruta al archivo de parámetros de usuario.
        
        Returns:
            str: Ruta completa al archivo parametros_usuario.json
        """
        return os.path.join(ConfigManager._safe_data_dir, "parametros_usuario.json")
    
    @staticmethod
    def get_config_path() -> str:
        """
        Ruta al archivo de configuración global del sistema.
        
        Returns:
            str: Ruta completa al archivo config_sistema.json
        """
        return os.path.join(ConfigManager._safe_data_dir, "config_sistema.json")
    
    @staticmethod
    def get_modalidad_path() -> str:
        """
        Ruta al archivo de modalidad actual.
        
        Returns:
            str: Ruta completa al archivo modalidad_actual.json
        """
        return os.path.join(ConfigManager._safe_data_dir, "modalidad_actual.json")
    
    @staticmethod
    def get_log_operaciones_path() -> str:
        """
        Ruta al archivo CSV de log de operaciones.
        
        Returns:
            str: Ruta completa al archivo log_operaciones.csv
        """
        return os.path.join(ConfigManager.get_logs_dir(), "log_operaciones.csv")
    
    @staticmethod
    def get_all_paths() -> dict:
        """
        Diccionario con todas las rutas del sistema.
        
        Returns:
            dict: Diccionario con todas las rutas organizadas por categoría
        """
        return {
            # Directorios principales
            'safe_data_dir': ConfigManager.get_safe_data_dir(),
            'logs_dir': ConfigManager.get_logs_dir(),
            'data_dir': ConfigManager.get_data_dir(),
            'backup_dir': ConfigManager.get_backup_dir(),
            
            # Archivos de configuración
            'parametros_path': ConfigManager.get_parametros_path(),
            'config_path': ConfigManager.get_config_path(),
            'modalidad_path': ConfigManager.get_modalidad_path(),
            
            # Archivos de logging
            'log_operaciones_path': ConfigManager.get_log_operaciones_path(),
        }
    
    @staticmethod
    def ensure_directories() -> bool:
        """
        Crea todos los directorios necesarios si no existen.
        
        Returns:
            bool: True si todos los directorios fueron creados/existen, False en caso de error
        """
        try:
            paths = ConfigManager.get_all_paths()
            
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
    
    @staticmethod
    def validate_paths() -> dict:
        """
        Valida que todas las rutas sean accesibles.
        
        Returns:
            dict: Diccionario con el estado de validación de cada ruta
        """
        paths = ConfigManager.get_all_paths()
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
    
    @staticmethod
    def get_system_info() -> dict:
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
            'total_paths': len(ConfigManager.get_all_paths()),
            'directories_managed': 4,
            'files_managed': 4
        }


# 🧪 Auto-test del ConfigManager
if __name__ == "__main__":
    print("🧪 Testing ConfigManager...")
    
    # Test 1: Obtener rutas
    paths = ConfigManager.get_all_paths()
    print(f"✅ {len(paths)} rutas configuradas")
    
    # Test 2: Crear directorios
    success = ConfigManager.ensure_directories()
    print(f"✅ Directorios creados: {success}")
    
    # Test 3: Validar rutas
    validation = ConfigManager.validate_paths()
    valid_count = sum(1 for v in validation.values() if v.get('exists', False) or v.get('parent_exists', False))
    print(f"✅ Rutas válidas: {valid_count}/{len(validation)}")
    
    # Test 4: Info del sistema
    info = ConfigManager.get_system_info()
    print(f"✅ ConfigManager v{info['version']} operativo")
    
    print("🎉 ConfigManager testing completado!")
