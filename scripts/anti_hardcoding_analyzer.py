#!/usr/bin/env python3
"""
🔧 SCRIPT PARA ELIMINAR HARDCODING
==================================

Este script identifica y reemplaza valores hardcodeados en todo el sistema
con configuraciones dinámicas desde trading_config.json

Autor: GitHub Copilot
Fecha: Agosto 13, 2025
"""

import os
import re
import json
from pathlib import Path

def load_config():
    """Carga la configuración del sistema"""
    config_path = Path(__file__).parent / "config" / "trading_config.json"
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {}

def find_hardcoded_values(directory):
    """Encuentra valores hardcodeados en archivos Python"""
    hardcoded_patterns = [
        (r"'EURUSD'", "Símbolo hardcodeado"),
        (r'"EURUSD"', "Símbolo hardcodeado"),
        (r"'GBPUSD'", "Símbolo hardcodeado"),
        (r'"GBPUSD"', "Símbolo hardcodeado"),
        (r"'H1'", "Timeframe hardcodeado"),
        (r'"H1"', "Timeframe hardcodeado"),
        (r"'M5'", "Timeframe hardcodeado"),
        (r'"M5"', "Timeframe hardcodeado"),
        (r"'M15'", "Timeframe hardcodeado"),
        (r'"M15"', "Timeframe hardcodeado"),
        (r"'LONDON'", "Sesión hardcodeada"),
        (r'"LONDON"', "Sesión hardcodeada"),
        (r"'NEUTRAL'", "Tendencia hardcodeada"),
        (r'"NEUTRAL"', "Tendencia hardcodeada"),
        (r"version.*=.*['\"]1\.0\.0['\"]", "Versión hardcodeada"),
        (r"1\.0950", "Precio hardcodeado"),
        (r"1\.2700", "Precio hardcodeado"),
    ]
    
    results = []
    
    for root, dirs, files in os.walk(directory):
        # Excluir directorios no relevantes
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.vscode', 'node_modules']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern, description in hardcoded_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            results.append({
                                'file': file_path,
                                'line': line_num,
                                'pattern': pattern,
                                'description': description,
                                'match': match.group()
                            })
                
                except Exception as e:
                    print(f"❌ Error leyendo {file_path}: {e}")
    
    return results

def generate_config_integration_code():
    """Genera código para integrar configuración dinámica"""
    
    config_integration = '''
# === CONFIGURACIÓN DINÁMICA - ANTI-HARDCODING ===
# Agregar al inicio de archivos que necesiten configuración:

from src.core.config_manager import ConfigManager

# Inicializar configuración
config = ConfigManager()

# Obtener valores dinámicos:
symbols = config.get_symbols()                    # En lugar de ['EURUSD']
primary_symbol = config.get_primary_symbol()     # En lugar de 'EURUSD'
timeframes = config.get_timeframes()             # En lugar de ['M5', 'M15', 'H1']
default_timeframe = config.get_default_timeframe() # En lugar de 'H1'
current_session = config.get_current_session()   # En lugar de 'LONDON'
fvg_config = config.get_fvg_config()            # Configuración FVG completa
alerts_config = config.get_alerts_config()      # Configuración de alertas

# Detectar tendencia dinámicamente:
trend_value = 0.5  # Desde análisis real
market_trend = config.detect_market_trend(trend_value)  # En lugar de 'NEUTRAL'

# === EJEMPLOS DE REEMPLAZO ===

# ANTES (hardcodeado):
# symbol = 'EURUSD'
# timeframe = 'H1'
# session = 'LONDON'

# DESPUÉS (dinámico):
# symbol = config.get_primary_symbol()
# timeframe = config.get_default_timeframe()
# session = config.get_current_session()
'''
    
    return config_integration

def create_anti_hardcoding_report():
    """Crea reporte completo de hardcoding en el sistema"""
    
    print("🔍 ANALIZANDO SISTEMA PARA DETECTAR HARDCODING...")
    
    # Directorio del proyecto
    project_dir = Path(__file__).parent
    
    # Buscar valores hardcodeados
    hardcoded_values = find_hardcoded_values(project_dir)
    
    # Generar reporte
    report = f"""
🚨 REPORTE ANTI-HARDCODING - TRADING GRID SYSTEM
===============================================

📊 RESUMEN:
- Total de archivos analizados: {len(list(project_dir.rglob('*.py')))}
- Valores hardcodeados encontrados: {len(hardcoded_values)}

📋 VALORES HARDCODEADOS DETECTADOS:
"""
    
    # Agrupar por archivo
    files_with_hardcoding = {}
    for item in hardcoded_values:
        file_path = item['file']
        if file_path not in files_with_hardcoding:
            files_with_hardcoding[file_path] = []
        files_with_hardcoding[file_path].append(item)
    
    for file_path, items in files_with_hardcoding.items():
        relative_path = os.path.relpath(file_path, project_dir)
        report += f"\n📄 {relative_path}:\n"
        
        for item in items:
            report += f"   Línea {item['line']}: {item['match']} - {item['description']}\n"
    
    # Agregar código de integración
    report += "\n" + "="*60 + "\n"
    report += generate_config_integration_code()
    
    # Guardar reporte
    report_path = project_dir / "anti_hardcoding_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Reporte generado: {report_path}")
    print(f"📊 Encontrados {len(hardcoded_values)} valores hardcodeados en {len(files_with_hardcoding)} archivos")
    
    return report_path

def main():
    """Función principal"""
    print("🔧 INICIANDO ANÁLISIS ANTI-HARDCODING...")
    
    # Cargar configuración
    config = load_config()
    print(f"✅ Configuración cargada: {len(config)} secciones")
    
    # Crear reporte
    report_path = create_anti_hardcoding_report()
    
    print("\n🎯 RECOMENDACIONES:")
    print("1. Revisar el reporte generado")
    print("2. Implementar ConfigManager en archivos con hardcoding")
    print("3. Reemplazar valores hardcodeados con métodos dinámicos")
    print("4. Validar que todo funcione después de los cambios")
    
    print("\n✅ ANÁLISIS COMPLETADO")

if __name__ == "__main__":
    main()
