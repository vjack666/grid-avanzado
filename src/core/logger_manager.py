"""
LoggerManager simplificado para Trading Grid
"""
import logging
from typing import Optional

class LoggerManager:
    def __init__(self):
        self.console = None
        try:
            from rich.console import Console
            self.console = Console()
            self.has_rich = True
        except ImportError:
            self.has_rich = False
        
        # Configurar logging básico
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """Obtener logger estándar de Python"""
        return logging.getLogger(name)
    
    def log_info(self, mensaje):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if self.has_rich and self.console:
            try:
                self.console.print(f"[{timestamp}] [cyan]INFO: {mensaje}[/cyan]")
            except:
                print(f"[{timestamp}] INFO: {mensaje}")
        else:
            print(f"[{timestamp}] INFO: {mensaje}")
    
    def log_success(self, mensaje):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if self.has_rich and self.console:
            try:
                self.console.print(f"[{timestamp}] [green]SUCCESS: {mensaje}[/green]")
            except:
                print(f"[{timestamp}] SUCCESS: {mensaje}")
        else:
            print(f"[{timestamp}] SUCCESS: {mensaje}")
    
    def log_error(self, mensaje):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if self.has_rich and self.console:
            try:
                self.console.print(f"[{timestamp}] [red]ERROR: {mensaje}[/red]")
            except:
                print(f"[{timestamp}] ERROR: {mensaje}")
        else:
            print(f"[{timestamp}] ERROR: {mensaje}")
    
    def log_warning(self, mensaje):
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if self.has_rich and self.console:
            try:
                self.console.print(f"[{timestamp}] [yellow]WARNING: {mensaje}[/yellow]")
            except:
                print(f"[{timestamp}] WARNING: {mensaje}")
        else:
            print(f"[{timestamp}] WARNING: {mensaje}")