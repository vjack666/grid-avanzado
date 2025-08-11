"""
Script de Reorganización del Sistema Trading Grid
Organiza archivos, elimina duplicados y crea estructura final
"""

import os
import shutil
from pathlib import Path

# Definir la estructura final deseada
ESTRUCTURA_FINAL = {
    'src/': {
        'core/': ['main.py', 'order_manager.py', 'riskbot_mt5.py'],
        'analysis/': ['grid_bollinger.py', 'analisis_estocastico_m15.py'],
        'utils/': ['data_logger.py', 'descarga_velas.py', 'trading_schedule.py'],
        'interfaces/': ['index.html']
    },
    'config/': ['config.py'],
    'tests/': ['test_sistema.py'],
    'data/': [],  # Mantener estructura de datos existente
    'documentacion/': [],  # Mantener documentación existente
    'logs/': [],  # Para archivos de log
    'backup/': []  # Para respaldos
}

def limpiar_pycache():
    """Elimina todas las carpetas __pycache__"""
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            print(f"🗑️ Eliminando {pycache_path}")
            shutil.rmtree(pycache_path, ignore_errors=True)

def eliminar_duplicados():
    """Elimina archivos duplicados y mantiene las versiones más recientes"""
    
    # Archivos duplicados conocidos en backup que se pueden eliminar
    duplicados_backup = [
        'backup/main (1).py',
        'backup/main (2).py', 
        'backup/grid_bollinger (2).py',
        'backup/config (2).py',
        'backup/analisis_estocastico_m15 (2).py',
        'backup/trading_schedule (2).py',
        'backup/riskbot_mt5 (2).py'
    ]
    
    for archivo in duplicados_backup:
        if os.path.exists(archivo):
            print(f"🗑️ Eliminando duplicado: {archivo}")
            os.remove(archivo)

def crear_estructura_directorios():
    """Crea los directorios necesarios si no existen"""
    directorios = [
        'src/core',
        'src/analysis', 
        'src/utils',
        'src/interfaces',
        'config',
        'tests',
        'logs',
        'scripts'  # Para scripts de utilidad
    ]
    
    for directorio in directorios:
        os.makedirs(directorio, exist_ok=True)
        print(f"📁 Directorio asegurado: {directorio}")

def mover_archivo_si_existe(origen, destino):
    """Mueve un archivo si existe, creando el directorio destino si es necesario"""
    if os.path.exists(origen):
        # Crear directorio destino si no existe
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        
        # Si el destino ya existe, hacer backup
        if os.path.exists(destino):
            backup_path = f"{destino}.backup"
            print(f"⚠️ Respaldando {destino} → {backup_path}")
            shutil.move(destino, backup_path)
        
        print(f"📦 Moviendo {origen} → {destino}")
        shutil.move(origen, destino)
        return True
    return False

def organizar_archivos():
    """Organiza los archivos en la estructura final"""
    
    # Mover archivos a src/interfaces si existen en raíz
    mover_archivo_si_existe('index.html', 'src/interfaces/index.html')
    
    # Los archivos ya están en src/, solo necesitamos asegurar que estén en el lugar correcto
    # Verificar que todos los archivos estén en su lugar
    
    archivos_requeridos = {
        'src/core/main.py': 'Controlador principal del sistema',
        'src/core/order_manager.py': 'Gestor de órdenes MT5',
        'src/core/riskbot_mt5.py': 'Sistema de gestión de riesgo',
        'src/analysis/grid_bollinger.py': 'Sistema Grid con Bollinger Bands',
        'src/analysis/analisis_estocastico_m15.py': 'Análisis estocástico M15',
        'src/utils/data_logger.py': 'Sistema de logging',
        'src/utils/descarga_velas.py': 'Descarga de datos MT5',
        'src/utils/trading_schedule.py': 'Horarios de trading',
        'config/config.py': 'Configuración global',
        'tests/test_sistema.py': 'Suite de tests'
    }
    
    print("\\n📋 VERIFICANDO ARCHIVOS PRINCIPALES:")
    for archivo, descripcion in archivos_requeridos.items():
        if os.path.exists(archivo):
            print(f"✅ {archivo} - {descripcion}")
        else:
            print(f"❌ {archivo} - {descripcion} [FALTANTE]")

