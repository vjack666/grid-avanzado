"""
Script para corregir todas las referencias de LogLevel en AnalyticsManager
"""

import re

def fix_analytics_manager_loglevel():
    """Corregir todas las referencias incorrectas de LogLevel"""
    
    file_path = r"C:\Users\v_jac\Desktop\grid\src\core\analytics_manager.py"
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazos necesarios
    replacements = [
        # Cambiar self.logger.LogLevel por LogLevel
        (r'self\.logger\.LogLevel\.', 'LogLevel.'),
    ]
    
    # Aplicar reemplazos
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Escribir el archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ AnalyticsManager corregido - referencias LogLevel arregladas")

if __name__ == "__main__":
    fix_analytics_manager_loglevel()
