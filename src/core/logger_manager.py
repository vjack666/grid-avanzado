"""
🗃️ LOGGER MANAGER - SISTEMA CAJA NEGRA TRADING GRID
==================================================

Sistema avanzado de logging que funciona como "caja negra" del sistema,
organizando automáticamente todos los logs en categorías específicas.

ESTRUCTURA DE CAJA NEGRA:
- logs/system/          - Logs del sistema principal
- logs/trading/         - Logs de operaciones de trading  
- logs/analytics/       - Logs de análisis y detección
- logs/mt5/            - Logs de conexión MT5
- logs/errors/         - Logs de errores críticos
- logs/performance/    - Logs de rendimiento
- logs/fvg/           - Logs de detección FVG
- logs/signals/       - Logs de señales generadas
- logs/archive/       - Logs archivados por fecha

Autor: GitHub Copilot
Fecha: Agosto 12, 2025
"""

import os
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

class LogCategory(Enum):
    """Categorías de logs para la caja negra"""
    SYSTEM = "system"
    TRADING = "trading"
    ANALYTICS = "analytics"
    MT5 = "mt5"
    ERRORS = "errors"
    PERFORMANCE = "performance"
    FVG = "fvg"
    SIGNALS = "signals"
    STRATEGY = "strategy"
    SECURITY = "security"

