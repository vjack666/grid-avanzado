"""
FUNDEDNEXT MT5 TERMINAL MANAGER - SÓTANO 1
=========================================
Gestor exclusivo para FundedNext MT5 Terminal - Infraestructura Base

PUERTA: PUERTA-S1-FUNDEDNEXT
VERSIÓN: v1.0.0
FECHA: 2025-08-11
SÓTANO: 1 - Infraestructura Base
"""

import os
import sys
import subprocess
import psutil
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import MetaTrader5 as mt5

# Imports del sistema SÓTANO 1
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.core.config_manager import ConfigManager
from src.core.logger_manager import LoggerManager
from src.core.error_manager import ErrorManager


class FundedNextMT5Manager:
    """
    Gestor exclusivo para FundedNext MT5 Terminal
    
    Funcionalidades:
    - Detección inteligente de terminal abierto/cerrado
    - Apertura automática solo cuando es necesario
    - Manejo exclusivo de FundedNext MT5
    - Cierre de otros terminales MT5 si es necesario
    - Gestión robusta de procesos
    """
    
    def __init__(self, 
                 config: ConfigManager,
                 logger: LoggerManager, 
                 error: ErrorManager):
        """
        Inicializar FundedNextMT5Manager
        
        Args:
            config: ConfigManager para configuración
            logger: LoggerManager para logging
            error: ErrorManager para manejo de errores
        """
        # Metadatos del componente
        self.component_id = "PUERTA-S1-FUNDEDNEXT"
        self.version = "v1.0.0"
        self.status = "initializing"
        
        # Dependencias core
        self.config = config
        self.logger = logger
        self.error = error
        
        # Configuración específica de FundedNext MT5
        self.fundednext_config = self._initialize_fundednext_config()
        
        # Estado del manager
        self.is_connected = False
        self.terminal_process_id = None
        self.account_info = None
        self.last_health_check = None
        
        # Métricas del manager
        self.manager_metrics = {
            "connection_attempts": 0,
            "successful_connections": 0,
            "terminal_restarts": 0,
            "other_terminals_closed": 0,
            "health_checks": 0,
            "uptime_seconds": 0,
            "last_connection_time": None
        }
        
        # Inicializar
        self._initialize_manager()
        
        self.logger.log_info(f"{self.component_id} {self.version} inicializado correctamente")
        self.status = "initialized"
    
    def _initialize_fundednext_config(self) -> Dict[str, Any]:
        """Inicializar configuración específica de FundedNext"""
        try:
            return {
                # Ruta exclusiva del terminal FundedNext
                "terminal_path": r"C:\Program Files\FundedNext MT5 Terminal\terminal64.exe",
                "terminal_name": "FundedNext MT5 Terminal",
                "process_name": "terminal64.exe",
                
                # Configuración de comportamiento
                "exclusive_mode": True,  # Solo FundedNext MT5 permitido
                "auto_open_if_closed": True,  # Abrir automáticamente si está cerrado
                "close_other_terminals": True,  # Cerrar otros terminales MT5
                "smart_detection": True,  # Detección inteligente de estado
                
                # Timeouts y reintentos
                "startup_timeout": 30,  # segundos para arranque
                "connection_timeout": 10,  # segundos para conexión
                "health_check_interval": 60,  # segundos entre checks
                "max_connection_attempts": 3,
                
                # Configuración de proceso
                "startup_arguments": [],  # Argumentos adicionales al abrir
                "working_directory": r"C:\Program Files\FundedNext MT5 Terminal",
                "run_as_admin": False,
                
                # Configuración de monitoreo
                "monitor_cpu_usage": True,
                "monitor_memory_usage": True,
                "cpu_threshold_percent": 80.0,
                "memory_threshold_mb": 512.0
            }
            
        except Exception as e:
            self.error._log_error(f"Error inicializando configuración FundedNext: {e}")
            return self._get_default_fundednext_config()
    
    def _get_default_fundednext_config(self) -> Dict[str, Any]:
        """Configuración por defecto de FundedNext"""
        return {
            "terminal_path": r"C:\Program Files\FundedNext MT5 Terminal\terminal64.exe",
            "terminal_name": "FundedNext MT5 Terminal",
            "process_name": "terminal64.exe",
            "exclusive_mode": True,
            "auto_open_if_closed": True,
            "close_other_terminals": False,  # Más conservador por defecto
            "startup_timeout": 15,
            "connection_timeout": 5,
            "max_connection_attempts": 2
        }
    
    def _initialize_manager(self) -> None:
        """Inicializar componentes del manager"""
        try:
            # Verificar que el ejecutable existe
            terminal_path = self.fundednext_config["terminal_path"]
            if not os.path.exists(terminal_path):
                raise FileNotFoundError(f"FundedNext MT5 Terminal no encontrado en: {terminal_path}")
            
            # Verificar permisos
            if not os.access(terminal_path, os.R_OK):
                raise PermissionError(f"Sin permisos para ejecutar: {terminal_path}")
            
            self.logger.log_info("FundedNext MT5 Terminal encontrado y accesible")
            
        except Exception as e:
            self.error._log_error(f"Error inicializando FundedNext manager: {e}")
            raise
    
    def is_fundednext_terminal_running(self) -> Tuple[bool, Optional[int]]:
        """
        Verificar si FundedNext MT5 Terminal está ejecutándose
        
        Returns:
            Tuple[bool, Optional[int]]: (está_ejecutándose, process_id)
        """
        try:
            terminal_path = self.fundednext_config["terminal_path"]
            process_name = self.fundednext_config["process_name"]
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_info = proc.info
                    
                    # Verificar por nombre de proceso
                    if proc_info['name'] and process_name.lower() in proc_info['name'].lower():
                        # Verificar por ruta del ejecutable
                        if proc_info['exe'] and terminal_path.lower() in proc_info['exe'].lower():
                            self.logger.log_info(f"FundedNext MT5 Terminal encontrado: PID {proc_info['pid']}")
                            return True, proc_info['pid']
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return False, None
            
        except Exception as e:
            self.error._log_error(f"Error verificando FundedNext MT5 Terminal: {e}")
            return False, None
    
    def get_other_mt5_terminals(self) -> List[Dict[str, Any]]:
        """
        Obtener lista de otros terminales MT5 ejecutándose
        
        Returns:
            List[Dict]: Lista de otros procesos MT5
        """
        try:
            other_terminals = []
            terminal_path = self.fundednext_config["terminal_path"]
            
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_info = proc.info
                    
                    # Buscar procesos que contengan "terminal" o "mt5"
                    if proc_info['name']:
                        name_lower = proc_info['name'].lower()
                        if ('terminal' in name_lower or 'mt5' in name_lower) and 'terminal64.exe' in name_lower:
                            # Verificar que NO sea FundedNext
                            if proc_info['exe'] and terminal_path.lower() not in proc_info['exe'].lower():
                                other_terminals.append({
                                    'pid': proc_info['pid'],
                                    'name': proc_info['name'],
                                    'exe': proc_info['exe'],
                                    'cmdline': proc_info['cmdline']
                                })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return other_terminals
            
        except Exception as e:
            self.error._log_error(f"Error obteniendo otros terminales MT5: {e}")
            return []
    
    def close_other_mt5_terminals(self) -> int:
        """
        Cerrar otros terminales MT5 que no sean FundedNext
        
        Returns:
            int: Número de terminales cerrados
        """
        try:
            if not self.fundednext_config["close_other_terminals"]:
                self.logger.log_info("Cierre de otros terminales MT5 deshabilitado")
                return 0
            
            other_terminals = self.get_other_mt5_terminals()
            closed_count = 0
            
            for terminal in other_terminals:
                try:
                    proc = psutil.Process(terminal['pid'])
                    proc.terminate()
                    
                    # Esperar a que termine
                    try:
                        proc.wait(timeout=5)
                        closed_count += 1
                        self.logger.log_info(f"Terminal MT5 cerrado: {terminal['name']} (PID: {terminal['pid']})")
                    except psutil.TimeoutExpired:
                        # Forzar cierre si no responde
                        proc.kill()
                        closed_count += 1
                        self.logger.log_warning(f"Terminal MT5 forzado a cerrar: {terminal['name']} (PID: {terminal['pid']})")
                
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.log_warning(f"No se pudo cerrar terminal {terminal['pid']}: {e}")
                    continue
            
            if closed_count > 0:
                self.manager_metrics["other_terminals_closed"] += closed_count
                self.logger.log_success(f"Se cerraron {closed_count} terminales MT5 adicionales")
            
            return closed_count
            
        except Exception as e:
            self.error._log_error(f"Error cerrando otros terminales MT5: {e}")
            return 0
    
    def start_fundednext_terminal(self) -> bool:
        """
        Iniciar FundedNext MT5 Terminal
        
        Returns:
            bool: True si se inició correctamente
        """
        try:
            terminal_path = self.fundednext_config["terminal_path"]
            working_dir = self.fundednext_config["working_directory"]
            startup_args = self.fundednext_config["startup_arguments"]
            
            self.logger.log_info(f"Iniciando FundedNext MT5 Terminal: {terminal_path}")
            
            # Preparar comando
            cmd = [terminal_path] + startup_args
            
            # Iniciar proceso
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            self.terminal_process_id = process.pid
            self.logger.log_info(f"FundedNext MT5 Terminal iniciado con PID: {process.pid}")
            
            # Esperar a que el terminal esté listo
            startup_timeout = self.fundednext_config["startup_timeout"]
            start_time = time.time()
            
            while time.time() - start_time < startup_timeout:
                is_running, pid = self.is_fundednext_terminal_running()
                if is_running:
                    self.logger.log_success("FundedNext MT5 Terminal iniciado correctamente")
                    self.manager_metrics["terminal_restarts"] += 1
                    return True
                
                time.sleep(1)
            
            self.logger.log_error("Timeout esperando inicio de FundedNext MT5 Terminal")
            return False
            
        except Exception as e:
            self.error._log_error(f"Error iniciando FundedNext MT5 Terminal: {e}")
            return False
    
    def ensure_fundednext_terminal(self) -> bool:
        """
        Asegurar que FundedNext MT5 Terminal esté ejecutándose
        
        Lógica inteligente:
        1. Verificar si FundedNext MT5 está ejecutándose
        2. Si está ejecutándose, no hacer nada
        3. Si no está ejecutándose, cerrar otros terminales MT5 y abrir FundedNext
        
        Returns:
            bool: True si FundedNext MT5 está disponible
        """
        try:
            self.logger.log_info("🔍 Verificando estado de FundedNext MT5 Terminal...")
            
            # 1. Verificar si FundedNext MT5 está ejecutándose
            is_running, pid = self.is_fundednext_terminal_running()
            
            if is_running:
                self.logger.log_success(f"✅ FundedNext MT5 Terminal ya está ejecutándose (PID: {pid})")
                self.terminal_process_id = pid
                return True
            
            # 2. FundedNext no está ejecutándose
            self.logger.log_info("📋 FundedNext MT5 Terminal no está ejecutándose")
            
            # 3. Verificar si hay otros terminales MT5 ejecutándose
            other_terminals = self.get_other_mt5_terminals()
            if other_terminals:
                self.logger.log_info(f"🔄 Encontrados {len(other_terminals)} otros terminales MT5")
                
                # Cerrar otros terminales si está configurado
                if self.fundednext_config["close_other_terminals"]:
                    closed_count = self.close_other_mt5_terminals()
                    if closed_count > 0:
                        time.sleep(2)  # Esperar a que se liberen recursos
            
            # 4. Abrir FundedNext MT5 Terminal si está configurado
            if self.fundednext_config["auto_open_if_closed"]:
                self.logger.log_info("🚀 Iniciando FundedNext MT5 Terminal...")
                return self.start_fundednext_terminal()
            else:
                self.logger.log_warning("⚠️ Auto-apertura deshabilitada. FundedNext MT5 Terminal debe ser abierto manualmente")
                return False
            
        except Exception as e:
            self.error._log_error(f"Error asegurando FundedNext MT5 Terminal: {e}")
            return False
    
    def connect_to_mt5(self) -> bool:
        """
        Conectar a MT5 asegurando que sea FundedNext Terminal
        
        Returns:
            bool: True si conexión exitosa
        """
        try:
            self.manager_metrics["connection_attempts"] += 1
            
            # 1. Asegurar que FundedNext MT5 Terminal esté ejecutándose
            if not self.ensure_fundednext_terminal():
                self.logger.log_error("❌ No se pudo asegurar FundedNext MT5 Terminal")
                return False
            
            # 2. Esperar un momento para que el terminal esté listo
            time.sleep(2)
            
            # 3. Intentar conectar a MT5
            self.logger.log_info("🔌 Conectando a FundedNext MT5...")
            
            if not mt5.initialize():
                error_code = mt5.last_error()
                self.logger.log_error(f"❌ Error inicializando MT5: {error_code}")
                return False
            
            # 4. Verificar información de cuenta
            account_info = mt5.account_info()
            if account_info is None:
                error_code = mt5.last_error()
                self.logger.log_error(f"❌ Error obteniendo info de cuenta: {error_code}")
                mt5.shutdown()
                return False
            
            # 5. Guardar información de conexión
            self.account_info = account_info._asdict()
            self.is_connected = True
            self.last_health_check = datetime.now()
            self.manager_metrics["successful_connections"] += 1
            self.manager_metrics["last_connection_time"] = datetime.now()
            
            self.logger.log_success(f"✅ Conectado a FundedNext MT5 - Cuenta: {account_info.login}")
            return True
            
        except Exception as e:
            self.error._log_error(f"Error conectando a FundedNext MT5: {e}")
            return False
    
    def disconnect_from_mt5(self) -> bool:
        """
        Desconectar de MT5
        
        Returns:
            bool: True si desconexión exitosa
        """
        try:
            if self.is_connected:
                mt5.shutdown()
                self.is_connected = False
                self.account_info = None
                self.logger.log_info("🔌 Desconectado de FundedNext MT5")
            
            return True
            
        except Exception as e:
            self.error._log_error(f"Error desconectando de MT5: {e}")
            return False
    
    def get_manager_status(self) -> Dict[str, Any]:
        """
        Obtener estado completo del manager
        
        Returns:
            Dict con estado del manager
        """
        try:
            is_running, pid = self.is_fundednext_terminal_running()
            other_terminals = self.get_other_mt5_terminals()
            
            return {
                "component_id": self.component_id,
                "version": self.version,
                "status": self.status,
                "is_connected": self.is_connected,
                "terminal_status": {
                    "is_running": is_running,
                    "process_id": pid,
                    "terminal_path": self.fundednext_config["terminal_path"]
                },
                "account_info": self.account_info,
                "other_terminals": {
                    "count": len(other_terminals),
                    "terminals": other_terminals
                },
                "configuration": self.fundednext_config.copy(),
                "metrics": self.manager_metrics.copy(),
                "last_health_check": self.last_health_check
            }
            
        except Exception as e:
            self.error._log_error(f"Error obteniendo estado del manager: {e}")
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Realizar check de salud del sistema
        
        Returns:
            Dict con resultados del check
        """
        try:
            self.manager_metrics["health_checks"] += 1
            
            # Verificar terminal
            is_running, pid = self.is_fundednext_terminal_running()
            
            # Verificar conexión MT5
            mt5_connected = self.is_connected and mt5.terminal_info() is not None
            
            # Verificar otros terminales
            other_terminals = self.get_other_mt5_terminals()
            
            health_status = {
                "timestamp": datetime.now(),
                "overall_health": is_running and mt5_connected,
                "terminal_running": is_running,
                "mt5_connected": mt5_connected,
                "process_id": pid,
                "other_terminals_count": len(other_terminals),
                "exclusive_mode": len(other_terminals) == 0,
                "configuration_valid": os.path.exists(self.fundednext_config["terminal_path"])
            }
            
            self.last_health_check = datetime.now()
            return health_status
            
        except Exception as e:
            self.error._log_error(f"Error en health check: {e}")
            return {"error": str(e), "overall_health": False}
