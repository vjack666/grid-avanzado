"""
Script para corregir ConfigManager - convertir métodos estáticos a instancia
"""

import re

def fix_config_manager():
    """Corregir todos los métodos estáticos del ConfigManager"""
    
    file_path = r"C:\Users\v_jac\Desktop\grid\src\core\config_manager.py"
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazos necesarios
    replacements = [
        # Cambiar @staticmethod por método de instancia
        (r'@staticmethod\s+', ''),
        
        # Cambiar ConfigManager._safe_data_dir por self._safe_data_dir
        (r'ConfigManager\._safe_data_dir', 'self._safe_data_dir'),
        
        # Cambiar ConfigManager.get_xxx() por self.get_xxx()
        (r'ConfigManager\.get_([a-zA-Z_]+)\(\)', r'self.get_\1()'),
        
        # Corregir definiciones de métodos estáticos
        (r'def (get_[a-zA-Z_]+)\(\) -> ', r'def \1(self) -> '),
        (r'def (ensure_directories)\(\) -> ', r'def \1(self) -> '),
        (r'def (get_all_paths)\(\) -> ', r'def \1(self) -> '),
    ]
    
    # Aplicar reemplazos
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Escribir el archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ ConfigManager corregido - métodos convertidos a instancia")

if __name__ == "__main__":
    fix_config_manager()