def crear_archivo_init():
    """Crea archivos __init__.py para hacer los directorios paquetes de Python"""
    directorios_python = [
        'src',
        'src/core',
        'src/analysis', 
        'src/utils',
        'src/interfaces',
        'tests'
    ]
    
    for directorio in directorios_python:
        init_path = os.path.join(directorio, '__init__.py')
        if not os.path.exists(init_path):
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(f'"""{directorio.replace("/", ".")} package"""\\n')
            print(f"📄 Creado: {init_path}")

def crear_requirements():
    """Crea archivo requirements.txt con las dependencias"""
    requirements = [
        "MetaTrader5>=5.0.0",
        "pandas>=1.5.0",
        "numpy>=1.20.0", 
        "rich>=13.0.0",
        "keyboard>=0.13.0",
        "pytz>=2022.0"
    ]
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        for req in requirements:
            f.write(f"{req}\\n")
    
    print("📄 Creado: requirements.txt")

def crear_readme_principal():
    """Crea README.md principal del proyecto"""
    readme_content = '''# 📊 Sistema Trading Grid

Sistema automatizado de trading con Grid y análisis técnico para MetaTrader 5.

## 🏗️ Estructura del Proyecto

```
grid/
├── src/                    # Código fuente principal
│   ├── core/              # Componentes principales
│   ├── analysis/          # Análisis técnico
│   ├── utils/             # Utilidades
│   └── interfaces/        # Interfaces de usuario
├── config/                # Configuración
├── tests/                 # Tests automatizados
├── data/                  # Datos históricos
├── documentacion/         # Documentación del proyecto
├── logs/                  # Archivos de log
└── backup/               # Respaldos

```

## 🚀 Inicio Rápido

1. **Instalación de dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar tests:**
   ```bash
   python tests/test_sistema.py
   ```

3. **Ejecutar sistema principal:**
   ```bash
   python src/core/main.py
   ```

## 📊 Componentes

- **Grid Bollinger:** Sistema de Grid con Bandas de Bollinger
- **Análisis Estocástico:** Análisis técnico en M15
- **Risk Management:** Gestión automática de riesgo
- **Data Logger:** Sistema de logging estructurado
- **Trading Schedule:** Horarios de operación

## 📝 Documentación

Ver `documentacion/README.md` para documentación completa.
'''
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("📄 Creado: README.md")

def main():
    """Función principal de reorganización"""
    print("🔧 INICIANDO REORGANIZACIÓN DEL SISTEMA TRADING GRID")
    print("=" * 60)
    
    # Paso 1: Limpiar archivos temporales
    print("\\n1️⃣ LIMPIANDO ARCHIVOS TEMPORALES")
    limpiar_pycache()
    
    # Paso 2: Eliminar duplicados
    print("\\n2️⃣ ELIMINANDO DUPLICADOS")
    eliminar_duplicados()
    
    # Paso 3: Crear estructura de directorios
    print("\\n3️⃣ CREANDO ESTRUCTURA DE DIRECTORIOS")
    crear_estructura_directorios()
    
    # Paso 4: Organizar archivos
    print("\\n4️⃣ ORGANIZANDO ARCHIVOS")
    organizar_archivos()
    
    # Paso 5: Crear archivos __init__.py
    print("\\n5️⃣ CREANDO ARCHIVOS PYTHON")
    crear_archivo_init()
    
    # Paso 6: Crear archivos de configuración
    print("\\n6️⃣ CREANDO ARCHIVOS DE CONFIGURACIÓN")
    crear_requirements()
    crear_readme_principal()
    
    print("\\n" + "=" * 60)
    print("✅ REORGANIZACIÓN COMPLETADA")
    print("\\n🎯 PRÓXIMOS PASOS:")
    print("  1. Revisar estructura con: dir /s")
    print("  2. Ejecutar tests: python tests/test_sistema.py")
    print("  3. Verificar documentación: documentacion/README.md")

if __name__ == "__main__":
    main()
