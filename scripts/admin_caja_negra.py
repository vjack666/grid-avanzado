"""
🗃️ ADMINISTRADOR DE CAJA NEGRA - TRADING GRID
===============================================

Script para administrar, analizar y mantener los logs del sistema 
de caja negra del Trading Grid.

FUNCIONALIDADES:
- 📊 Análisis de logs por categoría
- 🧹 Limpieza y archivado automático
- 📈 Estadísticas de sesiones
- 🔍 Búsqueda y filtrado de logs
- 📋 Resúmenes por período

Autor: GitHub Copilot
Fecha: Agosto 12, 2025
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional

# Rich para interfaz bonita
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.progress import track
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

class BlackBoxAdmin:
    """Administrador de la caja negra del Trading Grid"""
    
    def __init__(self, logs_path: str = None):
        """Inicializar administrador"""
        if logs_path is None:
            # Detectar automáticamente la ruta de logs
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            logs_path = project_root / "logs"
        
        self.logs_path = Path(logs_path)
        self.categories = [
            "system", "trading", "analytics", "mt5", "errors", 
            "performance", "fvg", "signals", "strategy", "security"
        ]
        
        if HAS_RICH:
            self.console = console
        else:
            self.console = None
    
    def print_info(self, message: str):
        """Imprimir mensaje de info"""
        if self.console:
            self.console.print(f"[cyan]ℹ️  {message}[/cyan]")
        else:
            print(f"ℹ️  {message}")
    
    def print_success(self, message: str):
        """Imprimir mensaje de éxito"""
        if self.console:
            self.console.print(f"[green]✅ {message}[/green]")
        else:
            print(f"✅ {message}")
    
    def print_warning(self, message: str):
        """Imprimir mensaje de warning"""
        if self.console:
            self.console.print(f"[yellow]⚠️  {message}[/yellow]")
        else:
            print(f"⚠️  {message}")
    
    def print_error(self, message: str):
        """Imprimir mensaje de error"""
        if self.console:
            self.console.print(f"[red]❌ {message}[/red]")
        else:
            print(f"❌ {message}")
    
    def analyze_log_structure(self) -> Dict[str, Any]:
        """Analizar estructura completa de logs"""
        structure = {
            "total_categories": 0,
            "total_files": 0,
            "total_sessions": set(),
            "categories": {},
            "file_sizes": {},
            "date_range": {"oldest": None, "newest": None}
        }
        
        if not self.logs_path.exists():
            return structure
        
        for category in self.categories:
            category_path = self.logs_path / category
            if category_path.exists():
                files = list(category_path.glob("*.log"))
                structure["categories"][category] = {
                    "files": len(files),
                    "sessions": [],
                    "total_size": 0
                }
                
                for file_path in files:
                    # Extraer session_id del nombre del archivo
                    filename = file_path.name
                    if "_" in filename:
                        session_id = filename.split("_", 1)[1].replace(".log", "")
                        structure["total_sessions"].add(session_id)
                        structure["categories"][category]["sessions"].append(session_id)
                    
                    # Tamaño del archivo
                    size = file_path.stat().st_size
                    structure["categories"][category]["total_size"] += size
                    structure["file_sizes"][str(file_path)] = size
                    
                    # Fechas
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if structure["date_range"]["oldest"] is None or mod_time < structure["date_range"]["oldest"]:
                        structure["date_range"]["oldest"] = mod_time
                    if structure["date_range"]["newest"] is None or mod_time > structure["date_range"]["newest"]:
                        structure["date_range"]["newest"] = mod_time
                
                structure["total_files"] += len(files)
                if len(files) > 0:
                    structure["total_categories"] += 1
        
        structure["total_sessions"] = len(structure["total_sessions"])
        return structure
    
    def analyze_session_logs(self, session_id: str) -> Dict[str, Any]:
        """Analizar logs de una sesión específica"""
        session_data = {
            "session_id": session_id,
            "categories": {},
            "total_logs": 0,
            "levels": Counter(),
            "timeline": [],
            "errors": [],
            "performance": {}
        }
        
        for category in self.categories:
            log_file = self.logs_path / category / f"{category}_{session_id}.log"
            if log_file.exists():
                session_data["categories"][category] = {
                    "file_size": log_file.stat().st_size,
                    "logs": []
                }
                
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if '|' in line and '{"timestamp"' in line:
                                # Extraer JSON de la línea
                                json_part = line.split('|', 3)[-1].strip()
                                try:
                                    log_entry = json.loads(json_part)
                                    session_data["categories"][category]["logs"].append(log_entry)
                                    session_data["total_logs"] += 1
                                    session_data["levels"][log_entry["level"]] += 1
                                    
                                    # Timeline
                                    session_data["timeline"].append({
                                        "timestamp": log_entry["timestamp"],
                                        "category": category,
                                        "level": log_entry["level"],
                                        "message": log_entry["message"]
                                    })
                                    
                                    # Recopilar errores
                                    if log_entry["level"] in ["ERROR", "CRITICAL"]:
                                        session_data["errors"].append(log_entry)
                                
                                except json.JSONDecodeError:
                                    continue
                
                except Exception as e:
                    self.print_warning(f"Error leyendo {log_file}: {e}")
        
        # Ordenar timeline por timestamp
        session_data["timeline"].sort(key=lambda x: x["timestamp"])
        
        return session_data
    
    def display_overview(self):
        """Mostrar resumen general de la caja negra"""
        if self.console:
            self.console.print(Panel.fit("🗃️ ADMINISTRADOR CAJA NEGRA TRADING GRID", style="bold blue"))
        else:
            print("🗃️ ADMINISTRADOR CAJA NEGRA TRADING GRID")
            print("=" * 50)
        
        structure = self.analyze_log_structure()
        
        if self.console:
            # Tabla de categorías
            table = Table(title="📊 Resumen por Categorías")
            table.add_column("Categoría", style="cyan")
            table.add_column("Archivos", justify="right")
            table.add_column("Sesiones", justify="right") 
            table.add_column("Tamaño", justify="right")
            
            for category, data in structure["categories"].items():
                if data["files"] > 0:
                    size_kb = data["total_size"] / 1024
                    table.add_row(
                        f"📁 {category}",
                        str(data["files"]),
                        str(len(set(data["sessions"]))),
                        f"{size_kb:.1f} KB"
                    )
            
            self.console.print(table)
            
            # Panel de estadísticas
            stats_text = f"""
