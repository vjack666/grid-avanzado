"""
LoggerManager simplificado para Trading Grid
"""

class LoggerManager:
    def __init__(self):
        self.console = None
        try:
            from rich.console import Console
            self.console = Console()
            self.has_rich = True
        except ImportError:
            self.has_rich = False
    
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