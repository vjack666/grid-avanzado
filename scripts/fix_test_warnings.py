#!/usr/bin/env python3
"""
Script para corregir warnings en tests - SÓTANO 2
================================================

Corrige los warnings de pytest reemplazando return True/False por assert statements

Fecha: 2025-08-12
Autor: GitHub Copilot
"""

import os
import re
from pathlib import Path

def fix_test_warnings(file_path):
    """Corregir warnings en un archivo de test"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrón para encontrar return True/False al final de funciones de test
        # Buscar 'return True' seguido de posible whitespace y nueva línea
        content = re.sub(
            r'(\s+)return True(\s*\n)',
            r'\1# Test passed successfully\2',
            content
        )
        
        # Buscar 'return False' en except blocks y reemplazar por raise
        content = re.sub(
            r'(\s+)(return False)(\s*\n)(\s+)(except Exception as e:.*?)\5(return False)',
            r'\1raise AssertionError(f"Test failed: {e}")\3',
            content,
            flags=re.DOTALL
        )
        
        # Patrón más específico para except blocks con return False
        content = re.sub(
            r'(\s+)except Exception as e:(\s*\n)(\s+)print\(f"❌([^"]+)"\)(\s*\n)(\s+)return False',
            r'\1except Exception as e:\2\3print(f"❌\4")\5\6raise AssertionError(f"Test failed: {e}")',
            content
        )
        
        # Si hubo cambios, escribir el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed warnings in: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed in: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 FIXING TEST WARNINGS - SÓTANO 2")
    print("=" * 50)
    
    # Directorio de tests SÓTANO 2
    test_dir = Path(__file__).parent.parent / "tests" / "sotano_2"
    
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        return
    
    # Buscar todos los archivos de test
    test_files = list(test_dir.glob("test_*.py"))
    
    if not test_files:
        print(f"❌ No test files found in: {test_dir}")
        return
    
    print(f"📂 Found {len(test_files)} test files")
    print()
    
    fixed_count = 0
    for test_file in test_files:
        if fix_test_warnings(test_file):
            fixed_count += 1
    
    print()
    print(f"🎉 COMPLETED: Fixed warnings in {fixed_count}/{len(test_files)} files")

if __name__ == "__main__":
    main()
