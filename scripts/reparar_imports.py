#!/usr/bin/env python3
"""
Script para reparar automáticamente todos los imports después de la reorganización
"""

import os
import re
from pathlib import Path

def add_import_paths(content, file_path):
    """Agrega las rutas de import necesarias al inicio del archivo"""
    
    # Determinar la ruta relativa al proyecto root desde el archivo actual
    file_path = Path(file_path)
    project_root = file_path.parents[2] if 'src' in file_path.parts else file_path.parent
    
    # Calcular las rutas relativas
    if 'src/core' in str(file_path):
        relative_root = "../.."
    elif 'src/analysis' in str(file_path):
        relative_root = "../.."
    elif 'src/utils' in str(file_path):
        relative_root = "../.."
    elif 'tests' in str(file_path):
        relative_root = ".."
    else:
        relative_root = "."
    
    # Template para agregar al inicio
    import_template = f'''import sys
from pathlib import Path

# Configurar rutas para imports
current_dir = Path(__file__).parent
project_root = current_dir / "{relative_root}"
sys.path.insert(0, str(project_root.absolute()))
sys.path.insert(0, str((project_root / "src" / "core").absolute()))
sys.path.insert(0, str((project_root / "src" / "analysis").absolute()))
sys.path.insert(0, str((project_root / "src" / "utils").absolute()))
sys.path.insert(0, str((project_root / "config").absolute()))

'''
    
    # Buscar si ya tiene imports de sys/pathlib
    lines = content.split('\n')
    has_sys = any('import sys' in line for line in lines[:10])
    has_pathlib = any('from pathlib import Path' in line or 'import pathlib' in line for line in lines[:10])
    
    if not has_sys or not has_pathlib:
        # Encontrar donde insertar (después de docstring si existe)
        insert_pos = 0
        in_docstring = False
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                elif line.strip().endswith('"""') or line.strip().endswith("'''"):
                    insert_pos = i + 1
                    break
            elif not in_docstring and line.strip() and not line.strip().startswith('#'):
                insert_pos = i
                break
        
        lines.insert(insert_pos, import_template)
        return '\n'.join(lines)
    
    return content

def repair_file(file_path):
    """Repara los imports de un archivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Solo procesar archivos que tengan imports problemáticos
        problematic_imports = [
            'from config import',
            'from grid_bollinger import',
            'from analisis_estocastico_m15 import',
            'from riskbot_mt5 import',
            'from trading_schedule import',
            'from data_logger import',
            'from descarga_velas import',
            'import config',
            'import grid_bollinger',
            'import analisis_estocastico_m15',
            'import riskbot_mt5',
            'import trading_schedule',
            'import data_logger',
            'import descarga_velas'
        ]
        
        needs_repair = any(imp in content for imp in problematic_imports)
        
        if needs_repair:
            print(f"🔧 Reparando imports en: {file_path}")
            
            # Agregar rutas de import
            new_content = add_import_paths(content, file_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        else:
            print(f"✅ Sin problemas en: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 REPARADOR AUTOMÁTICO DE IMPORTS")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    # Archivos a procesar
    files_to_process = [
        # Core
        project_root / "src" / "core" / "order_manager.py",
        project_root / "src" / "core" / "riskbot_mt5.py",
        
        # Analysis  
        project_root / "src" / "analysis" / "grid_bollinger.py",
        project_root / "src" / "analysis" / "analisis_estocastico_m15.py",
        
        # Utils
        project_root / "src" / "utils" / "data_logger.py",
        project_root / "src" / "utils" / "trading_schedule.py",
        project_root / "src" / "utils" / "descarga_velas.py",
        
        # Tests
        project_root / "tests" / "test_sistema.py"
    ]
    
    repaired_count = 0
    for file_path in files_to_process:
        if file_path.exists():
            if repair_file(file_path):
                repaired_count += 1
        else:
            print(f"⚠️ Archivo no encontrado: {file_path}")
    
    print("\n" + "=" * 50)
    print(f"✅ Proceso completado: {repaired_count} archivos reparados")
    print("🎯 Ahora ejecuta: python tests/test_sistema.py")

if __name__ == "__main__":
    main()
