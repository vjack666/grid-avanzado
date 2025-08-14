#!/usr/bin/env python3
"""
🛡️ GESTOR SEGURO DE TERMINALES - TRADING GRID
=============================================

Gestor que maneja terminales de manera inteligente sin interferir con otros bots
que puedan estar ejecutándose en terminales separados.

REGLAS CRÍTICAS:
- Solo gestiona terminales específicos del Trading Grid
- NO cierra terminales de otros sistemas/bots
- Usa variables de entorno para identificar contexto
- Respeta el aislamiento entre procesos

Fecha: Agosto 13, 2025
Versión: 1.0.0 - Seguridad Terminal
"""

import os
import sys
import psutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class SafeTerminalManager:
    """Gestor seguro de terminales que respeta otros procesos"""
    
    def __init__(self):
        """Inicializar gestor seguro"""
        self.workspace_path = os.environ.get('TRADING_GRID_WORKSPACE', '')
        self.fundednext_path = os.environ.get('FUNDEDNEXT_TERMINAL_PATH', 
                                            r"C:\Program Files\FundedNext MT5 Terminal\terminal64.exe")
        self.system_mode = os.environ.get('GRID_SYSTEM_MODE', 'DEVELOPMENT')
        
        # Identificadores de terminales del Trading Grid
        self.grid_terminal_markers = [
            'TRADING_GRID_WORKSPACE',
            'GRID_SYSTEM_MODE',
            'FUNDEDNEXT_TERMINAL_PATH'
        ]
        
        print(f"🛡️ SafeTerminalManager inicializado")
        print(f"   📁 Workspace: {self.workspace_path}")
        print(f"   ⚙️ Modo: {self.system_mode}")
        print(f"   🎯 FundedNext: {self.fundednext_path}")
    
    def get_safe_terminals(self) -> List[Dict]:
        """Obtener solo terminales que son seguros de gestionar (del Trading Grid)"""
        safe_terminals = []
        
        try:
            # Buscar procesos de PowerShell con variables del Trading Grid
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'environ']):
                try:
                    if proc.info['name'] and 'powershell' in proc.info['name'].lower():
                        # Verificar si tiene marcadores del Trading Grid
                        env_vars = proc.info.get('environ', {})
                        
                        # Solo considerar si tiene nuestras variables específicas
                        has_grid_markers = any(marker in env_vars for marker in self.grid_terminal_markers)
                        
                        if has_grid_markers:
                            safe_terminals.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': proc.info.get('cmdline', []),
                                'environ': env_vars,
                                'is_grid_terminal': True
                            })
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error obteniendo terminales seguros: {e}")
            
        return safe_terminals
    
    def get_fundednext_processes(self) -> List[Dict]:
        """Obtener procesos de FundedNext MT5 (estos SÍ los gestionamos)"""
        fundednext_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    if proc.info['name'] and 'terminal64.exe' in proc.info['name']:
                        exe_path = proc.info.get('exe', '')
                        
                        # Solo FundedNext terminal
                        if 'FundedNext' in exe_path:
                            fundednext_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'exe': exe_path,
                                'cmdline': proc.info.get('cmdline', []),
                                'is_fundednext': True
                            })
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error obteniendo procesos FundedNext: {e}")
            
        return fundednext_processes
    
    def check_terminal_safety(self) -> Dict:
        """Verificar el estado seguro de terminales"""
        safe_terminals = self.get_safe_terminals()
        fundednext_processes = self.get_fundednext_processes()
        
        # Obtener información de otros terminales (solo para información, NO para gestionar)
        other_terminals = self._get_other_terminals_info()
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'workspace_path': self.workspace_path,
            'system_mode': self.system_mode,
            'grid_terminals': len(safe_terminals),
            'grid_terminal_details': safe_terminals,
            'fundednext_processes': len(fundednext_processes),
            'fundednext_details': fundednext_processes,
            'other_terminals_count': len(other_terminals),
            'other_terminals_info': other_terminals,
            'is_safe_to_operate': len(fundednext_processes) > 0,
            'recommendations': []
        }
        
        # Generar recomendaciones
        if len(fundednext_processes) == 0:
            analysis['recommendations'].append("ABRIR_FUNDEDNEXT_MT5")
        
        if len(other_terminals) > 0:
            analysis['recommendations'].append(f"INFORMACIÓN: {len(other_terminals)} terminales externos detectados (NO se gestionarán)")
        
        return analysis
    
    def _get_other_terminals_info(self) -> List[Dict]:
        """Obtener información de otros terminales (solo para información)"""
        other_terminals = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and any(term in proc.info['name'].lower() 
                                               for term in ['cmd', 'powershell', 'bash', 'python']):
                        # Verificar si NO es un terminal del Trading Grid
                        env_vars = proc.environ() if hasattr(proc, 'environ') else {}
                        has_grid_markers = any(marker in env_vars for marker in self.grid_terminal_markers)
                        
                        if not has_grid_markers:
                            other_terminals.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': proc.info.get('cmdline', [])[:3],  # Solo primeros 3 args por seguridad
                                'is_external': True,
                                'note': 'Terminal externo - NO se gestionará'
                            })
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error obteniendo información de terminales externos: {e}")
            
        return other_terminals
    
    def ensure_fundednext_running(self) -> bool:
        """Asegurar que FundedNext esté ejecutándose (sin afectar otros terminales)"""
        fundednext_processes = self.get_fundednext_processes()
        
        if len(fundednext_processes) > 0:
            print(f"✅ FundedNext MT5 ya está ejecutándose ({len(fundednext_processes)} procesos)")
            return True
        
        # Intentar abrir FundedNext
        try:
            if os.path.exists(self.fundednext_path):
                print(f"🚀 Iniciando FundedNext MT5: {self.fundednext_path}")
                subprocess.Popen([self.fundednext_path], shell=False)
                
                # Esperar un momento
                import time
                time.sleep(3)
                
                # Verificar que se inició
                fundednext_processes = self.get_fundednext_processes()
                success = len(fundednext_processes) > 0
                
                if success:
                    print("✅ FundedNext MT5 iniciado correctamente")
                else:
                    print("❌ No se pudo verificar el inicio de FundedNext MT5")
                    
                return success
            else:
                print(f"❌ No se encontró FundedNext MT5 en: {self.fundednext_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error iniciando FundedNext MT5: {e}")
            return False
    
    def print_terminal_status(self):
        """Mostrar estado actual de terminales de manera segura"""
        analysis = self.check_terminal_safety()
        
        print(f"\n🛡️ === ESTADO SEGURO DE TERMINALES ===")
        print(f"⏰ Timestamp: {analysis['timestamp']}")
        print(f"📁 Workspace: {analysis['workspace_path']}")
        print(f"⚙️ Modo Sistema: {analysis['system_mode']}")
        print(f"\n📊 RESUMEN:")
        print(f"   🎯 Terminales Trading Grid: {analysis['grid_terminals']}")
        print(f"   🏦 Procesos FundedNext: {analysis['fundednext_processes']}")
        print(f"   ℹ️ Terminales externos (info): {analysis['other_terminals_count']}")
        print(f"   ✅ Seguro operar: {analysis['is_safe_to_operate']}")
        
        if analysis['recommendations']:
            print(f"\n📋 RECOMENDACIONES:")
            for rec in analysis['recommendations']:
                print(f"   • {rec}")
        
        if analysis['other_terminals_count'] > 0:
            print(f"\n🔒 TERMINALES EXTERNOS DETECTADOS (NO gestionados):")
            for terminal in analysis['other_terminals_info']:
                print(f"   • PID {terminal['pid']}: {terminal['name']} - {terminal['note']}")
        
        print(f"\n{'='*50}")


def main():
    """Función principal de verificación segura"""
    print("🛡️ INICIANDO VERIFICACIÓN SEGURA DE TERMINALES")
    print("=" * 60)
    
    # Crear gestor seguro
    manager = SafeTerminalManager()
    
    # Mostrar estado actual
    manager.print_terminal_status()
    
    # Asegurar que FundedNext esté funcionando
    print(f"\n🎯 VERIFICANDO FUNDEDNEXT MT5...")
    success = manager.ensure_fundednext_running()
    
    if success:
        print(f"\n✅ SISTEMA LISTO PARA OPERAR")
        print(f"   • FundedNext MT5 funcionando")
        print(f"   • Otros terminales respetados")
        print(f"   • Modo seguro activado")
    else:
        print(f"\n❌ REQUIERE ATENCIÓN")
        print(f"   • Verificar instalación FundedNext MT5")
        print(f"   • Revisar permisos del sistema")
    
    return success


if __name__ == "__main__":
    main()
