"""
Script temporal para corregir calls de logger en PISO 2
"""
import os
import re

def fix_logger_calls(file_path):
    """Corregir calls de logger eliminando parámetro extra"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar llamadas a logger con extra
    pattern = r'(self\.logger\.log_(?:info|success|error|warning))\(\s*([^,]+),\s*extra=\{[^}]+\}\s*\)'
    
    def replace_func(match):
        method_call = match.group(1)
        message = match.group(2)
        return f'{method_call}({message})'
    
    # Reemplazar todas las ocurrencias
    new_content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
    
    # También corregir multilinea
    pattern_multiline = r'(self\.logger\.log_(?:info|success|error|warning))\(\s*([^,]+),\s*extra=\{[^}]*\}\s*\)'
    new_content = re.sub(pattern_multiline, replace_func, new_content, flags=re.DOTALL)
    
    # Guardar archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Corregido: {file_path}")

# Archivos del PISO 2 a corregir
files_to_fix = [
    r"c:\Users\v_jac\Desktop\grid\src\core\piso_2\backtest_engine.py",
    r"c:\Users\v_jac\Desktop\grid\src\core\piso_2\backtest_components.py",
    r"c:\Users\v_jac\Desktop\grid\src\core\piso_2\backtest_manager.py"
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        fix_logger_calls(file_path)
    else:
        print(f"❌ No encontrado: {file_path}")

print("🏢 Corrección de logger calls completada para PISO 2")
