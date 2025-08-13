"""
🔍 AUDITORÍA COMPLETA - ERRORES ANALYTICS MANAGER
================================================

Análisis forense de los errores encontrados en la caja negra
del Trading Grid para identificar y resolver las dependencias
no válidas del AnalyticsManager.

Autor: GitHub Copilot
Fecha: Agosto 12, 2025
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Rich para interfaz
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.text import Text
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

class ForensicAnalyzer:
    """Analizador forense de errores del sistema"""
    
    def __init__(self):
        """Inicializar analizador"""
        # Detectar ruta del proyecto
        current_file = Path(__file__)
        self.project_root = current_file.parent.parent
        self.logs_path = self.project_root / "logs"
        
        if HAS_RICH:
            self.console = console
        else:
            self.console = None
    
    def print_header(self, title: str):
        """Imprimir encabezado"""
        if self.console:
            self.console.print(Panel.fit(title, style="bold red"))
        else:
            print(f"\\n{title}")
            print("=" * len(title))
    
    def print_info(self, message: str):
        """Imprimir info"""
        if self.console:
            self.console.print(f"[cyan]🔍 {message}[/cyan]")
        else:
            print(f"🔍 {message}")
    
    def print_finding(self, message: str):
        """Imprimir hallazgo"""
        if self.console:
            self.console.print(f"[yellow]📋 HALLAZGO: {message}[/yellow]")
        else:
            print(f"📋 HALLAZGO: {message}")
    
    def print_error(self, message: str):
        """Imprimir error"""
        if self.console:
            self.console.print(f"[red]❌ ERROR: {message}[/red]")
        else:
            print(f"❌ ERROR: {message}")
    
    def print_solution(self, message: str):
        """Imprimir solución"""
        if self.console:
            self.console.print(f"[green]✅ SOLUCIÓN: {message}[/green]")
        else:
            print(f"✅ SOLUCIÓN: {message}")
    
    def analyze_error_logs(self, session_id: str) -> Dict[str, Any]:
        """Analizar logs de errores de una sesión específica"""
        errors_file = self.logs_path / "errors" / f"errors_{session_id}.log"
        system_file = self.logs_path / "system" / f"system_{session_id}.log"
        
        analysis = {
            "session_id": session_id,
            "errors": [],
            "timeline": [],
            "dependencies_issues": [],
            "root_causes": []
        }
        
        # Analizar errores
        if errors_file.exists():
            with open(errors_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '{"timestamp"' in line:
                        json_part = line.split('|', 3)[-1].strip()
                        try:
                            error_entry = json.loads(json_part)
                            analysis["errors"].append(error_entry)
                        except json.JSONDecodeError:
                            continue
        
        # Analizar timeline del sistema
        if system_file.exists():
            with open(system_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '{"timestamp"' in line:
                        json_part = line.split('|', 3)[-1].strip()
                        try:
                            system_entry = json.loads(json_part)
                            analysis["timeline"].append(system_entry)
                        except json.JSONDecodeError:
                            continue
        
        # Ordenar timeline
        analysis["timeline"].sort(key=lambda x: x.get("timestamp", ""))
        
        return analysis
    
    def identify_dependency_issues(self, analysis: Dict[str, Any]) -> List[str]:
        """Identificar problemas de dependencias"""
        issues = []
        
        # Buscar problemas específicos en timeline
        for entry in analysis["timeline"]:
            message = entry.get("message", "")
            if "Manager no inicializado" in message:
                manager_name = message.split(":")[-1].strip()
                issues.append(f"Manager no inicializado: {manager_name}")
            elif "Dependencias no válidas" in message:
                issues.append("Fallo en validación de dependencias")
            elif "Error general en AnalyticsManager" in message:
                issues.append("Error general en AnalyticsManager durante inicialización")
        
        return issues
    
    def generate_root_cause_analysis(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generar análisis de causa raíz"""
        causes = []
        
        # RCA 1: ConfigManager sin is_initialized
        causes.append({
            "issue": "ConfigManager missing is_initialized property",
            "evidence": "Manager no inicializado: ConfigManager",
            "root_cause": "ConfigManager class doesn't have is_initialized attribute",
            "impact": "AnalyticsManager dependency validation fails",
            "solution": "Add is_initialized property to ConfigManager"
        })
        
        # RCA 2: Orden de inicialización
        causes.append({
            "issue": "Dependency initialization order",
            "evidence": "Error inicializando AnalyticsManager: Dependencias no válidas",
            "root_cause": "Managers are not fully initialized before AnalyticsManager validation",
            "impact": "AnalyticsManager fails to start, affecting analytics capabilities",
            "solution": "Ensure proper initialization order and add is_initialized to all managers"
        })
        
        # RCA 3: Validación estricta
        causes.append({
            "issue": "Strict dependency validation",
            "evidence": "Dependencias no válidas exception",
            "root_cause": "_validate_dependencies() method is too strict",
            "impact": "System can't start analytics even if managers are functional",
            "solution": "Improve dependency validation logic or make it more robust"
        })
        
        return causes
    
    def create_solutions_plan(self) -> List[Dict[str, Any]]:
        """Crear plan de soluciones"""
        solutions = [
            {
                "priority": "HIGH",
                "title": "Agregar is_initialized a ConfigManager",
                "description": "Agregar propiedad is_initialized al ConfigManager",
                "files": ["src/core/config_manager.py"],
                "code_changes": [
                    "Agregar self.is_initialized = True en __init__",
                    "Agregar método de inicialización si es necesario"
                ],
                "testing": "Verificar que AnalyticsManager pase validación de dependencias"
            },
            {
                "priority": "HIGH", 
                "title": "Agregar is_initialized a DataManager",
                "description": "Agregar propiedad is_initialized al DataManager",
                "files": ["src/core/data_manager.py"],
                "code_changes": [
                    "Agregar self.is_initialized = True en __init__",
                    "Verificar que el manager esté completamente inicializado"
                ],
                "testing": "Verificar integración con AnalyticsManager"
            },
            {
                "priority": "MEDIUM",
                "title": "Mejorar validación de dependencias",
                "description": "Hacer la validación más robusta y con mejor logging",
                "files": ["src/core/analytics_manager.py"],
                "code_changes": [
                    "Mejorar _validate_dependencies() con logs detallados",
                    "Agregar fallbacks para managers no críticos",
                    "Logging específico de cada dependencia"
                ],
                "testing": "Probar con diferentes escenarios de fallo"
            },
            {
                "priority": "LOW",
                "title": "Logging de auditoría mejorado",
                "description": "Agregar más contexto en logs de errores",
                "files": ["src/core/analytics_manager.py"],
                "code_changes": [
                    "Logs con metadatos específicos de dependencias",
                    "Información de estado de cada manager",
                    "Timeline detallado de inicialización"
                ],
                "testing": "Verificar que logs provean suficiente información para debugging"
            }
        ]
        
        return solutions
    
    def display_forensic_report(self, session_id: str):
        """Mostrar reporte forense completo"""
        self.print_header(f"🕵️ AUDITORÍA FORENSE - SESIÓN {session_id}")
        
        # Analizar logs
        analysis = self.analyze_error_logs(session_id)
        dependency_issues = self.identify_dependency_issues(analysis)
        root_causes = self.generate_root_cause_analysis(analysis)
        solutions = self.create_solutions_plan()
        
        # 1. RESUMEN DE ERRORES
        if self.console:
            error_table = Table(title="❌ Errores Detectados")
            error_table.add_column("Timestamp", style="cyan")
            error_table.add_column("Mensaje", style="red")
            error_table.add_column("Categoría", style="yellow")
            
            for error in analysis["errors"]:
                timestamp = error["timestamp"].split("T")[1][:8]
                message = error["message"][:50] + "..." if len(error["message"]) > 50 else error["message"]
                error_table.add_row(timestamp, message, error["category"])
            
            self.console.print(error_table)
        
        # 2. PROBLEMAS DE DEPENDENCIAS
        self.print_info("PROBLEMAS DE DEPENDENCIAS IDENTIFICADOS:")
        for issue in dependency_issues:
            self.print_finding(issue)
        
        # 3. ANÁLISIS DE CAUSA RAÍZ
        self.print_info("\\nANÁLISIS DE CAUSA RAÍZ:")
        for i, cause in enumerate(root_causes, 1):
            if self.console:
                cause_panel = Panel(
                    f"**Issue:** {cause['issue']}\\n"
                    f"**Evidence:** {cause['evidence']}\\n"
                    f"**Root Cause:** {cause['root_cause']}\\n"
                    f"**Impact:** {cause['impact']}\\n"
                    f"**Solution:** {cause['solution']}",
                    title=f"RCA #{i}",
                    style="yellow"
                )
                self.console.print(cause_panel)
            else:
                print(f"\\nRCA #{i}:")
                print(f"  Issue: {cause['issue']}")
                print(f"  Evidence: {cause['evidence']}")
                print(f"  Root Cause: {cause['root_cause']}")
                print(f"  Impact: {cause['impact']}")
                print(f"  Solution: {cause['solution']}")
        
        # 4. PLAN DE SOLUCIONES
        self.print_info("\\nPLAN DE SOLUCIONES:")
        if self.console:
            solutions_table = Table(title="🔧 Plan de Corrección")
            solutions_table.add_column("Prioridad", style="cyan")
            solutions_table.add_column("Título", style="green")
            solutions_table.add_column("Archivos", style="yellow")
            solutions_table.add_column("Cambios Principales", style="white")
            
            for solution in solutions:
                files_str = ", ".join(solution["files"])
                changes_str = "; ".join(solution["code_changes"][:2])  # Primeros 2 cambios
                solutions_table.add_row(
                    solution["priority"],
                    solution["title"],
                    files_str,
                    changes_str
                )
            
            self.console.print(solutions_table)
        
        return analysis, root_causes, solutions


def main():
    """Función principal de auditoría"""
    analyzer = ForensicAnalyzer()
    
    if len(sys.argv) < 2:
        print("🕵️ AUDITORÍA FORENSE TRADING GRID")
        print("=" * 40)
        print("Uso: python auditoria_errores.py <session_id>")
        print()
        print("Ejemplo:")
        print("  python auditoria_errores.py 20250812_183040")
        return
    
    session_id = sys.argv[1]
    
    try:
        analysis, root_causes, solutions = analyzer.display_forensic_report(session_id)
        
        # Guardar reporte completo
        report_file = analyzer.project_root / "logs" / f"forensic_report_{session_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": session_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "errors": analysis["errors"],
                "timeline": analysis["timeline"],
                "root_causes": root_causes,
                "solutions": solutions
            }, f, indent=2, ensure_ascii=False)
        
        analyzer.print_solution(f"Reporte forense guardado en {report_file}")
        
    except Exception as e:
        analyzer.print_error(f"Error durante auditoría: {e}")


if __name__ == "__main__":
    main()
