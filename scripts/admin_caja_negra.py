"""
🗃️ ADMINISTRADOR DE CAJA NEGRA - TRADING GRID
===============================================

Script para administrar, analizar y mantener los logs del sistema 
de caja negra del Trading Grid.

FUNCIONALIDADES:
- 📊 Análisis de logs por categoría y sesiones
- 🧹 Limpieza y archivado automático
- 📈 Estadísticas completas del sistema
- 🔍 Búsqueda y filtrado avanzado de logs
- 📋 Resúmenes por período y rendimiento
- 🛠️ Mantenimiento automático de la caja negra
- 📦 Integración completa con el sistema Trading Grid

Autor: GitHub Copilot
Fecha: Agosto 13, 2025
"""

# Imports estándar
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter
import re
import shutil
from dataclasses import dataclass

# Añadir path del proyecto para imports
current_file = Path(__file__)
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class LogEntry:
    """Estructura de una entrada de log"""
    timestamp: str
    session_id: str
    category: str
    level: str
    message: str
    metadata: Dict[str, Any]

@dataclass
class SessionStats:
    """Estadísticas de una sesión"""
    session_id: str
    start_time: datetime
    end_time: datetime
    duration: timedelta
    categories: List[str]
    total_logs: int
    level_counts: Dict[str, int]
    error_count: int
    warning_count: int
    success_count: int

@dataclass
class SystemHealth:
    """Estado de salud del sistema"""
    total_sessions: int
    active_categories: List[str]
    error_rate: float
    average_session_duration: timedelta
    disk_usage: Dict[str, int]
    performance_score: float