📈 ESTADÍSTICAS GENERALES
• Total de categorías activas: {structure['total_categories']}
• Total de archivos de log: {structure['total_files']}
• Total de sesiones: {structure['total_sessions']}
• Rango de fechas: {structure['date_range']['oldest'].strftime('%Y-%m-%d %H:%M') if structure['date_range']['oldest'] else 'N/A'} → {structure['date_range']['newest'].strftime('%Y-%m-%d %H:%M') if structure['date_range']['newest'] else 'N/A'}
"""
            
            self.console.print(Panel(stats_text, title="📊 Estadísticas", style="green"))
        else:
            print("\\n📊 RESUMEN POR CATEGORÍAS:")
            for category, data in structure["categories"].items():
                if data["files"] > 0:
                    size_kb = data["total_size"] / 1024
                    print(f"📁 {category}: {data['files']} archivos, {len(set(data['sessions']))} sesiones, {size_kb:.1f} KB")
            
            print(f"\\n📈 ESTADÍSTICAS GENERALES:")
            print(f"• Total de categorías activas: {structure['total_categories']}")
            print(f"• Total de archivos de log: {structure['total_files']}")
            print(f"• Total de sesiones: {structure['total_sessions']}")
    
    def display_session_analysis(self, session_id: str):
        """Mostrar análisis detallado de una sesión"""
        session_data = self.analyze_session_logs(session_id)
        
        if self.console:
            self.console.print(Panel.fit(f"🔍 ANÁLISIS SESIÓN: {session_id}", style="bold yellow"))
        else:
            print(f"🔍 ANÁLISIS SESIÓN: {session_id}")
            print("=" * 50)
        
        if session_data["total_logs"] == 0:
            self.print_warning(f"No se encontraron logs para la sesión {session_id}")
            return
        
        if self.console:
            # Tabla de niveles de log
            levels_table = Table(title="📊 Distribución por Niveles")
            levels_table.add_column("Nivel", style="cyan")
            levels_table.add_column("Cantidad", justify="right")
            levels_table.add_column("Porcentaje", justify="right")
            
            for level, count in session_data["levels"].items():
                percentage = (count / session_data["total_logs"]) * 100
                levels_table.add_row(level, str(count), f"{percentage:.1f}%")
            
            self.console.print(levels_table)
        else:
            print("\\n📊 DISTRIBUCIÓN POR NIVELES:")
            for level, count in session_data["levels"].items():
                percentage = (count / session_data["total_logs"]) * 100
                print(f"• {level}: {count} ({percentage:.1f}%)")
        
        # Mostrar errores si los hay
        if session_data["errors"]:
            if self.console:
                error_table = Table(title="❌ Errores Detectados")
                error_table.add_column("Tiempo", style="cyan")
                error_table.add_column("Categoría", style="red")
                error_table.add_column("Mensaje", style="red")
                
                for error in session_data["errors"][:10]:  # Máximo 10 errores
                    timestamp = error["timestamp"].split("T")[1][:8]  # Solo HH:MM:SS
                    error_table.add_row(timestamp, error["category"], error["message"][:60])
                
                self.console.print(error_table)
            else:
                print("\\n❌ ERRORES DETECTADOS:")
                for error in session_data["errors"][:10]:
                    timestamp = error["timestamp"].split("T")[1][:8]
                    print(f"• {timestamp} [{error['category']}] {error['message'][:60]}")
    
    def cleanup_old_logs(self, days_old: int = 7):
        """Limpiar logs antiguos (mover a archive)"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        archive_path = self.logs_path / "archive" / cutoff_date.strftime("%Y-%m")
        archive_path.mkdir(parents=True, exist_ok=True)
        
        moved_files = 0
        
        for category in self.categories:
            category_path = self.logs_path / category
            if category_path.exists():
                for log_file in category_path.glob("*.log"):
                    mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mod_time < cutoff_date:
                        # Mover a archivo
                        new_path = archive_path / log_file.name
                        log_file.rename(new_path)
                        moved_files += 1
        
        if moved_files > 0:
            self.print_success(f"Archivados {moved_files} archivos de log antiguos en {archive_path}")
        else:
            self.print_info("No se encontraron logs antiguos para archivar")
    
    def get_latest_sessions(self, limit: int = 5) -> List[str]:
        """Obtener las sesiones más recientes"""
        sessions = set()
        
        for category in self.categories:
            category_path = self.logs_path / category
            if category_path.exists():
                for log_file in category_path.glob("*.log"):
                    filename = log_file.name
                    if "_" in filename:
                        session_id = filename.split("_", 1)[1].replace(".log", "")
                        sessions.add((session_id, log_file.stat().st_mtime))
        
        # Ordenar por tiempo de modificación (más reciente primero)
        sorted_sessions = sorted(sessions, key=lambda x: x[1], reverse=True)
        return [session[0] for session in sorted_sessions[:limit]]


