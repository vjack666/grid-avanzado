#!/usr/bin/env python3
"""
🚨 VERIFICADOR Y CORRECTOR DE TERMINAL MT5 EXCLUSIVO
==================================================

Script para verificar y mantener el uso exclusivo del FundedNext MT5 Terminal
según las reglas del sistema Trading Grid.

REGLA CRÍTICA: Solo FundedNext MT5 Terminal permitido
- Cierra otros terminales MT5 no autorizados
- Verifica que FundedNext MT5 esté funcionando
- Reporta estado y toma acciones correctivas

Fecha: Agosto 12, 2025
Estado: Sistema de verificación automática
"""

import os
import sys
import psutil
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Configurar paths
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path.absolute()))

# Import del sistema
try:
    from src.core.common_imports import pd, Dict
    from core.config_manager import ConfigManager
    from core.logger_manager import LoggerManager  
    from core.error_manager import ErrorManager
    from core.fundednext_mt5_manager import FundedNextMT5Manager
    print("✅ Imports del sistema cargados correctamente")
except ImportError as e:
    print(f"❌ Error importando sistema: {e}")
    sys.exit(1)

class MT5TerminalChecker:
    """Verificador y corrector de terminales MT5"""
    
    def __init__(self):
        """Inicializar checker"""
        self.fundednext_path = r"C:\Program Files\FundedNext MT5 Terminal\terminal64.exe"
        self.authorized_paths = [self.fundednext_path]
        self.detected_terminals = []
        
        # Inicializar managers
        try:
            self.config = ConfigManager()
            self.logger = LoggerManager()
            self.error = ErrorManager(self.logger)
            print("✅ Managers del sistema inicializados")
        except Exception as e:
            print(f"❌ Error inicializando managers: {e}")
            sys.exit(1)
    
    def scan_mt5_terminals(self) -> List[Dict]:
        """
        Escanear todos los terminales MT5 ejecutándose
        
        Returns:
            List con información de cada terminal encontrado
        """
        print("\n🔍 ESCANEANDO TERMINALES MT5...")
        print("=" * 50)
        
        terminals = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'status']):
            try:
                # Buscar procesos terminal64.exe
                if proc.info['name'] and 'terminal64' in proc.info['name'].lower():
                    terminal_info = {
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'exe_path': proc.info['exe'],
                        'status': proc.info['status'],
                        'is_authorized': False,
                        'is_fundednext': False
                    }
                    
                    # Verificar si es el terminal autorizado
                    if proc.info['exe']:
                        if 'FundedNext' in proc.info['exe']:
                            terminal_info['is_fundednext'] = True
                            terminal_info['is_authorized'] = True
                            print(f"✅ FundedNext MT5 Terminal encontrado (PID: {proc.info['pid']})")
                        else:
                            print(f"⚠️ Terminal MT5 NO autorizado encontrado (PID: {proc.info['pid']})")
                            print(f"   Ruta: {proc.info['exe']}")
                    
                    terminals.append(terminal_info)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        self.detected_terminals = terminals
        
        if not terminals:
            print("ℹ️ No se encontraron terminales MT5 ejecutándose")
        
        return terminals
    
    def analyze_terminal_situation(self) -> Dict:
        """
        Analizar la situación actual de terminales MT5
        
        Returns:
            Dict con análisis de la situación
        """
        terminals = self.scan_mt5_terminals()
        
        analysis = {
            'total_terminals': len(terminals),
            'fundednext_running': False,
            'unauthorized_terminals': [],
            'authorized_terminals': [],
            'action_required': False,
            'recommended_actions': []
        }
        
        for terminal in terminals:
            if terminal['is_fundednext']:
                analysis['fundednext_running'] = True
                analysis['authorized_terminals'].append(terminal)
            else:
                analysis['unauthorized_terminals'].append(terminal)
                analysis['action_required'] = True
        
        # Determinar acciones recomendadas
        if analysis['unauthorized_terminals']:
            analysis['recommended_actions'].append("CERRAR_TERMINALES_NO_AUTORIZADOS")
        
        if not analysis['fundednext_running']:
            analysis['recommended_actions'].append("ABRIR_FUNDEDNEXT_MT5")
        
        return analysis
    
    def close_unauthorized_terminals(self, unauthorized_terminals: List[Dict]) -> bool:
        """
        Cerrar terminales MT5 no autorizados
        
        Args:
            unauthorized_terminals: Lista de terminales a cerrar
            
        Returns:
            bool: True si se cerraron exitosamente
        """
        print("\n🚨 CERRANDO TERMINALES NO AUTORIZADOS...")
        print("=" * 50)
        
        success_count = 0
        
        for terminal in unauthorized_terminals:
            try:
                pid = terminal['pid']
                exe_path = terminal.get('exe_path', 'Desconocido')
                
                print(f"🔄 Cerrando terminal PID {pid}: {exe_path}")
                
                # Intentar cerrar gracefully primero
                proc = psutil.Process(pid)
                proc.terminate()
                
                # Esperar unos segundos
                try:
                    proc.wait(timeout=5)
                    print(f"✅ Terminal PID {pid} cerrado exitosamente")
                    success_count += 1
                except psutil.TimeoutExpired:
                    # Force kill si no responde
                    print(f"⚠️ Forzando cierre del terminal PID {pid}")
                    proc.kill()
                    success_count += 1
                    
            except Exception as e:
                print(f"❌ Error cerrando terminal PID {terminal['pid']}: {e}")
        
        print(f"📊 Resultado: {success_count}/{len(unauthorized_terminals)} terminales cerrados")
        return success_count == len(unauthorized_terminals)
    
    def start_fundednext_terminal(self) -> bool:
        """
        Iniciar FundedNext MT5 Terminal si no está ejecutándose
        
        Returns:
            bool: True si se inició exitosamente
        """
        print("\n🚀 INICIANDO FUNDEDNEXT MT5 TERMINAL...")
        print("=" * 50)
        
        # Verificar que el ejecutable existe
        if not os.path.exists(self.fundednext_path):
            print(f"❌ FundedNext MT5 Terminal no encontrado en: {self.fundednext_path}")
            return False
        
        try:
            print(f"🔄 Iniciando: {self.fundednext_path}")
            
            # Iniciar el terminal
            subprocess.Popen([self.fundednext_path], 
                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            
            print("✅ FundedNext MT5 Terminal iniciado")
            print("ℹ️ Esperando unos segundos para que se complete la inicialización...")
            
            import time
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando FundedNext MT5 Terminal: {e}")
            return False
    
    def verify_mt5_connection(self) -> bool:
        """
        Verificar que MT5 está funcionando correctamente
        
        Returns:
            bool: True si la conexión es exitosa
        """
        print("\n🔗 VERIFICANDO CONEXIÓN MT5...")
        print("=" * 30)
        
        try:
            import MetaTrader5 as mt5
            
            # Intentar inicializar MT5
            if not mt5.initialize():
                print("❌ No se pudo inicializar conexión MT5")
                return False
            
            # Obtener información de la cuenta
            account_info = mt5.account_info()
            if account_info is None:
                print("❌ No se pudo obtener información de la cuenta")
                mt5.shutdown()
                return False
            
            print(f"✅ Conexión MT5 exitosa")
            print(f"   Cuenta: {account_info.login}")
            print(f"   Servidor: {account_info.server}")
            print(f"   Balance: ${account_info.balance:.2f}")
            
            mt5.shutdown()
            return True
            
        except Exception as e:
            print(f"❌ Error verificando conexión MT5: {e}")
            return False
    
    def run_full_check(self) -> bool:
        """
        Ejecutar verificación completa y correcciones
        
        Returns:
            bool: True si todo está correcto al final
        """
        print("🚨 VERIFICADOR MT5 EXCLUSIVO - TRADING GRID")
        print("=" * 60)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Regla: Solo FundedNext MT5 Terminal permitido")
        
        # Paso 1: Analizar situación actual
        analysis = self.analyze_terminal_situation()
        
        print(f"\n📊 ANÁLISIS INICIAL:")
        print(f"   Terminales totales: {analysis['total_terminals']}")
        print(f"   FundedNext ejecutándose: {'✅' if analysis['fundednext_running'] else '❌'}")
        print(f"   Terminales no autorizados: {len(analysis['unauthorized_terminals'])}")
        print(f"   Acción requerida: {'✅' if analysis['action_required'] else '❌'}")
        
        # Paso 2: Cerrar terminales no autorizados
        if analysis['unauthorized_terminals']:
            success = self.close_unauthorized_terminals(analysis['unauthorized_terminals'])
            if not success:
                print("❌ No se pudieron cerrar todos los terminales no autorizados")
                return False
        
        # Paso 3: Iniciar FundedNext si no está ejecutándose
        if not analysis['fundednext_running']:
            success = self.start_fundednext_terminal()
            if not success:
                print("❌ No se pudo iniciar FundedNext MT5 Terminal")
                return False
        
        # Paso 4: Verificar conexión final
        print("\n⏳ Esperando estabilización del sistema...")
        import time
        time.sleep(5)
        
        connection_ok = self.verify_mt5_connection()
        
        # Resultado final
        print("\n🏆 RESULTADO FINAL:")
        print("=" * 30)
        if connection_ok:
            print("✅ Sistema MT5 funcionando correctamente")
            print("✅ Solo FundedNext MT5 Terminal ejecutándose")
            print("✅ Conexión MT5 verificada")
            return True
        else:
            print("❌ Problemas detectados en el sistema MT5")
            return False

def main():
    """Función principal"""
    try:
        checker = MT5TerminalChecker()
        success = checker.run_full_check()
        
        if success:
            print("\n🎉 VERIFICACIÓN COMPLETADA EXITOSAMENTE")
            print("   El sistema cumple con las reglas de terminal MT5 exclusivo")
            sys.exit(0)
        else:
            print("\n⚠️ VERIFICACIÓN FALLÓ")
            print("   Se requiere intervención manual")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Verificación interrumpida por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