class BlackBoxAdmin:
    """Administrador completo de la caja negra del Trading Grid"""
    
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
        
        # Patrones de búsqueda para logs críticos
        self.critical_patterns = {
            "crashes": [r"CRITICAL", r"FATAL", r"crashed", r"terminated"],
            "errors": [r"ERROR", r"Exception", r"failed", r"error"],
            "performance": [r"slow", r"timeout", r"memory", r"cpu"],
            "trading": [r"order", r"position", r"trade", r"fill"],
            "connections": [r"connect", r"disconnect", r"network", r"mt5"]
        }
    
    def print_header(self, title: str, width: int = 80):
        """Imprimir header formateado"""
        print("=" * width)
        print(f" {title} ".center(width, "="))
        print("=" * width)
    
    def print_section(self, title: str, width: int = 60):
        """Imprimir sección"""
        print(f"\n{title}")
        print("-" * width)
    
    def parse_log_entry(self, line: str) -> LogEntry:
        """Parsear una línea de log en LogEntry"""
        try:
            # Buscar el JSON en la línea
            if '|' in line and '{"timestamp"' in line:
                json_part = line.split('|', 3)[-1].strip()
                data = json.loads(json_part)
                
                return LogEntry(
                    timestamp=data.get("timestamp", ""),
                    session_id=data.get("session_id", ""),
                    category=data.get("category", ""),
                    level=data.get("level", ""),
                    message=data.get("message", ""),
                    metadata=data.get("metadata", {})
                )
        except (json.JSONDecodeError, KeyError, IndexError):
            pass
        return None
    
    def get_all_sessions(self) -> List[str]:
        """Obtener todos los session_ids únicos"""
        sessions = set()
        
        for category in self.categories:
            category_path = self.logs_path / category
            if category_path.exists():
                for log_file in category_path.glob("*.log"):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                entry = self.parse_log_entry(line)
                                if entry and entry.session_id:
                                    sessions.add(entry.session_id)
                    except Exception:
                        continue
        
        return sorted(list(sessions), reverse=True)
    
    def analyze_session_complete(self, session_id: str) -> SessionStats:
        """Análisis completo de una sesión específica"""
        entries = []
        categories = set()
        level_counts = Counter()
        
        for category in self.categories:
            category_path = self.logs_path / category
            if category_path.exists():
                for log_file in category_path.glob("*.log"):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                entry = self.parse_log_entry(line)
                                if entry and entry.session_id == session_id:
                                    entries.append(entry)
                                    categories.add(entry.category)
                                    level_counts[entry.level] += 1
                    except Exception:
                        continue
        
        if not entries:
            return None
        
        # Calcular tiempos
        timestamps = [datetime.fromisoformat(entry.timestamp.replace('Z', '+00:00').replace('+00:00', '')) for entry in entries]
        start_time = min(timestamps)
        end_time = max(timestamps)
        duration = end_time - start_time
        
        return SessionStats(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            categories=list(categories),
            total_logs=len(entries),
            level_counts=dict(level_counts),
            error_count=level_counts.get('ERROR', 0) + level_counts.get('CRITICAL', 0),
            warning_count=level_counts.get('WARNING', 0),
            success_count=level_counts.get('SUCCESS', 0)
        )
    
    def get_system_health(self) -> SystemHealth:
        """Obtener estado de salud completo del sistema"""
        all_sessions = self.get_all_sessions()
        active_categories = []
        total_errors = 0
        total_logs = 0
        session_durations = []
        disk_usage = {}
        
        # Analizar categorías activas y uso de disco
        for category in self.categories:
            category_path = self.logs_path / category
            if category_path.exists():
                files = list(category_path.glob("*.log"))
                if files:
                    active_categories.append(category)
                    category_size = sum(f.stat().st_size for f in files)
                    disk_usage[category] = category_size
        
        # Analizar sesiones recientes para rendimiento
        recent_sessions = all_sessions[:10]  # Últimas 10 sesiones
        for session_id in recent_sessions:
            stats = self.analyze_session_complete(session_id)
            if stats:
                total_errors += stats.error_count
                total_logs += stats.total_logs
                session_durations.append(stats.duration.total_seconds())
        
        # Calcular métricas
        error_rate = (total_errors / total_logs * 100) if total_logs > 0 else 0
        avg_duration = timedelta(seconds=sum(session_durations) / len(session_durations)) if session_durations else timedelta(0)
        
        # Score de rendimiento (0-100)
        performance_score = max(0, 100 - error_rate * 2)  # Penalizar por errores
        if avg_duration.total_seconds() > 300:  # Penalizar sesiones muy largas (>5 min)
            performance_score -= 10
        
        return SystemHealth(
            total_sessions=len(all_sessions),
            active_categories=active_categories,
            error_rate=error_rate,
            average_session_duration=avg_duration,
            disk_usage=disk_usage,
            performance_score=performance_score
        )
    
    def search_logs_advanced(self, 
                           pattern: str, 
                           category: str = None, 
                           level: str = None, 
                           session_id: str = None,
                           start_date: str = None,
                           end_date: str = None) -> List[LogEntry]:
        """Búsqueda avanzada en logs"""
        results = []
        pattern_regex = re.compile(pattern, re.IGNORECASE)
        
        # Filtros de fecha
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        categories_to_search = [category] if category else self.categories
        
        for cat in categories_to_search:
            category_path = self.logs_path / cat
            if category_path.exists():
                for log_file in category_path.glob("*.log"):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                entry = self.parse_log_entry(line)
                                if not entry:
                                    continue
                                
                                # Aplicar filtros
                                if level and entry.level != level:
                                    continue
                                if session_id and entry.session_id != session_id:
                                    continue
                                
                                # Filtro de fecha
                                if start_dt or end_dt:
                                    try:
                                        entry_dt = datetime.fromisoformat(entry.timestamp.replace('Z', '+00:00').replace('+00:00', ''))
                                        if start_dt and entry_dt < start_dt:
                                            continue
                                        if end_dt and entry_dt > end_dt:
                                            continue
                                    except:
                                        continue
                                
                                # Buscar patrón en mensaje
                                if pattern_regex.search(entry.message):
                                    results.append(entry)
                    except Exception:
                        continue
        
        return results
    
    def generate_daily_report(self, date: str = None) -> Dict[str, Any]:
        """Generar reporte diario del sistema"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        date_pattern = date.replace("-", "")  # YYYYMMDD
        daily_stats = {
            "date": date,
            "categories": {},
            "total_logs": 0,
            "sessions": [],
            "critical_events": [],
            "performance_issues": [],
            "trading_activity": []
        }
        
        # Analizar logs del día
        for category in self.categories:
            log_file = self.logs_path / category / f"{category}_{date_pattern}.log"
            if log_file.exists():
                category_stats = {
                    "file_size": log_file.stat().st_size,
                    "log_count": 0,
                    "levels": Counter(),
                    "sessions": set()
                }
                
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            entry = self.parse_log_entry(line)
                            if entry:
                                category_stats["log_count"] += 1
                                category_stats["levels"][entry.level] += 1
                                category_stats["sessions"].add(entry.session_id)
                                
                                # Detectar eventos críticos
                                for pattern_type, patterns in self.critical_patterns.items():
                                    for pattern in patterns:
                                        if re.search(pattern, entry.message, re.IGNORECASE):
                                            daily_stats["critical_events"].append({
                                                "type": pattern_type,
                                                "timestamp": entry.timestamp,
                                                "category": entry.category,
                                                "message": entry.message[:100]
                                            })
                
                except Exception:
                    continue
                
                category_stats["sessions"] = list(category_stats["sessions"])
                daily_stats["categories"][category] = category_stats
                daily_stats["total_logs"] += category_stats["log_count"]
                daily_stats["sessions"].extend(category_stats["sessions"])
        
        # Sesiones únicas del día
        daily_stats["sessions"] = list(set(daily_stats["sessions"]))
        
        return daily_stats
    
    def cleanup_and_archive(self, days_old: int = 7, compress: bool = True):
        """Limpieza y archivado automático avanzado"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        archive_base = self.logs_path / "archive"
        archive_base.mkdir(exist_ok=True)
        
        moved_files = 0
        archived_sessions = set()
        total_size_archived = 0
        
        print(f"🧹 Iniciando limpieza de logs anteriores a {cutoff_date.strftime('%Y-%m-%d')}")
        
        for category in self.categories:
            category_path = self.logs_path / category
            if not category_path.exists():
                continue
            
            for log_file in category_path.glob("*.log"):
                mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mod_time < cutoff_date:
                    # Crear estructura de archivo por año/mes
                    archive_month = archive_base / mod_time.strftime("%Y") / mod_time.strftime("%m")
                    archive_month.mkdir(parents=True, exist_ok=True)
                    
                    # Mover archivo
                    new_path = archive_month / log_file.name
                    file_size = log_file.stat().st_size
                    
                    shutil.move(str(log_file), str(new_path))
                    
                    moved_files += 1
                    total_size_archived += file_size
                    
                    # Extraer session_id
                    filename = log_file.name
                    if "_" in filename:
                        session_id = filename.split("_", 1)[1].replace(".log", "")
                        archived_sessions.add(session_id)
        
        print(f"✅ Archivado completado:")
        print(f"   • {moved_files} archivos movidos")
        print(f"   • {len(archived_sessions)} sesiones archivadas")
        print(f"   • {total_size_archived / 1024 / 1024:.2f} MB liberados")
        
        return {
            "files_moved": moved_files,
            "sessions_archived": list(archived_sessions),
            "size_freed": total_size_archived
        }
    
    def display_overview(self):
        """Mostrar resumen completo del sistema"""
        self.print_header("🗃️ ADMINISTRADOR CAJA NEGRA TRADING GRID")
        
        health = self.get_system_health()
        sessions = self.get_all_sessions()
        
        print(f"\n📊 ESTADO GENERAL DEL SISTEMA")
        print(f"├─ Total de sesiones registradas: {health.total_sessions}")
        print(f"├─ Categorías activas: {len(health.active_categories)}/{len(self.categories)}")
        print(f"├─ Tasa de errores: {health.error_rate:.2f}%")
        print(f"├─ Duración promedio de sesión: {health.average_session_duration}")
        print(f"└─ Score de rendimiento: {health.performance_score:.1f}/100")
        
        print(f"\n📁 USO DE DISCO POR CATEGORÍA")
        total_size = sum(health.disk_usage.values())
        for category, size in health.disk_usage.items():
            size_mb = size / 1024 / 1024
            percentage = (size / total_size * 100) if total_size > 0 else 0
            print(f"├─ {category:12}: {size_mb:6.2f} MB ({percentage:5.1f}%)")
        print(f"└─ Total: {total_size / 1024 / 1024:.2f} MB")
        
        print(f"\n🕒 SESIONES RECIENTES (últimas 10)")
        for session_id in sessions[:10]:
            stats = self.analyze_session_complete(session_id)
            if stats:
                status = "🔴" if stats.error_count > 0 else "🟢"
                print(f"├─ {status} {session_id}: {stats.total_logs} logs, {stats.duration}, {stats.error_count} errores")
        
        # Recomendaciones automáticas
        print(f"\n💡 RECOMENDACIONES AUTOMÁTICAS")
        if health.error_rate > 5:
            print("├─ ⚠️  Tasa de errores alta - Revisar logs de errores")
        if health.performance_score < 70:
            print("├─ ⚠️  Rendimiento bajo - Optimización requerida")
        if total_size / 1024 / 1024 > 100:  # > 100MB
            print("├─ 🧹 Considerar limpieza de logs antiguos")
        if len(sessions) > 50:
            print("├─ 📦 Considerar archivado de sesiones antiguas")
        print("└─ ✅ Sistema operativo")
    
    def display_session_analysis(self, session_id: str):
        """Mostrar análisis detallado de una sesión"""
        self.print_header(f"🔍 ANÁLISIS DETALLADO - SESIÓN {session_id}")
        
        stats = self.analyze_session_complete(session_id)
        if not stats:
            print("❌ No se encontraron datos para esta sesión")
            return
        
        print(f"\n📊 INFORMACIÓN GENERAL")
        print(f"├─ Session ID: {stats.session_id}")
        print(f"├─ Inicio: {stats.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"├─ Fin: {stats.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"├─ Duración: {stats.duration}")
        print(f"├─ Total de logs: {stats.total_logs}")
        print(f"└─ Categorías activas: {', '.join(stats.categories)}")
        
        print(f"\n📈 DISTRIBUCIÓN POR NIVEL")
        for level, count in stats.level_counts.items():
            percentage = (count / stats.total_logs * 100)
            icon = {"ERROR": "🔴", "WARNING": "🟡", "INFO": "🔵", "SUCCESS": "🟢", "DEBUG": "⚪"}.get(level, "⚫")
            print(f"├─ {icon} {level:8}: {count:4} ({percentage:5.1f}%)")
        
        if stats.error_count > 0:
            print(f"\n❌ ANÁLISIS DE ERRORES ({stats.error_count} encontrados)")
            # Buscar errores específicos en esta sesión
            errors = self.search_logs_advanced("", session_id=session_id, level="ERROR")
            for error in errors[:5]:  # Mostrar máximo 5 errores
                timestamp = error.timestamp.split("T")[1][:8]
                print(f"├─ {timestamp} [{error.category}] {error.message[:60]}")
            if len(errors) > 5:
                print(f"└─ ... y {len(errors) - 5} errores más")
        
        # Análisis de rendimiento
        duration_seconds = stats.duration.total_seconds()
        if duration_seconds > 300:  # > 5 minutos
            print(f"\n⚠️  ALERTA DE RENDIMIENTO")
            print(f"├─ Sesión excesivamente larga: {stats.duration}")
            print(f"└─ Revisar logs de performance para esta sesión")

def main():
    """Función principal del administrador"""
    admin = BlackBoxAdmin()
    
    if len(sys.argv) < 2:
        print("🗃️ ADMINISTRADOR CAJA NEGRA TRADING GRID v2.0")
        print("=" * 60)
        print("Uso: python admin_caja_negra.py <comando> [opciones]")
        print()
        print("COMANDOS PRINCIPALES:")
        print("  overview              - Resumen completo del sistema")
        print("  session <id>          - Análisis detallado de sesión")
        print("  health                - Estado de salud del sistema")
        print("  latest [N]            - Últimas N sesiones (default: 5)")
        print("  daily [YYYY-MM-DD]    - Reporte diario")
        print("  search <patrón>       - Búsqueda avanzada en logs")
        print("  cleanup [días]        - Limpiar logs antiguos")
        print("  archive [días]        - Archivar logs antiguos")
        print()
        print("COMANDOS DE BÚSQUEDA:")
        print("  errors [sesión]       - Buscar errores")
        print("  performance           - Problemas de rendimiento")
        print("  trading [sesión]      - Actividad de trading")
        print("  crashes               - Eventos críticos")
        print()
        print("EJEMPLOS:")
        print("  python admin_caja_negra.py overview")
        print("  python admin_caja_negra.py session 20250813_105653")
        print("  python admin_caja_negra.py search 'MT5 connection'")
        print("  python admin_caja_negra.py daily 2025-08-13")
        print("  python admin_caja_negra.py cleanup 7")
        return
    
    command = sys.argv[1].lower()
    
    try:
        if command == "overview":
            admin.display_overview()
        
        elif command == "session" and len(sys.argv) > 2:
            session_id = sys.argv[2]
            admin.display_session_analysis(session_id)
        
        elif command == "health":
            health = admin.get_system_health()
            admin.print_header("🏥 ESTADO DE SALUD DEL SISTEMA")
            print(f"Score de rendimiento: {health.performance_score:.1f}/100")
            print(f"Tasa de errores: {health.error_rate:.2f}%")
            print(f"Categorías activas: {len(health.active_categories)}")
            print(f"Total de sesiones: {health.total_sessions}")
        
        elif command == "latest":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            sessions = admin.get_all_sessions()[:limit]
            admin.print_header(f"🕒 ÚLTIMAS {limit} SESIONES")
            for session_id in sessions:
                stats = admin.analyze_session_complete(session_id)
                if stats:
                    status = "🔴" if stats.error_count > 0 else "🟢"
                    print(f"{status} {session_id}: {stats.total_logs} logs, {stats.error_count} errores")
        
        elif command == "daily":
            date = sys.argv[2] if len(sys.argv) > 2 else None
            report = admin.generate_daily_report(date)
            admin.print_header(f"📅 REPORTE DIARIO - {report['date']}")
            print(f"Total de logs: {report['total_logs']}")
            print(f"Sesiones activas: {len(report['sessions'])}")
            print(f"Eventos críticos: {len(report['critical_events'])}")
            
            for category, stats in report['categories'].items():
                if stats['log_count'] > 0:
                    print(f"{category}: {stats['log_count']} logs")
        
        elif command == "search" and len(sys.argv) > 2:
            pattern = sys.argv[2]
            results = admin.search_logs_advanced(pattern)
            admin.print_header(f"🔍 BÚSQUEDA: '{pattern}'")
            print(f"Encontrados {len(results)} resultados")
            
            for result in results[:20]:  # Mostrar máximo 20 resultados
                timestamp = result.timestamp.split("T")[1][:8]
                print(f"[{timestamp}] {result.category}/{result.level}: {result.message[:80]}")
        
        elif command == "cleanup":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            result = admin.cleanup_and_archive(days)
            print(f"Limpieza completada: {result['files_moved']} archivos archivados")
        
        elif command == "errors":
            session_id = sys.argv[2] if len(sys.argv) > 2 else None
            errors = admin.search_logs_advanced("", level="ERROR", session_id=session_id)
            admin.print_header("❌ ERRORES ENCONTRADOS")
            for error in errors[:10]:
                print(f"[{error.timestamp}] {error.category}: {error.message}")
        
        elif command == "performance":
            perf_issues = admin.search_logs_advanced("slow|timeout|memory|cpu|performance")
            admin.print_header("📈 PROBLEMAS DE RENDIMIENTO")
            for issue in perf_issues[:10]:
                print(f"[{issue.timestamp}] {issue.category}: {issue.message}")
        
        elif command == "trading":
            session_id = sys.argv[2] if len(sys.argv) > 2 else None
            trading = admin.search_logs_advanced("order|position|trade|fill", session_id=session_id)
            admin.print_header("💹 ACTIVIDAD DE TRADING")
            for trade in trading[:10]:
                print(f"[{trade.timestamp}] {trade.category}: {trade.message}")
        
        elif command == "crashes":
            crashes = admin.search_logs_advanced("CRITICAL|FATAL|crash|terminated")
            admin.print_header("💥 EVENTOS CRÍTICOS")
            for crash in crashes:
                print(f"[{crash.timestamp}] {crash.category}: {crash.message}")
        
        else:
            print(f"❌ Comando desconocido: {command}")
            print("Use 'python admin_caja_negra.py' para ver la ayuda")
    
    except Exception as e:
        print(f"❌ Error ejecutando comando '{command}': {str(e)}")
        print("Use 'python admin_caja_negra.py' para ver la ayuda")

if __name__ == "__main__":
    main()