def main():
    """Función principal del administrador"""
    admin = BlackBoxAdmin()
    
    if len(sys.argv) < 2:
        print("🗃️ ADMINISTRADOR CAJA NEGRA TRADING GRID")
        print("=" * 50)
        print("Uso: python admin_caja_negra.py <comando> [opciones]")
        print()
        print("Comandos disponibles:")
        print("  overview        - Mostrar resumen general")
        print("  session <id>    - Analizar sesión específica")
        print("  latest          - Analizar las 5 sesiones más recientes")
        print("  cleanup [days]  - Archivar logs antiguos (default: 7 días)")
        print()
        print("Ejemplos:")
        print("  python admin_caja_negra.py overview")
        print("  python admin_caja_negra.py session 20250812_183040")
        print("  python admin_caja_negra.py latest")
        print("  python admin_caja_negra.py cleanup 7")
        return
    
    command = sys.argv[1].lower()
    
    if command == "overview":
        admin.display_overview()
    
    elif command == "session" and len(sys.argv) > 2:
        session_id = sys.argv[2]
        admin.display_session_analysis(session_id)
    
    elif command == "latest":
        latest_sessions = admin.get_latest_sessions()
        admin.print_info(f"Sesiones más recientes: {', '.join(latest_sessions)}")
        if latest_sessions:
            admin.display_session_analysis(latest_sessions[0])
    
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        admin.cleanup_old_logs(days)
    
    else:
        admin.print_error(f"Comando desconocido: {command}")


if __name__ == "__main__":
    main()
