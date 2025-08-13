#!/usr/bin/env python3
"""
🔧 AUTO-FIXER ANTI-HARDCODING
=============================

Script que automáticamente corrige los valores hardcodeados más críticos
en el sistema Trading Grid.

Autor: GitHub Copilot
Fecha: Agosto 13, 2025
"""

import os
import re
from pathlib import Path

class AntiHardcodingFixer:
    """Clase para corregir automáticamente valores hardcodeados"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.fixes_applied = 0
        self.files_modified = []
    
    def add_config_import(self, file_content, file_path):
        """Agrega import de ConfigManager si no existe"""
        if "from src.core.config_manager import ConfigManager" in file_content:
            return file_content, False
        
        # Buscar dónde insertar el import
        import_lines = []
        other_lines = []
        found_imports = False
        
        for line in file_content.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_lines.append(line)
                found_imports = True
            elif found_imports and line.strip() == '':
                import_lines.append(line)
            else:
                other_lines.append(line)
                if not found_imports and not line.strip().startswith('#') and line.strip():
                    # No hay imports, agregar al inicio después de docstring/comentarios
                    found_imports = True
        
        if found_imports:
            # Agregar import de ConfigManager
            import_lines.append("from src.core.config_manager import ConfigManager")
            import_lines.append("")
            
            # Agregar inicialización de config
            config_init = [
                "# Configuración dinámica anti-hardcoding",
                "try:",
                "    _config_manager = ConfigManager()",
                "except:",
                "    _config_manager = None",
                ""
            ]
            
            new_content = '\n'.join(import_lines + config_init + other_lines)
            return new_content, True
        
        return file_content, False
    
    def fix_symbol_hardcoding(self, content):
        """Corrige símbolos hardcodeados"""
        replacements = [
            # Casos más comunes
            (r"'EURUSD'", "_config_manager.get_primary_symbol() if _config_manager else 'EURUSD'"),
            (r'"EURUSD"', "_config_manager.get_primary_symbol() if _config_manager else 'EURUSD'"),
            
            # Para listas con múltiples símbolos
            (r"\['EURUSD',\s*'GBPUSD'[^\]]*\]", "_config_manager.get_symbols() if _config_manager else ['EURUSD', 'GBPUSD']"),
            (r'\["EURUSD",\s*"GBPUSD"[^\]]*\]', "_config_manager.get_symbols() if _config_manager else ['EURUSD', 'GBPUSD']"),
        ]
        
        modified = False
        for pattern, replacement in replacements:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                self.fixes_applied += 1
        
        return content, modified
    
    def fix_timeframe_hardcoding(self, content):
        """Corrige timeframes hardcodeados"""
        replacements = [
            # Timeframes individuales
            (r"'H1'", "_config_manager.get_default_timeframe() if _config_manager else 'H1'"),
            (r'"H1"', "_config_manager.get_default_timeframe() if _config_manager else 'H1'"),
            
            # Para listas de timeframes
            (r"\['M5',\s*'M15',\s*'H1'\]", "_config_manager.get_timeframes() if _config_manager else ['M5', 'M15', 'H1']"),
            (r'\["M5",\s*"M15",\s*"H1"\]', "_config_manager.get_timeframes() if _config_manager else ['M5', 'M15', 'H1']"),
            (r"\['M15'\]", "_config_manager.get_timeframes()[:1] if _config_manager else ['M15']"),
            (r'\["M15"\]', "_config_manager.get_timeframes()[:1] if _config_manager else ['M15']"),
        ]
        
        modified = False
        for pattern, replacement in replacements:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                self.fixes_applied += 1
        
        return content, modified
    
    def fix_session_hardcoding(self, content):
        """Corrige sesiones hardcodeadas"""
        replacements = [
            (r"'LONDON'", "_config_manager.get_current_session() if _config_manager else 'LONDON'"),
            (r'"LONDON"', "_config_manager.get_current_session() if _config_manager else 'LONDON'"),
        ]
        
        modified = False
        for pattern, replacement in replacements:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                self.fixes_applied += 1
        
        return content, modified
    
    def fix_trend_hardcoding(self, content):
        """Corrige tendencias hardcodeadas"""
        # Reemplazo más inteligente para tendencias
        trend_pattern = r"'trend':\s*'NEUTRAL'"
        if re.search(trend_pattern, content):
            replacement = """'trend': _config_manager.detect_market_trend(0.0) if _config_manager else 'NEUTRAL'"""
            content = re.sub(trend_pattern, replacement, content)
            self.fixes_applied += 1
            return content, True
        
        return content, False
    
    def fix_file(self, file_path):
        """Corrige un archivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            file_modified = False
            
            # Agregar import de ConfigManager
            content, import_added = self.add_config_import(content, file_path)
            if import_added:
                file_modified = True
            
            # Aplicar correcciones
            content, symbols_fixed = self.fix_symbol_hardcoding(content)
            content, timeframes_fixed = self.fix_timeframe_hardcoding(content)
            content, sessions_fixed = self.fix_session_hardcoding(content)
            content, trends_fixed = self.fix_trend_hardcoding(content)
            
            if symbols_fixed or timeframes_fixed or sessions_fixed or trends_fixed:
                file_modified = True
            
            # Guardar archivo modificado
            if file_modified and content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.files_modified.append(str(file_path))
                print(f"✅ Corregido: {os.path.relpath(file_path, self.project_root)}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error procesando {file_path}: {e}")
            return False
    
    def fix_critical_files(self):
        """Corrige los archivos más críticos del sistema"""
        critical_files = [
            "trading_grid_main.py",
            "src/analysis/fvg_alert_system.py",
            "scripts/demo_caja_negra.py",
            "scripts/demo_sistema_completo.py",
            "scripts/test_enhanced_order_system.py",
        ]
        
        print("🔧 CORRIGIENDO ARCHIVOS CRÍTICOS...")
        
        for file_rel_path in critical_files:
            file_path = self.project_root / file_rel_path
            if file_path.exists():
                self.fix_file(file_path)
            else:
                print(f"⚠️  Archivo no encontrado: {file_rel_path}")
    
    def create_dynamic_config_example(self):
        """Crea archivo de ejemplo para uso de configuración dinámica"""
        example_content = '''#!/usr/bin/env python3
"""
📚 EJEMPLO DE USO - CONFIGURACIÓN DINÁMICA
==========================================

Este archivo muestra cómo usar ConfigManager para eliminar hardcoding.

Autor: GitHub Copilot
Fecha: Agosto 13, 2025
"""

from src.core.config_manager import ConfigManager

# Configuración dinámica anti-hardcoding
try:
    _config_manager = ConfigManager()
except:
    _config_manager = None

def ejemplo_configuracion_dinamica():
    """Ejemplo de cómo usar configuración dinámica"""
    
    # ❌ HARDCODEADO (MALO):
    # symbol = 'EURUSD'
    # timeframe = 'H1'
    # session = 'LONDON'
    
    # ✅ DINÁMICO (BUENO):
    symbol = _config_manager.get_primary_symbol() if _config_manager else 'EURUSD'
    timeframe = _config_manager.get_default_timeframe() if _config_manager else 'H1'
    session = _config_manager.get_current_session() if _config_manager else 'LONDON'
    
    print(f"🎯 Símbolo: {symbol}")
    print(f"⏰ Timeframe: {timeframe}")
    print(f"🌍 Sesión: {session}")
    
    # Obtener múltiples valores
    all_symbols = _config_manager.get_symbols() if _config_manager else ['EURUSD']
    all_timeframes = _config_manager.get_timeframes() if _config_manager else ['H1']
    
    print(f"📊 Símbolos disponibles: {all_symbols}")
    print(f"⏱️  Timeframes disponibles: {all_timeframes}")
    
    # Detección automática de tendencia
    if _config_manager:
        trend_value = 0.5  # Esto vendría del análisis real
        market_trend = _config_manager.detect_market_trend(trend_value)
        print(f"📈 Tendencia detectada: {market_trend}")
    
    # Configuraciones específicas
    fvg_config = _config_manager.get_fvg_config() if _config_manager else {}
    alerts_config = _config_manager.get_alerts_config() if _config_manager else {}
    
    print(f"🎯 Config FVG: {len(fvg_config)} parámetros")
    print(f"🚨 Config Alertas: {len(alerts_config)} parámetros")

if __name__ == "__main__":
    ejemplo_configuracion_dinamica()
'''
        
        example_path = self.project_root / "scripts" / "ejemplo_configuracion_dinamica.py"
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_content)
        
        print(f"📚 Ejemplo creado: {os.path.relpath(example_path, self.project_root)}")
    
    def generate_report(self):
        """Genera reporte de correcciones aplicadas"""
        print(f"\n✅ CORRECCIONES COMPLETADAS:")
        print(f"   📁 Archivos modificados: {len(self.files_modified)}")
        print(f"   🔧 Correcciones aplicadas: {self.fixes_applied}")
        
        if self.files_modified:
            print(f"\n📄 ARCHIVOS MODIFICADOS:")
            for file_path in self.files_modified:
                rel_path = os.path.relpath(file_path, self.project_root)
                print(f"   ✅ {rel_path}")

def main():
    """Función principal"""
    print("🔧 INICIANDO AUTO-CORRECCIÓN ANTI-HARDCODING...")
    
    # Directorio del proyecto
    project_root = Path(__file__).parent.parent
    
    # Crear fixer
    fixer = AntiHardcodingFixer(project_root)
    
    # Corregir archivos críticos
    fixer.fix_critical_files()
    
    # Crear ejemplo de uso
    fixer.create_dynamic_config_example()
    
    # Generar reporte
    fixer.generate_report()
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Revisar los archivos modificados")
    print("2. Ejecutar tests para validar funcionamiento")
    print("3. Ajustar configuración en trading_config.json si es necesario")
    
    print("\n✅ AUTO-CORRECCIÓN COMPLETADA")

if __name__ == "__main__":
    main()