class LogLevel(Enum):
    """Niveles de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class BlackBoxLogger:
    """Sistema de logging caja negra avanzado"""
    
    def __init__(self, base_path: str = None):
        """
        Inicializar sistema de caja negra
        
        Args:
            base_path: Ruta base para logs (por defecto: proyecto/logs)
        """
        # Configurar rutas
        if base_path is None:
            # Detectar automáticamente la ruta del proyecto
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            base_path = project_root / "logs"
        
        self.base_path = Path(base_path)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Crear estructura de directorios
        self._setup_directory_structure()
        
        # Configurar Rich console si está disponible
        self.console = None
        self.has_rich = False
        try:
            from rich.console import Console
            self.console = Console()
            self.has_rich = True
        except ImportError:
            pass
        
        # Configurar loggers por categoría
        self.loggers = {}
        self._setup_category_loggers()
        
        # Metadatos de sesión
        self.session_metadata = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "system": "Trading Grid",
            "version": "2.0",
            "logs_created": 0,
            "categories_used": set()
        }
        
        # Log de inicio de sesión
        self.log_system(LogLevel.INFO, "🗃️ Sistema Caja Negra inicializado", {
            "session_id": self.session_id,
            "log_path": str(self.base_path)
        })
    
    def _setup_directory_structure(self):
        """Crear estructura completa de directorios para caja negra"""
        directories = [
            "system",
            "trading", 
            "analytics",
            "mt5",
            "errors",
            "performance", 
            "fvg",
            "signals",
            "strategy",
            "security",
            "archive",
            "daily"
        ]
        
        for directory in directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _setup_category_loggers(self):
        """Configurar loggers específicos por categoría"""
        # Usar fecha del día en lugar de session_id para archivos únicos por día
        date_stamp = datetime.now().strftime("%Y%m%d")
        
        for category in LogCategory:
            logger = logging.getLogger(f"BlackBox.{category.value}")
            logger.setLevel(logging.DEBUG)
            
            # Handler para archivo - UN ARCHIVO POR DÍA, NO POR SESIÓN
            file_path = self.base_path / category.value / f"{category.value}_{date_stamp}.log"
            
            # Si el logger ya existe, no agregar handlers duplicados
            if not logger.handlers:
                file_handler = logging.FileHandler(file_path, encoding='utf-8', mode='a')  # Append mode
                
                # Formato detallado para archivos
                formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            
            self.loggers[category] = logger
    
    def _log_to_file(self, category: LogCategory, level: LogLevel, message: str, metadata: Dict[str, Any] = None):
        """Escribir log a archivo con metadatos"""
        logger = self.loggers.get(category)
        if not logger:
            return
        
        # Crear entrada de log estructurada
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "category": category.value,
            "level": level.value,
            "message": message,
            "metadata": metadata or {}
        }
        
        # Escribir como JSON en línea separada para fácil parsing
        json_line = json.dumps(log_entry, ensure_ascii=False)
        
        # Usar el nivel de logging apropiado
        if level == LogLevel.DEBUG:
            logger.debug(json_line)
        elif level == LogLevel.INFO:
            logger.info(json_line)
        elif level == LogLevel.SUCCESS:
            logger.info(json_line)  # SUCCESS como INFO en archivo
        elif level == LogLevel.WARNING:
            logger.warning(json_line)
        elif level == LogLevel.ERROR:
            logger.error(json_line)
        elif level == LogLevel.CRITICAL:
            logger.critical(json_line)
        
        # Actualizar metadatos de sesión
        self.session_metadata["logs_created"] += 1
        self.session_metadata["categories_used"].add(category.value)
    
    def _display_console(self, level: LogLevel, message: str):
        """Mostrar mensaje en consola con formato Rich"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if self.has_rich and self.console:
            try:
                if level == LogLevel.INFO:
                    self.console.print(f"[{timestamp}] [cyan]INFO: {message}[/cyan]")
                elif level == LogLevel.SUCCESS:
                    self.console.print(f"[{timestamp}] [green]SUCCESS: {message}[/green]")
                elif level == LogLevel.WARNING:
                    self.console.print(f"[{timestamp}] [yellow]WARNING: {message}[/yellow]")
                elif level == LogLevel.ERROR:
                    self.console.print(f"[{timestamp}] [red]ERROR: {message}[/red]")
                elif level == LogLevel.CRITICAL:
                    self.console.print(f"[{timestamp}] [bold red]CRITICAL: {message}[/bold red]")
                else:
                    self.console.print(f"[{timestamp}] {level.value}: {message}")
            except:
                print(f"[{timestamp}] {level.value}: {message}")
        else:
            print(f"[{timestamp}] {level.value}: {message}")
    
    # === MÉTODOS PÚBLICOS DE LOGGING ===
    
    def log_system(self, level: LogLevel, message: str, metadata: Dict[str, Any] = None):
        """Log del sistema principal"""
        self._log_to_file(LogCategory.SYSTEM, level, message, metadata)
        self._display_console(level, message)
    
    def log_trading(self, level: LogLevel, message: str, metadata: Dict[str, Any] = None):
        """Log de operaciones de trading"""
        self._log_to_file(LogCategory.TRADING, level, message, metadata)
        self._display_console(level, message)
    
    def log_analytics(self, level: LogLevel, message: str, metadata: Dict[str, Any] = None):
        """Log de análisis y detección"""
        self._log_to_file(LogCategory.ANALYTICS, level, message, metadata)
        self._display_console(level, message)
    
    def log_mt5(self, level: LogLevel, message: str, metadata: Dict[str, Any] = None):
        """Log de conexión MT5"""
        self._log_to_file(LogCategory.MT5, level, message, metadata)
        self._display_console(level, message)
    
    def log_error(self, message: str, metadata: Dict[str, Any] = None):
        """Log de errores (shorthand)"""
        self._log_to_file(LogCategory.ERRORS, LogLevel.ERROR, message, metadata)
        self._display_console(LogLevel.ERROR, message)
    
    def log_fvg(self, level: LogLevel, message: str, metadata: Dict[str, Any] = None):
        """Log de detección FVG"""
        self._log_to_file(LogCategory.FVG, level, message, metadata)
        if level in [LogLevel.WARNING, LogLevel.ERROR]:
            self._display_console(level, message)
    
    def log_signal(self, level: LogLevel, message: str, metadata: Dict[str, Any] = None):
        """Log de señales generadas"""
        self._log_to_file(LogCategory.SIGNALS, level, message, metadata)
        self._display_console(level, message)
    
    def log_performance(self, level: LogLevel, message: str, metadata: Dict[str, Any] = None):
        """Log de rendimiento"""
        self._log_to_file(LogCategory.PERFORMANCE, level, message, metadata)
        # Solo mostrar en consola si es WARNING o ERROR
        if level in [LogLevel.WARNING, LogLevel.ERROR]:
            self._display_console(level, message)
    
    def log_strategy(self, level: LogLevel, message: str, metadata: Dict[str, Any] = None):
        """Log de estrategias"""
        self._log_to_file(LogCategory.STRATEGY, level, message, metadata)
        self._display_console(level, message)
    
    # === MÉTODOS DE COMPATIBILIDAD ===
    
    def log_info(self, message: str, metadata: Dict[str, Any] = None):
        """Compatibilidad: log info"""
        self.log_system(LogLevel.INFO, message, metadata)
    
    def log_success(self, message: str, metadata: Dict[str, Any] = None):
        """Compatibilidad: log success"""
        self.log_system(LogLevel.SUCCESS, message, metadata)
    
    def log_warning(self, message: str, metadata: Dict[str, Any] = None):
        """Compatibilidad: log warning"""
        self.log_system(LogLevel.WARNING, message, metadata)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Compatibilidad: obtener logger estándar"""
        return logging.getLogger(name)
    
    # === MÉTODOS DE GESTIÓN ===
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la sesión actual"""
        return {
            **self.session_metadata,
            "categories_used": list(self.session_metadata["categories_used"]),
            "uptime": str(datetime.now() - datetime.fromisoformat(self.session_metadata["start_time"]))
        }
    
    def archive_old_logs(self, days_old: int = 7):
        """Archivar logs antiguos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            archive_path = self.base_path / "archive" / cutoff_date.strftime("%Y-%m")
            archive_path.mkdir(parents=True, exist_ok=True)
            
            # Implementar lógica de archivado aquí
            self.log_system(LogLevel.INFO, f"Archivado de logs > {days_old} días iniciado")
            
        except Exception as e:
            self.log_error(f"Error archivando logs: {e}")
    
    def emergency_log(self, message: str, metadata: Dict[str, Any] = None):
        """Log de emergencia - siempre se escribe"""
        emergency_file = self.base_path / "emergency.log"
        timestamp = datetime.now().isoformat()
        
        with open(emergency_file, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | EMERGENCY | {message}\n")
            if metadata:
                f.write(f"{timestamp} | METADATA | {json.dumps(metadata)}\n")
        
        print(f"[EMERGENCY] {message}")


# Clase de compatibilidad
class LoggerManager(BlackBoxLogger):
    """
    Clase de compatibilidad que extiende BlackBoxLogger
    para mantener la interfaz existente
    """
    
    def __init__(self):
        super().__init__()
        self.log_system(LogLevel.INFO, "🔄 LoggerManager (Caja Negra) inicializado")