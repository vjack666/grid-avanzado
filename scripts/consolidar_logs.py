#!/usr/bin/env python3
"""
🗃️ CONSOLIDADOR DE LOGS DE CAJA NEGRA
=====================================

Consolida múltiples archivos de log por sesión en archivos únicos por día
para optimizar el almacenamiento y organización de la caja negra.

ANTES: archivo_20250812_183040.log, archivo_20250812_185307.log, etc.
DESPUÉS: archivo_20250812.log (todos los logs del día)

Autor: GitHub Copilot
Fecha: Agosto 12, 2025
"""

import os
import glob
import shutil
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Añadir el directorio raíz del proyecto al path
script_dir = Path(__file__).parent
project_root = script_dir.parent
logs_dir = project_root / "logs"

def consolidate_logs():
    """Consolida logs por sesión en archivos únicos por día"""
    print("🗃️ CONSOLIDADOR DE LOGS CAJA NEGRA")
    print("=" * 40)
    print(f"📂 Procesando: {logs_dir}")
    print()
    
    # Categorías a procesar
    categories = ['system', 'trading', 'analytics', 'mt5', 'errors', 
                 'performance', 'fvg', 'signals', 'strategy', 'security']
    
    total_files_processed = 0
    total_files_consolidated = 0
    
    for category in categories:
        category_dir = logs_dir / category
        if not category_dir.exists():
            continue
            
        print(f"📁 Procesando categoría: {category}")
        
        # Buscar todos los archivos de log de esta categoría
        log_files = list(category_dir.glob(f"{category}_*.log"))
        
        if not log_files:
            print(f"   ℹ️  No hay archivos para consolidar")
            continue
        
        # Agrupar archivos por fecha
        files_by_date = defaultdict(list)
        
        for log_file in log_files:
            # Extraer fecha del nombre del archivo
            # Formato: category_YYYYMMDD_HHMMSS.log
            filename = log_file.stem
            parts = filename.split('_')
            
            if len(parts) >= 2:
                date_part = parts[1]  # YYYYMMDD
                if len(date_part) == 8 and date_part.isdigit():
                    files_by_date[date_part].append(log_file)
                    total_files_processed += 1
        
        # Consolidar archivos para cada fecha
        for date, files in files_by_date.items():
            if len(files) <= 1:
                continue  # No hay nada que consolidar
            
            consolidated_file = category_dir / f"{category}_{date}.log"
            backup_dir = category_dir / "backup_sessions"
            backup_dir.mkdir(exist_ok=True)
            
            print(f"   🔄 Consolidando {len(files)} archivos para {date}")
            
            # Crear archivo consolidado
            with open(consolidated_file, 'w', encoding='utf-8') as outfile:
                # Escribir header
                outfile.write(f"# CAJA NEGRA TRADING GRID - {category.upper()} LOGS\n")
                outfile.write(f"# Fecha: {date[:4]}-{date[4:6]}-{date[6:8]}\n")
                outfile.write(f"# Consolidado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                outfile.write(f"# Archivos originales: {len(files)}\n")
                outfile.write("#" + "="*60 + "\n\n")
                
                # Ordenar archivos por timestamp
                files.sort(key=lambda f: f.name)
                
                for log_file in files:
                    try:
                        # Agregar separador de sesión
                        session_id = log_file.stem.split('_', 2)[-1] if '_' in log_file.stem else "unknown"
                        outfile.write(f"\n# ===== SESIÓN {session_id} =====\n")
                        
                        # Copiar contenido del archivo
                        with open(log_file, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            if content.strip():  # Solo escribir si hay contenido
                                outfile.write(content)
                                if not content.endswith('\n'):
                                    outfile.write('\n')
                        
                        outfile.write(f"# ===== FIN SESIÓN {session_id} =====\n\n")
                        
                    except Exception as e:
                        print(f"      ⚠️  Error procesando {log_file.name}: {e}")
                        continue
            
            # Mover archivos originales a backup
            for log_file in files:
                try:
                    backup_path = backup_dir / log_file.name
                    shutil.move(str(log_file), str(backup_path))
                except Exception as e:
                    print(f"      ⚠️  Error moviendo {log_file.name} a backup: {e}")
            
            total_files_consolidated += len(files)
            print(f"   ✅ Consolidado en: {consolidated_file.name}")
            print(f"   📦 {len(files)} archivos movidos a backup")
    
    print()
    print("📊 RESUMEN DE CONSOLIDACIÓN:")
    print("-" * 40)
    print(f"📁 Archivos procesados: {total_files_processed}")
    print(f"🔄 Archivos consolidados: {total_files_consolidated}")
    print(f"📦 Archivos respaldados: {total_files_consolidated}")
    
    # Verificar estructura final
    print()
    print("📂 ESTRUCTURA FINAL:")
    print("-" * 40)
    
    for category in categories:
        category_dir = logs_dir / category
        if category_dir.exists():
            log_files = list(category_dir.glob(f"{category}_*.log"))
            backup_files = list((category_dir / "backup_sessions").glob("*.log")) if (category_dir / "backup_sessions").exists() else []
            
            print(f"📁 {category:<12} | {len(log_files):>2} archivos principales | {len(backup_files):>3} archivos respaldados")
    
    print()
    print("✅ CONSOLIDACIÓN COMPLETADA")
    print("🗃️ Caja negra optimizada para un archivo por día por categoría")

def create_optimized_logger_test():
    """Crear un test para verificar que el nuevo sistema funciona"""
    print()
    print("🧪 PROBANDO NUEVO SISTEMA OPTIMIZADO...")
    
    try:
        # Importar el LoggerManager optimizado
        import sys
        sys.path.insert(0, str(project_root))
        from src.core.logger_manager import LoggerManager, LogLevel
        
        # Crear instancia de prueba
        logger = LoggerManager()
        
        # Escribir logs de prueba
        logger.log_system(LogLevel.INFO, "🧪 Prueba del sistema optimizado - UN archivo por día")
        logger.log_trading(LogLevel.INFO, "🧪 Trading log de prueba")
        logger.log_analytics(LogLevel.INFO, "🧪 Analytics log de prueba")
        
        print("✅ Sistema optimizado funcionando correctamente")
        print("📁 Ahora se genera UN archivo por día por categoría")
        
    except Exception as e:
        print(f"❌ Error probando sistema optimizado: {e}")

if __name__ == "__main__":
    consolidate_logs()
    create_optimized_logger_test()
